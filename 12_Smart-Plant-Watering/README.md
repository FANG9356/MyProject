# Smart Plant Watering (เครื่องรดน้ำต้นไม้อัตโนมัติควบคุมระยะไกลด้วยมือถือ)
[![Download Folder](https://img.shields.io/badge/Download-ZIP_Folder-238636?style=for-the-badge&logo=github)](https://download-directory.github.io/?url=https://github.com/FANG9356/MyProject/tree/main/12_Smart-Plant-Watering)
*ดาวน์โหลดเฉพาะโฟลเดอร์นี้เป็นไฟล์ ZIP (หรือ [ดาวน์โหลดผ่าน DownGit](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/FANG9356/MyProject/tree/main/12_Smart-Plant-Watering))*

ระบบรดน้ำต้นไม้อัจฉริยะแบบอัตโนมัติและควบคุมผ่านสมาร์ตโฟนด้วยแอปพลิเคชัน Blynk และไมโครคอนโทรลเลอร์ ESP8266 โดยตรวจวัดค่าความชื้นในดิน (Soil Moisture Sensor) และสั่งการวาล์วน้ำโซลินอยด์ (Solenoid Valve 12V) ผ่านรีเลย์ 4 ช่อง พร้อมระบบควบคุมแบบแมนนวลและตัวตั้งเวลารดน้ำอัตโนมัติ

![Smart Plant Demo](../assets/demo_12_smart_plant.gif)

## ข้อมูลโครงการและเอกสารประกอบ

- ผู้จัดทำ: นายภคพล สุขมี (Phakhaphon Sukmee), นายกรพล สวัสดิ์ตระกูล, นายพงศ์พีช โสมเกศตรินทร์
- ครูประจำวิชา: นายธนวัฒน์ พร้อมสุข (วิชาพื้นฐานการอินเตอร์เฟส 20128-2005 วิทยาลัยเทคนิคอุบลราชธานี)
- เอกสารโครงงานฉบับสมบูรณ์ (107 หน้าเต็ม พร้อมหน้าปกและคำนำ): [docs/รายงาน-พื้นฐานการอินเตอร์เฟซ.pdf](docs/รายงาน-พื้นฐานการอินเตอร์เฟซ.pdf)
- อุปกรณ์หลัก: NodeMCU ESP8266, Soil Moisture Sensor, DHT11, 4-Channel Relay Module, Solenoid Valve 12V, Mist Spray, Step-Down Buck Converter

## คุณสมบัติเด่น

- ตรวจวัดความชื้นในดินแบบเรียลไทม์ และคำนวณเป็นเปอร์เซ็นต์ความชื้น
- โหมดอัตโนมัติ: ควบคุมการเปิด-ปิดวาล์วน้ำตามค่าเกณฑ์ความชื้น (Threshold Triggering)
- โหมดควบคุมระยะไกล (IoT): สั่งเปิด-ปิดวาล์วผ่าน Blynk Virtual Pins (V0-V4)
- โหมดตั้งเวลา (Timer Mode): กำหนดรอบเวลาและระยะเวลาการรดน้ำอัตโนมัติ
- ป้องกันการรดน้ำเกินขนาดด้วย Safety Timeout ตัดการทำงานอัตโนมัติ

## ผังการเชื่อมต่อวงจร (Hardware Wiring)

```
+--------------------------------------------------------+
|                   NodeMCU ESP8266                      |
|                                                        |
|  A0 (ADC) <-------- Soil Moisture Sensor Analog Output |
|  D1 (GPIO5) ------> Relay CH1 (Solenoid Valve 1)       |
|  D2 (GPIO4) ------> Relay CH2 (Solenoid Valve 2)       |
|  D5 (GPIO14) -----> Relay CH3 (Pump / Valve 3)         |
|  D6 (GPIO12) -----> Relay CH4 (Status Indicator)       |
|  3V3 / GND -------> Soil Moisture Sensor Power         |
|  VIN / GND <------- 5V DC Power Supply                 |
+--------------------------------------------------------+
```

## โครงสร้างไดเรกทอรี

```
12_Smart-Plant-Watering/
├── docs/
│   └── project_report_full.pdf
├── arduino/
│   ├── blynk_valve_control.ino
│   └── smart_watering_multimode.ino
├── watering_sim.html
├── test_simulation.py
├── PORTFOLIO_INFO.md
└── README.md
```

## การทดสอบและจำลองการทำงาน

รันชุดทดสอบจำลองระบบตรวจจับความชื้นและควบคุมรีเลย์:

```bash
python3 test_simulation.py
```
