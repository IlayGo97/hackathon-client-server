import scapy.all as scapy
import socket
import threading
import time
import select
import random
import sys


def look_for_game(team_name):
    pass

def game_mode():
    pass

def main():
    print("Enter a team name:\n")
    team_name = input()
    while True:
        look_for_game(team_name)


if __name__ == '__main__':
    main()