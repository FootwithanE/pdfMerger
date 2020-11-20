import socket
import threading
import select

BUFFER_SIZE = 1024
FORMAT = "utf-8"
PORT = 5050
HOST = "127.0.0.1"

sockets = []
clients = {}
games = {}

# Game class to track game stats
class Game:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.players = []

# Handle new client connections
def setNewClient(connection):
    clientName = connection.recv(BUFFER_SIZE).decode(FORMAT)
    sockets.append(connection)
    clients[connection] = clientName
    print(f'{clientName} connected to the server.')
    
# broadcast message to all clients
def broadcast(sender, message, type):
    # if chat message add sender info
    if type == "message":
        for sock in sockets:
            if sock != sockets[0]:
                sock.send(bytes(type + "\n" + str(clients[sender] + ": ") + message, FORMAT))
                print("Message sent!")
    # if new game send just game info
    elif type == "newgame":
        for sock in sockets:
            if sock != sockets[0]:
                sock.send(bytes(message, FORMAT))
                print("Game sent!")
                 
# parse incoming messages for header info
def messageParser(message):
    parsedMessage = message.split("\n")
    return parsedMessage[0], parsedMessage[1]

# parse the game info
def gameParser(message):
    # game name and players split by \t char
    parsedGame = message.split("\t")
    return parsedGame[0], parsedGame[1]

# Start and run main thread of server
def start():
    # Make connection
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    # Add server socket to lists of sockets
    sockets.append(server)

    print("Server has started...")
    
    while True:
        # continually checks list of sockets for something to read, something to write, or error state
        clientSockets, waitingSockets, badSockets = select.select(sockets, [], [], 1) # set T.O. to 1 sec
        
        # Iterate through clientSockets
        for sock in clientSockets:
            # If server socket then create new connection
            if sock == server:
                # Handle new connection with client
                client, clientAddress = server.accept()
                print(f'{client} connected to the lobby...')
                setNewClient(client)
            else:
                try:
                    # receive any message
                    msg = sock.recv(BUFFER_SIZE).decode(FORMAT)
                    # parse for relevant info
                    header, message = messageParser(msg)
                    # if both header and message have data
                    if message and header:
                        # if header is message (lobby chat message)
                        if header == "message":
                            # broadcast message to all clients in lobby
                            print(f'Received a message...\n{message}\n')
                            broadcast(sock, message, header)
                        # if header is new game creation
                        elif header == "newgame":
                            # parse game info for name and players
                            gameName, numPlayers = gameParser(message)
                            # create new game object
                            newGame = Game(gameName, numPlayers)
                            # add creator to game players list
                            newGame.players.append(clients[sock])
                            # add game to game list
                            games[gameName] = newGame
                            # send new game info to clients
                            broadcast(sock, msg, header)
                        # add join game
                # need logic for smooth disconnect of client          
                except:        
                    continue
start()