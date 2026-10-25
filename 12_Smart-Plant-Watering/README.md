# Smart Plant Watering (เครื่องรดน้ำต้นไม้อัตโนมัติควบคุมระยะไกลด้วยมือถือ)

ระบบรดน้ำต้นไม้อัจฉริยะแบบอัตโนมัติและควบคุมผ่านสมาร์ตโฟนด้วยแอปพลิเคชัน Blynk และไมโครคอนโทรลเลอร์ ESP8266 โดยตรวจวัดค่าความชื้นในดิน (Soil Moisture Sensor) และสั่งการวาล์วน้ำโซลินอยด์ (Solenoid Valve 12V) ผ่านรีเลย์ 4 ช่อง พร้อมระบบควบคุมแบบแมนนวลและตัวตั้งเวลารดน้ำอัตโนมัติ

![Smart Plant Demo](../assets/demo_12_smart_plant.gif)

## ข้อมูลโครงการและเอกสารประกอบ

- ผู้จัดทำ: ภคพล สุขมี (Phakhaphon Sukmee)
- เอกสารโครงงานฉบับสมบูรณ์ (99 หน้า): [docs/project_report_full.pdf](docs/project_report_full.pdf)
- อุปกรณ์หลัก: NodeMCU ESP8266, Soil Moisture Sensor, 4-Channel Relay Module, Solenoid Valve 12V, Step-Down Buck Converter

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
