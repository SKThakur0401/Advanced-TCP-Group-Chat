# Code for Client side of Advanced TCP group chat

import socket
import threading

c= socket.socket()
c.connect(('localhost', 9999))

nickname= str(input("Enter your nickname: "))

def recieve():
    while True:
        msg = c.recv(1024).decode()
    
        if(msg == "FK"):
            c.send(nickname.encode('utf-8'))
        else:
            print(msg)

def write():
    while True:
        msg= str(input(""))
        msg= nickname+ ": " + msg
        c.send(msg.encode('utf-8'))

recieveThread= threading.Thread(target=recieve)
writeThread= threading.Thread(target=write)

recieveThread.start()
writeThread.start()

