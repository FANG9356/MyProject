# ระบบสตรีมมิ่งหน้าจอและสื่อสารด้วยเสียงแบบเรียลไทม์ (Project 23)

## ข้อมูลผลงาน
- ผู้พัฒนา: Phakhaphon Sukmee
- ประเภทโครงงาน: Real-Time Network Communication, Audio/Video Streaming, Socket Programming
- เทคโนโลยี: Python, TCP Sockets, PyAudio, OpenCV, MSS, Tkinter Desktop GUI

## สถาปัตยกรรมและโพรโทคอลการทำงาน
1. **ช่องสัญญาณสตรีมมิ่งหน้าจอ (Screen Share Protocol)**
   - ใช้ TCP Socket แบบกำหนดหัวเฟรมข้อมูลความยาว 4 ไบต์ (Big-Endian Length Header) ตามด้วยไบนารีข้อมูลภาพบีบอัด JPEG
   - ไคลเอนต์จับภาพหน้าจอความเร็วสูงด้วยไลบรารี MSS ย่อขนาดสเกลและส่งต่อให้เซิร์ฟเวอร์เพื่อกระจายภาพสู่ผู้ใช้รายอื่นแบบ Broadcast

2. **ช่องสัญญาณถ่ายทอดเสียง (Voice Streaming Channel)**
   - สตรีมสัญญาณเสียงแบบฟูลดูเพล็กซ์ด้วย PyAudio (PCM 16-bit, 44.1 kHz, Chunk 1024)
   - ส่งผ่านแพ็กเก็ตเสียงขนาด 4096 ไบต์แบบ Non-blocking Multithreading

3. **ส่วนต่อประสานผู้ใช้สไตล์ Discord Dark Theme**
   - พัฒนาด้วย Tkinter จำลองห้องพูดคุย รายชื่อสมาชิก และหน้าต่างแสดงผลหน้าจอผู้สตรีม
