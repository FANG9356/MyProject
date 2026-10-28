# ระบบบริหารจัดการหอพักระดับองค์กร DormiNetX Enterprise Native iOS & Cloud Management (Project 26)

## ข้อมูลผลงาน
- ผู้พัฒนา: Phakhaphon Sukmee
- ประเภทโครงงาน: Enterprise Dormitory Cloud Platform, Native iOS & iPadOS Application, Local-First Architecture, LINE OA & LIFF Integration
- เทคโนโลยีหลัก: Swift 5.9, SwiftUI, SwiftData, Go (Golang 1.22), Multi-Tenant SQLite (WAL Mode), LINE Messaging API, LINE Front-end Framework (LIFF), SHA-256 Audit Ledger, Apple Keychain, PromptPay QR Engine

## สถาปัตยกรรมและโครงสร้างระบบ
1. **สถาปัตยกรรม Native iOS และ Local-First Data Synchronization**
   - พัฒนาแอปพลิเคชันสำหรับ iOS และ iPadOS ด้วยภาษา Swift 5.9 และ SwiftUI ร่วมกับ SwiftData Framework
   - ทำงานแบบ Local-First 100% สามารถเปิดดู ค้นหา และบันทึกข้อมูลได้แม้ไม่มีสัญญาณอินเทอร์เน็ต
   - ระบบ SyncManager พร้อม Snapshot Protocol 2 และ SyncOutbox คอยจับคู่และซิงก์ข้อมูลสองทิศทางเมื่อกลับมาออนไลน์ พร้อมกลไกความปลอดภัย Rebase Conflict ป้องกันข้อมูลสูญหาย

2. **ระบบบริการหลังบ้าน Go Cloud Engine และ Multi-Tenant SQLite Isolation**
   - เซิร์ฟเวอร์พัฒนาด้วยภาษา Go 1.22 ให้ประสิทธิภาพการประมวลผลสูงและใช้หน่วยความจำต่ำ
   - สถาปัตยกรรมแยกฐานข้อมูล Multi-Tenant SQLite อิสระตามรหัสหอพัก ป้องกันการรั่วไหลของข้อมูลข้ามองค์กร 100%
   - ผ่านการทดสอบ Concurrency Safety ด้วย Go Race Detector โดยมี Data Races เป็นศูนย์

3. **ระบบบัญชีและการตรวจสอบธุรกรรมย้อนหลัง (Financial Immutable Ledger)**
   - คำนวณค่าเช่า ค่าน้ำ-ไฟ และค่าส่วนกลางรายเดือนอัตโนมัติจากหน่วยมิเตอร์
   - บันทึกประวัติการเงินและการปรับปรุงยอดด้วย SHA-256 Hash Chaining ป้องกันการปลอมแปลงและตรวจสอบย้อนกลับได้ทุกรายการ

4. **การเชื่อมต่อ LINE Official Account และพอร์ทัลลูกบ้าน LIFF**
   - ส่งใบแจ้งหนี้รายเดือนอัตโนมัติผ่าน LINE Flex Messages พร้อมยอดรวมและกำหนดชำระ
   - พอร์ทัลลูกบ้านผ่าน LINE LIFF ให้ผู้เช่าตรวจสอบประวัติการใช้น้ำ-ไฟ ชำระเงินผ่าน PromptPay QR และอัปโหลดสลิป
   - ระบบยืนยันสลิปอัตโนมัติ (Slip Verification Dual Engine) พร้อมระบบ Fail-Closed ป้องกันสลิปปลอมและการ Replay สลิปซ้ำ

5. **กระบวนการจัดการงานซ่อมแซม 6 ขั้นตอน (Maintenance Workflow State Machine)**
   - ลำดับขั้นตอนรัดกุม: แจ้งปัญหา -> ประเมินราคาและเสนอราคา -> ผู้เช่าอนุมัติผ่าน LINE -> เข้าซ่อมแซม -> ออกบิล/แนบสลิป -> ปิดงาน
   - รองรับกรณีงานซ่อมที่ไม่มีค่าใช้จ่าย (Free Flow) เพื่อความสะดวกรวดเร็ว

6. **ระบบแปลภาษาและการรองรับหลายภาษา (Localization)**
   - แค็ตตาล็อกการแปลภาษา Localizable.xcstrings ครอบคลุม 4 ภาษา: ภาษาไทย, ภาษาอังกฤษ, ภาษาพม่า และภาษาจีน
