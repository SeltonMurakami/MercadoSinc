import socket

def client():
  host = '192.168.25.17'  # get local machine name
  port = 49153  # Make sure it's within the > 1024 $$ <65535 range
  
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.connect((host, port))
  
  message = input('-> ')
  while message != 'q':
    s.send(message.encode('utf-8'))
    data = s.recv(1024).decode('utf-8')
    print('Received from server: ' + data)
    message = input('==> ')
  s.close()

if __name__ == '__main__':
  client()