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
    total = 0
    while total < size:
        if size - total < packet_size:
            conn.send(b'a' * (size - total))
            total = size
        else:
            conn.send(b'a' * packet_size)
            total += packet_size
    conn.close()
    
def udp_payload(addr, size):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    #udp_socket.sendto(b'a' * size, addr)
    total = 0
    while total < size:
        if size - total < packet_size:
            # header = struct.pack("ibH", magic_cookie, hex(payload_type))
            # packet = header + b'a' * (size - total)
            # udp_socket.sendto(packet, addr)
            udp_socket.sendto(b'a' * (size - total), addr)
            total = size
        else:
            # header = struct.pack("ibH", magic_cookie, hex(payload_type))
            # packet = header + b'a' * packet_size
            # udp_socket.sendto(packet, addr)
            udp_socket.sendto(b'a' * packet_size, addr)
            total += packet_size
    udp_socket.close()

    
def wait_for_clients_tcp():
    address = ('', TCP_PORT)
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.bind(address)
    tcp_server.listen()
    thread_list = []
    while True:
        conn, addr = tcp_server.accept()
        print("Connection from", addr)
        thread = threading.Thread(target=tcp_payload, args=(conn, addr))
        thread_list.append(thread)
        thread.start()
        for thread in thread_list:
            thread.join()

def wait_for_clients_udp():
    address = ('', 13355)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)   
    udp_socket.bind(address)
    thread_list = []
    while True:
        data, addr = udp_socket.recvfrom(1024)
        print("Connection from", addr)
        #header = struct.unpack("IHHB", data)
        #if(header[0] == magic_cookie and header[3] == request_type):
        size = int(data.decode(),10)
        #print("size = " + str(size))
        thread = threading.Thread(target=udp_payload, args=(addr, size))
        thread_list.append(thread)
        thread.start()
        for thread in thread_list:
            thread.join()
        #else:
        #    print("Invalid request")

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
        
        tcp_thread.join()
        udp_thread.join()
        broadcast_thread.join()

    except Exception as e:
        print(e)

def main():
    start_server()

main()