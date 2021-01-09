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

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

keys = pickle.load(open("keys.pkl", "rb"))
client_secret = "TnkpxGW9LnCbaYrnGvetdZ2lfj3udxjE"
client_id = "6545766642471155"
token_splash = keys['token_s']
refresh_splash = keys['refresh_s']
token_abib = keys['token_a']
refresh_abib = keys['refresh_a']
tempo = 180

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

def modp(nml, n, token, reftoken, conta):
    print("Atualizando:", nml)
    if nml[0] == "#":
        nml = nml[1:]
    headers = {'Authorization':'Bearer '+token, "content-type": "application/json", "accept": "application/json"}
    arg = "{available_quantity: "+str(n)+"}"
    url = "https://api.mercadolibre.com/items/MLB"+nml
    r = requests.put(url, data = arg, headers = headers)
    a = json.loads(r.text)
    print(a)
    if r.status_code == 200:
        print(nml, "atualizado com sucesso.")
    else:
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


def cic():
    qtd = getqtd("qtdloj.DBF")
    print('Esperando...('+datetime.now().strftime("%d/%m/%Y %H:%M:%S)"))
    time.sleep(tempo)
    qtd2 = getqtd("//Fxsorbase/acsn/CENTRAL/DADOS/qtdloj.DBF")
    dsplash = pickle.load(open("data_splash.pkl", "rb"))
    dabib = pickle.load(open("data_abib.pkl", "rb"))
    lista = []
    mciclo = []
    for i in qtd2:
        if i not in qtd:
            continue
        if qtd2[i] != qtd[i] and i not in mciclo:
            lista.append([i, qtd2[i]])
            mciclo.append(i)
    for i in lista:
        try:
            modp(dsplash[i[0]][1], int(i[1]), token_splash, refresh_splash, 's')
        except Exception as e:
            log = pickle.load(open('erros.pkl', 'rb'))
            log.append([i[0], int(i[1]), str(e), 'MLsplash'])
            pickle.dump(log, open('erros.pkl', 'wb'))
            print(e)
        try:
            modp(dabib[i[0]][1], int(i[1]), token_abib, refresh_abib, 'a')
        except Exception as e:
            log = pickle.load(open('erros.pkl', 'rb'))
            log.append([i[0], int(i[1]), str(e), 'MLabib'])
            pickle.dump(log, open('erros.pkl', 'wb'))
            print(e)
        driver = webdriver.Chrome(options = options)
        try:
            modolist(i[0], int(i[1]), driver)
        except Exception as e:
            log = pickle.load(open('erros.pkl', 'rb'))
            log.append([i[0], int(i[1]), str(e), 'olist'])
            pickle.dump(log, open('erros.pkl', 'wb'))
            print(e)
        driver.close()
    if len(lista) > 0:
        copyfile("//Fxsorbase/acsn/CENTRAL/DADOS/qtdloj.DBF", os.getcwd()+ "/qtdloj.DBF")
    else:
        erros = pickle.load(open("erros.pkl", "rb"))
        corrigido = []
        for i in erros:
            print("Corrigindo:", i[0])
            if i[0] == i[2]:
                continue
            if i[3] == "MLabib":
                try:
                    modp(dabib[i[0]][1], i[1], token_abib, refresh_abib, 'a')
                    corrigido.append(i)
                except Exception as e:
                    print(e)
            elif i[3] == "MLsplash":
                try:
                    modp(dsplash[i[0]][1], i[1], token_splash, refresh_splash, 's')
                    corrigido.append(i)
                except Exception as e:
                    print(e)
            elif i[3] == "olist":
                driver = webdriver.Chrome(options = options)
                try:
                    modolist(i[0], i[1], driver)
                    corrigido.append(i)
                except Exception as e:
                    print(e)
                driver.close()
        atual = [x for x in erros if x not in corrigido]
        pickle.dump([], open('erros.pkl', 'wb'))
        pickle.dump(atual, open('erros_b.pkl', 'wb'))

if __name__ == "__main__":
    while True:
        try:
            cic()
        except Exception as e:
            print(e)
