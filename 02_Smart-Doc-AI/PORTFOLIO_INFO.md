# Smart Doc AI — Automated Academic Research & Document Generator

**หมวดหมู่:** GenAI Agent / Full-Stack Web Application
**เทคโนโลยีหลัก (Tech Stack):** React, Tailwind CSS, Vite, FastAPI (Python), Wikipedia API, DuckDuckGo Search, ArXiv API, python-docx, Docker

---

## ภาพรวมโครงการ (Project Overview)
ระบบ AI Agent สำหรับช่วยค้นคว้าวิจัยและร่างเอกสารทางวิชาการอัตโนมัติ เพียงกรอกหัวข้อ ระบบจะค้นคว้าข้อมูลจากแหล่งข้อมูลออนไลน์ (Wikipedia, งานวิจัย ArXiv, ข่าวสารเว็บ) สรุปเนื้อหา และสร้างออกมาเป็นไฟล์ Word (.docx) ตาม Template มาตรฐาน

---

## วิธีการรันและทดสอบระบบ (How to Run)
```bash
ใช้ docker-compose up -d หรือ:
Backend: cd app && uvicorn main:app --reload --port 8000
Frontend: cd frontend && npm run dev (เข้า http://localhost:5173)
```

---
*Author: Phakhaphon Sukmee*
