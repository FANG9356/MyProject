# 🎤 Smart Karaoke Studio — Self-Hosted Streaming & Mobile Remote Control

> **หมวดหมู่:** Multimedia Server & Distributed Web App  
> **ผู้พัฒนา:** ภคพล / Phakaphon  

---

## 📖 คู่มือการติดตั้งและทดลองใช้งานสำหรับกรรมการ (Examiner's Guide)

### 1. สิ่งที่ต้องมีในเครื่อง (Prerequisites)
* Python 3.10+

### 2. การติดตั้งและเปิดเซิร์ฟเวอร์
```bash
pip install fastapi uvicorn yt-dlp
python3 main.py
```

### 3. การทดลองใช้งานแบบ 2 หน้าจอ (Dual-Screen Demonstration)
1. **หน้าจอหลัก (จำลองหน้าจอทีวีในบ้าน):**  
   เปิดเบราว์เซอร์ไปที่: `http://localhost:8000`  
   *(หน้านี้คือหน้าเล่นเพลงและแสดงเนื้อเพลง)*
2. **หน้ารีโมตมือถือ (เปิดในแท็บใหม่ หรือเปิดบนสมาร์ทโฟนในวงแลนเดียวกัน):**  
   เปิดเบราว์เซอร์ไปที่: `http://localhost:8000/remote.html`
3. **การสั่งการ:**  
   พิมพ์ชื่อเพลงที่ต้องการในหน้ารีโมต -> กดปุ่ม "ค้นหา" -> กด "จองคิวเพลง" เพลงจะถูกส่งไปเข้าคิวและเล่นบนหน้าจอหลักทันทีแบบเรียลไทม์

#### โหมดทดสอบด่วน (Quick Test):
```bash
python3 test_simulation.py
```
---
