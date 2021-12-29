import scapy.all as scapy
import struct
import socket
import threading
UDP_ADDRESS = ('<broadcast>', 13117)
# receives messages from the server and notifies if the server shutdown.
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
        # the main thread is stuck on input() so we need to guide him...
        print("Server disconnected, listening for offer requests...\npress enter to search for a new game.")

# listens to the predetermined port for broadcasted invites.
def look_for_game(my_ip: str):
    invites_port = 13117
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((my_ip, invites_port))
    print("Client started, listening for offer requests...")
    while True:
        data, address = sock.recvfrom(512)
        (HOST_IP, trash) = address
        print("Received offer from {hostip}, attempting to connect...".format(hostip=HOST_IP))
        try:
            (COOKIE, MESSAGE_TYPE, HOST_PORT) = struct.unpack('!IbH', data)
            break
        except:
            print("Recieved bad invite, trying to find anothr...")
    sock.close()
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
    # sends messages until servers shuts the connection on its end
    while signal[0]:
        message = input()
        sock.sendall(str.encode(message))
    print("Game shutdown.")


def main():
    print("What network do you want to use? (Ethernet 1 etc)")
    inteface = input()
    try:
        my_ip = scapy.get_if_addr(inteface)
    except:
        print("Couldn't connect to " + inteface)
        return
    print("Enter a team name:")
    team_name = input()
    while True:
        host_address = look_for_game(my_ip)
        game_mode(host_address, team_name)
        print("Searching for a new game.")


if __name__ == '__main__':
    main()
