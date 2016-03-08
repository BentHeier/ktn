# -*- coding: utf-8 -*-
import SocketServer
import json
import datetime
import time
import select

"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""

SERVER_NAME = "Server"
users = {}
history = []


def broadcast(message):
    for ip in users:
        if users[ip].username is not None:
            users[ip].connection.send(message)


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

        #self.connection.setblocking(0)

        users[self.client_address] = self

        print "Connection accepted:", self.client_address
        # Loop that listens for messages from the client
        try:
            while True:
                received_string = self.connection.recv(4096)
                if received_string:
                    print "Received", received_string, "from", self.client_address
                    package = json.loads(received_string)
                    request = package['request']
                    content = package['content']

                    if request == "login":
                        self.change_username(content)
                    elif request == "help":
                        help_msg = "    login <username> - log in with the given username\n    logout - log out\n" \
                                    "    msg <message> - send message\n    names - list users in chat" \
                                   "\n    help - view help text"
                        self.send_payload(SERVER_NAME, "info", help_msg)
                    elif request == "logout" and self.username:
                        del users[self.client_address]
                        self.connection.close()
                        break
                    elif (request == "msg" or not request) and self.username:
                        history.append((get_timestamp(), self.username, content))
                        self.send_payload(self.username, "message", content, True)
                    elif request == "names" and self.username:
                        user_names = ""
                        for ip in users:
                            user_names += "    " + users[ip].username + "\n"
                        self.send_payload(SERVER_NAME, "info", user_names)
                    else:
                        self.send_payload(SERVER_NAME, "error", "Bad request")
        except:
            print "Connection error with", self.username,  self.client_address
            del users[self.client_address]
            self.connection.close()

    def send_payload(self, sender, response, content, do_broadcast=False):
        message = json.dumps({'timestamp': get_timestamp(), 'sender': sender, 'response': response, 'content': content})
        print "Sending:", message, "to", self.client_address
        if do_broadcast:
            broadcast(message)
        else:
            self.connection.send(message)

    def change_username(self, username):
        print "Requested login", username, "from", self.client_address
        if username.isalnum():
            self.username = username
            self.send_payload(SERVER_NAME, "info", "Login successful")
            self.send_payload(SERVER_NAME, "history", history)
        else:
            self.send_payload(SERVER_NAME, "error", "Usernames must be letters and numbers only")


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
    HOST, PORT = '78.91.25.10', 9998
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
