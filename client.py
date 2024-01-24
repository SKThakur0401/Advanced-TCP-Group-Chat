# Code for Client side of Advanced TCP group chat

from ast import Delete
import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import BOTTOM, simpledialog

from time import sleep

HOST= '127.0.0.1'
PORT = 9999

class Client:

    def __init__(self, host, port):

        self.sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        # Now, when we start our program, we want a dialog box to appear which will ask for user's name, this can be done by importing "simpledialog" library and using its "askstring function"
        msg= tkinter.Tk()
        msg.withdraw()
        self.nickname= simpledialog.askstring("Nickname", "Please choose a nickname", parent= msg)

        #So, now user's nickname is stored in "self.nickname"

        self.gui_done= False    # We will make it true when our GUI will be made, ie. our interface 
                                #will be read for the user to use or to see
        self.running= True      # We keep it "True" to determine that our code is still running, we 
                                #will make it "False" when the someone closes the window, using "stop" function

        #Now we will call the "gui_loop" function which is responsible for creating the user interface, we could've CALLED "gui_loop" as well as "receive" function here only,,, BUT!! THAT DOES NOT WORK ON A "MAC!" BECAUSE "UI FRAMEWORKS" SHOULD BE ON THE "MAIN THREAD" ONLY!

        #So, here, we r only calling "gui_loop" fn on the main thread, later we'll create a child thread to execute "receive" fn code..
        self.gui_loop()


    def gui_loop(self):

        self.win= tkinter.Tk()
        self.win.configure(bg= "lightgray")     # Will make the entire interface "lightgray"

        self.win.title(self.nickname)       # Now the title of interface would be user's name


        # A simple "label" stating "Chat as your_Name"
        self.chat_label= tkinter.Label(self.win, text= f"Chat as {self.nickname}", bg="lightgray")
        self.chat_label.config(font= ("Arial", 15))
        self.chat_label.pack(padx=20, pady=5)


        # Now we'll create "text_area" where all the entered text will be printed and stored, this is where you will read text sent by others also...
        self.text_area= tkinter.scrolledtext.ScrolledText(self.win, width=88)
        self.text_area.pack(padx=10, pady=5)
        self.text_area.config(state= 'disabled')        # So that no one can enter data in text_area


        # A simple "label" stating "Message"
        self.msg_label= tkinter.Label(self.win, text= "Message:", bg="lightgray")
        self.msg_label.config(font= ("Arial", 15))
        self.msg_label.pack(padx=20, pady=5)

        # Now we will make the input area, where the user will type his text, we can initialise it with height and width acc to our will but we'll simply use "pack" and height=3 (or whatever u like) to keep things aligned well
        self.input_area = tkinter.Text(self.win, height=3, width=88)
        self.input_area.pack(padx=20, pady=5)


        # Now we will create the "Send" button, when we press this button, the text will be sent to the "text_area" of all the group-chat-members, and this text will be deleted from "input_area", just like it happens in whatsapp or other chat apps!!!
        self.send_button = tkinter.Button(self.win, text= "Send", command= self.write)
        self.send_button.config(font=("Arial", 15))
        self.send_button.pack(padx=20, pady=5)
        self.gui_done= True

        self.showCmdsPressCount=0
        self.showCmdsButton = tkinter.Button(self.win, text= "Show Commands", command= self.toggleCmdPalette)
        self.showCmdsButton.config(font=("Arial", 15))
        self.showCmdsButton.pack(padx=20, pady=5)
        self.gui_done= True

        # Now we will create a child "thread" on which our "receive" function will run in a while True format and that thread will be responsible for receiving all the information
        receive_thread= threading.Thread(target=self.receive)
        receive_thread.start()

        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def destroyInSeconds(self, X, time):      # This fn is used to destroy labels and buttons
        sleep(time)                           # after doing so it will "show" the command palette
        X.destroy()
        if(self.showCmdsPressCount%2 == 0):
            self.toggleCmdPalette()

    def directMsg(self, name):          # When user presses the button with name, this fn is called
        recieverName= f'/dm {name} '

        self.send_button.config(text= f"Send this Msg to: {name}", command= lambda:self.dmWrite(recieverName))

    def dmWrite(self, recieverName):
        msg= self.input_area.get('1.0', 'end')

        self.text_area.config(state= "normal")
        self.text_area.insert(tkinter.END, f"(ONLY YOU AND RECEIVER CAN SEE THIS MSG) {msg}")
        self.text_area.config(state= "disabled")
        msg= recieverName+msg

        self.input_area.delete('1.0', 'end')        # After send button is pressed, text should be 
                                                    # deleted from input_area
        self.sock.send(bytes(msg, 'utf-8'))
        self.send_button.config(text= "Send", command=self.write)

        # After the DM has been sent, we need to rearrange the command palette into it's original form and delete these new unnecessary buttons...
        self.DMtextLabel.destroy()
        for button in self.buttonList:
            dt= threading.Thread(target= self.destroyInSeconds, args=(button,0))
            dt.start()

        self.toggleCmdPalette()     # To get back the command palette

    def kickFunction(self, name):
        msg= f"/kick {name} "
        self.write(msg)
        self.lblKick.destroy()
        for button in self.buttonList:
            button.destroy()

        self.toggleCmdPalette()


    # Now we will create the write function, here, this "write" function can also take a 2nd argument which is only given to it in case of a command! that 2nd argument would be the command executed in back-end like "/headCount", "/displayNames" etc... In all other cases the 2nd argument would be "None" and it will work like normal write function
    def write(self, msg=None):        # This function executes when we press the "Send" button
                                # Note, we have given it a second parameter "msg" which will only be
        if(msg== None):
            msg= self.input_area.get('1.0', 'end')

            if(msg[0] != '/'):         # if msg doesn't start with '/', it means its normal msg
                msg= f"{self.nickname}: {msg}"

            self.sock.send(bytes(msg, 'utf-8'))
            self.input_area.delete('1.0', 'end')


        else:

            if(msg == "/headCount"):    # Incase the user is asking for headCount, we want to show
                
                self.sock.send(bytes(msg, 'utf-8'))     # it below the cmd palette
                reply= self.sock.recv(1024).decode()    # This is reply we get from backend
                self.toggleCmdPalette()           # This will "Unshow Cmd Palette"
                self.lhc= tkinter.Label(self.win, text= reply, font=("Arial", 12), bg= "lightgray")
                self.lhc.pack()
                #Now, we don't want this label forever right? , we want to erase this after the user is done reading it, so we'll destroy it in 3 secs, which is enough time for reading, but we don't want to engage main-thread for such a task like waiting for 3 seconds... so we'll create a separate thread for deletion, it will wait for 3 secs and then destroy we call it "destroyInSeconds"
                dt= threading.Thread(target= self.destroyInSeconds, args=(self.lhc, 3))
                dt.start()

            elif(msg== "/displayNames"):

                self.sock.send(bytes(msg, 'utf-8'))         # "/displayNames" is sent to back-end
                reply= (self.sock.recv(1024).decode())      # It will return a "str" with all names

                nameList= reply.split("\n")             # This will convert str to "list-of names"
                nameList.remove("002 displayNames")     # This will remove the first member of list,
                                                        # the only member of list which is not name of an user
                self.toggleCmdPalette()

                self.lbdd= tkinter.Label(self.win, text= "Names of group Members :", bg="lightgray")
                self.lbdd.pack(side= tkinter.LEFT)

                buttonList=[]               # We could have used label, but using non-functional
                                            # buttons anyways
                for name in nameList:
                    self.bx= tkinter.Button(self.win, text=name, bg="lightgray")
                    self.bx.pack(side= tkinter.LEFT)
                    buttonList.append(self.bx)

                for button in buttonList:
                    dt= threading.Thread(target= self.destroyInSeconds, args=(button,3))
                    dt.start()
                dt= threading.Thread(target= self.destroyInSeconds, args=(self.lbdd,3))
                dt.start()


            elif(msg== "/dm"):
                self.sock.send(bytes("/displayNames", 'utf-8'))
                reply= (self.sock.recv(1024).decode())

                nameList= reply.split("\n")
                nameList.remove("002 displayNames")
                self.toggleCmdPalette()
                self.lbl= tkinter.Label(self.win, text= "Who do you want to DM")
                self.buttonList=[]

                self.DMtextLabel= tkinter.Label(self.win, text="Who do you want to DM: ", bg= "lightgray")
                self.DMtextLabel.pack(side= tkinter.LEFT)

                for name in nameList:
                    bx= tkinter.Button(self.win, text=name, command=lambda n=name:self.directMsg(n))
                    bx.pack(side= tkinter.LEFT)
                    self.buttonList.append(bx)
            
            elif(msg== "/kick"):
                self.sock.send(bytes("/displayNames", 'utf-8'))
                reply= (self.sock.recv(1024).decode())

                nameList= reply.split("\n")
                nameList.remove("002 displayNames")
                self.toggleCmdPalette()
                self.lblKick= tkinter.Label(self.win, text= "Who do you want to kick")
                self.lblKick.pack(side= tkinter.LEFT)
                self.buttonList=[]
                

                for name in nameList:
                    bx= tkinter.Button(self.win, text=name, command=lambda n=name: self.kickFunction(n))
                    bx.pack(side=tkinter.LEFT)
                    self.buttonList.append(bx)
                
            else:
                self.sock.send(bytes(msg, 'utf-8'))
                self.input_area.delete('1.0', 'end')


    def stop(self):
        self.running= False
        self.win.destroy()
        self.sock.close()
        exit(0)



    def toggleCmdPalette(self):     # This function when called, will show the "button-palette"
                                    # Having various buttons like "Tell headcount", "display names", "load previous chat" etc.., OR!!, if button palette is already visible, when this function is called, it will make it disappear!!!! And the button corresponding to this function will have written on it "show commands"
        self.showCmdsPressCount+=1
        if(self.showCmdsPressCount%2):
            self.showCmdsButton.config(text= "Unshow Commands", font= ("Arial",15),fg= "blue")

            self.headCount= tkinter.Button(self.win, text= "Head count", command= lambda: self.write("/headCount"))
            self.headCount.config(font=("Arial", 12))
            self.headCount.pack(side= tkinter.LEFT)


            self.displayNames= tkinter.Button(self.win, text= "Show Names", command= lambda: self.write("/displayNames"))
            self.displayNames.config(font= ("Arial", 12))
            self.displayNames.pack(side= tkinter.LEFT)


            self.voting= tkinter.Button(self.win, text= "Voting", command= lambda:self.write("/voting"))
            self.voting.config(font= ("Arial", 12))
            self.voting.pack(side= tkinter.LEFT)


            self.loadChat= tkinter.Button(self.win, text= "Show Previous Chat", command= lambda:self.write("/loadChat"))
            self.loadChat.config(font= ("Arial", 12))
            self.loadChat.pack(side= tkinter.LEFT)


            self.delChat= tkinter.Button(self.win, text= "Del Chat", command=self.deleteChat)
            self.delChat.config(font= ("Arial", 12))
            self.delChat.pack(side= tkinter.LEFT)

            self.dm= tkinter.Button(self.win, text= "Direct Msg", command= lambda:self.write("/dm"))
            self.dm.config(font= ("Arial", 12))
            self.dm.pack(side= tkinter.LEFT)

            self.kick= tkinter.Button(self.win, text= "Kick", command= lambda:self.write("/kick"))
            self.kick.config(font=("Arial",12))
            self.kick.pack(side= tkinter.LEFT)


        else:       # In case the command-palette is already visible, it will make it disappear
            self.showCmdsButton.config(text= "Show Commands", font= ("Arial", 15), fg= "black")
            self.headCount.destroy()
            self.displayNames.destroy()
            self.loadChat.destroy()
            self.voting.destroy()
            self.dm.destroy()
            self.delChat.destroy()
            self.kick.destroy()


    def deleteChat(self):           # Used to delete all the chat/text from text_area
        self.text_area.config(state= 'normal')
        self.text_area.delete('1.0', tkinter.END)
        self.text_area.config(state='disabled')



    def receive(self):
        while self.running:
            try:
                msg= str(self.sock.recv(1024).decode())

                if msg == "NICK":
                    self.sock.send(self.nickname.encode('utf-8'))

                elif "Number of people in this group : " in msg:    # This kind of would be delivered from back-end if we call "headCount" function, we don't want this text to be printed here bcoz we have r printing headCount anyways using "Label" in a more attractive way, so we don't want to do it here again, therefore just continue
                    continue

                elif "002 displayNames" in msg:         # Same reason as the msg above
                    continue

                elif("CODE-112 DELETE CHAT" in msg):    # If this text is sent from server, we'll
                                                        # delete text from text_area, (ITS A PART OF "deleteChat" function)
                    self.text_area.config(state= 'normal')
                    self.text_area.delete('1.0', tkinter.END)
                    self.text_area.config(state= 'disabled')

                elif("CODE-006You have been kicked out" in msg):
                    self.text_area.config(state= 'normal')
                    self.text_area.insert('end', msg[8:])
                    self.text_area.insert('end', "\nThis Window will close in 3 Seconds")
                    self.text_area.yview('end')
                    self.text_area.config(state= 'disabled')
                    sleep(3)
                    self.stop()

                else:
                    if self.gui_done:
                        self.text_area.config(state= 'normal')
                        self.text_area.insert('end', msg)
                        self.text_area.yview('end')
                        self.text_area.config(state= 'disabled')

            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break


x=Client(HOST, PORT)

