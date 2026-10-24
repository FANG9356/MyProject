import cv2
from ultralytics import YOLO
import sys
import json
import os
from datetime import datetime
import numpy as np

# =================================================================
# การตั้งค่า (Settings)
# =================================================================
CAMERA_SOURCES = [0] 
LOG_FILE = "detection_log.json"
SNAPSHOT_DIR = "snapshots"

if not os.path.exists(SNAPSHOT_DIR):
    os.makedirs(SNAPSHOT_DIR)

# =================================================================
# ตัวแปรสำหรับระบบเมาส์ (Globals)
# =================================================================
# สำหรับวาดห้องใหม่
drawing = False
current_cam_drawing = None
temp_rect = None 

# สำหรับย้ายห้องเดิม
moving_zone = None
drag_offset_x = 0
drag_offset_y = 0

zones = {} # { '0': { 'Room_1': (x1,y1,x2,y2), ... } }

def mouse_callback(event, x, y, flags, param):
    global drawing, temp_rect, current_cam_drawing, zones
    global moving_zone, drag_offset_x, drag_offset_y
    
    cam_name = param['cam_name']
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # 1. เช็คก่อนว่าคลิก "โดน" ห้องไหนที่วาดไว้แล้วหรือเปล่า
        clicked_zone = None
        for z_name, (zx1, zy1, zx2, zy2) in zones.get(cam_name, {}).items():
            if zx1 <= x <= zx2 and zy1 <= y <= zy2:
                clicked_zone = z_name
                break
                
        if clicked_zone:
            # 1.1 ถ้าคลิกโดนห้องเก่า -> เริ่มเข้าโหมด "ย้ายห้อง"
            moving_zone = clicked_zone
            current_cam_drawing = cam_name
            zx1, zy1, zx2, zy2 = zones[cam_name][clicked_zone]
            # จดจำระยะห่างระหว่างจุดที่คลิก กับ มุมซ้ายบนของกล่อง
            drag_offset_x = x - zx1
            drag_offset_y = y - zy1
        else:
            # 1.2 ถ้าคลิกพื้นที่ว่าง -> เริ่มเข้าโหมด "วาดห้องใหม่"
            drawing = True
            temp_rect = [x, y, x, y]
            current_cam_drawing = cam_name
            
    elif event == cv2.EVENT_MOUSEMOVE:
        if moving_zone and current_cam_drawing == cam_name:
            # อัปเดตพิกัดห้องให้วิ่งตามเมาส์
            zx1, zy1, zx2, zy2 = zones[cam_name][moving_zone]
            w = zx2 - zx1
            h = zy2 - zy1
            
            new_x1 = x - drag_offset_x
            new_y1 = y - drag_offset_y
            zones[cam_name][moving_zone] = (new_x1, new_y1, new_x1 + w, new_y1 + h)
            
        elif drawing and current_cam_drawing == cam_name:
            # อัปเดตเส้นกรอบชั่วคราวตอนลากวาดห้องใหม่
            temp_rect[2] = x
            temp_rect[3] = y
            
    elif event == cv2.EVENT_LBUTTONUP:
        if moving_zone and current_cam_drawing == cam_name:
            # จบการย้ายห้อง
            moving_zone = None
            current_cam_drawing = None
            
        elif drawing and current_cam_drawing == cam_name:
            # จบการวาดห้องใหม่ บันทึกเป็นโซน
            drawing = False
            current_cam_drawing = None
            temp_rect[2] = x
            temp_rect[3] = y
            
            x1, x2 = min(temp_rect[0], temp_rect[2]), max(temp_rect[0], temp_rect[2])
            y1, y2 = min(temp_rect[1], temp_rect[3]), max(temp_rect[1], temp_rect[3])
            
            if (x2 - x1) > 20 and (y2 - y1) > 20:
                room_num = len(zones.get(cam_name, {})) + 1
                room_name = f"Room_{room_num}"
                if cam_name not in zones:
                    zones[cam_name] = {}
                zones[cam_name][room_name] = (x1, y1, x2, y2)
                print(f"✅ สร้างพื้นที่: {room_name} บนกล้อง {cam_name}")
                
            temp_rect = None

