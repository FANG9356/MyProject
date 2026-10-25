# 22_PDF-Speech-Synthesizer

ระบบสกัดข้อความจากเอกสาร PDF และสังเคราะห์เป็นไฟล์เสียงพูดภาษาไทยอัตโนมัติ (PDF to Audiobook)

## ภาพถ่ายหน้าจอการทำงานจริง (Screenshot)
![PDF Speech Engine](../assets/real_hw_22_pdf_speech.png)

## ภาพเคลื่อนไหวสาธิตการทำงาน (Demonstration)
![PDF Speech Synthesizer Demo](../assets/demo_22_pdf_speech.gif)

## ผู้พัฒนา
Phakhaphon Sukmee

## คุณสมบัติหลัก
- อ่านข้อความจากเอกสาร PDF ทุกหน้าโดยอัตโนมัติ
- ทำความสะอาดข้อความ ปรับระยะห่าง และจัดเรียงคำสำหรับระบบสังเคราะห์เสียง
- แปลงข้อความเป็นเสียงพูดภาษาไทยด้วย Google Text-to-Speech
- บันทึกผลลัพธ์เป็นไฟล์เสียง MP3

## วิธีการทดสอบ
```bash
python3 test_simulation.py
```
