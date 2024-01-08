# CODE FOR CREATING A TCP-Chat Server

import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', 9999))

s.listen(3)
clients=[]
nicknames=[]
print("Server setup done")

def broadcast(msg, theSender = None):
    for c in clients:
        if(c != theSender):
            c.send(msg.encode('utf-8'))

def handle(c):
    while True:
        msg= c.recv(1024).decode()
        if(msg[len(msg)-9: len(msg)] != "adminMode"):
            broadcast(msg, c)

        else:
            # print(nicknames)
            s1 = "Admin mode activated\n"
            s2 = "Who do you want to kick?"
            c.send(s1.encode('utf-8'))
            c.send(s2.encode('utf-8'))

            nick = c.recv(1024).decode()
            coIdx=0
            for i in range(len(nick)):
                if(nick[i] == ':'):
                    coIdx=i+2
                    break

            nick = nick[coIdx:]
            idx = nicknames.index(nick)
            nicknames.remove(nick)
            cl = clients[idx]
            clients.remove(cl)

            idxOfKicker= clients.index(c)
            nameOfKicker= nicknames[idxOfKicker]

            broadcast(f'{nick} has been kicked out by {nameOfKicker}')


while True:
    c, adr= s.accept()
    c.send(bytes("FK", 'utf-8'))

    nickname= str(c.recv(1024).decode())

    clients.append(c)
    nicknames.append(nickname)
    
    msg = f'{nickname} has joined the chat!!!'

    broadcast(msg)
    print(msg)

    handle_Thread = threading.Thread(target=handle, args=(c,))
    handle_Thread.start()

