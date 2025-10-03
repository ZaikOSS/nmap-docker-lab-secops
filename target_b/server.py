#!/usr/bin/env python3
import socket
import os

HOST = '0.0.0.0'
PORT = 10991

# Define the base directory for file access
BASE_DIR = "/app/files" 

def list_files():
    out = []
    # os.walk finds files recursively starting from the base directory
    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            path = os.path.join(root, f)
            try:
                st = os.stat(path)
                # Extract the last 9 bits for user/group/other permissions
                perm = oct(st.st_mode & 0o777) 
            except Exception:
                perm = "???"
            out.append(f"{path} | perms: {perm}")
    return "\n".join(out)

def read_file(filepath):
    # 1. Resolve absolute paths for both the base directory and the user's input.
    # This correctly handles paths like /app/files/../server.py and prevents path traversal attacks.
    resolved_base_dir = os.path.realpath(BASE_DIR)
    resolved_path = os.path.realpath(filepath)
    
    # 2. CRUCIAL FIX: Check if the resolved user path starts with the resolved base directory path.
    if not resolved_path.startswith(resolved_base_dir):
        return "ERROR: Access denied. File must be within the /app/files directory (no path traversal allowed).\n"
    
    # 3. Security: Only allow reading regular files (not directories or special files).
    if not os.path.isfile(resolved_path):
        return f"ERROR: '{filepath}' is not a regular file or does not exist.\n"

    try:
        # 4. Read the file using the secure, resolved path.
        with open(resolved_path, "r") as fh:
            data = fh.read()
        return data + "\n"
    except Exception as e:
        return f"ERROR: Could not read file: {e}\n"

def handle_client(conn, addr):
    ip = addr[0]
    print(f"Connection from {ip}")
    
    # Set a timeout for the connection
    conn.settimeout(30) 
    
    try:
        # -------------------------------------------------------------------------
        # BANNER FOR NMAP/SERVICE PROBES (Must be the first send)
        # Nmap will show this line under the "Service" column or in script output.
        conn.sendall(b"Custom File Service 1.0. Connect with 'nc' for a shell.\n")
        # -------------------------------------------------------------------------

        conn.sendall(b"Welcome to CustomService (no auth required).\n")
        conn.sendall(b"Commands: LIST, READ <filename>, EXIT\n")
        
        while True:
            # Send prompt and wait for command
            conn.sendall(b"> ")
            
            # Receive data and clean it up
            data_raw = conn.recv(1024).strip()
            if not data_raw:
                break # Client disconnected or sent empty data

            # Decode to string and split the command parts
            data = data_raw.decode()
            parts = data.upper().split(maxsplit=1)
            command = parts[0]
            
            response = ""

            if command == "LIST":
                response = "Listing files:\n" + list_files() + "\n"
            
            elif command == "READ":
                if len(parts) < 2:
                    response = "ERROR: Usage: READ <filename>\n"
                else:
                    # Get the filename exactly as typed by the user (case-sensitive path)
                    filename = data.split(maxsplit=1)[1].strip()
                    response = read_file(filename)
            
            elif command == "EXIT":
                response = "Goodbye!\n"
                conn.sendall(response.encode())
                break
            
            else:
                response = f"ERROR: Unknown command '{command}'.\n"

            conn.sendall(response.encode())

    except socket.timeout:
        print(f"Connection from {ip} timed out.")
    except Exception as e:
        print(f"Error handling {ip}: {e}")
    finally:
        try:
            conn.close()
        except:
            pass
        print(f"Connection closed from {ip}")

if __name__ == "__main__":
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR, exist_ok=True)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"Custom service listening on {PORT} (no auth).")
        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)