import socket
import pickle

authorized_clients = pickle.load(open("clients.pkl", "rb"))

def server():
	host = socket.gethostname() # get local machine name
	port = 8001 # Mais de 8 mil!!!!!

	s = socket.socket()
	s.bind((host, port))

	while True:
		s.listen(1)
		print('Esperando...')
		client_socket, adress = s.accept()
		print("Conexão do endereço: " + str(addr))
		auth = c.recv(1024).decode('utf-8')
		if not auth:
			continue
		if auth in authorized_clients:
			c.send("authorized".encode('utf-8'))
		else:
			c.send("forbidden".encode('utf-8'))

if __name__ == '__main__':
	server()