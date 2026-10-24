# Smart Doc AI — Automated Academic Research & Document Generator

> **หมวดหมู่:** GenAI Agent / Full-Stack Web Application
> **ผู้พัฒนา:** Phakhaphon Sukmee

---

## วิธีติดตั้งและเริ่มใช้งาน (Quick Start)

### 1. สิ่งที่ต้องมีในเครื่อง (Prerequisites)
* Python 3.10+ และ Node.js 18+ (หรือติดตั้ง Docker & Docker Compose)

### 2. วิธีเริ่มใช้งานระบบ

#### วิธีที่ A: รันผ่าน Docker Compose (ง่ายที่สุด แนะนำ)
```bash
docker compose up -d
```
เปิดเบราว์เซอร์ไปที่: `http://localhost:5173`

#### วิธีที่ B: รันแบบ Manual (แยก Frontend / Backend)
**Terminal ที่ 1 (Backend FastAPI):**
```bash
cd app
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
**Terminal ที่ 2 (Frontend React + Vite):**
```bash
cd frontend
npm install
npm run dev
```
เปิดเบราว์เซอร์ไปที่: `http://localhost:5173`

### 3. ขั้นตอนการทดลองใช้งานจริง
1. พิมพ์หัวข้องานวิจัยที่ต้องการในช่องค้นหา เช่น:
 * `"Artificial Intelligence in Healthcare"`
 * `"Quantum Computing Algorithms"`
2. กดปุ่ม **"ค้นคว้าและสร้างเอกสาร" (Generate Document)**
3. สังเกตแถบ Pipeline ความคืบหน้า 4 ขั้นตอน:
 * *1. วิเคราะห์คำค้นหา* -> *2. ดึงข้อมูลจาก Wikipedia* -> *3. ค้นคว้างานวิจัย ArXiv* -> *4. จัดรูปแบบ Word*
4. เมื่อสร้างเสร็จ กดปุ่ม **"Download .docx"** จะได้ไฟล์ Microsoft Word ที่จัดหัวข้อ ย่อหน้า และแหล่งอ้างอิงเสร็จสมบูรณ์

#### โหมดทดสอบด่วน (Quick Test):
```bash
python3 test_simulation.py
```
---
