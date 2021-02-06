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
import PySimpleGUI as gui
import apiutils

acc = pickle.load(open("accounts.pkl", "rb"))
for i in acc:
    acc['api_obj'] = apiutils.meli(acc['key_path'])

layout = [[gui.Text(key = "texto")]]
janela = gui.Window("MercadoSinc v1").layout(layout)

#lista de chaves e dia limite
autentica = ['JK88CZGLC1WD', 'DVVCIYG4GESM', 'TQBZEVVJPMR0', '27994FQPMY0J', 'N951C3RKYZ8Z', '6HA07HVEI7AZ', 'IGPPSYNF27JC', 'F1ZQ7GJJ2N7J', '8XSUVCQQLQ2Y', 'EDJRA1A52N3K', 'FLBY92KGFTJG', '1AINOXR4DKLH']
dialimite = 10

#configurações do driver selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

tempo = 180

def atualizajanela(*args):
    event, values = janela.Read(timeout = 1)
    janela['texto'].update(" ".join(args))

#input: filepath de um arquivo .DBF, output: dict de quantidades
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

#atualiza olist
def modolist(ean, n, driver):
    atualizajanela("Atualizando: ", ean)
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
        atualizajanela(str(e))

#atualiza ML
def modp(nml, n, acdic, ean):
    atualizajanela("Atualizando:", nml)
    api_obj = acdic['api_obj']
    if nml[0] == "#":
        nml = nml[1:]
    nml = "MLB"+nml

    #checa se o produto tem variações, e caso sim, modifica apenas uma delas
    s = api_obj.getitem(nml, 'variations')
    if len(s) > 1:
        for i in s:
            if i['id'] == ean:
                r = api_obj.setres(nml, "available_quantity", n, ean)
    else:
        r = api_obj.setres(nml, "available_quantity", n, ean)

    #lida com a resposta
    if r == 200:
        atualizajanela(nml, "atualizado com sucesso.")
    else:
        raise(Exception("Erro do servidor Mercado Livre: "+ r))

def cic():
    #checa por autorização de acesso
    dia = datetime.today().day
    ind = datetime.today().month - 1
    if ind != pickle.load(open('a.pkl', 'rb')) and dia == dialimite:
        layout2 = [[gui.Text("Chave de Acesso deste mês("+str(ind+1)+")", key = 'texto')],[gui.InputText("", key = "chave")], [gui.Button("Liberar Acesso")]]
        acesso = gui.Window().layout(layout2)
        event, values = acesso.Read()
        while True:
            if values['chave'] == autentica[ind]:
                pickle.dump(ind, open("a.pkl", "wb"))
                gui.SystemTray.notify('Acesso Liberado!', 'Você deverá inserir a próxima senha mês que vem, no mesmo dia')
                acesso.close()
                break
            else:
                acesso['texto'].update("Chave errada! Tente Novamente")
                event, values = acesso.Read()

    #carrega quantidade local e espera
    qtd = getqtd("qtdloj.DBF")
    atualizajanela('Esperando...('+datetime.now().strftime("%d/%m/%Y %H:%M:%S)"))
    time.sleep(tempo)

    #carrega quantidade global
    qtd2 = getqtd("//Fxsorbase/acsn/CENTRAL/DADOS/qtdloj.DBF")

    #carrega base de dados
    data = {}
    for i in acc:
        data[i] = pickle.load(open(acc[i]['data_path']), "rb")

    #compara local x global
    lista = []
    mciclo = []
    for i in qtd2:
        if i not in qtd:
            atualizajanela(i, "cadastrado no sistema local.")
            continue
        if qtd2[i] != qtd[i] and i not in mciclo:
            lista.append([i, qtd2[i]])
            mciclo.append(i)

    #sincroniza as diferenças
    erros = pickle.load(open('relatorios/erros.pkl', 'rb'))
    for i in lista:
        for c in acc:
            try:
                modp(data[c][i[0]][1], int(i[1]), acc[c], i[0])
            except Exception as e:
                erros.append([i[0], int(i[1]), str(e), c])
                if e == KeyError:
                    atualizajanela(i, "não está cadastrado em "+c+", ou seu cadastro está errado. Registrado em C:/MercadoSinc/relatorios/")
                elif "Erro do servidor Mercado Livre:" in str(e):
                    atualizajanela(str(e))
                else:
                    atualizajanela("Erro:",i,"Registrado em C:/MercadoSinc/relatorios/")
        driver = webdriver.Chrome(options = options)
        try:
            modolist(i[0], int(i[1]), driver)
        except Exception as e:
            erros.append([i[0], int(i[1]), str(e), 'olist'])
            atualizajanela(i,"não está cadastrado no OLIST, ou seu cadastro está errado.")
        driver.close()
    pickle.dump(erros, open('relatorios/erros.pkl', 'wb'))
    
    if len(lista) > 0:
        copyfile("//Fxsorbase/acsn/CENTRAL/DADOS/qtdloj.DBF", os.getcwd()+ "/qtdloj.DBF")
    else:
        #corrige erros quando não há nada para sincronizar
        atualizajanela("Iniciando correção automática...")
        erros = pickle.load(open("relatorios/erros.pkl", "rb"))
        log = pickle.load(open('relatorios/log.pkl', 'rb'))
        for i in erros:
            atualizajanela("Corrigindo:", i[0])
            for c in acc:
                if c == i[3]
                    try:
                        modp(data[c][i[0]][1], int(i[1]), acc[c], i[0])
                    except Exception as e:
                        if e == KeyError:
                            texto = "Este produto não está cadastrado online, ou seu cadastro está errado."
                        elif "Erro do servidor Mercado Livre:" in str(e):
                            texto = "Erro no servidor Mercado Livre: "+str(e)
                        else:
                            texto = "Erro desconhecido: "+str(e)
                        log.append({"Código": i[0], "Quantidade":i[1],"Erro": texto, "Conta:":c})

            if i[3] == "olist":
                driver = webdriver.Chrome(options = options)
                try:
                    modolist(i[0], i[1], driver)
                except Exception as e:
                    atualizajanela(i[0], "não está cadastrado no olist")
                driver.close()

        pickle.dump([], open('relatorios/erros.pkl', 'wb'))
        pickle.dump(log, open('relatorios/log.pkl', 'wb'))
        df = pd.DataFrame(log)
        df.to_excel("/relatorios/erros.xlsx")

if __name__ == "__main__":
    while True:
        event, values = janela.Read(timeout = tempo*1000)
        try:
            cic()
        except Exception as e:
            atualizajanela(str(e))
