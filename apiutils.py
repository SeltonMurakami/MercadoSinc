import requests
import json
import pickle

class meli():
	client_secret = "TnkpxGW9LnCbaYrnGvetdZ2lfj3udxjE"
	client_id = "6545766642471155"
	
	def __init__(self, key_path, data_path):
		self.key_path = key_path
		self.data_path = data_path
		self.token = pickle.load(open(key_path, "rb"))
		self.h = {"Authorization": "Bearer "+ self.token['token'], "content-type": "application/json", "accept": "application/json"}

	def getitem(self, nml, res = None):
		r = requests.get("https://api.mercadolibre.com/items/"+nml, headers = self.h)
		if r.status_code == 401:
			self.refresh()
			return self.getitem(nml)
		if res:
			return json.loads(r.text)[res]
		else:
			return json.loads(r.text)

	def getdesc(self, nml):
		r = requests.get("https://api.mercadolibre.com/items/"+nml+"/descriptions", headers = self.h)
		if r.status_code == 401:
			self.refresh()
			return self.getitem(nml)
		return json.loads(r.text)

	def search(self, query, arg = 'q'):
		r = requests.get("https://api.mercadolibre.com/sites/MLB/search?"+arg+"="+query.replace(" ","%20"), headers = self.h)
		if r.status_code == 401:
			self.refresh()
			return self.search(query, arg)
		return json.loads(r)['results']

	def setres(self, nml,res, val, varid = None):
		url = "https://api.mercadolibre.com/items/"+nml
		if varid:
			arg = {"variations":{"id":varid, res:val}}
		else:
			arg = {res:val}

		r = requests.put(url, data = json.dumps(arg), headers = self.h)
		if r.status_code == 401:
			self.refresh()
			return self.setres(nml, res, val, varid or None)

		if r.status_code == 200:
			return 200
		else:
			return r.text

	def refresh(self):
		ref = requests.post("https://api.mercadolibre.com/oauth/token?grant_type=refresh_token&client_id="+self.client_id+"&client_secret="+self.client_secret+"&refresh_token="+self.token['refresh'])
		resp = json.loads(ref.text)
		self.token = {"token":resp['access_token'], "refresh":resp['refresh_token']}
		self.h = {"Authorization": "Bearer "+ self.token['token']}
		pickle.dump(self.token, open(self.key_path, 'wb'))

	def publica(self, item, ean = None, nome = None):
		r = requests.post("https://api.mercadolibre.com/items", data = json.dumps(item), headers = self.h)
		if r.status_code == 401:
			self.refresh()
			return self.publica(item)
		nml = json.loads(r.text)['id']
		if self.data_path != None:
			d = pickle.load(open(self.data_path, 'rb'))
			d.update({ean:[nome, nml]})
			pickle.dump(d,open(self.data_path, 'wb'))
		return nml

