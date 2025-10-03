#!/usr/bin/env python3
import socket
import time
from collections import defaultdict

HOST = '0.0.0.0'
PORT = 22222

VALID_USER = "secops"
VALID_PASS = "zaikos123"
FLAG = "SECOPS3{ssh-credentials-found}"

MAX_ATTEMPTS = 3
BLOCK_SECONDS = 300
BACKOFF_BASE = 1.0

fails = defaultdict(lambda: {"count": 0, "last": 0.0, "blocked_until": 0.0})

def is_blocked(ip):
    return time.time() < fails[ip]["blocked_until"]

def register_failure(ip):
    now = time.time()
    entry = fails[ip]
    entry["count"] += 1
    entry["last"] = now
    if entry["count"] > MAX_ATTEMPTS:
        entry["blocked_until"] = now + BLOCK_SECONDS
        print(f"[{time.ctime()}] {ip} blocked until {time.ctime(entry['blocked_until'])}")

def reset_failures(ip):
    if ip in fails:
        fails[ip] = {"count": 0, "last": 0.0, "blocked_until": 0.0}

def handle_client(conn, addr):
    ip = addr[0]
    print(f"[{time.ctime()}] SSH-like connection from {ip}")

    if is_blocked(ip):
        conn.sendall(b"Too many attempts. Try later.\n")
        conn.close()
        return

    try:
        # send fake SSH banner first (so initial connection looks normal)
        conn.sendall(b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3\n")
        session_attempts = 0
        while True:
            if is_blocked(ip):
                conn.sendall(b"Too many attempts. Try later.\n")
                break

            conn.sendall(b"login: ")
            user = conn.recv(1024)
            if not user:
                break
            user = user.decode(errors="ignore").strip()

            conn.sendall(b"password: ")
            password = conn.recv(1024)
            if not password:
                break
            password = password.decode(errors="ignore").strip()

            session_attempts += 1
            print(f"[{time.ctime()}] Auth attempt from {ip}: user='{user}' attempt {session_attempts}")

            if user == VALID_USER and password == VALID_PASS:
                conn.sendall(b"Access granted.\n")
                conn.sendall(f"Flag: {FLAG}\n".encode())
                reset_failures(ip)
                break
            else:
                register_failure(ip)
                conn.sendall(b"Authentication failed.\n")
                backoff = BACKOFF_BASE * session_attempts
                conn.sendall(f"Backoff: {backoff:.1f}s\n".encode())
                if is_blocked(ip):
                    conn.sendall(b"You are blocked due to multiple failed attempts.\n")
                    break
                time.sleep(backoff)

            if session_attempts >= MAX_ATTEMPTS:
                conn.sendall(b"Session attempt limit reached. Bye.\n")
                break

    except Exception as e:
        print(f"[{time.ctime()}] Error {ip}: {e}")
    finally:
        try:
            conn.close()
        except:
            pass
        print(f"[{time.ctime()}] Connection closed from {ip}")

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"SSH-like auth listening on {PORT}")
        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)
