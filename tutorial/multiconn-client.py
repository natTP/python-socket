import socket
import selectors
import types

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 33169

messages = [b'Message 1 from client.', b'Message 2 from client.']

sel = selectors.DefaultSelector()
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def start_connections(host, port, num_conns):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print('Starting connection', connid, 'to', server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr) # won;t block
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(connid=connid,
                                     msg_total=sum(len(m) for m in messages),
                                     recv_total=0,
                                     messages=list(messages),
                                     outb=b'')
        sel.register(sock, events, data=data)

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('Accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ: # Should be ready to read
        recv_data = sock.recv(1024)  
        if recv_data:
            print('Received', repr(recv_data), 'from connection', data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print('Closing connection', data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:  # Should be ready to write
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb: 
            print('Sending', repr(data.outb), 'to connection', data.connid)
            sent = sock.send(data.outb) 
            data.outb = data.outb[sent:]

start_connections(SERVER_HOST, SERVER_PORT, 1)
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

while True:
    # blocks until sockets are ready, then returns (key, events) of each socket
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:  # From listener socket - we accept it
            accept_wrapper(key.fileobj)
        else: # From client socket - we service it
            service_connection(key, mask)