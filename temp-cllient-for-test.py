import socket

# Listening client settings
LISTEN_PORT = 13117  # Port to listen on

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast
client_socket.bind(("", LISTEN_PORT))  # Bind to all available interfaces

print(f"Listening for broadcasts on port {LISTEN_PORT}...")

try:
    while True:
        data, addr = client_socket.recvfrom(1024)  # Buffer size of 1024 bytes
        print(f"Received message: '{data.decode()}' from {addr}")
except KeyboardInterrupt:
    print("Client stopped listening.")
finally:
    client_socket.close()