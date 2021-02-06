import requests
import json
import pickle

class meli():
	client_secret = "TnkpxGW9LnCbaYrnGvetdZ2lfj3udxjE"
	client_id = "6545766642471155"
	
	def __init__(self, path):
		self.path = path
		self.token = pickle.load(open(path, "rb"))
		self.h = {"Authorization": "Bearer "+ self.token['token'], "content-type": "application/json", "accept": "application/json"}

	def getvar(self, nml):

	def getitem(self, nml, res = None):
		r = requests.get("https://api.mercadolibre.com/items/"+nml, headers = self.h)
		if r.status_code == 401:
			self.refresh()
			self.getitem(nml)
		if res:
			return json.loads(r.text)[res]
		else:
			return json.loads(r.text)

	def setres(self, nml,res, val, varid = None):
		url = "https://api.mercadolibre.com/items/"+nml
		if varid:
			arg = {"variations":{"id":varid, res:val}}
		else:
			arg = {res:val}

		r = requests.put(url, data = json.dumps(arg), headers = self.h)
		if r.status_code == 401:
			self.refresh()
			self.setres(nml, res, val, varid or None)
			
		if r.status_code == 200:
			return 200
		else:
			return r.text

	def refresh(self):
		ref = requests.post("https://api.mercadolibre.com/oauth/token?grant_type=refresh_token&client_id="+self.client_id+"&client_secret="+self.client_secret+"&refresh_token="+self.token['refresh'])
		resp = json.loads(ref.text)
		self.token = {"token":resp['access_token'], "refresh":resp['refresh_token']}
		self.h = {"Authorization": "Bearer "+ self.token['token']}
		pickle.dump(self.token, open(self.path, 'wb'))

