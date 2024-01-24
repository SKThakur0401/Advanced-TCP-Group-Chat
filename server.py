# CODE FOR CREATING A TCP-Chat Server

import socket
import threading
from time import sleep

s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 9999))
s.listen()

history=[]              # for loadChat function, all the msgs (in form of list of string) is stored 
                        # here, when we use loadChat function, it will print all chat in history
cl = dict()



# These 3 global variables are for "voting function"
votingOn= False
hasAnyoneCalledVotingFunction= False        # To prevent someone else from calling the "voting 
                                            #function", if someone is already using it
voteBank=[]                         #To store count of votes corresponding to each option,



print("Server setup done!")



def broadcast(msg, sender= None):        # To broadcast same msg to all clients (imp function)
    for c in cl.values():                  # Will iterate on values of dictionary, i.e. the socket
        if(c != sender):                   # object :)
            c.send(msg.encode('utf-8'))


def isAdmin(c):                 # To check if the person knows password, returns true if he knows
    
    c.send(bytes("This command is an admin privilege, please enter passCode for verification: \n", 'utf-8'))
    passCode = str(c.recv(1024).decode())

    if(passCode != "/admin123\n"):
        c.send(bytes("Access denied!\n", 'utf-8'))
        return False
    return True



def kick(c, msg, idx):                  # Code for kick command, to remove a client, after this
                                        # that person will not be able to send/recieve any msg
    name= msg[idx+1: len(msg)-1]        # Bcoz in case of tkinter, there would be a "\n" after name
    if(name not in cl):
        c.send(bytes(f"Entered username '{name}' is not valid", 'utf-8'))
        return
    
    if(not isAdmin(c)):                 # For verification, calling the isAdmin() function
        return

    kickerIdx= list(cl.values()).index(c)       # To get the index of person who wants to kick
    kickerName= list(cl.keys())[kickerIdx]      # To get the name of person who wants to kick

    cl[name].send(bytes(f"CODE-006You have been kicked out by {kickerName}", 'utf-8'))
    cl[name].close()
    cl.pop(name)

    msg2= f'{name} has been kicked out by {kickerName}'
    broadcast(msg2)
    history.append(msg2)


def displayNames(c):            # To display names of all group-chat members

    text= "002 displayNames"

    for clientName in cl:
        text+= "\n" + clientName
    c.send(bytes(text, 'utf-8'))


def loadChat(c):            # All the previous chat will be loaded on the screen :)

    c.send(bytes("CODE-112 DELETE CHAT", 'utf-8'))
    global history
    chat= ""
    for text in history:
        chat= chat + text
    c.send(chat.encode('utf-8'))


def dm(c, msg, idx):

    i=0
    for i in range(idx+1, len(msg)):
        if(msg[i] == ' '):
            break

    name= msg[idx+1:i]

    if(name not in cl):
        print(f"GDB The msg recieved is : {msg}")
        c.send(bytes(f"{name} is not a valid name", 'utf-8'))
        return
    
    text= msg[i+1:]

    senderIdx= list(cl.values()).index(c)
    senderName= list(cl.keys())[senderIdx]

    cl[name].send(bytes(f"(ONLY SENDER & RECEIVER CAN SEE THIS MSG) {senderName}: {text}", 'utf-8'))
    return


