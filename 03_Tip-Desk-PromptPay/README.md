# Tip Desk

ระบบรับโดเนทส่วนตัวด้วย React, FastAPI และ PromptPay QR

## เริ่มใช้งาน

1. คัดลอก `backend/.env.example` เป็น `backend/.env` แล้วใส่เลขพร้อมเพย์ของคุณ
2. เปิด backend:

```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000 --env-file backend/.env
```

3. เปิดอีก terminal แล้วเริ่มหน้าเว็บ:

```bash
npm run dev
```

เปิด `http://localhost:5173`

## การรับเงินจริง

QR ที่สร้างเป็น EMVCo PromptPay QR แบบระบุยอดเงิน ผู้สนับสนุนสามารถสแกนและจ่ายเงินจริงผ่านแอปธนาคารได้ทันที แต่ QR เพียงอย่างเดียวไม่สามารถแจ้งระบบว่ามีเงินเข้าแล้ว จึงมีปุ่มยืนยันสำหรับการทดสอบ และ endpoint `POST /api/webhooks/payment` สำหรับต่อกับธนาคารหรือ payment provider ที่รองรับ webhook

Webhook ต้องส่ง header `X-Tip-Signature` เป็น HMAC-SHA256 ของ request body โดยใช้ `WEBHOOK_SECRET` และ body อย่างน้อยต้องมี `tip_id` เช่น:

```json
{"tip_id":"รายการที่ต้องการยืนยัน"}
```

ก่อนเปิดใช้งานจริง ควรใช้ HTTPS, ตั้ง `WEBHOOK_SECRET` ใหม่ และใช้ webhook จากผู้ให้บริการที่ตรวจสอบรายการเงินเข้าได้จริง
