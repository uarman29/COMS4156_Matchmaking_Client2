# Matchmaking API Client

This is a client for our matchmaking API

Note that this client requires that developers set up
some background information and obtain an API Key from our developer portal.

Matchmaking API Developer Portal:
https://github.com/uarman29/COMS4156_Matchmaking_Client

## Function
The client is a server that does the following things:
 - Manages player connections
 - Calls our matchmaking API to matchmake based on those connections
 - Assigns connected player to game rooms
 - Lets players "play" the game
 - Computes updated stats from the result of the game and updates the stats in our API
 - Returns updated stats to player
 - Continues listening for player connections


## Simulation
To simulate this you can do the following:
1. Run the server: ```python3 server.py <API-KEY> <Game_Id>```
2. Simulate Player connections by running the player script multiple times and 
inputting a player email each time ```python3 player.py```