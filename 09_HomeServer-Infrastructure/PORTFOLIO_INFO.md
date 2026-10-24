# HomeServer Infrastructure & Cross-VLAN Network Scanner

**หมวดหมู่:** Network Engineering, Infrastructure Management & Full-Stack Cloud
**เทคโนโลยีหลัก (Tech Stack):** Go (Goroutines), SQLite3, React 18, Tailwind CSS, Docker

---

## ภาพรวมโครงการ (Project Overview)
ระบบศูนย์กลางบริหารจัดการ Private Cloud Services และเครื่องมือค้นหาอุปกรณ์เครือข่ายข้าม VLAN (Cross-VLAN Network Scanner) ที่เขียนขึ้นเองทั้งหมดโดยใช้ Go Goroutines ในการยิงโพรบพอร์ตแบบขนาน จัดเก็บข้อมูลใน SQLite3 และแสดงผลผ่านหน้าเว็บ React + Tailwind CSS แบบเรียลไทม์

---

## วิธีการรันและทดสอบระบบ (How to Run)
```bash
# รัน Backend (Go)
cd backend && go run .

# หรือรันผ่าน Docker
docker compose up -d --build
```
เข้าใช้งานผ่านเบราว์เซอร์ที่: `http://localhost:8001`

---
*Author: Phakhaphon Sukmee*
