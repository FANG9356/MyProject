# ระบบตรวจจับผู้บุกรุกและตรวจสอบความปลอดภัยเครือข่าย LAN (Project 24)

## ข้อมูลผลงาน
- ผู้พัฒนา: Phakhaphon Sukmee
- ประเภทโครงงาน: Network Security, Intruder Detection System (IDS), Real-Time Monitoring
- เทคโนโลยี: Node.js, Express, Socket.io, Systeminformation, ARP Table Inspection

## สถาปัตยกรรมและกลไกความปลอดภัย
1. **การตรวจสอบและสแกนตาราง ARP (ARP Table Inspection)**
   - สแกนอุปกรณ์ทั้งหมดที่เชื่อมต่ออยู่ในเครือข่ายวงแลน (Local Area Network)
   - ดึงข้อมูล IP Address, MAC Address และทดสอบค่า Latency (Ping) รายอุปกรณ์

2. **ระบบบัญชีขาวป้องกันผู้บุกรุก (MAC Address Whitelist Verification)**
   - นำค่า MAC Address ที่พบมาเปรียบเทียบกับรายการอุปกรณ์ที่ได้รับอนุญาต (Trusted MACs)
   - หากพบ MAC Address แปลกปลอม ระบบจะติดแท็กแจ้งเตือนเป็น UNKNOWN / Intruder พร้อมแสดงแถบสีเตือนภัยในหน้าแดชบอร์ด

3. **การตรวจสอบความเร็วและการเชื่อมต่ออินเทอร์เน็ต (WAN Connectivity & Throughput)**
   - ทดสอบการเชื่อมต่อเครือข่ายภายนอก (WAN Ping) ไปยังเซิร์ฟเวอร์ปลายทาง
   - ตรวจวัดอัตราการรับ-ส่งข้อมูล Network Bandwidth (Upload / Download) และทรัพยากรฮาร์ดแวร์แบบเรียลไทม์
