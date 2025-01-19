import socket
import struct
import time
import threading
import random
import math

TCP_PORT = 12345
UDP_PORT = 13117
magic_cookie = 0xabcddcba
message_type = 0x2
request_type = 0x3
payload_type = 0x4
packet_size = 1024



def tcp_payload(conn, addr):
    request = conn.recv(1024)
    size = int(request.decode().split('\n')[0])
    file = b'a' * size
    conn.sendall(file)
    conn.close()
    
def start_server_udp(address):
    my_ip = socket.gethostbyname(socket.gethostname())
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.bind(address)
    data, addr = server.recvfrom(1024)
    if(addr[0] != my_ip):
        print("Connection from", addr)

    
def wait_for_clients_tcp():
    address = ('', TCP_PORT)
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.bind(address)
    tcp_server.listen()

    while True:
        conn, addr = tcp_server.accept()
        if conn is None:
            continue
        print("TCP connection from", addr)
        tcp_thread = threading.Thread(tcp_payload(conn, addr))
        tcp_thread.start()

    tcp_server.close()


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
    message = struct.pack("IHHB", magic_cookie, UDP_PORT, TCP_PORT, message_type)
    while True:
        server.sendto(message, ('<broadcast>', UDP_PORT))
        time.sleep(1)

def start_server():
    my_ip = socket.gethostbyname(socket.gethostname())
    print("Server started, listening on IP address", my_ip)
    try:
        broadcast_thread = threading.Thread(target=broadcast)
        broadcast_thread.start()
        tcp_thread = threading.Thread(target=wait_for_clients_tcp)
        tcp_thread.start()
        udp_thread = threading.Thread(target=wait_for_clients_udp)
        udp_thread.start()

    except Exception as e:
        print(e)

def main():
    start_server()

main()