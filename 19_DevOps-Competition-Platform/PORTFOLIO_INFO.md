# โครงการแข่งขันทักษะวิชาชีพด้านเทคโนโลยีสารสนเทศ DevOps 2568 (Project 19)

## ข้อมูลผลงาน
- ผู้พัฒนา: Phakhaphon Sukmee
- รายการแข่งขัน: รายการที่ 58 ทักษะเทคโนโลยีสารสนเทศด้าน DevOps การแข่งขันทักษะวิชาชีพ
- ประเภทโครงงาน: Full-Stack Web Application, IoT Telemetry System และ Enterprise Infrastructure Automation

## สถาปัตยกรรมและองค์ประกอบ
1. **Module 1: Web Application & CI/CD Pipeline**
   - Frontend: Nuxt 3, Vue 3, TailwindCSS, TypeScript
   - Backend: Express.js, RESTful API, JWT Authentication, Multer file upload
   - Automation: GitLab CI/CD (.gitlab-ci.yml) สำหรับทดสอบและสร้าง Docker image อัตโนมัติ

2. **Module 2: IoT Environmental Telemetry**
   - ฮาร์ดแวร์: ESP32 ร่วมกับเซนเซอร์ BMP280 ตรวจวัดอุณหภูมิและความดันบรรยากาศ
   - เครือข่าย: เชื่อมต่อ WiFi และเผยแพร่ข้อมูลผ่านโพรโทคอล MQTT ด้วยรูปแบบ JSON Payload
   - มอนิเตอร์: นำเข้าข้อมูลด้วย Node-RED flow ลงฐานข้อมูล MySQL และแสดงผลแบบกราฟิกบน Grafana Dashboard

3. **Module 3: DevOps & Enterprise Network Infrastructure**
   - Virtualization: Proxmox VE สำหรับจัดการ Virtual Machines
   - Services: Portainer, GitLab Self-hosted, Verdaccio NPM Proxy, Private Docker Registry UI, EMQX MQTT Broker, MySQL Database, Nginx Reverse Proxy
   - Network: สคริปต์กำหนดค่า Switch, Router, Access Point และการคำนวณ Subnet IP
