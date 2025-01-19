import socket
import struct
import threading
import time

TCP_PORT = 12345
UDP_PORT = 13117
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE_REQUEST = 0x3
MESSAGE_TYPE_OFFER = 0x2


def listen_for_offer_udp(byte_size, tcp_connections, udp_connections):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.bind(("", 13117))
    print("Client started, listening for offer requests...")
    data, addr = udp_socket.recvfrom(1024)
    print("Received offer from: %s" % addr[0])
    data_converted = struct.unpack('IbHH', data)
    if(data_converted[0] == MAGIC_COOKIE and data_converted[1] == MESSAGE_TYPE_OFFER):
        print("Offer is valid, sending back request")
        threads = []
        counter = 1
        for i in range(tcp_connections):
            threads.append(threading.Thread(tcp_connection(byte_size, addr[0], data_converted[3], counter)))
            counter += 1
        for i in range(udp_connections):
            threads.append(threading.Thread(udp_connection(byte_size, addr[0], data_converted[2], counter)))
            counter += 1

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        print("All transfers complete, listening to offer requests")

    else:
        print("Message is not a valid offer")
    udp_socket.close()

def tcp_connection(byte_size, address, port, id):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    tcp_socket.connect((address, port))
    start_time = time.time()
    tcp_request_packet = struct.pack('QIB', byte_size, MAGIC_COOKIE, MESSAGE_TYPE_REQUEST)
    tcp_socket.send(tcp_request_packet)
    data = tcp_socket.recv(21)
    print(f"Received message: {data}")
    print(f"Data length: {len(data)}")
    end_time = time.time()
    print("RECIEVIED!")
    data_converted = struct.unpack('QQIB', data)
    print("Received message!!!: " + str(data_converted))
    if(data_converted[0] != MAGIC_COOKIE or data_converted[1] != 0x4):
        print("Bad payload received in UDP connection " + str(id)+"#")
        return
    print("TCP transfer #" + str(id) + " finished, total time: " + str(round(end_time - start_time, 2)) + " seconds, total speed: " + str(round(byte_size*8/(end_time - start_time), 2)) + " bits/second")
    tcp_socket.close()

    print("Connection failed")
    #print(f"Error: {e}")
    tcp_socket.close()

def udp_connection(byte_size, address, port, id):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.connect((address, int(port, 16)))
    start_time = time.time()
    udp_request_packet = struct.pack('IbH', MAGIC_COOKIE, MESSAGE_TYPE_REQUEST, hex(byte_size))
    udp_socket.send(udp_request_packet)
    data, addr = udp_socket.recv(byte_size)
    end_time = time.time()
    data_converted = struct.unpack('IbH', data)
    if(data_converted[0] != MAGIC_COOKIE or data_converted[1] != 0x4):
        print("Bad payload received in UDP connection " + str(id)+"#")
        return
    print("UDP transfer #" + str(id) + " finished, total time: " + str(round(end_time - start_time, 2)) + " seconds, total speed: " + str(round(byte_size*8/(end_time - start_time), 2)) + " bits/second")
    udp_socket.close()






def main():
    byte_size = 1073741824#input("Enter file size (in Bytes):")
    tcp_connections = 1#input("Enter number of TCP connections:")
    udp_connections = 0#input("Enter number of UDP connections:")
    while True:
        listen_for_offer_udp(byte_size, tcp_connections, udp_connections)


main()