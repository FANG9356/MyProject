# Project Portfolio Information

## ชื่อโครงการ
โปรแกรมค้นหาและลบไฟล์ซ้ำ ด้วย Python (Duplicate File Cleaner & Storage Optimizer)

## ผู้พัฒนา
ภคพล สุขมี (Phakhaphon Sukmee)

## หมวดหมู่
Desktop Application / Storage Utilities / System Tools

## เทคโนโลยีที่ใช้
- ภาษาหลัก: Python 3
- ส่วนติดต่อผู้ใช้ (GUI): CustomTkinter (Modern Dark Theme, CTkScrollableFrame, CTkCheckBox)
- ขั้นตอนวิธีและวิทยาการรหัสลับ: SHA-256 Hashing (`hashlib`), Chunked Stream Processing, Collections (`defaultdict`)
- การจัดการระบบไฟล์: `os.walk`, `os.path.getsize`, `os.remove`

## สรุปภาพรวมและผลการดำเนินงาน
โปรแกรมยูทิลิตี้สำหรับบริหารจัดการพื้นที่จัดเก็บข้อมูลบนเครื่องคอมพิวเตอร์ โดยสแกนค้นหาไฟล์ที่มีข้อมูลซ้ำซ้อนกันในระดับไบต์อย่างแม่นยำ 100% แม้จะมีชื่อไฟล์หรือวันที่สร้างแตกต่างกัน ระบบทำงานด้วยความเร็วสูงผ่านการกรองขนาดไฟล์ก่อนคำนวณแฮช และเปิดโอกาสให้ผู้ใช้งานตรวจสอบรายการและเลือกไฟล์ที่ต้องการลบได้อย่างปลอดภัย พร้อมระบบรายงานปริมาณพื้นที่หน่วยความจำที่ได้รับคืนกลับมา

## เอกสารอ้างอิง
- เอกสารสถาปัตยกรรมขั้นตอนวิธี: docs/duplicate_detection_algorithm.md
