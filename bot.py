import pynput
import time
from pynput.mouse import Button
from pynput.keyboard import Key, Controller

t = 1
eanbase = input('eanbase: ')
d = {}
mouse = pynput.mouse.Controller()
kbd = Controller()

while True:
	ean = input('ean: ')
	nome = input('nome: ')
	qnt = input('qnt: ')
	pre = input('preço(deixe em branco para mesmo da base): ')
	if ean == '':
		break
	else:
		if pre == '':
			d[ean] = [nome, qnt]
		else:
			d[ean] = [nome, qnt, pre]

mouse.position = (347, 882)
mouse.click()
time.sleep(t)
mouse.position = (228, 141)
mouse.click(Button.left, 2)
time.sleep(t)
kbd.type(eanbase)
kbd.press(Key.enter)
time.sleep(t)
for i in d:
	kbd.press("a")
	time.sleep(t)
	mouse.position = (1044, 692)
	mouse.click()
	time.sleep(2*t)
	kbd.press(Key.enter)
	time.sleep(t)
	kbd.type(i)
	kbd.press(Key.enter)
	kbd.type(d[i][0])
	if len(d[i]) == 3:
		mouse.position = (1055, 501)
		mouse.click(Button.left, 2)
		kbd.type(d[i][2])
	mouse.position = (1036, 693)
	mouse.click()
	time.sleep(t)
	kbd.press(Key.right)
	kbd.press(Key.enter)
	kbd.press('t')
	time.sleep(t)
	kbd.type(i)
	kbd.press(Key.tab)
	kbd.press(Key.tab)
	kbd.press('c')
	kbd.press(Key.enter)
	kbd.press(Key.enter)
	kbd.type(d[i][1])
	kbd.press(Key.enter)
	kbd.press(Key.enter)
	time.sleep(t)