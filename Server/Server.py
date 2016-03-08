# -*- coding: utf-8 -*-
import SocketServer
import json
import datetime
import time

"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""

SERVER_NAME = "Server"
users = {}
history = []

"""
MESSAGE FORMAT:
{
'timestamp': <timestampt>,
 'sender': <username>,
 'response': <response>,
 'content': <content>,
 }
"""

def broadcast(message):
    for user in users:
        user.connection.send(message)

def get_timestamp():
        return datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M')

class ClientHandler(SocketServer.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """
    ip = None
    port = None
    connection = None
    username = None

    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request

        users[self.ip] = self
        # Loop that listens for messages from the client
        while True:
            received_string = self.connection.recv(4096)
            # TODO: Add handling of received payload from client
            if received_string:
                package = json.loads(received_string)
                request = package['request']
                content = package['content']

                if request == "login":
                    self.change_username(content)
                elif request == "help":
                    help = "login <username> - log in with the given username\nlogout - log out\n" \
                           "msg <message> - send message\nnames - list users in chat\nhelp - view help text\n"
                    self.send_payload(SERVER_NAME, "Info", help)
                elif request == "logout" and self.username:
                    self.connection.close()
                    del users[self.ip]
                    break
                elif request == "msg" and self.username:
                    history.append((get_timestamp(), self.username, content))
                    self.send_payload(self.username, "Message", content, True)
                elif request == "names" and self.username:
                    user_names = ""
                    for user in users:
                        user_names += user.username + "\n"
                    self.send_payload(SERVER_NAME, "Info", user_names)
                else:
                    self.send_payload(SERVER_NAME, "Error", "Bad request")

    def send_payload(self, sender, response, content, do_broadcast=False):
        message = json.dumps({get_timestamp(), sender, response, content})
        if do_broadcast:
            broadcast(message)
        else:
            self.connection.send(message)

    def change_username(self, username):
        if username.isalnum():
            self.username = username
        else:
            self.send_payload(SERVER_NAME, "Error", "Usernames must be letters and numbers only")


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations are necessary
    """
    allow_reuse_address = True

if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations are necessary
    """
    HOST, PORT = 'localhost', 9998
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
