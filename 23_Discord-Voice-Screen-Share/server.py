import socket
import threading

HOST = '0.0.0.0'
PORT_SCREEN = 65432
PORT_VOICE = 65433

clients_screen = []
clients_voice = []

def handle_screen(conn, addr):
    clients_screen.append(conn)
    try:
        while True:
            length_bytes = conn.recv(4)
            if not length_bytes:
                break
            length = int.from_bytes(length_bytes, 'big')
            data = b''
            while len(data) < length:
                packet = conn.recv(length - len(data))
                if not packet:
                    break
                data += packet
            if not data:
                break
            for client in clients_screen:
                if client != conn:
                    try:
                        client.sendall(length_bytes + data)
                    except:
                        if client in clients_screen:
                            clients_screen.remove(client)
    finally:
        if conn in clients_screen:
            clients_screen.remove(conn)
        conn.close()

def handle_voice(conn, addr):
    clients_voice.append(conn)
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            for client in clients_voice:
                if client != conn:
                    try:
                        client.sendall(data)
                    except:
                        if client in clients_voice:
                            clients_voice.remove(client)
    finally:
        if conn in clients_voice:
            clients_voice.remove(conn)
        conn.close()

def start_server():
    screen_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    screen_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    screen_server.bind((HOST, PORT_SCREEN))
    screen_server.listen(5)

    voice_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    voice_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    voice_server.bind((HOST, PORT_VOICE))
    voice_server.listen(5)

    threading.Thread(target=accept_connections, args=(screen_server, handle_screen), daemon=True).start()
    threading.Thread(target=accept_connections, args=(voice_server, handle_voice), daemon=True).start()

def accept_connections(server_socket, handler):
    while True:
        try:
            conn, addr = server_socket.accept()
            threading.Thread(target=handler, args=(conn, addr), daemon=True).start()
        except:
            break

if __name__ == '__main__':
    start_server()
