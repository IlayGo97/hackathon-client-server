import scapy.all as scapy
import socket
import threading
import time
import select


found_match = [False]

def invites(SERVER_PORT: int, MY_IP: str):
    ENDIAN = 'little'
    MAGICK_COOKIE = 0xabcddcba.to_bytes(4, ENDIAN)
    MESSAGE_TYPE = 0x2.to_bytes(1, ENDIAN)
    INVITES_PORT = 13117
    SERVER_PORT = SERVER_PORT.to_bytes(2, ENDIAN)
    packet = MAGICK_COOKIE + MESSAGE_TYPE + SERVER_PORT

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((MY_IP, 0))
    try:
        while not found_match[0]:
            sock.sendto(packet, ("255.255.255.255", INVITES_PORT))
            time.sleep(1)
    finally:
        sock.close()
    pass

def wait_for_clients(ip_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip_address, 0))
    invites_thread = threading.Thread(target= invites, args=(sock.getsockname()[1],ip_address,))
    invites_thread.start()
    print("port = {port}".format(port=sock.getsockname()[1]))

    number_of_players = 0
    player_sockets = []
    print("Server started, listening on IP {ip}".format(ip=ip_address))
    while number_of_players < 2:
        sock.listen()
        (socket_player, player_IP) = sock.accept()
        player_sockets.append(socket_player)
        number_of_players = number_of_players + 1
        print("Found player {player} !".format(player= number_of_players))
    found_match[0] = True
    sock.close()
    print("found 2 players!")
    return player_sockets

def game_mode(player_sockets):
    player1_socket = player_sockets[0]
    player2_socket = player_sockets[1]
    player1_name = player1_socket.recv(1024).decode()
    player2_name = player2_socket.recv(1024).decode()
    number_question = "2+2"
    answer = "4"
    welcome_string = "Welcome to Quick Maths.\nPlayer 1: {player1}\nPlayer 2: {player2}\n==".format(player1=player1_name, player2=player2_name)
    question_string = "\nPlease answer the following question as fast as you can:\nHow much is {question}?".format(question= number_question)
    timeout_string = "Connection timed-out, a draw."
    player1_socket.send((welcome_string + question_string).encode())
    player2_socket.send((welcome_string + question_string).encode())
    first_player, x, y = select.select(player_sockets, [], player_sockets, 10)
    if not first_player or len(first_player) == 0:
        player2_socket.send(timeout_string.encode())
        player1_socket.send(timeout_string.encode())
        player1_socket.close()
        player2_socket.close()
        return
    answering_sock = first_player[0]
    winning_string = "The answer was {ans}!\n".format(ans=answer)
    try:
        first_answer = answering_sock.recv(512).decode("utf-8")
        first_answer = first_answer.split()[0]
        print("received answer! {answer}".format(answer= first_answer))
        if first_answer == answer and answering_sock == player1_socket:
            winning_string = winning_string + "TEAM {team_name} WINS, FATALITY!".format(team_name= player1_name)
        elif answering_sock == player1_socket:
            winning_string = winning_string + "TEAM {team_name} WINS, PERFECT!".format(team_name= player2_name)
        elif first_answer == answer and answering_sock == player2_socket:
            winning_string = winning_string + "TEAM {team_name} WINS, THEY ARE UNBEATABLE (in the last 1 matches)!".format(team_name= player2_name)
        elif answering_sock == player2_socket:
            winning_string = winning_string + "TEAM {team_name} WINS, AMAZING PERFORMANCE!".format(team_name= player1_name)
        player1_socket.send(winning_string.encode("utf-8"))
        player2_socket.send(winning_string.encode("utf-8"))
    finally:
        player1_socket.shutdown(socket.SHUT_RDWR)
        player2_socket.shutdown(socket.SHUT_RDWR)
        print("game is over.")


def main():
    while True:
        found_match[0] = False
        players = wait_for_clients("127.0.0.1")
        print("a new game starts in 10 seconds!")
        time.sleep(10)
        game_mode(players)

if __name__ == '__main__':
    main()