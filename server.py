import socket
import time
import threading
import random

TCP_PORT = 12345
UDP_PORT = 13117
magic_cookie = 0xabcddcba
message_type = 0x2
request_type = 0x3
packet_size = 1024



def tcp_payload(size, conn):
    count = 0
    while size:
        data = magic_cookie.to_bytes(4, byteorder='big') + message_type.to_bytes(1, byteorder='big') + size.to_bytes(8, byteorder='big') + count.to_bytes(8, byteorder='big')
        if size > packet_size:
            data += b'a' * packet_size  # Generate mock data
            data += b'\n'  # Add a newline character
            conn.send(data.encode())
            size -= packet_size
        else:
            data += b'a' * size
            data += b'\n'
            conn.send(data.encode())
            size = 0
        count += 1
        
            
            
    
def start_server_udp(address):
    ipv4 = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.bind(address)
    data, addr = server.recvfrom(1024)
    if(addr[0] != ipv4[0]):
        print("Connection from", addr)
    server.close()

def start_server_tcp(address):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(address)
    server.listen()
    conn, addr = server.accept()
    print("Connection from", addr)
    data = conn.recv(1024)
    print("received message: %s" % data.decode())
    if data.decode()[0:4] != str(magic_cookie) or data.decode()[4] != str(request_type):
        print("Wrong magic cookie or message type")
        conn.close()
        server.close()
        return
    else:
        size = data.decode()[5:]
        tcp_payload(size, conn)
    conn.close()
    server.close()
    
def wait_for_clients_tcp():
    address = ('', TCP_PORT)
    try:
        thread = threading.Thread(target=start_server_tcp, args=(address,))
        thread.start()
    except Exception as e:
        print(e)

def wait_for_clients_udp():
    address = ('', UDP_PORT)
    try:
        thread = threading.Thread(target=start_server_udp, args=(address,))
        thread.start()
    except Exception as e:
        print(e)
        

def broadcast():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(0.2)
    message = magic_cookie.to_bytes(4, byteorder='big') + message_type.to_bytes(1, byteorder='big') + UDP_PORT.to_bytes(2, byteorder='big') + TCP_PORT.to_bytes(2, byteorder='big')
    #message = b"Hello, new game starting soon!"
    while True:
        server.sendto(message, ('<broadcast>', UDP_PORT))
        time.sleep(1)

def start_server():
    ipv4 = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]
    print("Server started, listening on IP address", ipv4[0])
    try:
        thread = threading.Thread(target=broadcast)
        thread.start()
        thread2 = threading.Thread(target=wait_for_clients_tcp)
        #thread2.start()
        thread3 = threading.Thread(target=wait_for_clients_udp)
        #thread3.start()

    except Exception as e:
        print(e)

if __name__ == '__main__':
    start_server()