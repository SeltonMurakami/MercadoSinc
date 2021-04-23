import PySimpleGUI as sg
import apiutils
import json
import urllib
import os
from PIL import Image

api = apiutils.meli("keys/key_selton.pkl", None)
delargs = ['expiration_time', 'shipping', 'item_relations',
           'geolocation', 'end_time', 'inventory_id', 'stop_time',
           'start_time', 'id', 'site_id', 'seller_id', 'sold_quantity',
           'initial_quantity', 'original_price', 'base_price', "international_delivery_mode",
           "subtitle", "permalink", "thumbnail_id", "thumbnail", "secure_thumbnail",
           "descriptions", "seller_address", "seller_contact", "location", "coverage_areas",
           "warnings", "listing_source", "status", "sub_status", "tags", "catalog_product_id",
           "domain_id", "parent_item_id", "differential_pricing", "deal_ids", "date_created",
           "last_updated", "health", "catalog_listing", "official_store_id", "video_id", "channels"]
args = ['title', 'price', 'available_quantity', 'id']
img = []
imgind = 0
tab1 = [
    [sg.Frame('', layout=[
        [sg.I('', key = "search_term"), sg.B("Pesquisar", key = "search"), sg.T("              ", key="logistic_type")],
        [sg.T('ID'), sg.I('', key="id"), sg.B('Buscar', key='pushButton'),
         sg.B('Copiar', key='copy'), sg.B('Publicar', key='publica')],
        [sg.T('Nome', key='lblnome'), sg.I('', key='title'),
         sg.T('EAN', key='lblean'), sg.I('', key='ean')],
        [sg.T('Preço'), sg.I('', key='price'), sg.T(
            'Estoque'), sg.I('', key="available_quantity")],
        [sg.T("Tempo de preparação"), sg.I('0', key = 'handling_time')],
        [sg.Frame('Descrição', key='descFrame', layout=[
            [sg.Multiline('', size=(100, 20), key='desc')]
        ])]
    ])]]

tab2 = [
    [sg.T("Ficha Técnica"), sg.B("Alterar", key='alteraficha', visible=False)],
    [sg.Table(values=[[' ', ' '], [' ', ' ']], headings=['Atributo', 'Valor'], justification="left",
              col_widths=[50 for x in range(2)], row_height=20, auto_size_columns=False, key="ficha")],
    [sg.T("Garantia"), sg.B("Alterar", key='alteragarantia', visible=False)],
    [sg.Table(values=[[' ', ' '], [' ', ' ']], headings=['Atributo', 'Valor'], justification="left",
              col_widths=[50 for x in range(2)], row_height=20, auto_size_columns=False, key="garantia")]
]

tab3 = [
    [sg.Button("<", key='prev'),sg.T("", key='indfotos'), sg.Button(">", key='next'), sg.B("Excluir", key = 'excluirimg', visible = False)],
    [sg.Image(None, key="img")]
]

tab4 = [
    [sg.Table(values=[[' ', ' '], [' ', ' ']], headings=['Atributo', 'Valor'], justification="left",
              col_widths=[50 for x in range(2)], row_height=20, auto_size_columns=False, key="var")]
]


layout = [[sg.TabGroup([[sg.Tab('Principal', tab1), sg.Tab(
    'Atributos', tab2, key='tab2'), sg.Tab('Fotos', tab3), sg.Tab('Variações', tab4)]])]]
window = sg.Window('App', layout)


def dele(item, args):
    for i in args:
        item.pop(i, None)


def parseatt(l):
    li = []
    for i in l:
        try:
            li.append([i['name'], i['value_name']])
        except Exception as e:
            print(e)
    return li

