import socket
import struct
import threading
import time

from bcolors import bcolors

BROADCAST_PORT = 13117
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE_PAYLOAD = 0x4
MESSAGE_TYPE_REQUEST = 0x3
MESSAGE_TYPE_OFFER = 0x2


def listen_for_offer_udp(byte_size, tcp_connections, udp_connections):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.bind(("", BROADCAST_PORT))
    print(f"{bcolors.BOLD}Client started, listening for offer requests...{bcolors.ENDC}")
    data, addr = udp_socket.recvfrom(9)
    print(f"{bcolors.OKCYAN}Received offer from: {addr[0]}{bcolors.ENDC}")
    data_converted = struct.unpack('!IBHH', data)
    data_converted = list(data_converted)
    if(data_converted[0] == MAGIC_COOKIE and data_converted[1] == MESSAGE_TYPE_OFFER):
        udp = data_converted[2]
        tcp = data_converted[3]
        tcp_threads = []
        udp_threads = []
        for i in range(tcp_connections):
            tcp_thread = threading.Thread(target=tcp_connection, args=(byte_size//tcp_connections, addr[0], tcp, i))
            tcp_threads.append(tcp_thread)
            tcp_thread.start()
        for i in range(udp_connections):
            udp_thread = threading.Thread(target=udp_connection, args=(byte_size//udp_connections, addr[0], udp, i))
            udp_threads.append(udp_thread)
            udp_thread.start()
        for thread in tcp_threads:
            thread.join()
        for thread in udp_threads:
            thread.join()
    else:
        print(f"{bcolors.WARNING}Message is not a valid offer{bcolors.ENDC}")
    udp_socket.close()

def tcp_connection(byte_size, address, port, id):
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        tcp_socket.connect((address, port))

        start_time = time.time()

        tcp_request_packet = str(byte_size) + "\n"
        tcp_socket.send(tcp_request_packet.encode())

        data_count = 0
        
        while data_count < byte_size:
            data = tcp_socket.recv(1024)
            data_count += len(data)
            if not data:
                raise Exception(f"{bcolors.FAIL}Connection closed by server{bcolors.ENDC}")
        end_time = time.time()
        if data_count != byte_size:
            print(f"{bcolors.WARNING}Data count is less than byte size{bcolors.ENDC}")
            return
        print(f"{bcolors.OKBLUE}TCP transfer #" + str(id) + " finished, total time: " + str(round(end_time - start_time, 2)) + " seconds, total speed: " + str(round(byte_size*8/(end_time - start_time), 2)) + f" bits/second{bcolors.ENDC}")
        tcp_socket.close()
    except Exception as e:
        print(f"{bcolors.FAIL}An error occurred in TCP connection " + str(id) + "#, error: " + str(e) + f"{bcolors.ENDC}")



def udp_connection(byte_size, address, port, id):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    HEADER_SIZE = struct.calcsize('!IBQQ')  # Calculate header size
    payload_size = byte_size - HEADER_SIZE  # Only the actual payload
    
    # Send request packet
    udp_request_packet = struct.pack('!IBQ', MAGIC_COOKIE, MESSAGE_TYPE_REQUEST, payload_size)
    udp_socket.sendto(udp_request_packet, (address, port))
    
    start_time = time.time()
    udp_socket.settimeout(10)
    
    data_count = 0
    
    while data_count < payload_size:
        try:
            data = udp_socket.recv(8192)
            if not data:
                break
            
            if len(data) < HEADER_SIZE:
                print(f"{bcolors.WARNING}Received incomplete packet: {len(data)} bytes{bcolors.ENDC}")
                continue  # Skip processing if data is too small

            payload_data = data[HEADER_SIZE:]  # Exclude header
            data_count += len(payload_data)  # Count only payload bytes

        except Exception as e:
            print(f"{bcolors.FAIL}An error occurred in UDP connection {id}#, error: {e}{bcolors.ENDC}")
            break

    end_time = time.time()
    
    if data_count == payload_size:
        pass
    else:
        print(f"{bcolors.FAIL}Data not fully received{bcolors.ENDC}")
    
    print(f"{bcolors.OKGREEN}UDP transfer #{id} finished, total time: {round(end_time - start_time, 2)} seconds, "
          f"total speed: {round(payload_size * 8 / (end_time - start_time), 2)} bits/second, "
          f"total percentage of data received: {round(data_count / payload_size * 100, 2)}%{bcolors.ENDC}")
    
    udp_socket.close()







def main():
    byte_size = input(f"{bcolors.OKBLUE}Enter file size (in Bytes):{bcolors.ENDC}")
    tcp_connections = input(f"{bcolors.OKCYAN}Enter number of TCP connections:{bcolors.ENDC}")
    udp_connections = input(f"{bcolors.OKGREEN}Enter number of UDP connections:{bcolors.ENDC}")

    try:
        while True:
            listen_for_offer_udp(byte_size, tcp_connections, udp_connections)
    except Exception as e:
        print(f"{bcolors.WARNING}An error occurred: " + str(e) + f"{bcolors.ENDC}")


main()