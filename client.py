import socket
import struct
import threading
import time

MAGIC_COOKIE = 0xabcddcba
REQUEST_TYPE = 0x3
OFFER_TYPE = 0x2
UDP_PORT = 13117

def listen_for_offers():
    """Listens for UDP broadcast offers from servers."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_sock.bind(('', UDP_PORT))
        print("Client listening for server offers...")
        while True:
            try:
                message, address = udp_sock.recvfrom(1024)
                if len(message) < 8:
                    print(f"Received invalid offer packet from {address[0]}")
                    continue
                # Unpack the offer message
                magic_cookie, message_type, server_udp, server_tcp = struct.unpack('!IBHH', message)
                if magic_cookie == MAGIC_COOKIE and message_type == OFFER_TYPE:
                    print(f"Received offer from {address[0]} (TCP: {server_tcp}, UDP: {server_udp})")
                    return address[0], server_tcp
                else:
                    print(f"Invalid offer from {address[0]}: Magic cookie or type mismatch")
            except Exception as e:
                print(f"Error while listening for offers: {e}")

def perform_speed_test(server_ip, server_tcp_port, file_size):
    """Performs a TCP speed test."""
    try:
        start_time = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            tcp_sock.settimeout(10)  # Add a timeout for the connection
            tcp_sock.connect((server_ip, server_tcp_port))
            tcp_sock.sendall(f"{file_size}\n".encode())
            
            received_data = b''
            while True:
                data = tcp_sock.recv(1024)
                if not data:
                    break
                received_data += data

        total_time = time.time() - start_time
        speed = len(received_data) * 8 / total_time  # Convert bytes to bits
        print(f"TCP transfer complete: {len(received_data)} bytes in {total_time:.2f} seconds. Speed: {speed:.2f} bits/second")
    except socket.timeout:
        print(f"Connection to server {server_ip} timed out.")
    except Exception as e:
        print(f"Error during speed test: {e}")


if __name__ == "__main__":
    try:
        server_ip, server_tcp_port = listen_for_offers()
        while True:
            try:
                file_size = int(input("Enter file size (in bytes): "))
                if file_size <= 0:
                    print("File size must be greater than 0.")
                    continue
                perform_speed_test(server_ip, server_tcp_port, file_size)
            except ValueError:
                print("Please enter a valid integer for file size.")
    except KeyboardInterrupt:
        print("\nClient shutting down.")
    except Exception as e:
        print(f"Unexpected error in client: {e}")