def voting(c):

    idxVotingInitialiser = list(cl.values()).index(c)
    nameVotingInitialiser = list(cl.keys())[idxVotingInitialiser]

    c.send(bytes("Enter the topic for voting\n", 'utf-8'))

    statement= c.recv(1024).decode()
    statement= statement[len(nameVotingInitialiser)+2:]  # To remove the name part and ": "from str,

    c.send(bytes("Enter number of options to vote from :\n", 'utf-8'))

    nn= str(c.recv(1024).decode())

    num= "0123456789"
    i= len(nn)-2               # To get the last index of last character here,
    val=""
    while(i):
        if(nn[i] in num):
            val= nn[i]+val
            i-=1
        else:
            break

    if(len(val) == 0):
        c.send(bytes("Invalid data-type entered, process terminated\n", 'utf-8'))
        return
    n= int(val)

    global voteBank
    voteBank= [0]*n
    options= []
    for i in range (n):
        c.send(bytes(f"Enter option-{i+1}:\n", 'utf-8'))
        option = str(c.recv(1024).decode())
        option = option[len(nameVotingInitialiser)+2:]   # To remove the name part and ": "from str,
        options.append(option)

    broadcast("-|-Attention All members-|-")
    broadcast("\n")
    sleep(0.3)
    broadcast(f"    ---{nameVotingInitialiser} has started a poll---")

    sleep(0.2)
    broadcast("        Topic :\n")
    sleep(0.3)
    broadcast(f'        {statement}')
    for i in range(n):
        broadcast(f"            Option-{i+1}: {options[i]}")
        sleep(1)


    global votingOn
    votingOn= True          # Now all the msgs sent will be detected for voting for the next 15 sec
    
    broadcast("All group members please enter your vote by typing the option number: ")
    broadcast("Voting ends in 15 seconds...\n \n")

    sleep(15)

    broadcast("------------------------ENDED-------------------------\n")
    votingOn= False


    mostChoosenOption= ""
    maxChoosen=0
    for i in range (n):
        if(voteBank[i] > maxChoosen):
            maxChoosen= voteBank[i]
            mostChoosenOption= options[i]
    
    voteBank.clear()
    broadcast(f"The most choosen option is : {mostChoosenOption}")
    broadcast("\n")
    sleep(0.3)
    broadcast(f"It was choosen by {maxChoosen} people!")
    return



def handleCommands(c, msg):
    idx=-1
    for i in range(len(msg)):
        if(msg[i] == ' '):
            idx=i
            break

    if(idx== -1):
        idx= len(msg)

    cmd= msg[1: idx]

    if(cmd == "headCount"):
        ans= f'Number of people in this group : {len(cl)}\n'
        c.send(ans.encode('utf-8'))

    elif(cmd == "displayNames"):
        displayNames(c)

    elif(cmd == "loadChat"):
        loadChat(c)

    elif(cmd == "kick"):
        kick(c, msg, idx)

    elif(cmd == "dm"):
        dm(c, msg, idx)

    elif(cmd == "voting"):
        
        global hasAnyoneCalledVotingFunction        # To explicitly tell that we r calling this
                                                    # global var

        if(hasAnyoneCalledVotingFunction):
            c.send(bytes("Someone else is using this feature right now...", 'utf-8'))
        else:
            hasAnyoneCalledVotingFunction=True
            voting(c)
            hasAnyoneCalledVotingFunction=False
    else:
        print(f"'{cmd}' is not a valid command!")

def handle(c):
    while True:

        msg = c.recv(1024).decode()

        if(len(msg) == 0):
            continue

        elif(c not in cl.values()):
            break
        
        elif(votingOn):

            num = "0123456789"
            op=""
            i=1
            while(len(msg) > i and msg[len(msg)-i] not in num):
                i+=1
            while(len(msg) > i and msg[len(msg)-i] in num):
                op= msg[len(msg)-i] + op
                i+=1

            if(len(op) == 0):       #To handle the case where voting is on and user enters some
                continue            # non-integral string

            val= int(op)
            voteBank[val-1]+=1
            c.send(bytes("Your vote has been taken into account, Thanks :)", 'utf-8'))

        elif(msg[0] != '/'):
            history.append(msg)
            broadcast(msg)

        else:
            handleCommands(c, msg)


while True:
    c, adr = s.accept()

    c.send(bytes("NICK", 'utf-8'))
    nickname= str(c.recv(1024).decode())

    cl[nickname]= c

    msg= f'{nickname} has joined the chat!!!' + '\n'
    print(msg)
    broadcast(msg)
    history.append(msg)

    c_thread= threading.Thread(target= handle, args= (c,))
    c_thread.start()


