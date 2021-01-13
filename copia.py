import requests
import json
import pickle

tokens = pickle.load(open('keys.pkl', 'rb'))

def copia(nml, qtd, pre, token, datapath = None, ean = None):
	headers = {"Authorization":"Bearer "+token}
	r = requests.get("https://api.mercadolibre.com/items/MLB"+nml, headers = headers)
	if r.status_code != 200:
		return r
	base = json.loads(r.text)
	desc = json.loads(requests.get("https://api.mercadolibre.com/items/MLB"+nml+"/descriptions", headers = headers).text)[0]
	dele(desc, 'id', 'created')
	print(desc['text'])
	print(desc['plain_text'])
	if input("editar desc?") == 's':
		desc['plain_text'] == input("Descrição: ")
	dele(base,'expiration_time', 'item_relations', 'geolocation', 'end_time', 'inventory_id', 'stop_time', 'start_time', 'id', 'site_id', 'seller_id', 'sold_quantity', 'initial_quantity', 'original_price', 'base_price', "international_delivery_mode", "subtitle", "permalink", "thumbnail_id", "thumbnail", "secure_thumbnail", "descriptions", "seller_address", "seller_contact", "location", "coverage_areas", "warnings", "listing_source", "status", "sub_status", "tags", "catalog_product_id", "domain_id", "parent_item_id", "differential_pricing", "deal_ids", "date_created", "last_updated", "health", "catalog_listing", )
	base['description'] = {"plain_text": desc['plain_text']}
	base['price'] = pre
	headers["Content-Type"] = "application/json"
	r = requests.post("https://api.mercadolibre.com/items", data = json.dumps(base), headers = headers)
	print(r.text)
	if r.status_code == 201:
		print(json.loads(r.text)['id'], "publicado com sucesso!")
		if datapath != None:
			d = pickle.load(open(datapath, 'rb'))
			d[ean] = [json.loads(r.text)['title'], json.loads(r.text)['id'][3:]]
			pickle.dump(d, open(datapath, 'wb'))

def busca(nome, ean, token):
	headers = {"Authorization":"Bearer "+token}
	r = requests.get("https://api.mercadolibre.com/sites/MLB/search?q="+nome.replace(" ","%20"), headers = headers)
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
    d = pickle.load(open('temp.pkl','rb'))
    dataa = pickle.load(open('data_abib.pkl', 'rb'))
    datas = pickle.load(open('data_splash.pkl', 'rb'))
    token = pickle.load(open('keys.pkl', 'rb'))
    for i in d:
    	if i in datas and i in dataa:
    		continue
    	if d[i][0] < 1:
    		continue
    	print('ean:', i)
    	if (input(d[i][1] + ' pula?') or 's') == 's':
    		continue
    	try:
    		if i not in datas:
    			print('splash')
    			copia(busca(d[i][1], i, token['token_s'])[3:], d[i][0], d[i][2], token['token_s'], 'data_splash.pkl', i)
    		if i not in dataa:
    			print('abib')
    			copia(busca(d[i][1], i, token['token_a'])[3:], d[i][0], d[i][2], token['token_a'], 'data_abib.pkl', i)
    	except Exception as e:
    		print(e)