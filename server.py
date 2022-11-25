import socket
import os
import time
from random import randint
from queue import Queue
import uuid
import threading
import random
import requests
import sys
from datetime import datetime


USAGE = "Usage: server.py <API Key> <Game Id> <Mode(Optional)>"
matchmaking_api_url = "http://127.0.0.1:18080"
player_queue = []
game_rooms = {}
threads = {}

API_KEY = ""
GAME_ID = -1

mutex = threading.Lock()

def print_time(*arg, **kwarg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(timestamp, *arg, **kwarg)


def get_game_details():
    global API_KEY
    global GAME_ID
    headers = {"Authorization": "Bearer " + API_KEY}

    response = requests.get(
        matchmaking_api_url + "/games/" + GAME_ID,
        headers = headers,
    )

    if (response.status_code == 200):
        game = response.json()
        return game
    return None


def get_player_stats(player_email):
    global API_KEY
    global GAME_ID
    headers = {"Authorization": "Bearer " + API_KEY}

    request_obj = {
        "player_emails": [player_email]
    }
    response = requests.get(
        matchmaking_api_url + "/games/" + GAME_ID + "/players/" + player_email,
        headers = headers,
        json=request_obj
    )

    if (response.status_code == 200):
        stats = response.json()
        return stats[player_email]
    return None


def update_player_stats(player_email, stats):
    global API_KEY
    global GAME_ID
    headers = {"Authorization": "Bearer " + API_KEY}

    request_obj = {}
    request_obj[player_email] = stats
    response = requests.put(
        matchmaking_api_url + "/games/" + GAME_ID + "/players",
        headers = headers,
        json = request_obj
    )

    if (response.status_code == 200):
        return 200
    return None


def play_game(room_id):
    global game_rooms
    for team in game_rooms[room_id]:
        for player in team:
            stats = get_player_stats(player)
            stats["game_parameter1_value"] += random.randint(0, 5)
            stats["game_parameter2_value"] += random.randint(0, 5)
            stats["game_parameter3_value"] += random.randint(0, 5)
            stats["game_parameter4_value"] += random.randint(0, 5)
            update_player_stats(player, stats)
            stats = get_player_stats(player)

    for team in game_rooms[room_id]:
        for player in team:
            for thread_id in threads:
                if threads[thread_id]["player_email"] == player:
                    threads[thread_id]["active"] = False
                    threads[thread_id]["details"] = game_rooms[room_id]
    del game_rooms[room_id]


def matchmake(mode):
    global player_queue
    global matchmaking_api_url
    global API_KEY
    global GAME_ID
    global mutex
    headers = {"Authorization": "Bearer " + API_KEY}
    matchmake_obj = {
        'game_id': GAME_ID,
        'matchmaking_type': mode,
        'player_emails': player_queue
    }

    response = requests.post(matchmaking_api_url +"/matchmake", headers=headers, json = matchmake_obj)
    if(response.status_code == 200):
        matches = response.json()
        rooms = []
        for game_number in matches:
            room = []
            if game_number != "overflow":
                for team_number in matches[game_number]:
                    team = []
                    for player in matches[game_number][team_number]:
                        team.append(player)
                        mutex.acquire()
                        player_queue.remove(player)
                        mutex.release()
                    room.append(team)
                rooms.append(room)
        return rooms
    return []




def multi_threaded_client(connection):
    global player_queue
    global threads
    global stats
    global mutex
    connection.send(str.encode('Server is working:'))
    data = connection.recv(2048)
    data = data.decode("utf-8")
    mutex.acquire()
    if data in player_queue:
        mutex.release()
        connection.close()
        return
    else:
        player_queue.append(data)
        mutex.release()
        threads[threading.get_ident()] = {"player_email": data, "active": True}
        while threads[threading.get_ident()]["active"] == True:
            pass
        response = "Played Game,\nRoom Details: \n"+ str(threads[threading.get_ident()]["details"]) + "\nNew stats:\n" + str(get_player_stats(data))
        del threads[threading.get_ident()]
        connection.sendall(str.encode(response))
        connection.close()

def internal_matchmake(mode):
    global player_queue
    global game_rooms
    global mutex
    game_details = get_game_details()
    min_players = game_details["players_per_team"] * game_details["teams_per_match"]

    while True:
        time.sleep(10)
        mutex.acquire()
        if len(player_queue) >= min_players:
            mutex.release()
            matches = matchmake(mode)
            print_time("Matches Made")
            print_time(matches)
            for match in matches:
                room_id = uuid.uuid1()
                game_rooms[room_id] = match
                threading.Thread(target=play_game, args=(room_id, )).start()
        else:
            mutex.release()
            print_time("Not enough players to matchmake")
    
def main():
    global player_queue
    global game_rooms
    global API_KEY
    global GAME_ID
    global mutex

    mode = "basic"
    if len(sys.argv) == 3:
        API_KEY, GAME_ID = sys.argv[1:]
    elif len(sys.argv) == 4:
        API_KEY, GAME_ID, mode = sys.argv[1:]
    else:
        sys.exit(USAGE)

    ServerSideSocket = socket.socket()
    host = '127.0.0.1'
    port = 2022

    try:
        ServerSideSocket.bind((host, port))
    except socket.error as e:
        print_time(str(e))

    print_time('Socket is listening..')
    ServerSideSocket.listen(20)

    threading.Thread(target=internal_matchmake, args=(mode, )).start()
    while True:
        try:
            Client, address = ServerSideSocket.accept()
            print_time('Connected to: ' + address[0] + ':' + str(address[1]))
            threading.Thread(target=multi_threaded_client, args=(Client, )).start()
        except:
            ServerSideSocket.close()
            sys.exit()
    ServerSideSocket.close()

main()