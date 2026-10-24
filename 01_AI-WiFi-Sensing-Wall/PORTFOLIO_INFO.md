# AI Wi-Fi Sensing & Activity Recognition (Wall Penetration)

**หมวดหมู่:** Artificial Intelligence / IoT & Hardware Sensing  
**เทคโนโลยีหลัก (Tech Stack):** ESP32, WiFi CSI (Channel State Information), Python, Scikit-Learn (Random Forest), HTML5/CSS3 Dashboard  

---

## 📌 ภาพรวมโครงการ (Project Overview)
ระบบตรวจจับการเคลื่อนไหวของมนุษย์ทะลุกำแพงโดยไม่ต้องใช้กล้อง โดยดักจับและวิเคราะห์สัญญาณคลื่นวิทยุ WiFi CSI ผ่าน ESP32 นำมาสกัดคุณลักษณะ (Feature Extraction) และจำแนกท่าทาง (เดิน, หกล้ม, ห้องว่าง) ด้วย Machine Learning แบบเรียลไทม์

---

## 🚀 วิธีการรันและทดสอบระบบ (How to Run)
```bash
1. รัน ai_trainer.py เพื่อเทรนโมเดล (หากต้องการเทรนใหม่)
2. เสียบ ESP32 ที่แฟลช sketch_jul24a แล้ว
3. รัน ai_web_server.py และเปิดเบราว์เซอร์ไปที่ http://localhost:8080
```

---
*Author: Phakhaphon Sukmee*
