# 🌐 Home Server & DevOps Infrastructure

> **หมวดหมู่:** DevOps, Infrastructure as Code & Private Cloud  
> **ผู้พัฒนา:** Phakhaphon Sukmee  

---

## 📖 วิธีติดตั้งและเริ่มใช้งาน (Quick Start)

### 1. สิ่งที่ต้องมีในเครื่อง (Prerequisites)
* Docker และ Docker Compose

### 2. คำสั่งเปิดระบบ
เปิด Terminal ในโฟลเดอร์นี้แล้วรันคำสั่ง:
```bash
docker compose up -d
```
เปิดเบราว์เซอร์ไปที่: `http://localhost:8001`

### 3. การแสดงผลของระบบในหน้า Dashboard
* **หน้า Homepage Dashboard:** รวม Service ที่โฮสต์เองภายในบ้าน
* **วิดเจ็ตแสดงผลสถานะ:** CPU, RAM, อุณหภูมิ, และการเชื่อมต่อ Proxmox Node
* **การจัดกลุ่มบริการ:** Docker Containers, สื่อบันเทิง (Jellyfin), คลังรหัสผ่าน (Vaultwarden), และระบบคลาวด์รูปภาพ (Immich)

#### โหมดทดสอบด่วน (Quick Test ตรวจสอบความถูกต้องของคอนฟิก):
```bash
python3 test_simulation.py
```
---
