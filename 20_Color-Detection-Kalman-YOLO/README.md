# 20_Color-Detection-Kalman-YOLO

ระบบตรวจจับสีวัตถุแบบเรียลไทม์จากกรอบ Bounding Box พร้อมโมเดลตัวกรองสัญญาณ Kalman Filter สำหรับงานประมวลผลภาพ

## ภาพถ่ายหน้าจอการทำงานจริง (Screenshot)
![Color Detection Kalman HUD](../assets/real_hw_20_color_kalman_yolo.png)

## ภาพเคลื่อนไหวสาธิตการทำงาน (Demonstration)
![Color Detection Kalman Demo](../assets/demo_20_color_kalman_yolo.gif)

## ผู้พัฒนา
Phakhaphon Sukmee

## คุณสมบัติหลัก
- แยกสีเด่นของวัตถุด้วย K-Means Clustering บนพื้นที่พิกเซล
- แมปช่วงสี HSV สู่คำเรียกชื่อสีภาษาไทยได้อย่างแม่นยำ
- ตัวกรอง 1D Kalman Filter สำหรับติดตามความเสถียรและระยะวัตถุแบบเรียลไทม์
- รองรับการทำงานร่วมกับโมเดล YOLOv8

## วิธีการทดสอบ
```bash
python3 test_simulation.py
```
