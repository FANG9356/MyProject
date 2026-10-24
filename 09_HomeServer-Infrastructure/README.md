# HomeServer Infrastructure & Cross-VLAN Network Scanner

> **หมวดหมู่:** Network Engineering, Infrastructure Management & Full-Stack Cloud
> **ผู้พัฒนา:** Phakhaphon Sukmee
> **เทคโนโลยี:** Go (Goroutines, Net/TCP Probe), SQLite3, React 18, Tailwind CSS, Docker

---

## สถาปัตยกรรมระบบ (System Architecture)

ระบบศูนย์กลางบริหารจัดการ Home Cloud Infrastructure และเครื่องมือสำรวจเครือข่ายข้าม VLAN (Cross-VLAN Network Scanner) ที่เขียนขึ้นเองทั้งหมด 100%:
* **Frontend:** React 18 + Tailwind CSS ออกแบบในรูปแบบ Glassmorphism Dark Theme รองรับการดูสถานะ Cloud Services และควบคุมการสแกน IP แบบเรียลไทม์
* **Backend:** Go (Golang) พัฒนา REST API และ Network Probing Engine ใช้ Goroutine ทำงานแบบขนาน (Concurrent Workers) สแกน IP และตรวจจับพอร์ต TCP ข้าม Subnet ได้อย่างรวดเร็ว
* **Database:** SQLite3 จัดเก็บรายชื่อ Cloud Services และประวัติอุปกรณ์เครือข่ายที่ค้นพบ

---

## การเริ่มต้นใช้งาน (Quick Start)

### 1. รันระบบผ่าน Go และ React โดยตรง

**Backend (Go):**
```bash
cd backend
go run .
```

**Frontend (React + Tailwind):**
```bash
cd frontend
npm install
npm run dev
```

เปิดเบราว์เซอร์ไปที่: `http://localhost:8001` (หรือพอร์ต Vite `http://localhost:5173`)

### 2. รันผ่าน Docker

```bash
docker compose up -d --build
```

---

## คุณสมบัติหลัก (Key Features)

1. **Private Cloud Services Hub:** ศูนย์รวมและตรวจเช็กสถานะการทำงาน (Latency & Health Check) ของบริการภายในบ้าน เช่น Immich, Jellyfin, FileBrowser, Bitwarden, Memos
2. **Cross-VLAN Network Scanner:** ระบบสแกนหาไอพีและอุปกรณ์ในวงเน็ตเวิร์กที่เชื่อมต่ออยู่ และสแกนข้ามวง VLAN / Subnets ได้แบบ Multi-threaded ผ่าน Go Goroutines พร้อมตรวจจับ Open Ports และ Latency
3. **Persistent SQLite Store:** ข้อมูลบริการและอุปกรณ์ที่ค้นพบจะถูกบันทึกลงฐานข้อมูล SQLite โดยอัตโนมัติ

---

## โหมดทดสอบระบบ (Test Simulation)

```bash
python3 test_simulation.py
```
