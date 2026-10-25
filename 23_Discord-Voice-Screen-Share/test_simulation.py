import socket
import threading
import time
import sys

def test_socket_streaming():
    server_host = '127.0.0.1'
    port_screen = 59123
    port_voice = 59124

    screen_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    screen_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    screen_server.bind((server_host, port_screen))
    screen_server.listen(1)

    voice_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    voice_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    voice_server.bind((server_host, port_voice))
    voice_server.listen(1)

    received_screen = []
    received_voice = []

    def run_screen():
        conn, _ = screen_server.accept()
        length_bytes = conn.recv(4)
        length = int.from_bytes(length_bytes, 'big')
        data = conn.recv(length)
        received_screen.append(data)
        conn.close()

    def run_voice():
        conn, _ = voice_server.accept()
        data = conn.recv(4096)
        received_voice.append(data)
        conn.close()

    t1 = threading.Thread(target=run_screen, daemon=True)
    t2 = threading.Thread(target=run_voice, daemon=True)
    t1.start()
    t2.start()

    time.sleep(0.1)

    dummy_screen = b"JPEG_SIMULATED_SCREEN_FRAME_BYTES"
    client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_s.connect((server_host, port_screen))
    client_s.sendall(len(dummy_screen).to_bytes(4, 'big') + dummy_screen)
    client_s.close()

    dummy_voice = b"PCM_AUDIO_DATA_SIMULATION"
    client_v = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_v.connect((server_host, port_voice))
    client_v.sendall(dummy_voice)
    client_v.close()

    t1.join(timeout=2)
    t2.join(timeout=2)

    screen_server.close()
    voice_server.close()

    assert len(received_screen) == 1 and received_screen[0] == dummy_screen, "Screen frame transmission failed"
    assert len(received_voice) == 1 and received_voice[0] == dummy_voice, "Voice packet transmission failed"

    print("Project 23 Discord Voice Screen Share socket tests passed")

if __name__ == "__main__":
    test_socket_streaming()
