# ระบบบริหารจัดการหอพักแบบสแตนด์อโลนสำหรับ Windows Desktop (Project 25)

## ข้อมูลผลงาน
- ผู้พัฒนา: Phakhaphon Sukmee
- ประเภทโครงงาน: Windows Desktop Native Application, Enterprise Dormitory Management, Offline-First Architecture
- เทคโนโลยี: Wails v2, Go (Golang), React 18, Tailwind CSS, Vite, SQLite (WAL Mode), NSIS Installer

## สถาปัตยกรรมและโครงสร้างระบบ
1. **สถาปัตยกรรม Native Desktop ผ่าน Wails v2**
   - รวบรวมแบ็กเอนด์ภาษา Go และฟรอนต์เอนด์ React ไว้ในรูปแบบไฟล์ปฏิบัติการเดี่ยว (Single Binary Executable)
   - ไม่จำเป็นต้องติดตั้ง Node.js, Python หรือเว็บเซิร์ฟเวอร์ภายนอกบนเครื่องลูกข่าย
   - ทำงานได้ทั้งแบบออฟไลน์ 100% ภายในเครื่อง และโหมดแชร์ผ่านเครือข่ายท้องถิ่น (LAN)

2. **ระบบการทำงานสองโหมด (Dual Operation Modes)**
   - **โหมดเครื่องแม่ข่าย (Host Server):** เปิดรันเซิร์ฟเวอร์ Go HTTP และฐานข้อมูล SQLite แบบ WAL Mode อัตโนมัติ พร้อมให้บริการเครื่องลูกข่ายผ่านเครือข่ายภายใน
   - **โหมดเครื่องลูกข่าย (Client Terminal):** ตรวจจับและค้นหา IP ของเครื่องแม่ข่ายอัตโนมัติผ่าน Subnet Scanner เชื่อมต่อไปยังพอร์ต 4282 เพื่อทำงานร่วมกันได้หลายเครื่องพร้อมกัน

3. **การจัดการฐานข้อมูลและธุรกรรมออฟไลน์**
   - ฐานข้อมูล SQLite รองรับการทำงานแบบมัลติคอนเนกชันด้วยโหมด WAL (Write-Ahead Logging) และ Busy Timeout
   - จัดการข้อมูลห้องพัก ผู้เช่า ประวัติการเข้าพัก การคำนวณมิเตอร์น้ำ-ไฟ และบันทึกกิจกรรมระบบ (System Audit Logs)
   - ระบบสำรองและกู้คืนฐานข้อมูลในตัว (Snapshot Backup & Restore)

4. **ระบบคำนวณมิเตอร์น้ำ-ไฟและพิมพ์เอกสารผ่าน Wails IPC**
   - คำนวณผลต่างหน่วยมิเตอร์และคำนวณยอดเงินรวมใบแจ้งหนี้อัตโนมัติตามเรตราคา
   - คำสั่ง Wails IPC `PrintHtml` เชื่อมต่อหน้าต่างการพิมพ์ของระบบปฏิบัติการ Windows สำหรับออกใบแจ้งหนี้และใบเสร็จรับเงิน

5. **ตัวติดตั้งและแพ็กเกจการใช้งาน Windows**
   - ไฟล์รันแบบพกพา (Portable): `bin/DormiNetX.exe` (ขนาด 30 MB)
   - ตัวติดตั้งมาตรฐาน (NSIS Installer): `bin/DormiNetX-Installer.exe` (ขนาด 13 MB) พร้อมสร้าง Shortcut บน Desktop และ Start Menu
