import sys
import tkinter.simpledialog
from tkinter import *
from api_server import Server
from api_client import Storage
import utils
from security import WrongPassword
import threading
import os

def create_server():
    if not os.path.exists(utils.database_path):
        #initial start
        name = tkinter.simpledialog.askstring("Welcome to the Ark!", "Welcome to The Ark!\nEnter your username that other people will see.")
        if name is None:
            sys.exit()
        password = tkinter.simpledialog.askstring("Welcome to the Ark!", "Now create a new password.\nIt will be used to encrypt your data, so if you lose it, there will be no way to recover it!")
        if password is None:
            sys.exit()
        server.key = password
        server.start(name=name)
    else:
        password = ""
        prompt_text = "Enter your password"
        while password == "":
            password = tkinter.simpledialog.askstring("Welcome to the Ark!", prompt_text)
            if password is not None:
                try:
                    server.key = password
                    testing_storage = Storage(utils.database_path, password)
                    testing_storage.read()
                except WrongPassword:
                    password = ""
                    prompt_text = "Wrong password, please try again."
        if password is None:
            sys.exit()
        threading.Thread(target=server.start).start()
      
#GuiCode set in its own class
class ArkGUI:
    def __init__(self):
        self.server = Server()

        self.window = Tk()
        self.window.title("The Ark")
        self.window.geometry("600x400")
        self.window.resizable(width=False, height=False)

        self.chat_frame = Frame(self.window, height=400, width=400, bg="#E0E1DD", borderwidth=1, relief=RIDGE)
        self.contacts_frame = Frame(self.window, height=400, width=200, bg="#778DA9", borderwidth=1, relief=RIDGE)
        self.contacts_frame.pack(side=LEFT)
        self.chat_frame.pack(side=RIGHT)

        create_server()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    ark_gui = ArkGUI()
    ark_gui.run()
