import socket
import struct
import threading
import time

TCP_PORT = 12345
UDP_PORT = 13117
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE_PAYLOAD = 0x4
MESSAGE_TYPE_REQUEST = 0x3
MESSAGE_TYPE_OFFER = 0x2


def listen_for_offer_udp(byte_size, tcp_connections, udp_connections):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.bind(("", 13117))
    print("Client started, listening for offer requests...")
    data, addr = udp_socket.recvfrom(9)
    print("Received offer from: %s" % addr[0])
    data_converted = struct.unpack('IHHB', data)
    if(data_converted[0] == MAGIC_COOKIE and data_converted[3] == MESSAGE_TYPE_OFFER):
        print("Offer received, connecting to server")
        tcp_threads = []
        udp_threads = []
        for i in range(tcp_connections):
            tcp_thread = threading.Thread(target=tcp_connection, args=(byte_size//tcp_connections, addr[0], TCP_PORT, i))
            tcp_threads.append(tcp_thread)
            tcp_thread.start()
        for i in range(udp_connections):
            udp_thread = threading.Thread(target=udp_connection, args=(byte_size//udp_connections, addr[0], 13355, i))
            udp_threads.append(udp_thread)
            udp_thread.start()
        for thread in tcp_threads:
            thread.join()
        for thread in udp_threads:
            thread.join()

        print("All transfers complete, listening to offer requests")

    else:
        print("Message is not a valid offer")
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
                raise Exception("Connection closed by server")
        end_time = time.time() 
        print("Data count: " + str(data_count))
        print("Byte size: " + str(byte_size))
        if data_count != byte_size:
            print("Data count is less than byte size")
            return
        print("TCP transfer #" + str(id) + " finished, total time: " + str(round(end_time - start_time, 2)) + " seconds, total speed: " + str(round(byte_size*8/(end_time - start_time), 2)) + " bits/second")
        tcp_socket.close()
    except Exception as e:
        print("An error occurred in TCP connection " + str(id) + "#, error: " + str(e))



def udp_connection(byte_size, address, port, id):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    packet = str(byte_size)
    udp_socket.sendto(packet.encode(), (address, port))
    start_time = time.time()
    udp_socket.settimeout(10)
    #udp_request_packet = struct.pack('IbH', MAGIC_COOKIE, MESSAGE_TYPE_REQUEST, hex(byte_size))
    #udp_socket.send(udp_request_packet)
    data_count = 0
    while data_count < byte_size:
        try:
            data = udp_socket.recv(1024)
            if not data:
                break
            data_count += len(data)
            if not data:
                raise Exception("Connection closed by server")
        except Exception as e:
            print("An error occurred in UDP connection " + str(id) + "#, error: " + str(e))
            break
    end_time = time.time()
    print("Data count: " + str(data_count))
    print("Byte size: " + str(byte_size))
    # if data_count == byte_size:
    #     data_conversion = struct.unpack('IHHB', data)
    #     if(data_conversion[0] == MAGIC_COOKIE and data_conversion[3] == MESSAGE_TYPE_PAYLOAD):
    #         print("Data received")
    #     else:
    #         print("Data not received")
    print("UDP transfer #" + str(id) + " finished, total time: " + str(round(end_time - start_time, 2)) + " seconds, total speed: " + str(round(byte_size*8/(end_time - start_time), 2)) + " bits/second" \
        + "total percentage of data recevied: " + str(round(data_count/byte_size*100, 2)) + "%")
    udp_socket.close()






def main():
    byte_size = 16#input("Enter file size (in Bytes):")
    tcp_connections = 6#input("Enter number of TCP connections:")
    udp_connections = 6#input("Enter number of UDP connections:")

    try: 
        listen_for_offer_udp(byte_size, tcp_connections, udp_connections)
    except Exception as e:
        print("An error occurred: " + str(e))


main()