import socket

# This server listens on the specified port
HOST = '127.0.0.1'
PORT = 33169

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.bind((HOST, PORT))
  s.listen()
  print('Listening...')
  conn, addr = s.accept()
  with conn:
    print('Connected by', addr)
    while True:
      data = conn.recv(1024)
      if not data:
        break
      conn.sendall(data)
