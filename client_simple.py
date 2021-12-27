import socket
import threading
import sys


def receive(socket, signal):
    try:
        while signal:
            try:
                data = socket.recv(1024)
                print(data.decode("utf-8"))
            except:
                print("You have been disconnected from the server")
                signal = False
                break
    finally:
        print("Stopped receiving from the server.")

#Get host and port
host = input("Host: ")
port = int(input("Port: "))

#Attempt connection to server
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
except:
    print("Could not make a connection to the server")
    input("Press enter to quit")
    sys.exit(0)

#Create new thread to wait for data
receiveThread = threading.Thread(target = receive, args = (sock, True))
receiveThread.start()

#Send data to server
#str.encode is used to turn the string message into bytes so it can be sent across the network
while True:
    message = input()
    sock.sendall(str.encode(message))