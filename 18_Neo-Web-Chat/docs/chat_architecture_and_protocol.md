# สถาปัตยกรรมระบบแชทออนไลน์และการสื่อสารไร้สาย (Chat Architecture & Wireless Protocol)

เอกสารทางเทคนิคอธิบายสถาปัตยกรรมระบบคุยแชทออนไลน์ (Neo-Brutalist Web Chat & Offline BLE Chat) ซึ่งรองรับการสื่อสารแบบสองโหมด (Dual-Mode Communication Architecture)

## 1. ภาพรวมสถาปัตยกรรมระบบ (System Architecture)

ระบบประกอบด้วย 2 ส่วนประกอบหลัก:
1. **Neo-Brutalist Web Chat (Frontend SPA)**:
   - สไตล์การออกแบบ: Neo-Brutalist Design System (Monochrome Palette, 1px/2px Solid Black Borders, Hard Shadows `box-shadow: 8px 8px 0px #000`, Monospace Typography)
   - โหมด Wi-Fi: สื่อสารแบบเรียลไทม์ผ่าน Firebase Realtime Database และ Firebase Authentication
   - โหมด Bluetooth (Web Bluetooth API): ค้นหาและเชื่อมต่อกับไมโครคอนโทรลเลอร์ ESP32 ไร้สายในระยะใกล้โดยไม่ต้องใช้อินเทอร์เน็ต
2. **Offline BLE Chat Desktop Client (Python & Bleak)**:
   - สร้างส่วนติดต่อผู้ใช้ด้วย Tkinter (`ScrolledText`, `Entry`)
   - ควบคุมการเชื่อมต่อ Bluetooth Low Energy แบบอะซิงโครนัสด้วย `asyncio` และ `Bleak`
   - จัดคิวข้อความรับเข้าด้วย `asyncio.Queue` เพื่อความปลอดภัยในการอัปเดตเธรด GUI

## 2. นิยามโปรโตคอล Bluetooth Low Energy (BLE GATT Profiles)

- Service Name: `ESP32_Chat_App`
- Service UUID: `6e400001-b5a3-f393-e0a9-e50e24dcca9e` (Nordic UART Service Emulation)
- RX Characteristic UUID: `6e400002-b5a3-f393-e0a9-e50e24dcca9e` (Write Property: Client -> ESP32)
- TX Characteristic UUID: `6e400003-b5a3-f393-e0a9-e50e24dcca9e` (Notify Property: ESP32 -> Client)

## 3. สตรีมข้อมูลและการจัดการสถานะข้อความ (Message Pipeline)

- รูปแบบข้อความ: UTF-8 Encoded Byte Stream
- ข้อความฝั่งผู้ส่ง (Sent Message): จัดวางชิดขวา สีพื้นหลังสีดำ ตัวหนังสือสีขาว
- ข้อความฝั่งผู้รับ (Received Message): จัดวางชิดซ้าย สีพื้นหลังสีขาว ขอบดำ ตัวหนังสือสีดำ
- โหมด Screen Sharing: อินเทอร์เฟซสไตล์ Discord รองรับ WebRTC MediaStream API
