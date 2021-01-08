from dbfread import DBF
import pickle
from selenium import webdriver
import urllib.request
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import pyautogui
import os
import cadastro

user = "sorocaba3@splashkidsbrinquedos.com.br"
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options = options)
driver.get("https://www.mercadolivre.com/jms/mlb/lgz/msl/login/")
u= driver.find_element_by_id("user_id")
u.send_keys(user)
#u.submit()
print("NAO FECHE NENHUMA DAS JANELAS DO CHROME NEM ESSA JANELA DO TERMINAL!")
input("pressione ENTER quando tiver logado")

d = DBF("//Fxsorbase/acsn/CENTRAL/DADOS/PROLOJ.DBF", load = True)
qtd = DBF("//Fxsorbase/acsn/CENTRAL/DADOS/qtdloj.DBF", load = True)
file = open("data.pkl", "rb")
c = pickle.load(file)
r = {}
n = {}
t = 3
t1 = 1
for i in qtd.records:
	if i['QTDE'] > 0:
		n[i['PROD']] = i['QTDE']

for i in d.records:
	if i['PL_PROCOD'] not in c.keys() and i['PL_PROCOD'] in n:
		r[i['PL_PROCOD']] = [i['PROPDV'], n[i['PL_PROCOD']]]

def getinfo(ean):
	driver.get("https://www.google.com/search?q="+ean+"&tbm=shop")
	time.sleep(t1)
	try:
		tmp = driver.find_element_by_tag_name("h3")
		nome = tmp.text
		tmp.click()
	except Exception as e:
		tmp = driver.find_element_by_tag_name("h4")
		nome = tmp.text
		tmp.click()
	time.sleep(t1)
	try:
		driver.find_element_by_css_selector(".sh-ds__trunc > .\_-ku").click()
		time.sleep(t1)
		desc = driver.find_element_by_css_selector('.sh-ds__full-txt').text
	except Exception as e:
		desc = driver.find_element_by_xpath(".//p[@class = 'sh-ds__desc']").text
	pre = r[ean][0]
	qtd = r[ean][1]
	src = []
	try:
		marca = driver.find_element_by_css_selector(".\_-6").text
	except Exception as e:
		marca = 'marca'
	time.sleep(t1)
	driver.find_element_by_xpath("//div[2]/a/div/div/img").click()
	for n, i in enumerate(driver.find_elements_by_css_selector(".sg-m__media-item")):
		if n == 4:
			break
		try:
			time.sleep(t1)
			i.click()
			time.sleep(t1)
			src.append(driver.find_element_by_css_selector(".sg-m-i__content").get_attribute('src'))
		except Exception as e:
			break

	return [nome, desc, pre, qtd, marca, src]

