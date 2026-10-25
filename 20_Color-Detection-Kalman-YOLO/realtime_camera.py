import cv2
import numpy as np
import math

class KalmanDistanceTracker:
    def __init__(self):
        self.kf = cv2.KalmanFilter(2, 1)
        self.kf.transitionMatrix = np.array([[1, 1], [0, 1]], np.float32)
        self.kf.measurementMatrix = np.array([[1, 0]], np.float32)
        self.kf.processNoiseCov = np.array([[1e-4, 0], [0, 1e-4]], np.float32)
        self.kf.measurementNoiseCov = np.array([[5e-1]], np.float32) 
        self.kf.errorCovPost = np.array([[1, 0], [0, 1]], np.float32)
        self.initialized = False

    def update(self, measurement):
        if not self.initialized:
            self.kf.statePost = np.array([[np.float32(measurement)], [0.0]], np.float32)
            self.initialized = True
            return measurement
        self.kf.predict()
        estimated = self.kf.correct(np.array([[np.float32(measurement)]], np.float32))
        return float(estimated[0][0])

def main():
    cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    color_ranges = {
        "Red": [
            (np.array([0, 100, 70]), np.array([10, 255, 255])),
            (np.array([160, 100, 70]), np.array([179, 255, 255]))
        ],
        "Green": [
            (np.array([35, 80, 70]), np.array([85, 255, 255]))
        ],
        "Blue": [
            (np.array([85, 100, 70]), np.array([130, 255, 255]))
        ]
    }

    draw_colors = {
        "Red": (0, 0, 255),
        "Green": (0, 255, 0),
        "Blue": (255, 0, 0)
    }

    REAL_WIDTH_CM = 4.0  # (ประมาณจากรูป) สมมติว่าบล็อกมีความกว้าง 4.0 เซนติเมตร
    
    FOCAL_LENGTH = 1200.0  
    
    trackers = {
        "Red": KalmanDistanceTracker(),
        "Green": KalmanDistanceTracker(),
        "Blue": KalmanDistanceTracker()
    }

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        for color_name, ranges in color_ranges.items():
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for lower, upper in ranges:
                mask |= cv2.inRange(hsv, lower, upper)
                
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=1)
            mask = cv2.dilate(mask, kernel, iterations=2)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                
                if area < 15000:
                    continue
                    
                x, y, w, h = cv2.boundingRect(cnt)
                
                
                aspect_ratio = float(w) / max(h, 1)
                if not (0.5 <= aspect_ratio <= 1.5): # ขยายให้รับความเบี้ยวได้มากขึ้น
                    continue
                    
                epsilon = 0.04 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                if len(approx) < 4 or len(approx) > 8:
                    continue  # ถ้าไม่ใช่ทรง 4-8 เหลี่ยม ให้ข้ามไปเลย
                    
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                if hull_area == 0: continue
                solidity = float(area)/hull_area
                if solidity < 0.7:
                    continue # ตัดวัตถุที่มีรูปร่างเว้าแหว่ง

                
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box_2d = np.array(box, dtype=np.float32)
                
                half_w = REAL_WIDTH_CM / 2.0
                obj_3d = np.array([
                    [-half_w, -half_w, 0],
                    [ half_w, -half_w, 0],
                    [ half_w,  half_w, 0],
                    [-half_w,  half_w, 0]
                ], dtype=np.float32)
                
                screen_height, screen_width, _ = frame.shape
                cam_matrix = np.array([
                    [FOCAL_LENGTH, 0, screen_width / 2.0],
                    [0, FOCAL_LENGTH, screen_height / 2.0],
                    [0, 0, 1]
                ], dtype=np.float32)
                
                success, rot_vec, trans_vec = cv2.solvePnP(obj_3d, box_2d, cam_matrix, None)
                if not success:
                    continue
                    
                x_3d, y_3d, z_3d = trans_vec[0][0], trans_vec[1][0], trans_vec[2][0]
                raw_distance = math.sqrt(x_3d**2 + y_3d**2 + z_3d**2)
                
                final_distance_cm = trackers[color_name].update(raw_distance)
                
                box_int = np.int32(box)
                cv2.drawContours(frame, [box_int], 0, draw_colors[color_name], 2)
                
                M = cv2.moments(cnt)
                if M["m00"] == 0: continue
                center_x, center_y = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
                cv2.circle(frame, (center_x, center_y), 5, draw_colors[color_name], -1)
                
                camera_origin = (int(screen_width / 2), screen_height)
                cv2.line(frame, camera_origin, (center_x, center_y), (0, 255, 255), 2)
                
                label = f"{color_name} | {final_distance_cm:.1f} cm"
                x_txt, y_txt, w_txt, h_txt = cv2.boundingRect(cnt) # ใช้ x,y เดิมแค่วาง text
                (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(frame, (x_txt, y_txt - 25), (x_txt + text_w, y_txt), draw_colors[color_name], -1)
                cv2.putText(frame, label, (x_txt, y_txt - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                print(f"Detected: {color_name:<6} | Area: {int(area):<6} | Distance: {final_distance_cm:.1f} cm")

        cv2.imshow("Smooth Color Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
