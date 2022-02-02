import socket

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 33169

print('Started...')
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect((SERVER_HOST, SERVER_PORT))
  print('Connected...')
  message = input().strip()
  s.sendall(message.encode('UTF-8'))
  data = s.recv(1024)

print('Received', repr(data))
