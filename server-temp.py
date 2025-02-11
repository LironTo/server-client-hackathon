from socket import *
import time
import threading
import struct

packet_size = 1024

def main():
    print("starting brodcast")
    thread1 = threading.Thread(target=UDP_Brodcast)
    
    #_thread.start_new_thread(UDP_Brodcast,())
    print("starting TCP server")
    thread2 = threading.Thread(target=TCP_Server)
    print("starting UDP server")
    thread3 = threading.Thread(target=UDP_Server)

    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()




def TCP_Server():
    #create a socket object
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    port = 13117
    tcp_socket.bind(('', port))
    #start listening
    tcp_socket.listen(5)
    print("TCP socket is listening")
    thredList =[]
    while True:
        #connection with client
        conn, addr = tcp_socket.accept()
        print("Got TCP connection from", addr)
        #create a new thread to send the file
        therd = threading.Thread(target=TCP_Payload,args=(conn,addr,"server.py"))
        thredList.append(therd)
        therd.start()
    for t in thredList:
        t.join()

def UDP_Server():
    #create a socket object
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    port = 0x303A
    udp_socket.bind(('', port))
    thredList =[]
    print("UDP socket is listening")
    while True:
        #get a packet
        data, addr = udp_socket.recvfrom(1024)
        print("Got UDP connection from", addr)
        #unpack the header
        header = struct.unpack('I B L',data[:13])
        #check if the packet is a file request
        if header[0] != 0xabcddcba or header[1] != 0x03:
            continue
        #create a new thread to send the file
        therd = threading.Thread(target=UDP_Payload,args=(addr,header[2],"file.pdf"))
        thredList.append(therd)
        therd.start()
    for t in thredList:
        t.join()


def TCP_Payload(conn,addr,file):
    print("TCP payload")
    #open the file
    file = open(file, "rb")

    #get the size of the file
    data = conn.recv(1024)
    size = int(data[:-1])
    print("Server received", size)

    #send the file
    dataToSend = str(file.read(size)) + '\n'
    conn.send(dataToSend.encode())
    conn.close()

def UDP_Payload(addres,size,file):
    print("UDP payload")
    #create a socket object
    Udp_socket = socket(AF_INET, SOCK_DGRAM)
    #open the file
    file = open(file, "rb")

    index = 0
    while size:
        #read the file
        if size > packet_size:
            data = file.read(packet_size)
            size -= packet_size
        else:
            data = file.read(size)
            size = 0
        index+=1

        """
        21 bit header:
        magic number: 0xabcddcba
        message type: 0x04
        Total segment count: unsigned int, size/packet_size
        Packet index: unsigned int, index
        """
        header = struct.pack('I B L L',0xabcddcba,0x04,size//packet_size + 1 ,index)  
        packet = header + data

        #send part of the file
        Udp_socket.sendto(packet, addres)
        
    Udp_socket.close()


def UDP_Brodcast():
    # Create a socket object
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    print("Brodcast Socket created")
    """
    9 bit messege:
    magic number: 0xabcddcba
    message type: 0x02
    UDP port: 0x303A
    TCP port: 0x303B
    """
    packet = struct.pack('I B H H',0xabcddcba,0x02,0x303A,0x303B)  # Packet index as unsigned int
    # Define the port on which you want to connect
    port = 12345

    udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    while True:
        udp_socket.sendto(packet, ('<broadcast>', port))
        time.sleep(1)


if __name__ == "__main__":
    main()