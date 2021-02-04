import requests
import json
import pickle
from dbfread import DBF

tokens = pickle.load(open('keys.pkl', 'rb'))

delargs = ['expiration_time','shipping', 'item_relations',
'geolocation', 'end_time', 'inventory_id', 'stop_time',
'start_time', 'id', 'site_id', 'seller_id', 'sold_quantity',
'initial_quantity', 'original_price', 'base_price', "international_delivery_mode",
"subtitle", "permalink", "thumbnail_id", "thumbnail", "secure_thumbnail",
"descriptions", "seller_address", "seller_contact", "location", "coverage_areas",
"warnings", "listing_source", "status", "sub_status", "tags", "catalog_product_id",
"domain_id", "parent_item_id", "differential_pricing", "deal_ids", "date_created",
"last_updated", "health", "catalog_listing", "official_store_id","video_id"]

def getqtd(file, file2):
    qtd = {}
    esto = DBF(file, load = True)
    for i in esto.records:
        if int(i['QTDE']) < 0:
            continue
        if i['PROD'] not in qtd:
            qtd[i['PROD']] = int(i['QTDE'])
        else:
            if int(i['QTDE']) > qtd[i['PROD']]:
                qtd[i['PROD']] = [int(i['QTDE'])]
    nome = DBF(file2, load = True)
    for i in nome.records:
    	if i['PL_PROCOD'] in qtd:
    		qtd[i['PL_PROCOD']].append(i["PRODES"])
    		qtd[i['PL_PROCOD']].append(i["PROPDV"])
    return qtd

def copia(nml, qtd, pre, token, datapath = None, ean = None, rp = None):
	headers = {"Authorization":"Bearer "+token}
	r = requests.get("https://api.mercadolibre.com/items/MLB"+nml, headers = headers)
	if r.status_code != 200:
		return r
	base = json.loads(r.text)
	if base['status'] != 'active':
		return
	if base['shipping']['logistic_type'] == "fulfillment":
		return
	desc = json.loads(requests.get("https://api.mercadolibre.com/items/MLB"+nml+"/descriptions",  headers = headers).text)[0]
	dele(desc, 'id', 'created')
	dele(base, *delargs)
	try:
		base['description'] = {"plain_text": desc['plain_text'].replace("DD M\u00e1quinas", "Murakami Ferramentas")}
	except Exception as e:
		base['description'] = {"plain_text": desc['plain_text']}
	if rp:
		base['price'] = "{:.2f}".format(rp(base['price']))
	else:
		base['price'] = pre
	if 'variations' in base:
		if len(base['variations']) > 0:
			for i in base['variations']:
				dele(i, *delargs)
				if rp:
					i['price'] = "{:.2f}".format(rp(i['price']))
				else:
					i['price'] = pre
				if i['available_quantity'] == 0:
					continue
				elif i['available_quantity'] > qtd:
					i['available_quantity'] = qtd
		else:
			if base['available_quantity'] == 0:
				return
			elif base['available_quantity'] > qtd:
				base['available_quantity'] = qtd
	headers["Content-Type"] = "application/json"
	r = requests.post("https://api.mercadolibre.com/items", data = json.dumps(base), headers = headers)
	print(r)
	if r.status_code == 201:
		print(json.loads(r.text)['id'], "publicado com sucesso!")
		if datapath != None:
			d = pickle.load(open(datapath, 'rb'))
			d[ean] = [json.loads(r.text)['title'], json.loads(r.text)['id'][3:]]
			pickle.dump(d, open(datapath, 'wb'))
	else:
		raise Exception(r.status_code)
	#elif r.status_code == 400:
	#	response = json.loads(r.text)
	#	if response['error'] == 'validation_error':
	#		delatt = []
	#		for i in response['cause']:
	#			st = i['message']
	#			att = st[st.index('[')+1:st.index(']')]
	#			delatt.append(att)

def busca(query, ean, token, arg = 'q'):
	headers = {"Authorization":"Bearer "+token}
	r = requests.get("https://api.mercadolibre.com/sites/MLB/search?"+arg+"="+query.replace(" ","%20"), headers = headers)
	ids = [x['id'] for x in json.loads(r.text)['results']]
	print(nome)
	for i in ids:
		r = requests.get("https://api.mercadolibre.com/items/"+i, headers = headers)
		if r.status_code != 200:
			continue
		resp = json.loads(r.text)
		gtin = None
		for j in resp['attributes']:
			if j['id'] == "GTIN":
				gtin = j['value_name']
		if gtin != ean:
			continue
		print(resp['title'])
		if input('seleciona? ') == 's':
			return i


def dele(item, *args):
	for i in args:
		try:
			del item[i]
		except Exception as e:
			continue

if __name__ == "__main__":
    d = getqtd('qtdloj.DBF', 'PROD.DBF')
    dataa = pickle.load(open('data_abib.pkl', 'rb'))
    datas = pickle.load(open('data_splash.pkl', 'rb'))
    token = pickle.load(open('keys.pkl', 'rb'))
    print("Ferramenta de cadastro MercadoSinc.")
    print("1 - para cadastrar o produtos detectados como não cadastrados.")
    print("2 - cadastro por EAN")
    if input("Selecione sua opção: ") == '1':
    	log = pickle.load(open('log.pkl','rb'))
    	for i in log:
    		if log[i]["Erro"] != "Este produto não está cadastrado online, ou seu cadastro está errado.":
    			continue
    		if i in datas and i in dataa:
    			continue
    		if d[i][0] < 1:
    			continue
    		print('ean:', i)
    		if (input(d[i][1] + ' pula?') or 's') == 's':
    			continue
    		try:
    			alvo = busca(d[i][1], i, token['token_s'])[3:]
    			if i not in datas:
    				print('Cadastrando em SPLASH...')
    				copia(alvo, d[i][0], d[i][2], token['token_s'], 'data_splash.pkl', i)
    			if i not in dataa:
    				print('Cadastrando em ABIB...')
    				copia(alvo, d[i][0], d[i][2], token['token_a'], 'data_abib.pkl', i)
    		except Exception as e:
    			print(e)
    else:
    	ean = input("EAN: ")
    	alvo = busca(d[ean][1], ean, token['token_s'])[3:]
    	copia(alvo, d[ean][0], d[i][2], token['token_s'], 'data_splash.pkl', i)