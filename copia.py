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
	desc = json.loads(requests.get("https://api.mercadolibre.com/items/MLB"+nml+"/descriptions", headers = headers).text)
	dele(desc, 'id', 'created')
	print(desc['text'])
	print(desc['plain_text'])
	dele(base, 'id', 'site_id', 'seller_id', 'sold_quantity', 'initial_quantity', 'original_price', 'base_price', "international_delivery_mode", "subtitle", "permalink", "thumbnail_id", "thumbnail", "secure_thumbnail", "descriptions", "seller_address", "seller_contact", "location", "coverage_areas", "warnings", "listing_source", "status", "sub_status", "tags", "catalog_product_id", "domain_id", "parent_item_id", "differential_pricing", "deal_ids", "date_created", "last_updated", "health", "catalog_listing", )
	base['description'] = {"plain_text": desc['plain_text']}
	base['price'] = pre
	headers["Content-Type"] = "application/json"
	r = requests.post("https://api.mercadolibre.com/items", data = json.dumps(base), headers = headers)
	if r.status_code == 201:
		print(json.loads(r.text)['id'], "publicado com sucesso!")
		if datapath != None:
			d = pickle.load(open(datapath, 'rb'))
			d[ean] = json.loads(r.text)['title'], json.loads(r.text)['id'][3:]
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