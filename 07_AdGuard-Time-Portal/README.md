# AdGuard Time Portal — Internet Access & Quota Control
[![Download Folder](https://img.shields.io/badge/Download-ZIP_Folder-238636?style=for-the-badge&logo=github)](https://download-directory.github.io/?url=https://github.com/FANG9356/MyProject/tree/main/07_AdGuard-Time-Portal)
*ดาวน์โหลดเฉพาะโฟลเดอร์นี้เป็นไฟล์ ZIP (หรือ [ดาวน์โหลดผ่าน DownGit](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/FANG9356/MyProject/tree/main/07_AdGuard-Time-Portal))*

> **หมวดหมู่:** Network Administration & API Automation
> **ผู้พัฒนา:** Phakhaphon Sukmee

---

![AdGuard User Portal](../assets/real_web_07_adguard_portal.png)

![Live Simulation Demo](../assets/demo_07_adguard_portal.gif)

## วิธีติดตั้งและเริ่มใช้งาน (Quick Start)

### 1. สิ่งที่ต้องมีในเครื่อง (Prerequisites)
* Node.js 16+

### 2. การติดตั้งและเปิดระบบ
```bash
npm install
cp .env.example .env
node server.js
```
เปิดเบราว์เซอร์ไปที่: `http://localhost:8080`

### 3. ขั้นตอนการทดลองใช้งาน
1. **หน้าสำหรับผู้ใช้งานขอใช้งานเน็ต:** `http://localhost:8080/index.html`
 * กรอกรหัส PIN เพื่อขอเปิดการเชื่อมต่ออินเทอร์เน็ต
2. **หน้าผู้ดูแลระบบสร้างรหัส PIN:** `http://localhost:8080/admin.html`
 * สร้างรหัส PIN ใหม่พร้อมกำหนดระยะเวลาใช้งาน เช่น 30 นาที หรือ 1 ชั่วโมง
 * ระบบจะนับถอยหลัง และส่งคำสั่ง Block/Unblock IP ผ่าน AdGuard Home API อัตโนมัติ

#### โหมดทดสอบด่วน (Quick Test):
```bash
node test_simulation.js
```
---
