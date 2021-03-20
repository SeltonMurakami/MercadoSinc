import PySimpleGUI as sg
import apiutils
import json
import urllib
from PIL import Image

api = apiutils.meli("keys/key_pai.pkl", None)
delargs = ['expiration_time','shipping', 'item_relations',
'geolocation', 'end_time', 'inventory_id', 'stop_time',
'start_time', 'id', 'site_id', 'seller_id', 'sold_quantity',
'initial_quantity', 'original_price', 'base_price', "international_delivery_mode",
"subtitle", "permalink", "thumbnail_id", "thumbnail", "secure_thumbnail",
"descriptions", "seller_address", "seller_contact", "location", "coverage_areas",
"warnings", "listing_source", "status", "sub_status", "tags", "catalog_product_id",
"domain_id", "parent_item_id", "differential_pricing", "deal_ids", "date_created",
"last_updated", "health", "catalog_listing", "official_store_id","video_id"]
args = ['title', 'price', 'available_quantity', 'id']
img = []
imgind = 0
tab1 = [
		[sg.Frame('', layout = [
		 [sg.T('ID'), sg.I('', key = "id"), sg.B('Buscar', key='pushButton'), sg.B('Copiar', key='copy'), sg.B('Publicar', key='publica')], 
		 [sg.T('Nome', key='lblnome'), sg.I('', key='title'), sg.T('EAN', key='lblean'), sg.I('', key='ean')],
		 [sg.T('Preço'), sg.I('', key = 'price'), sg.T('Estoque'), sg.I('', key = "available_quantity")],
		 [sg.Frame('Descrição', key='descFrame', layout = [
				 [sg.Multiline('',size = (100, 20), key='desc')]
		])]
])]]

tab2 = [
		[sg.T("Ficha Técnica"), sg.B("Alterar", key = 'alteraficha', visible = False)],
		[sg.Table(values = [[' ',' '],[' ',' ']],headings = ['Atributo', 'Valor'],justification = "left", col_widths = [50 for x in range(2)],row_height = 20,auto_size_columns = False,key = "ficha")],
		[sg.T("Garantia"), sg.B("Alterar", key = 'alteragarantia', visible = False)],
		[sg.Table(values = [[' ',' '], [' ',' ']],headings = ['Atributo', 'Valor'],justification = "left", col_widths = [50 for x in range(2)], row_height = 20,auto_size_columns = False, key = "garantia")]
]

tab3 = [
		[sg.Button("<", key = 'prev'),sg.Image(None, key = "img"),sg.Button(">", key = 'next')],
		[sg.T("", key = 'indfotos', size = (1, 10))]
]

tab4 = [
		[sg.Table(values = [[' ',' '],[' ',' ']],headings = ['Atributo', 'Valor'],justification = "left", col_widths = [50 for x in range(2)],row_height = 20,auto_size_columns = False,key = "var")]
]

layout = [[sg.TabGroup([[sg.Tab('Principal', tab1), sg.Tab('Atributos', tab2, key = 'tab2'), sg.Tab('Fotos', tab3), sg.Tab('Variações', tab4)]])]]
window = sg.Window('App', layout)

def dele(item, *args):
	for i in args:
		try:
			del item[i]
		except Exception as e:
			continue

def parseatt(l):
		li = []
		for i in l:
				try:
						li.append([i['name'], i['value_name']])
				except Exception as e:
						print(e)
		return li

def showitem(nml):
		img = []
		dados = api.getitem(nml)
		for i in dados:
				if i == 'attributes':
						for j in dados[i]:
							if j['id'] == 'GTIN':
								window['ean'].update(j['value_name'])
						window['ficha'].update(values = parseatt(dados[i]))
				if i == 'sale_terms':
						window['garantia'].update(values = parseatt(dados[i]))
				if i == 'pictures':
						for j in dados[i]:
								formato = j['url'].split('.')[-1]
								urllib.request.urlretrieve(j['url'], j['id']+"."+formato)
								if formato != "png":
										im = Image.open(j['id']+"."+formato)
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
				varspec.append(['id',i['id']])
				varspec.append(['quantidade', i['available_quantity']])
				varspec.append(['preço', i['price']])
				for j in i['attribute_combinations']:
					varspec.append([j['name'],j['value_name']])
			window['var'].update(values = varspec)
		window['desc'].update(api.getdesc(nml)[0]['plain_text'])
		window['desc'].Widget.config(state='disabled')
		window['img'].update(img[imgind])
		window['indfotos'].update(str(imgind+1)+"/"+str(len(img)))
		return img

while True:
		event, values = window.read()
		if event in (None, 'Exit'):
				break

		if event == '':
				pass

		if event == 'copy':
			desc = api.getdesc(values['id'])[0]['plain_text']
			base = api.getitem(values['id'])
			base['description'] = {'plain_text':desc}
			dele(base, *delargs)
			window['alteraficha'].update(visible=True)
			window['alteragarantia'].update(visible=True)
			window['desc'].Widget.config(state='normal')
			for i in args:
				window[i].Widget.config(state='normal')
		if event == 'prev':
				print(img)
				if imgind > 0:
						imgind -= 1
						window['img'].update(img[imgind])
						window['indfotos'].update(str(imgind+1)+"/"+str(len(img)))

		if event == 'next':
				print('b')
				if imgind < len(img) - 1:
						imgind += 1
						window['img'].update(img[imgind])
						window['indfotos'].update(str(imgind+1)+"/"+str(len(img)))

		if event == 'pushButton':
				img = showitem(values['id'])
		if event == 'publica':
			if base['description']['plain_text'] != values['desc']:
				print("de", base['description']['plain_text'],"para", values['desc'])
				base['description']['plain_text'] = values['desc']
			for i in args:
				if i == 'id':
					continue
				if str(base[i]) != str(values[i]):
					print("de", base[i],"para", values[i])
					base[i] = values[i]
			base['price'] = float(values['price'])
			base['available_quantity'] = int(values['available_quantity'])
			sg.popup(api.publica(base, values['ean'], base['title']))

window.close()
