import socket
import struct
import threading
import time

BROADCAST_PORT = 13117
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE_PAYLOAD = 0x4
MESSAGE_TYPE_REQUEST = 0x3
MESSAGE_TYPE_OFFER = 0x2


def listen_for_offer_udp(byte_size, tcp_connections, udp_connections):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.bind(("", BROADCAST_PORT))
    print("Client started, listening for offer requests...")
    data, addr = udp_socket.recvfrom(9)
    print("Received offer from: %s" % addr[0])
    data_converted = struct.unpack('!IBHH', data)
    data_converted = list(data_converted)
    if(data_converted[0] == MAGIC_COOKIE and data_converted[1] == MESSAGE_TYPE_OFFER):
        udp = data_converted[2]
        tcp = data_converted[3]
        print("Offer received, connecting to server")
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
                print(f"Received incomplete packet: {len(data)} bytes")
                continue  # Skip processing if data is too small

            payload_data = data[HEADER_SIZE:]  # Exclude header
            data_count += len(payload_data)  # Count only payload bytes

        except Exception as e:
            print(f"An error occurred in UDP connection {id}#, error: {e}")
            break

    end_time = time.time()
    
    print(f"Data count (payload only): {data_count}")
    print(f"Expected payload size: {payload_size}")
    
    if data_count == payload_size:
        print("Data received successfully")
    else:
        print("Data not fully received")
    
    print(f"UDP transfer #{id} finished, total time: {round(end_time - start_time, 2)} seconds, "
          f"total speed: {round(payload_size * 8 / (end_time - start_time), 2)} bits/second, "
          f"total percentage of data received: {round(data_count / payload_size * 100, 2)}%")
    
    udp_socket.close()







def main():
    byte_size = 999999#input("Enter file size (in Bytes):")
    tcp_connections = 6#input("Enter number of TCP connections:")
    udp_connections = 6#input("Enter number of UDP connections:")

    try: 
        listen_for_offer_udp(byte_size, tcp_connections, udp_connections)
    except Exception as e:
        print("An error occurred: " + str(e))


main()