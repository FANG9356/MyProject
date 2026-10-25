# Grade Calculator Python (โปรแกรมคำนวณเกรด ด้วย Python)
[![Download Folder](https://img.shields.io/badge/Download-ZIP_Folder-238636?style=for-the-badge&logo=github)](https://download-directory.github.io/?url=https://github.com/FANG9356/MyProject/tree/main/17_Grade-Calculator-Python)
*ดาวน์โหลดเฉพาะโฟลเดอร์นี้เป็นไฟล์ ZIP (หรือ [ดาวน์โหลดผ่าน DownGit](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/FANG9356/MyProject/tree/main/17_Grade-Calculator-Python))*

โปรแกรมประยุกต์สำหรับคำนวณแต้มระดับคะแนนเฉลี่ยรายภาคเรียน (GPA) และแต้มระดับคะแนนเฉลี่ยสะสม (GPAX) พัฒนาด้วยภาษา Python และ CustomTkinter ในธีมสีมืด (Dark Mode) รองรับการคำนวณตามเกณฑ์มาตรฐานการศึกษา 8 ระดับ (A, B+, B, C+, C, D+, D, F) พร้อมระบบจัดการรายวิชาแบบไดนามิกและตรวจสอบความถูกต้องของข้อมูล

![Grade Calculator Demo](../assets/demo_17_grade_calculator.gif)

## ข้อมูลโครงการและเอกสารคู่มือเกณฑ์การตัดเกรด

- ผู้พัฒนา: ภคพล สุขมี (Phakhaphon Sukmee)
- เอกสารคู่มือเกณฑ์การตัดเกรดและสูตรคำนวณ: [docs/grading_system_manual.md](docs/grading_system_manual.md)

## คุณสมบัติเด่น

- คำนวณเกรดรายวิชาและแปลงคะแนนดิบ (0-100) เป็นระดับเกรดและแต้มคะแนน (Grade Point) อัตโนมัติ
- คำนวณแต้มระดับคะแนนเฉลี่ยประจำภาคเรียน (GPA) ถ่วงน้ำหนักตามหน่วยกิตของแต่ละวิชา
- คำนวณผลการเรียนเฉลี่ยสะสมรวม (GPAX) โดยนำผลการเรียนเดิมและหน่วยกิตสะสมมารวมคำนวณถ่วงน้ำหนักอย่างแม่นยำ
- ส่วนติดต่อผู้ใช้แบบ Modern Dark Mode เลื่อนดูข้อมูลได้สะดวกด้วย Scrollable Frame
- ระบบตรวจสอบข้อมูลป้องกันการกรอกคะแนนเกิน 100 หรือหน่วยกิตติดลบ

## โครงสร้างไดเรกทอรี

```
17_Grade-Calculator-Python/
├── docs/
│   └── grading_system_manual.md
├── cal.py
├── cal_sim.html
├── test_simulation.py
├── PORTFOLIO_INFO.md
└── README.md
```

## การทดสอบระบบ

รันชุดทดสอบตรวจสอบโครงสร้างไฟล์ การตัดเกรดตามช่วงคะแนน การคำนวณ GPA และการคำนวณ GPAX สะสม:

```bash
python3 test_simulation.py
```