def anunciar(ean):
	info = getinfo(ean)
	driver.get("https://www.mercadolivre.com.br/anuncie/hub#nav-header")
	time.sleep(t)
	driver.find_element_by_css_selector(".andes-card:nth-child(1) .hub-box__image").click()
	time.sleep(t)
	#try:
	#	element = driver.find_element_by_xpath(".//a[@class = 'syi-onboarding__link']")
	#	actions = ActionChains(driver)
	#	actions.move_to_element(element).click().perform()
	#except Exception as e:
	#	print(e)
	#time.sleep(t)
	driver.find_element_by_id('title').send_keys(info[0])
	time.sleep(t)
	driver.find_element_by_css_selector(".andes-button").click()
	time.sleep(t)
	driver.find_element_by_xpath(".//div[@class = 'andes-list__item-image-container']").click()
	time.sleep(2*t)
	#driver.find_element_by_xpath(".//div[@id='category_task']/div[2]/div[3]/button/span").click()
	input('Cheque a categoria e aperte ENTER')
	try:
		m = info[4]
		driver.find_element_by_name("BRAND").send_keys(m)
		input('brand')
	except Exception as e:
		print(e)
	l = driver.find_elements_by_xpath(".//button[@type = 'submit']")
	for i in l:
		if i.text == 'Confirmar':
			try:
				i.click()
				break
			except Exception as e:
				print(e)
	time.sleep(2*t)
	driver.find_element_by_id('NEW').click()
	time.sleep(t)
	input('Se solicitado, informe a cor do produto. ENTER para continuar')
	try:
		div = driver.find_element_by_id("specifications_container")
	except Exception as e:
		div = driver.find_element_by_xpath(".//table[@class = 'sc-ui-table__table']")
	q = div.find_element_by_tag_name("input")
	for i in range(5):
		q.send_keys(Keys.BACKSPACE)
	q.send_keys(str(int(info[3])))
	time.sleep(t)
	paths = []
	for n, i in enumerate(info[5]):
		urllib.request.urlretrieve(i, "img/"+ean +"#" +str(n)+".png")
		paths.append(os.getcwd() +" \img\ "+ ean +"#" +str(n)+".png")

	for i in paths:
		div = driver.find_element_by_xpath(".//div[@class = 'sc-ui-image-uploader__container']")
		div.click()
		time.sleep(t)
		pyautogui.write(i)
		pyautogui.press('enter')
		time.sleep(t)

	time.sleep(t)
	driver.find_element_by_css_selector(".sc-ui-card-footer:nth-child(4) > .andes-button--loud > .andes-button__content").click()
	time.sleep(t)
	inpean = driver.find_element_by_xpath(".//input[@name = '0']")
	inpean.send_keys(ean)
	time.sleep(t)
	l = driver.find_elements_by_xpath(".//button[@type = 'submit']")
	for i in l:
		if i.text == 'Continuar':
			try:
				i.click()
				break
			except Exception as e:
				print(e)
	time.sleep(t)
	l = driver.find_elements_by_xpath(".//button[@type = 'submit']")
	for i in l:
		if i.text == 'Confirmar':
			try:
				i.click()
				break
			except Exception as e:
				print(e)
	input('Confira a primeira seção e aperte PRÓXIMO e então ENTER')
	time.sleep(t)
	inppr = driver.find_element_by_xpath(".//input[@class = 'andes-form-control__field']")
	p = "{:.2f}".format(info[2]).split('.')
	inppr.send_keys(p[0]+','+p[1])
	time.sleep(t)
	l = driver.find_elements_by_xpath(".//button[@type = 'submit']")
	for i in l:
		if i.text == 'Confirmar':
			try:
				i.click()
				break
			except Exception as e:
				print(e)
	time.sleep(2*t)
	driver.find_element_by_css_selector(".sc-ui-listing-type:nth-child(1) .sc-ui-listing-type__title").click()
	time.sleep(t)
	driver.find_element_by_css_selector(".sc-ui-card-footer:nth-child(3) > .andes-button--loud > .andes-button__content").click()
	time.sleep(t)
	driver.find_element_by_css_selector("#shipping_task .andes-button").click()
	time.sleep(t)
	try:
		driver.find_element_by_css_selector(".andes-radio:nth-child(3) span").click()
		time.sleep(t)
		driver.find_element_by_css_selector("#free_shipping_task .andes-button--loud").click()
		time.sleep(t)
		l = driver.find_elements_by_xpath(".//button[@type = 'submit']")
		for i in l:
			if i.text == 'Confirmar':
				try:
					i.click()
					break
				except Exception as e:
					print(e)
	except Exception as e:
		print(e)
	driver.find_element_by_css_selector(".sc-ui-option-value:nth-child(1) .andes-list__item-primary").click()
	time.sleep(t)
	driver.find_element_by_xpath(".//div[@id='warranty_task']/div[2]/div/div/div/div[2]/div/div/input").click()
	time.sleep(t)
	driver.find_element_by_css_selector(".andes-form-control--focused .andes-form-control__field").send_keys('3')
	time.sleep(t)
	driver.find_element_by_css_selector("#warranty_task .andes-button--loud > .andes-button__content").click()
	time.sleep(t)
	driver.find_element_by_css_selector("#description_task .sc-ui-card-header__icon").click()
	time.sleep(t)
	descinp = driver.find_element_by_id("description")
	time.sleep(t)
	descinp.send_keys(info[1])
	input("Confira a descrição e aperte ENTER")
	time.sleep(t)
	l = driver.find_elements_by_xpath(".//button[@type = 'submit']")
	for i in l:
		if i.text == 'Confirmar':
			try:
				i.click()
				break
			except Exception as e:
				print(e)
	time.sleep(t)
	l = driver.find_elements_by_xpath(".//button[@type = 'submit']")
	for i in l:
		if i.text == 'Anunciar':
			try:
				i.click()
				break
			except Exception as e:
				print(e)
	time.sleep(2*t)
	driver.find_element_by_xpath(".//span[@class='andes-button__content']").click()
	time.sleep(t)
	nml = driver.current_url[40:50]
	driver.get("https://www.mercadolivre.com.br/anuncios/lista/?page=1&search="+nml)
	time.sleep(t)
	try:
		driver.find_element_by_xpath(".//a[@class = 'andes-modal-dialog__button-close']").click()
	except Exception as e:
		print(e)
	div = driver.find_element_by_xpath(".//div[@class='sc-list-item-row__visible']")
	div.find_elements_by_tag_name('a')[0].click()
	time.sleep(t)
	link = driver.current_url
	cadastro.cadastro(ean, info[0], nml, link)
	del r[ean]

if __name__ == "__main__":
	while True:          
		try:
			input("ENTER para cadastrar")
			ean = input("EAN: ")
			anunciar(ean)
		except Exception as e:
			print(e)