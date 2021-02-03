from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from dbfread import DBF
from shutil import copyfile
import time
import pickle
from datetime import datetime
import os
import requests
import json
import pandas as pd

autentica = ['JK88CZGLC1WD', 'DVVCIYG4GESM', 'TQBZEVVJPMR0', '27994FQPMY0J', 'N951C3RKYZ8Z', '6HA07HVEI7AZ', 'IGPPSYNF27JC', 'F1ZQ7GJJ2N7J', '8XSUVCQQLQ2Y', 'EDJRA1A52N3K', 'FLBY92KGFTJG', '1AINOXR4DKLH']
dialimite = 10

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

keys = pickle.load(open("keys.pkl", "rb"))

client_secret = "TnkpxGW9LnCbaYrnGvetdZ2lfj3udxjE"
client_id = "6545766642471155"
tempo = 180
print("MercadoSinc v1.0")

def getqtd(file):
    qtd = {}
    esto = DBF(file, load = True)
    for i in esto.records:
        if int(i['QTDE']) < 0:
            continue
        if i['PROD'] not in qtd:
            qtd[i['PROD']] = int(i['QTDE'])
        else:
            if int(i['QTDE']) > qtd[i['PROD']]:
                qtd[i['PROD']] = int(i['QTDE'])
    return qtd

def modolist(ean, n, driver):
    print("Atualizando: ", ean)
    t = 6
    driver.get("https://app.olist.com/")
    time.sleep(t)
    driver.find_element_by_id("email").send_keys("compras@grupoabib.com.br")
    pw = driver.find_element_by_id("password")
    pw.send_keys("FeViMa0406")
    pw.submit()
    driver.get("https://app.olist.com/stock/stock-and-price/")
    time.sleep(t)
    search = driver.find_element_by_id("id_search")
    time.sleep(t)
    search.send_keys(ean)
    time.sleep(t)
    search.submit()
    try:
        time.sleep(t)
        st = driver.find_element_by_name("stock")
        time.sleep(t)
        st.click()
        for x in range(15):
            st.send_keys(Keys.DELETE)
        time.sleep(t)
        st.send_keys(n)
        time.sleep(t)
        st.send_keys(Keys.ENTER)
        time.sleep(t)
    except Exception as e:
        print(e)

def modp(nml, n, token, reftoken, conta, ean):
    print("Atualizando:", nml)
    if nml[0] == "#":
        nml = nml[1:]
    headers = {'Authorization':'Bearer '+token, "content-type": "application/json", "accept": "application/json"}
    url = "https://api.mercadolibre.com/items/MLB"+nml
    s = json.loads(requests.get(url, headers=headers))
    if len(s['variations']) > 1:
        arg = {'variations':[]}
        for n, i in enumerate(arg):
            if i['id'] = ean:
                arg['variations'].append({"id":i['id'], "available_quantity":n}) 
    else:
        arg = {'available_quantity': n}
    r = requests.put(url, data = json.dumps(arg), headers = headers)
    if r.status_code == 200:
        print(nml, "atualizado com sucesso.")
    elif r.status_code == 403 or r.status_code == 401:
        print("Atualizando Access Token...")
        ref = requests.post("https://api.mercadolibre.com/oauth/token?grant_type=refresh_token&client_id="+client_id+"&client_secret="+client_secret+"&refresh_token="+reftoken)
        resp = json.loads(ref.text)
        if conta == "s":
            token_splash = resp['access_token']
            refresh_splash = resp['refresh_token']
            keys['token_s'] = token_splash
            keys['refresh_s'] = refresh_splash
            pickle.dump(keys, open("keys.pkl", "wb"))
            modp(nml, n, token_splash, refresh_splash, 's')
        else:
            token_abib = resp['access_token']
            refresh_abib = resp['refresh_token']
            keys['token_a'] = token_abib
            keys['refresh_a'] = refresh_abib
            pickle.dump(keys, open("keys.pkl", "wb"))
            modp(nml, n, token_abib, refresh_abib, 'a')
    else:
        raise(Exception("Erro do servidor Mercado Livre: "+r.text))



