# HomeServer Infrastructure & Network Scanner

**หมวดหมู่:** Network & Full-Stack
**เทคโนโลยีหลัก:** Go, SQLite, React, Tailwind CSS, Docker

---

## ภาพรวมโครงการ (Project Overview)
แดชบอร์ดรวบรวมทางเข้าและเช็กสถานะบริการในเครื่อง พร้อมฟังก์ชันค้นหาไอพีและอุปกรณ์ในเครือข่ายข้ามวง VLAN ใช้งานส่วนติดต่อผู้ใช้ด้วย React + Tailwind CSS และหลังบ้านด้วย Go จัดเก็บข้อมูลใน SQLite

---

## วิธีการรันระบบ (How to Run)
```bash
# รัน Backend (Go)
cd backend && go run .

# หรือรันผ่าน Docker
docker compose up -d --build
```
เข้าใช้งานผ่านเบราว์เซอร์ที่: `http://localhost:8001`

---
*Author: Phakhaphon Sukmee*
