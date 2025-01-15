import socket
import struct
import threading
import time

# Constants
MAGIC_COOKIE = 0xabcddcba
OFFER_TYPE = 0x2
UDP_PORT = 13117
TCP_PORT = 12345

def broadcast_offers():
    """Broadcasts UDP offers to all clients on the network."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as udp_sock:
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        offer_message = struct.pack('!IBHH', MAGIC_COOKIE, OFFER_TYPE, UDP_PORT, TCP_PORT)
        while True:
            udp_sock.sendto(offer_message, ('<broadcast>', UDP_PORT))
            #print("Server: Broadcast offer sent.")
            time.sleep(1)

def handle_client(client_socket, client_address):
    """Handles TCP/UDP requests from a client."""
    try:
        print(f"Connected to client {client_address}")
        file_size = int(client_socket.recv(1024).decode().strip())  # Receive file size
        data = b'a' * file_size  # Generate mock data
        client_socket.sendall(data)
        print(f"Sent {file_size} bytes to client {client_address}.")
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        client_socket.close()

def start_server():
    """Starts the server to handle client requests."""
    threading.Thread(target=broadcast_offers, daemon=True).start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.bind(('', TCP_PORT))
        tcp_sock.listen()
        print(f"Server listening on TCP port {TCP_PORT}...")
        while True:
            client_sock, client_addr = tcp_sock.accept()
            threading.Thread(target=handle_client, args=(client_sock, client_addr), daemon=True).start()

if __name__ == "__main__":
    start_server()