def cic():
    #carrega os tokens
    dia = datetime.today().day
    ind = datetime.today().month - 1 and dia == dialimite:
    if ind != pickle.load('a.pkl', 'rb'):
        while True:
            if input("Chave de Acesso deste mês: ") == autentica[ind]:
                pickle.dump(inp, open("a.pkl", "wb"))
                print("Acesso liberado! a próxima chave deve ser inserida no mesmo dia, mês que vem.")
                break
            else:
                print("Chave errada! Tente Novamente")
    keys = pickle.load(open("keys.pkl", "rb"))
    token_splash = keys['token_s']
    refresh_splash = keys['refresh_s']
    token_abib = keys['token_a']
    refresh_abib = keys['refresh_a']

    #carrega quantidade local e espera
    qtd = getqtd("qtdloj.DBF")
    print('Esperando...('+datetime.now().strftime("%d/%m/%Y %H:%M:%S)"))
    time.sleep(tempo)

    #carrega quantidade global
    qtd2 = getqtd("//Fxsorbase/acsn/CENTRAL/DADOS/qtdloj.DBF")

    #carrega base de dados
    dsplash = pickle.load(open("data_splash.pkl", "rb"))
    dabib = pickle.load(open("data_abib.pkl", "rb"))

    #compara local x global
    lista = []
    mciclo = []
    for i in qtd2:
        if i not in qtd:
            print(i, "cadastrado no sistema local.")
            continue
        if qtd2[i] != qtd[i] and i not in mciclo:
            lista.append([i, qtd2[i]])
            mciclo.append(i)

    #sincroniza as diferenças
    erros = pickle.load(open('erros.pkl', 'rb'))
    for i in lista:
        try:
            modp(dsplash[i[0]][1], int(i[1]), token_splash, refresh_splash, 's', i[0])
        except Exception as e:
            erros.append([i[0], int(i[1]), str(e), 'MLsplash'])
            if e == KeyError:
                print(i, "não está cadastrado online, ou seu cadastro está errado. Registrado em C:/MercadoSinc/relatorios/")
            elif "Erro do servidor Mercado Livre:" in str(e):
                print(str(e))
            else:
                print("Erro:",i,"Registrado em C:/MercadoSinc/relatorios/")
        try:
            modp(dabib[i[0]][1], int(i[1]), token_abib, refresh_abib, 'a', i[0])
        except Exception as e:
            erros.append([i[0], int(i[1]), str(e), 'MLabib'])
            if e == KeyError:
                print(i, "não está cadastrado online, ou seu cadastro está errado. Registrado em C:/MercadoSinc/relatorios/")
            elif "Erro do servidor Mercado Livre:" in str(e):
                print(str(e))
            else:
                print("Erro:",i,"Registrado em C:/MercadoSinc/relatorios/")
        driver = webdriver.Chrome(options = options)
        try:
            modolist(i[0], int(i[1]), driver)
        except Exception as e:
            erros.append([i[0], int(i[1]), str(e), 'olist'])
            print(i,"não está cadastrado no OLIST, ou seu cadastro está errado.")
        driver.close()
    pickle.dump(erros, open('erros.pkl', 'wb'))
    if len(lista) > 0:
        copyfile("//Fxsorbase/acsn/CENTRAL/DADOS/qtdloj.DBF", os.getcwd()+ "/qtdloj.DBF")
    else:
        #corrige erros quando não há nada para sincronizar
        print("Iniciando correção automática...")
        erros = pickle.load(open("erros.pkl", "rb"))
        log = pickle.load(open('log.pkl', 'rb'))
        for i in erros:
            print("Corrigindo:", i[0])
            if i[0] == i[2]:
                continue
            if i[3] == "MLabib":
                try:
                    modp(dabib[i[0]][1], i[1], token_abib, refresh_abib, 'a')
                except Exception as e:
                    if e == KeyError:
                        texto = "Este produto não está cadastrado online, ou seu cadastro está errado."
                    elif "Erro do servidor Mercado Livre:" in str(e):
                        texto = "Erro no servidor Mercado Livre: "+str(e)
                    else:
                        texto = "Erro desconhecido: "+str(e)
                    log.append({"Código": i[0], "Quantidade":i[1],"Erro": texto, "Conta:":'ML - Abib'})
            elif i[3] == "MLsplash":
                try:
                    modp(dsplash[i[0]][1], i[1], token_splash, refresh_splash, 's')
                except Exception as e:
                    if e == KeyError:
                        texto = "Este produto não está cadastrado online, ou seu cadastro está errado."
                    elif "Erro do servidor Mercado Livre:" in str(e):
                        texto = "Erro no servidor Mercado Livre: "+str(e)
                    else:
                        texto = "Erro desconhecido: "+str(e)
                    log.append({"Código": i[0], "Quantidade":i[1],"Erro": texto, "Conta:":'ML - Splash'})
            elif i[3] == "olist":
                driver = webdriver.Chrome(options = options)
                try:
                    modolist(i[0], i[1], driver)
                except Exception as e:
                    print(i[0], "não está cadastrado no olist, ou seu cadastro ertá errado.")
                driver.close()
        pickle.dump([], open('erros.pkl', 'wb'))
        pickle.dump(log, open('log.pkl', 'wb'))
        df = pd.DataFrame(log)
        df.to_excel("/relatorios/erros.xlsx")

if __name__ == "__main__":
    while True:
        try:
            cic()
        except Exception as e:
            print(e)
