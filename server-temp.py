import socket
import time

# Broadcast server settings
BROADCAST_IP = "<broadcast>"  # Broadcast address
BROADCAST_PORT = 13117        # Port to broadcast on
MESSAGE = "Hello, clients!".encode()  # Message to broadcast

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast

print(f"Broadcasting on {BROADCAST_IP}:{BROADCAST_PORT}...")

try:
    while True:
        server_socket.sendto(MESSAGE, (BROADCAST_IP, BROADCAST_PORT))
        print(f"Broadcasted: {MESSAGE.decode()}")
        time.sleep(2)  # Broadcast every 2 seconds
except KeyboardInterrupt:
    print("Broadcast server stopped.")
finally:
    server_socket.close()