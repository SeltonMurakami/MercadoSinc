import pickle

print('Bem vindo à ferramenta de cadastro!')
while True:
	c = input("Cadastro na conta Splash ou Abib?(Digite S ou A)").lower()
	if c == 's':
		d = pickle.load(open("data_splash.pkl", "rb"))
		nml = input("ID do mercado livre'(só números):")
		d[nml] = [input("Nome: ") or None, input("EAN(Código de barras assim como consta no anúncio): ")]
		pickle.dump(nml, open("data_splash.pkl", "wb"))
	elif c == 'a': 
		d = pickle.load(open("data_abib.pkl", "rb"))
		nml = input("ID do mercado livre'(só números):")
		d[nml] = [input("Nome: ") or None, input("EAN(Código de barras assim como consta no anúncio): ")]
		pickle.dump(nml, open("data_abib.pkl", "wb"))
	else:
		print("Opção inválida.")