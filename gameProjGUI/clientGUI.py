import socket
from threading import Thread
from tkinter import *

FORMAT = 'utf-8'
BUFFER_SIZE = 1024

# Set GUI for client-side lobby
class ClientGUI:

    def __init__(self):
        # Set up Networking Base
        self.port = 5050
        self.host = "127.0.0.1"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1)
        self.name = "Anonymous"
        self.activeGames = []

        #root window - hidden until sign-in and connection 
        self.window = Tk()
        self.window.title("Fight Game Lobby")
        self.window.configure(width = 500, height = 600)

        # Game List Box
        self.gameListLabel = Label(self.window, text = "Game List", pady = 5)
        self.gameListLabel.place(relwidth = 1)
        self.gameList = Listbox(self.window, selectmode = SINGLE, width = 20, height = 2)
        self.gameList.place(relwidth = 1, relheight = .3, rely = .05)
        self.gameListScroll = Scrollbar(self.gameList)
        self.gameListScroll.pack(side = RIGHT, fill = Y)

        # Join Game Button
        self.joinBtn = Button(self.window, text = "Join Game")
        self.joinBtn.place(relx = .44, rely = .36)

        # Create Game Button
        self.createBtn = Button(self.window, text = "Create New Game", command = self.createWindow)
        self.createBtn.place(relx = .75, rely = .36)

        # Chat Area
        self.gameListLabel = Label(self.window, text = "Chat Room")
        self.gameListLabel.place(relwidth = 1, rely = .43)
        self.chatRoomTxt = Text(self.window, width = 20, height = 2)
        self.chatRoomTxt.place(relwidth = 1, relheight = .3, rely = .48)
        self.chatRoomTxt.config(state=DISABLED)
        self.chatScroll = Scrollbar(self.chatRoomTxt)
        self.chatScroll.pack(side = RIGHT, fill = Y)

        # Message bar
        self.messageBar = Entry(self.window)
        self.messageBar.place(relwidth = .7, relx =.04, rely = .81)
        self.messageBar.focus()

        # Send chat Message Button
        self.sendBtn = Button(self.window, text = "Send Message", command = lambda: self.sendMessage(self.messageBar.get()))
        self.sendBtn.place(relx = .8, rely = .8)

        # Hide main lobby window
        self.window.withdraw()

        # Set up log-in window
        self.login = Toplevel()
        self.login.title("Welcome to the Fight Game")
        self.login.configure(width=300, height=100)
        self.userLoginMSG = Label(self.login, text = "Enter User Name to Connect", justify = CENTER)
        self.userLoginMSG.place(relx = .24, rely = .05)

        # Text input for user name
        self.userName = Entry(self.login)
        self.userName.place(relheight = .2, relwidth = .5, relx = .25, rely = .3)
        self.userName.focus()

        # Login Button - which will initialize connect
        self.loginBtn = Button(self.login, text = "Login", command = lambda: self.loginConnect(self.userName.get()))
        self.loginBtn.place(relx = .45, rely = .6)
        
        self.window.mainloop()

    def loginConnect(self, userName):
        self.name = userName
        # Make server connection
        self.sock.connect((self.host, self.port))
        # send username
        userName = userName.encode(FORMAT)
        self.sock.send(userName)
        # Remove login window
        self.login.destroy()
        # Reveal main window
        self.window.deiconify()
        # Set thread for receiving message from server
        receiveThread = Thread(target=self.receive)
        receiveThread.start()
        
    def createWindow(self):
        # Create Game window
        self.createGame = Toplevel()
        self.createGame.title("Create a New Game")
        self.createGame.configure(width=300, height=100)
        # game name
        self.newgameNameLbl = Label(self.createGame, text = "Game name: ", justify = LEFT)
        self.newgameNameLbl.place(relx = .1, rely = .05)
        self.gameName = Entry(self.createGame)
        self.gameName.place(relheight = .2, relwidth = .3, relx = .1, rely = .25)
        self.gameName.focus()
        # Number of Players
        self.newgameNumberLbl = Label(self.createGame, text = "Players: ", justify = RIGHT)
        self.newgameNumberLbl.place(relx = .7, rely = .05)
        self.numPlayers = IntVar(self.createGame)
        self.numPlayers.set(2)
        self.playerNumOption = OptionMenu(self.createGame, self.numPlayers, 2, 4)
        self.playerNumOption.place(relx = .7, rely = .25)
        # create Game
        self.createNewGameBtn = Button(self.createGame, text = "Create Game", 
                                       command = lambda: self.createNewGame(self.gameName.get(), self.numPlayers.get()))
        self.createNewGameBtn.place(relx = .1, rely = .62)
        
    # parse incoming messages for header info
    def messageParser(self, message):
        parsedMessage = message.split("\n")
        return parsedMessage[0], parsedMessage[1]
    
    # parse the game info
    def gameParser(self, message):
        parsedGame = message.split("\t")
        return parsedGame[0], parsedGame[1]
        
    def receive(self):
        while True:
            try:
                msg = self.sock.recv(BUFFER_SIZE).decode(FORMAT)
                # parse for relevant info
                header, message = self.messageParser(msg)
                if message and header:
                    if header == "message":
                        # insert message into lobby chat
                        self.chatRoomTxt.config(state=NORMAL)
                        self.chatRoomTxt.insert(END, message+"\n")
                        self.chatRoomTxt.config(state=DISABLED)
                        self.chatRoomTxt.see(END)
                    elif header == "newgame":
                        # insert new game info into game list
                        gameName, numPlayers = self.gameParser(message)
                        gameItem = gameName + "          " + numPlayers
                        self.gameList.delete(0, END)
                        self.activeGames.append(gameItem)
                        for game in self.activeGames:
                            self.gameList.insert(END, game)    
            except socket.timeout:
                continue
    
    # send chat message
    def sendMessage(self, message):
        self.messageBar.delete(0, END)
        message = "message\n" + message
        self.sock.send(bytes(message, FORMAT))
    
    # send new game info
    def createNewGame(self, game, num):
        self.createGame.destroy()
        message = "newgame\n" + game + "\t" + str(num)
        self.sock.send(bytes(message, FORMAT))
                      
app = ClientGUI()