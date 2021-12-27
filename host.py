import scapy.all as scapy
import socket
import threading
import time
import select
import random
import struct

# used for colored prompts
class bcolors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


found_match = [False]

# a function for sending invites over the predetermined port.
# runs on a different thread.
def invites(SERVER_PORT: int, MY_IP: str):
    MAGIC_COOKIE = 0xabcddcba
    MESSAGE_TYPE = 0x2
    INVITES_PORT = 13117
    packet = struct.pack('IbH', MAGIC_COOKIE, MESSAGE_TYPE, SERVER_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((MY_IP, 0))
    while not found_match[0]:
        sock.sendto(packet, ("255.255.255.255", INVITES_PORT))
        time.sleep(1)
    sock.close()
    return

# wait for 2 clients.
def wait_for_clients(ip_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip_address, 0))
    invites_thread = threading.Thread(target=invites, args=(sock.getsockname()[1], ip_address,))
    invites_thread.start()
    print("starting on port = {port}".format(port=sock.getsockname()[1]))
    number_of_players = 0
    player_sockets = []
    print("Server started, listening on IP {ip}".format(ip=ip_address))
    while number_of_players < 2:
        sock.listen()
        (socket_player, player_IP) = sock.accept()
        player_sockets.append(socket_player)
        number_of_players = number_of_players + 1
        print("Found player {player}!".format(player=number_of_players))
    found_match[0] = True # to notify the invites thread it should die.
    sock.close()
    return player_sockets

# simple question generation function.
def generate_question():
    scalar1 = random.randint(0, 3)
    scalar2 = random.randint(0, 3)
    operator_r = random.randint(0, 2)
    if operator_r == 0:
        operator = " + "
        answer = str(scalar1 + scalar2)
    elif operator_r == 1:
        operator = " * "
        answer = str(scalar1 * scalar2)
    else:
        operator = " - "
        if scalar1 > scalar2:
            answer = str(scalar1 - scalar2)
        else:
            temp = scalar1
            scalar1 = scalar2
            scalar2 = temp
            answer = str(scalar1 - scalar2)
    question = str(scalar1) + operator + str(scalar2)
    return question, answer

# when starting a game session.
def game_mode(player_sockets):
    player1_socket = player_sockets[0]
    player2_socket = player_sockets[1]
    try:
        # receives team names.
        player1_name = player1_socket.recv(1024).decode()
        player2_name = player2_socket.recv(1024).decode()

        number_question, answer = generate_question()
        welcome_string = (bcolors.BLUE + "Welcome to Quick Maths." + bcolors.ENDC + bcolors.GREEN + "\nPlayer 1: {player1}" + bcolors.ENDC + bcolors.CYAN + "\nPlayer 2: {player2}" + bcolors.ENDC + "\n==").format(
            player1=player1_name, player2=player2_name)
        question_string = "\nPlease answer the following question as fast as you can:\nHow much is {question}?".format(
            question=number_question)
        question_string = bcolors.PURPLE + bcolors.BOLD + question_string + bcolors.ENDC
        timeout_string = bcolors.RED + "Connection timed-out, a draw." + bcolors.ENDC
        # sending welcome message and question to both players.
        player1_socket.sendall((welcome_string + question_string).encode())
        player2_socket.sendall((welcome_string + question_string).encode())
        first_player, x, y = select.select(player_sockets, [], player_sockets, 10)
        if not first_player or len(first_player) == 0:
            player2_socket.sendall(timeout_string.encode())
            player1_socket.sendall(timeout_string.encode())
            player1_socket.shutdown(socket.SHUT_RDWR)
            player2_socket.shutdown(socket.SHUT_RDWR)
            return
        answering_sock = first_player[0]
        winning_string = "The answer was {ans}!\n".format(ans=answer)
        first_answer = answering_sock.recv(512).decode("utf-8")
        first_answer = first_answer.split()[0]
        print("received answer! {answer}".format(answer=first_answer))
        if first_answer == answer and answering_sock == player1_socket:
            winning_string = winning_string + "TEAM {team_name} WINS, FATALITY!".format(team_name=player1_name)
        elif answering_sock == player1_socket:
            winning_string = winning_string + "TEAM {team_name} WINS, PERFECT!".format(team_name=player2_name)
        elif first_answer == answer and answering_sock == player2_socket:
            winning_string = winning_string + "TEAM {team_name} WINS, THEY ARE UNBEATABLE (in the last 1 matches)!".format(
                team_name=player2_name)
        elif answering_sock == player2_socket:
            winning_string = winning_string + "TEAM {team_name} WINS, AMAZING PERFORMANCE!".format(
                team_name=player1_name)
        winning_string = bcolors.YELLOW + winning_string + bcolors.ENDC
        player1_socket.sendall(winning_string.encode())
        player2_socket.sendall(winning_string.encode())
    except:
        print("Connection error.")
    finally:
        player1_socket.shutdown(socket.SHUT_RDWR)
        player2_socket.shutdown(socket.SHUT_RDWR)
        print("Game over, sending out offer requests...")


def main():
    # for lab purposes.
    print("What network do you want to use? (Ethernet 1 etc)")
    inteface = input()
    try:
        my_ip = scapy.get_if_addr(inteface)
    except:
        print("Couldn't connect to "+inteface)
        return
    while True:
        found_match[0] = False
        players = wait_for_clients(my_ip)
        my_ip = my_ip.split()[0]
        print("a new game starts in 10 seconds!")
        time.sleep(10)
        game_mode(players)


if __name__ == '__main__':
    main()