# =================================================================
# ฟังก์ชันสำหรับจัดการไฟล์ JSON
# =================================================================
def load_log():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_log(data):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =================================================================
# โปรแกรมหลัก
# =================================================================
def main():
    print("=" * 50)
    print("ระบบตรวจจับบุคคล (Multi-Zone + Snapshots + Drag/Drop)")
    print("=" * 50)
    print("วิธีการใช้งานเมาส์:")
    print("- [สร้างห้อง]: คลิกลากที่พื้นที่ว่าง เพื่อวาดห้องใหม่")
    print("- [ย้ายห้อง]: คลิกค้างในห้องที่มีอยู่แล้ว เพื่อลากย้ายตำแหน่ง")
    print("- [ลบห้อง]: กด 'z' เพื่อลบห้องล่าสุด (Undo)")
    print("- [ออก]: กด 'q' เพื่อปิดโปรแกรม")
    print("=" * 50)
    
    model = YOLO("yolov8n.pt")
    caps = []
    
    active_persons = {} 

    for source in CAMERA_SOURCES:
        cam_name = str(source)
        cap = cv2.VideoCapture(source)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        if cap.isOpened():
            caps.append((cam_name, cap))
            zones[cam_name] = {}
            active_persons[cam_name] = {}
            print(f"เปิดกล้อง '{cam_name}' สำเร็จ!")
            
            window_name = f"Camera {cam_name} - Multi-Zone Tracking"
            cv2.namedWindow(window_name)
            cv2.setMouseCallback(window_name, mouse_callback, param={'cam_name': cam_name})
        else:
            print(f"ไม่สามารถเปิดกล้อง '{cam_name}' ได้")
            
    if not caps:
        print("\nไม่สามารถเปิดกล้องได้เลยสักตัวเดียว โปรแกรมกำลังจะปิด")
        sys.exit()

    detection_history = load_log()

    while True:
        frames = []
        source_names = []
        
        for name, cap in caps:
            success, frame = cap.read()
            if success:
                frames.append(frame)
            else:
                frames.append(np.zeros((720, 1280, 3), dtype=np.uint8))
            source_names.append(name)
            
        results = model.track(frames, classes=[0], conf=0.5, persist=True, tracker="botsort.yaml", verbose=False)
        
        for idx, r in enumerate(results):
            cam_name = source_names[idx]
            cam_zones = zones.get(cam_name, {})
            raw_frame = frames[idx] 
            frame_h, frame_w = raw_frame.shape[:2]
            
            current_ids_in_zones = {z: set() for z in cam_zones.keys()}
            annotated_frame = r.plot()
            
            # --- วาดโซนทั้งหมดบนจอ ---
            for z_name, (zx1, zy1, zx2, zy2) in cam_zones.items():
                # เปลี่ยนสีเส้นเป็นสีชมพู จะได้เห็นชัดๆ เวลาลากย้าย
                cv2.rectangle(annotated_frame, (zx1, zy1), (zx2, zy2), (255, 105, 180), 2)
                cv2.putText(annotated_frame, z_name, (zx1, zy1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 105, 180), 2)
                if z_name not in active_persons[cam_name]:
                    active_persons[cam_name][z_name] = {}
                    
            # --- วาดโซนชั่วคราว (ตอนกำลังสร้างห้องใหม่) ---
            if drawing and current_cam_drawing == cam_name and temp_rect is not None:
                cv2.rectangle(annotated_frame, (temp_rect[0], temp_rect[1]), (temp_rect[2], temp_rect[3]), (0, 255, 255), 2)
            
            # --- ตรวจจับคนเข้าโซน ---
            if r.boxes.id is not None:
                track_ids = r.boxes.id.int().cpu().tolist()
                boxes = r.boxes.xyxy.cpu().numpy()
                
                for i, track_id in enumerate(track_ids):
                    x1, y1, x2, y2 = boxes[i]
                    # เปลี่ยนจุด Tracking จาก "กลางอก" เป็น "ปลายเท้า" (Bottom-Center)
                    # สำคัญมากสำหรับกล้องทางเดินยาวๆ เพื่อแก้ปัญหาคนเดินผ่านบังเอิญทับโซน
                    cx = int((x1 + x2) / 2)
                    cy = int(y2) # ใช้พิกัด y ด้านล่างสุดของกรอบ (ปลายเท้า)
                    
                    cv2.circle(annotated_frame, (cx, cy), 6, (0, 0, 255), -1)
                    
                    for z_name, (zx1, zy1, zx2, zy2) in cam_zones.items():
                        # เช็คว่า "ปลายเท้า" เหยียบเข้าไปในโซนหรือไม่
                        in_zone = (zx1 <= cx <= zx2) and (zy1 <= cy <= zy2)
                        
                        if in_zone:
                            current_ids_in_zones[z_name].add(track_id)
                            
                            if track_id not in active_persons[cam_name][z_name]:
                                enter_time = get_current_time()
                                
                                crop_x1, crop_y1 = max(0, int(x1)), max(0, int(y1))
                                crop_x2, crop_y2 = min(frame_w, int(x2)), min(frame_h, int(y2))
                                
                                snapshot_filename = ""
                                if crop_x2 > crop_x1 and crop_y2 > crop_y1:
                                    crop_img = raw_frame[crop_y1:crop_y2, crop_x1:crop_x2]
                                    time_str = enter_time.replace(":", "-").replace(" ", "_")
                                    snapshot_filename = f"{SNAPSHOT_DIR}/cam{cam_name}_{z_name}_p{track_id}_{time_str}.jpg"
                                    cv2.imwrite(snapshot_filename, crop_img)
                                
                                active_persons[cam_name][z_name][track_id] = {
                                    "enter_time": enter_time,
                                    "snapshot": snapshot_filename
                                }

            # --- หาคนที่เดินออกจากโซน ---
            for z_name in cam_zones.keys():
                known_ids = set(active_persons[cam_name][z_name].keys())
                disappeared_ids = known_ids - current_ids_in_zones[z_name]
                
                if disappeared_ids:
                    for t_id in disappeared_ids:
                        person_data = active_persons[cam_name][z_name][t_id]
                        exit_time = get_current_time()
                        
                        detection_history.append({
                            "camera": cam_name,
                            "zone": z_name,
                            "person_id": t_id,
                            "enter_time": person_data["enter_time"],
                            "exit_time": exit_time,
                            "snapshot": person_data["snapshot"]
                        })
                        del active_persons[cam_name][z_name][t_id]
                    save_log(detection_history)
            
            total_persons = sum(len(ids) for ids in current_ids_in_zones.values()) if cam_zones else 0
            cv2.putText(annotated_frame, f"Total in Zones: {total_persons}", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                        
            window_name = f"Camera {cam_name} - Multi-Zone Tracking"
            cv2.imshow(window_name, annotated_frame)
            
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nกำลังปิดโปรแกรม...")
            break
        elif key == ord('z'):
            for name in source_names:
                if zones[name]:
                    last_zone = list(zones[name].keys())[-1]
                    del zones[name][last_zone]
                    if last_zone in active_persons[name]:
                        del active_persons[name][last_zone]
                    print(f"🗑️ ลบพื้นที่ {last_zone} ของกล้อง {name} แล้ว")

    for cam_name, cam_zones_data in active_persons.items():
        for z_name, persons in cam_zones_data.items():
            for t_id, person_data in persons.items():
                detection_history.append({
                    "camera": cam_name,
                    "zone": z_name,
                    "person_id": t_id,
                    "enter_time": person_data["enter_time"],
                    "exit_time": get_current_time(),
                    "snapshot": person_data["snapshot"],
                    "note": "Program Terminated"
                })
    save_log(detection_history)

    for _, cap in caps:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
