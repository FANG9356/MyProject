import socket
import csv
import threading
import sys
import time

ESP32_IP = "192.168.4.1" 
ESP32_PING_PORT = 8081

UDP_IP = "0.0.0.0"
UDP_PORT = 8080

recording = False
current_label = ""
dataset = []

def radar_pinger():
    """
    หัวใจสำคัญของ Standalone Mode:
    Mac ต้องส่งข้อความ (Ping) ไปกวนบอร์ด ESP32 รัวๆ (50 ครั้งต่อวินาที)
    เพื่อให้เกิดคลื่นวิทยุเด้งไปมาในห้อง ถ้าไม่มี Ping นี้ จะไม่มีคลื่นให้วัด
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(" Started Radar Wave Generator (Pinging ESP32)...")
    while True:
        try:
            sock.sendto(b"PING", (ESP32_IP, ESP32_PING_PORT))
            time.sleep(0.02)
        except Exception:
            time.sleep(1)

def udp_listener():
    global recording, dataset
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    while True:
        try:
            data, _ = sock.recvfrom(4096)
            line = data.decode('utf-8', errors='ignore').strip()
            
            if line.startswith("AMP:"):
                amp_part = line.replace("AMP:", "")
                amp_values = [float(x) for x in amp_part.split(',') if x.strip()]
                
                if len(amp_values) == 64 and recording:
                    row = amp_values + [current_label]
                    dataset.append(row)
        except Exception:
            pass

def main():
    global recording, current_label, dataset
    
    threading.Thread(target=radar_pinger, daemon=True).start()
    threading.Thread(target=udp_listener, daemon=True).start()
    
    print("="*50)
    print(" Phase 1: AI Data Collection (Standalone AP)")
    print("="*50)
    print(f"กำลังเชื่อมต่อกับเสา Wi-Fi 'AI_Radar_Scanner'...")
    time.sleep(2) 
    print("พร้อมแล้ว! กดปุ่มตัวเลขเพื่อเริ่มบันทึกท่าทางต่างๆ:")
    print(" [1] บันทึกตอน 'ห้องว่าง (Empty)'")
    print(" [2] บันทึกตอน 'คนกำลังเดิน (Walking)'")
    print(" [3] บันทึกตอน 'คนล้ม (Falling)'")
    print(" [q] ออกจากโปรแกรม")
    print("="*50)

    while True:
        choice = input("\n กดเลือกคำสั่ง (1, 2, 3 หรือ q): ").strip().lower()
        
        if choice == 'q':
            print("ปิดโปรแกรมครับ")
            sys.exit(0)
            
        if choice not in ['1', '2', '3']:
            print(" กดผิดครับ กรุณากด 1, 2 หรือ 3")
            continue
            
        labels = {'1': 'Empty', '2': 'Walking', '3': 'Falling'}
        current_label = labels[choice]
        
        print(f"\n กำลังบันทึกข้อมูลท่าทาง: [{current_label}]")
        print("กรุณาทำท่าทางไปเรื่อยๆ (ระบบจะบันทึกเป็นเวลา 15 วินาที)...")
        
        dataset = []
        recording = True
        
        for i in range(15, 0, -1):
            sys.stdout.write(f"\rเหลือเวลาอีก {i} วินาที... (เก็บได้ {len(dataset)} ตัวอย่าง)")
            sys.stdout.flush()
            time.sleep(1)
            
        recording = False
        print(f"\n บันทึกเสร็จสิ้น! ได้ข้อมูลมาทั้งหมด {len(dataset)} ชุด")
        
        filename = f"dataset_{current_label.lower()}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            header = [f"sub_{i}" for i in range(64)] + ["Label"]
            writer.writerow(header)
            writer.writerows(dataset)
            
        print(f" เซฟข้อมูลลงไฟล์ '{filename}' เรียบร้อยแล้ว!\n")

if __name__ == "__main__":
    main()
