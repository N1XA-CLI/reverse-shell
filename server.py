import socket
import threading
import json
import time

class Server():

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.t = threading.Thread()

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
        while True:
            conn, addr = self.sock.accept()
            print(f"Got connection from {addr}")

            self._handle_client(conn)

    def _handle_client(self, conn:socket.socket):
        while conn:
    
            data = input("--> ")

            self._send(conn, data)
    
            if data == "exit":
                time.sleep(5)
                conn.close()
    
            receive_data = self._receive(conn)
    
            if not receive_data:
                continue
            else:
                print(receive_data)

    def start_server(self, ip, port):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(0)
        print(f"Server listening on {ip}:{port}")
        self._accept_connection()

if __name__ == "__main__":
    server = Server()
    server.start_server("127.0.0.1", 4444)