def resultadobusca(search_term):
    layoutb = []
    resultado = api.search(search_term)
    for i in resultado:
        formato = i['thumbnail'].split('.')[-1]
        urllib.request.urlretrieve(i['thumbnail'], i['id']+"_thumbnail."+formato)
        if formato != "png":
            im = Image.open(i['id']+"_thumbnail."+formato).resize((200, 200), Image.ANTIALIAS)
            im.save(i['id']+"_thumbnail.png")
            os.remove(os.getcwd() + "/" + i['id']+"_thumbnail."+formato)
        layoutb.append([sg.Image(i['id']+"_thumbnail.png"), sg.T(i['id']), sg.T(i['title']), sg.T(i['price']), sg.T(i['shipping']['logistic_type']), sg.B('selecionar', key = i['id'])])
    windowb = sg.Window('Busca', [[sg.Column(layoutb, size =  (1000,600),  scrollable = True)]])
    while True:
        event, values = windowb.read()
        if event in (None, 'Exit'):
            break

        elif event == '':
            pass

        else:
            showitem(event)
            break
    windowb.close()

def showitem(nml):
    global img
    img = []
    dados = api.getitem(nml)
    for i in dados:
        if i == 'attributes':
            for j in dados[i]:
                if j['id'] == 'GTIN':
                    window['ean'].update(j['value_name'])
            window['ficha'].update(values=parseatt(dados[i]))
        if i == 'sale_terms':
            window['garantia'].update(values=parseatt(dados[i]))
        if i == 'pictures':
            for j in dados[i]:
                formato = j['url'].split('.')[-1]
                urllib.request.urlretrieve(j['url'], j['id']+"."+formato)
                if formato != "png":
                    im = Image.open(j['id']+"."+formato)
                    os.remove(os.getcwd() + "/" + j['id']+"."+formato)
                    im.save(j['id']+".png")
                img.append(j['id']+".png")
        if i not in args:
            continue
        try:
            window[i].update(dados[i])
            window[i].Widget.config(state='disabled')
        except Exception as e:
            print(e)
    if len(dados['variations']) > 1:
        varspec = []
        for i in dados['variations']:
            varspec.append(['id', i['id']])
            varspec.append(['quantidade', i['available_quantity']])
            varspec.append(['preço', i['price']])
            for j in i['attribute_combinations']:
                varspec.append([j['name'], j['value_name']])
        window['var'].update(values=varspec)
    window['desc'].update(api.getdesc(nml)[0]['plain_text'])
    window['desc'].Widget.config(state='disabled')
    window['img'].update(img[imgind])
    window['indfotos'].update(str(imgind+1)+"/"+str(len(img)))
    window['logistic_type'].update(dados['shipping']['logistic_type'])


while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        for file in os.listdir(os.getcwd()):
            if file.endswith('.png'):
                os.remove(file) 
        break

    if event == '':
        pass

    if event == 'copy':
        desc = api.getdesc(values['id'])[0]['plain_text']
        base = api.getitem(values['id'])
        base['description'] = {'plain_text': desc}
        dele(base, delargs)
        window['alteraficha'].update(visible=True)
        window['alteragarantia'].update(visible=True)
        window['desc'].Widget.config(state='normal')
        window['excluirimg'].update(visible = True)
        for i in args:
            window[i].Widget.config(state='normal')
    if event == 'prev':
        imgind -= 1
        window['img'].update(img[imgind%len(img)])
        window['indfotos'].update(str(imgind%len(img)+1)+"/"+str(len(img)))

    if event == 'next':
        imgind += 1
        window['img'].update(img[imgind%len(img)])
        window['indfotos'].update(str(imgind%len(img)+1)+"/"+str(len(img)))

    if event == 'pushButton':
        try:
            showitem(values['id'])
        except Exception as e:
            print(e)
    if event == 'publica':
        if base['description']['plain_text'] != values['desc']:
            print("de", base['description']
                  ['plain_text'], "para", values['desc'])
            base['description']['plain_text'] = values['desc']
        for i in args:
            if i == 'id':
                continue
            if str(base[i]) != str(values[i]):
                print("de", base[i], "para", values[i])
                base[i] = values[i]
        base['price'] = float(values['price'])
        base['available_quantity'] = int(values['available_quantity'])
        base['sale_terms'].append({"id":"MANUFACTURING_TIME", "value_name":values['handling_time']+" dias"})
        #base['pictures'] = [os.getcwd()+"/"+x for x in img]
        try:
            sg.popup(api.publica(base, values['ean'], base['title']))
        except Exception as e:
            print(e)
    if event == 'search':
        img = []
        resultadobusca(values['search_term'])
    if event == 'excluirimg':
        del img[imgind]

window.close()
