# 📡 AI Wi-Fi Sensing & Activity Recognition (Wall Penetration)

> **หมวดหมู่:** Artificial Intelligence / IoT & RF Hardware Sensing  
> **ผู้พัฒนา:** ภคพล (ฟาง) / Phakaphon  

---

## 📖 คู่มือการติดตั้งและทดลองใช้งานสำหรับกรรมการ (Examiner's Guide)

### 1. สิ่งที่ต้องมีในเครื่อง (Prerequisites)
* Python 3.9 หรือใหม่กว่า
* บอร์ด ESP32 (หากต้องการทดสอบกับฮาร์ดแวร์จริง) หรือสามารถทดสอบผ่านโหมดจำลอง (Simulation Mode) ได้ทันทีโดยไม่ต้องมีฮาร์ดแวร์

### 2. การติดตั้ง Dependencies
เปิด Terminal ในโฟลเดอร์นี้แล้วรันคำสั่ง:
```bash
pip install scikit-learn pandas numpy joblib
```

### 3. การทดสอบระบบ (2 วิธี)

#### วิธีที่ 1: โหมดทดสอบจำลอง (Simulation Mode - ไม่ต้องต่ออุปกรณ์)
คำสั่งนี้จะโหลดโมเดล `ai_model.pkl` และสุ่มตัวอย่างสัญญาณคลื่นวิทยุจริงจากไฟล์ Dataset มาทดสอบจำแนกท่าทาง (Empty, Walking, Falling):
```bash
python3 test_simulation.py
```
*ผลลัพธ์ที่ได้:* จะแสดงผลลัพธ์ความแม่นยำ (Accuracy) และสถานะการทายผลแยกแต่ละคลาส

#### วิธีที่ 2: โหมดรัน Web Dashboard แสดงผลแบบ Real-time
เปิดเซิร์ฟเวอร์จำลองการรับส่งข้อมูลผ่าน UDP และหน้า Web Dashboard:
```bash
python3 ai_web_server.py
```
จากนั้นเปิดเบราว์เซอร์ไปที่: `http://localhost:8080/ai_index.html`
* **สิ่งที่กรรมการจะเห็น:** หน้าจอแดชบอร์ดเปลี่ยนสีตามสถานะการตรวจจับคลื่นวิทยุ:
  * 🟢 **สีเขียว (Empty):** ห้องว่าง ไม่มีมนุษย์
  * 🔵 **สีน้ำเงิน (Walking):** ตรวจพบคนกำลังเดินทะลุกำแพง
  * 🔴 **สีแดง (Falling Alert):** ตรวจพบลักษณะคลื่นสัญญาณของการหกล้มฉับพลัน

---
