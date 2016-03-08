import json
import os
import platform

def clear():
        if platform.system() == "Windows":
            _ = os.system("cls")
        else:
            _ = os.system("clear")

class MessageParser:
    def __init__(self):

        self.possible_responses = {
            'error': self.parse_error,
            'info': self.parse_info,
            'message': self.parse_message,
            'history': self.parse_history
        }

    def parse(self, payload):
        # Load json
        payload = json.loads(payload)

        if payload['response'] in self.possible_responses:
            return self.possible_responses[payload['response']](payload)
        else:
            # Response not valid
            pass

    def parse_error(self, payload):
        message = "Error: " + payload['content']
        return message

    def parse_info(self, payload):
        #message = payload['timestamp'] + "Info: " + payload['content']
        message = payload['content']
        return message

    def parse_message(self, payload):
        message = payload['timestamp'] + " " + payload['sender'] + ": " + payload['content']
        return message

    def parse_history(self, payload):
        clear()
        li = payload['content']
        retr = ""
        for i in li:
            time, user, msg = i
            retr += time + " " + user + ": " + msg + "\n"
        return retr[:-1]

    # Include more methods for handling the different responses...
