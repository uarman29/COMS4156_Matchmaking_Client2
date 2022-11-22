import socket
import os
import time
from random import randint
from queue import Queue
import uuid
import threading
import random

player_queue = []
stats = {
    "john@gmail.com": {
        "game_parameter1_value": 10,
        "game_parameter2_value": 10,
        "game_parameter3_value": 10,
    },
    "jake@gmail.com": {
        "game_parameter1_value": 5,
        "game_parameter2_value": 2,
        "game_parameter3_value": 8,
    },
    "will@gmail.com": {
        "game_parameter1_value": 100,
        "game_parameter2_value": 25,
        "game_parameter3_value": 10,
    }
}

threads = {}

'''
# format is {
        game_id: [[player1, player2], [player3, player4]]
        game_id: [[player5, player6], [player7, player8]]
    }
'''
game_rooms = {}

def play_game(room_id):
    global game_rooms
    global stats
    for team in game_rooms[room_id]:
        for player in team:
            if player not in stats:
                stats[player] = {
                    "game_parameter1_value": 0,
                    "game_parameter2_value": 0,
                    "game_parameter3_value": 0,
                }
            stats[player]["game_parameter1_value"] += random.randint(0, 5)
            stats[player]["game_parameter2_value"] += random.randint(0, 5)
            stats[player]["game_parameter3_value"] += random.randint(0, 5)
    #time.sleep(5)

    for team in game_rooms[room_id]:
        for player in team:
            for thread_id in threads:
                if threads[thread_id]["player_email"] == player:
                    threads[thread_id]["active"] = False
    del game_rooms[room_id]

def matchmake(players_per_team, teams_per_match):
    global player_queue
    rooms = []
    while len(player_queue) > 0:
        room = []
        for i in range(0, teams_per_match):
            team = []
            for j in range(0, players_per_team):
                team.append(player_queue[0])
                player_queue.pop(0)
            room.append(team)
        rooms.append(room)
    return rooms




def multi_threaded_client(connection):
    global player_queue
    global threads
    global stats
    connection.send(str.encode('Server is working:'))
    data = connection.recv(2048)
    data = data.decode("utf-8")
    if data in player_queue:
        connection.close()
        return
    player_queue.append(data)
    threads[threading.get_ident()] = {"player_email": data, "active": True}
    while threads[threading.get_ident()]["active"] == True:
        pass
    response = ("game_parameter1_value: " + str(stats[data]["game_parameter1_value"]) + "\n" + "game_parameter2_value: " + str(stats[data]["game_parameter2_value"]) + "\n" + "game_parameter3_value: " + str(stats[data]["game_parameter3_value"]) + "\n")
    del threads[threading.get_ident()]
    connection.sendall(str.encode(response))
    connection.close()


def main():
    global player_queue
    global game_rooms

    finished_queue = Queue()
    ServerSideSocket = socket.socket()
    host = '127.0.0.1'
    port = 2022
    ThreadCount = 0

    try:
        ServerSideSocket.bind((host, port))
    except socket.error as e:
        print(str(e))

    print('Socket is listening..')
    ServerSideSocket.listen(20)

    while True:
        matches = []
        if len(player_queue) >= 2:
            matches = matchmake(1,2)
            for match in matches:
                room_id = uuid.uuid1()
                game_rooms[room_id] = match
                threading.Thread(target=play_game, args=(room_id, )).start()
        Client, address = ServerSideSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        threading.Thread(target=multi_threaded_client, args=(Client, )).start()
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
    ServerSideSocket.close()

main()