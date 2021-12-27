import scapy.all as scapy
import struct
import socket
import threading


def receive(socket, signal):
    try:
        while signal[0]:
            try:
                data = socket.recv(1024)
                message = data.decode("utf-8")
                if message == '':
                    signal[0] = False
                print(message)
            except:
                signal[0] = False
                break
    finally:
        print("Server disconnected, listening for offer requests...\npress enter to search for a new game.")


def look_for_game(my_ip: str):
    invites_port = 13117
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((my_ip, invites_port))
    print("Client started, listening for offer requests...")
    data, address = sock.recvfrom(512)
    (HOST_IP, trash) = address
    print("Received offer from {hostip}, attempting to connect...".format(hostip=HOST_IP))
    (COOKIE, MESSAGE_TYPE, HOST_PORT) = struct.unpack('IbH', data)
    # sock.close()
    return HOST_IP, HOST_PORT


def game_mode(host_address, team_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(host_address)
    except:
        print("TCP connection was declined.")
        return
    signal = [True]
    receive_thread = threading.Thread(target=receive, args=(sock, signal))
    receive_thread.start()
    sock.sendall(str.encode(team_name))
    while signal[0]:
        message = input()
        sock.sendall(str.encode(message))
    print("Game shutdown.")


def main():
    my_ip = socket.gethostbyname(socket.gethostname())
    print("Enter a team name:")
    team_name = input()
    while True:
        host_address = look_for_game(my_ip)
        game_mode(host_address, team_name)
        print("Searching for a new game.")


if __name__ == '__main__':
    main()
