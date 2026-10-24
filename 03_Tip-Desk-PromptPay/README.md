# 💳 Tip Desk — Real-time PromptPay Donation & Voice Alert System

> **หมวดหมู่:** FinTech / Modern Full-Stack Application  
> **ผู้พัฒนา:** Phakhaphon Sukmee  

---

## 📖 วิธีติดตั้งและเริ่มใช้งาน (Quick Start)

### 1. สิ่งที่ต้องมีในเครื่อง (Prerequisites)
* Python 3.10+ และ Node.js 18+

### 2. การติดตั้งและเปิดระบบ

**Terminal ที่ 1 (Backend FastAPI & EMVCo Engine):**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

**Terminal ที่ 2 (Frontend React 19 UI):**
```bash
npm install
npm run dev
```
เปิดเบราว์เซอร์ไปที่: `http://localhost:5173`

### 3. ขั้นตอนการทดลองใช้งานจริง
1. ในหน้าเว็บ กรอกชื่อผู้สนับสนุน เช่น *"ผู้สนับสนุน"* หรือชื่อที่ต้องการ
2. ระบุจำนวนเงิน (เช่น `50` หรือ `100` บาท) และพิมพ์ข้อความให้กำลังใจ
3. กดปุ่ม **"Confirm Donation"**
4. หน้าต่าง Modal จะเด้งขึ้นมาพร้อม **PromptPay QR Code มาตรฐาน EMVCo** ที่มีจำนวนเงินตรงตามที่ระบุ
5. เมื่อจำลองการชำระเงินสำเร็จ ระบบจะมี **เสียงสังเคราะห์ Text-to-Speech (TTS)** พูดขอบคุณผู้บริจาคออกทางลำโพงทันที และมีรายการขึ้นบน Live Donation Feed

#### โหมดทดสอบด่วน (Quick Test):
```bash
python3 test_simulation.py
```
---
