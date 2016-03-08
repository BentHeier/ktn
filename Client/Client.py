# -*- coding: utf-8 -*-
import socket
from MessageReceiver import MessageReceiver
from MessageParser import MessageParser
import os
import platform
import json


class Client:
    """
    This is the chat client class
    """

    def __init__(self, host, server_port):
        """
        This method is run when creating a new Client object
        """

        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # TODO: Finish init process with necessary code
        self.host = host
        self.server_port = server_port
        self.run()

        # Start a MessageReceiver thread
        receiver = MessageReceiver(self, self.connection)
	receiver.start()
        receiver.run()

        # Create a MessageParser object for use later
        self.parser = MessageParser()


        # Loop to handle continuously reading from input
        while True:
            user_input = raw_input()
            if user_input != None:
                self.send_payload(user_input)

    def run(self):
        # Initiate the connection to the server
        self.connection.connect((self.host, self.server_port))
        
    def disconnect(self):
        # TODO: Handle disconnection
        # LOGOUT
        self.connection.close()

    def receive_message(self, message):
        # TODO: Handle incoming message
        parsedMessage = self.parser.parse(message)
        self.display_message(parsedMessage)


    def send_payload(self, data):
        # TODO: Handle sending of a payload
        input_splitted = data.split(' ', 1)
        firstWord = input_splitted[0]

        # Create json object based on the structure of the data string
        if firstWord == 'login':
            # Find username from data_string
            username = input_splitted[1]
            payload = json.dumps( { "request" : "login", "content" : "username" } )

        elif firstWord == 'logout':
            payload = json.dumps( { "request" : "logout", "content" : None } )
        elif firstWord == 'names' :
            payload = json.dumps( { "request" : "names", "content" : None } )
        elif firstWord == 'help' :
            payload = json.dumps( { "request" : "help", "content" : None } )
        else:
            # Find message from the data string
            message = input_splitted[1]
            payload = json.dumps( {"request" : "msg", "content" : message } )
        self.connection.send(payload)
        
    def display_message(self, message):
        print message

    def clear(self):
        if platform.system() == "Windows":
            _ = os.system("cls")
        else:
            _ = os.system("clear")


if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations are necessary
    """
    client = Client('localhost', 9998)
