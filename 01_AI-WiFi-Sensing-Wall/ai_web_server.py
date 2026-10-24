import socket
import threading
import json
import time
import joblib
import pandas as pd
from http.server import BaseHTTPRequestHandler, HTTPServer
from collections import Counter

try:
    print("[INIT] Loading AI Model...")
    ai_model = joblib.load('ai_model.pkl')
    print("[OK] Model loaded successfully.")
except Exception as e:
    print("[ERROR] ai_model.pkl not found.")
    exit()

ESP32_IP = "192.168.4.1"
ESP32_PING_PORT = 8081

UDP_IP = "0.0.0.0"
UDP_PORT = 8080

prediction_history = []
current_status = "Waiting for data..."

def radar_pinger():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("[STATUS] Started Radar Wave Generator...")
    while True:
        try:
            sock.sendto(b"PING", (ESP32_IP, ESP32_PING_PORT))
            time.sleep(0.02)
        except Exception:
            time.sleep(1)

def udp_listener():
    global prediction_history, current_status
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    while True:
        try:
            data, _ = sock.recvfrom(4096)
            line = data.decode('utf-8', errors='ignore').strip()
            
            if line.startswith("AMP:"):
                amp_part = line.replace("AMP:", "")
                amp_values = [float(x) for x in amp_part.split(',') if x.strip()]
                
                if len(amp_values) == 64:
                    df = pd.DataFrame([amp_values], columns=[f"sub_{i}" for i in range(64)])
                    pred = ai_model.predict(df)[0]
                    
                    prediction_history.append(pred)
                    if len(prediction_history) > 15:
                        prediction_history.pop(0)
                    
                    most_common = Counter(prediction_history).most_common(1)[0][0]
                    current_status = most_common
        except Exception:
            pass

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global current_status
        
        if self.path in ('/', '/ai_index.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            try:
                with open('ai_index.html', 'rb') as f:
                    self.wfile.write(f.read())
            except Exception:
                self.wfile.write(b"ai_index.html not found")
                
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {"status": current_status}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
            
    def log_message(self, format, *args):
        pass

def main():
    threading.Thread(target=radar_pinger, daemon=True).start()
    threading.Thread(target=udp_listener, daemon=True).start()
    
    print("="*50)
    print("Live AI Dashboard Active")
    print("="*50)
    print("Starting Web Server at http://localhost:8050")
    print("Open your browser at: http://localhost:8050")
    
    server = HTTPServer(('0.0.0.0', 8050), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")

if __name__ == "__main__":
    main()
