# My Projects

> **ผู้พัฒนา:** Phakhaphon Sukmee
> **GitHub Repository:** [FANG9356/MyProject](https://github.com/FANG9356/MyProject)

คลังรวบรวมโค้ดและโปรเจกต์ต่างๆ ที่ทำไว้ แต่ละโฟลเดอร์มีโค้ด ตัวอย่างการรัน และสคริปต์สำหรับทดสอบ

---

## สารบัญโปรเจกต์

| ลำดับ | โปรเจกต์ | หมวดหมู่ | คำสั่งรัน | URL | คำสั่งทดสอบ |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **01** | [`01_AI-WiFi-Sensing-Wall`](./01_AI-WiFi-Sensing-Wall) | AI & RF Sensing | `python3 ai_web_server.py` | `http://localhost:8050` | `python3 test_simulation.py` |
| **02** | [`02_Smart-Doc-AI`](./02_Smart-Doc-AI) | GenAI Agent | `docker compose up -d` | `http://localhost:5173` | `python3 test_simulation.py` |
| **03** | [`03_Tip-Desk-PromptPay`](./03_Tip-Desk-PromptPay) | FinTech / Web | `uvicorn main:app` & `npm run dev` | `http://localhost:5173` | `python3 test_simulation.py` |
| **04** | [`04_Club-Management-System`](./04_Club-Management-System) | Web Management | `cd backend && node server.js` | `http://localhost:3000` | `node test_simulation.js` |
| **05** | [`05_ATM-YOLOv8-Detector`](./05_ATM-YOLOv8-Detector) | Computer Vision | `python3 person_detector.py` | หน้าต่างกล้อง | `python3 test_simulation.py` |
| **06** | [`06_Karaoke-Streaming-System`](./06_Karaoke-Streaming-System) | Streaming Server | `python3 main.py` | `http://localhost:8000` (รีโมต: `/remote.html`) | `python3 test_simulation.py` |
| **07** | [`07_AdGuard-Time-Portal`](./07_AdGuard-Time-Portal) | Network & Admin | `node server.js` | `http://localhost:8080` (แอดมิน: `/admin.html`) | `node test_simulation.js` |
| **08** | [`08_System-Monitor-Desktop-App`](./08_System-Monitor-Desktop-App) | Desktop Utility | `.exe` (Win) หรือ `node server.js` | `http://localhost:3000` | `node test_simulation.js` |
| **09** | [`09_HomeServer-Infrastructure`](./09_HomeServer-Infrastructure) | Go, SQLite & React | `cd backend && go run .` | `http://localhost:8001` | `python3 test_simulation.py` |
| **10** | [`10_Music-Shuffle-AI`](./10_Music-Shuffle-AI) | AI Desktop Player | `python3 main.py` | หน้าต่างโปรแกรม Desktop | `python3 test_simulation.py` |
| **11** | [`11_Bottle-Can-Sorter`](./11_Bottle-Can-Sorter) | Embedded & IoT | `arduino/bottle_can_sorter.ino` | ฮาร์ดแวร์ / `sorter_sim.html` | `python3 test_simulation.py` |
| **12** | [`12_Smart-Plant-Watering`](./12_Smart-Plant-Watering) | Smart Agriculture | `arduino/blynk_valve_control.ino` | ฮาร์ดแวร์ / `watering_sim.html` | `python3 test_simulation.py` |
| **13** | [`13_General-Education-Web`](./13_General-Education-Web) | EdTech / Web | `open index.html` | `index.html` | `python3 test_simulation.py` |
| **14** | [`14_Computer-Quiz-System`](./14_Computer-Quiz-System) | Web Assessment | `open index.html` | `index.html` | `python3 test_simulation.py` |
| **15** | [`15_SD-Calculator-Python`](./15_SD-Calculator-Python) | Data Science GUI | `python3 sd.py` | หน้าต่างโปรแกรม Desktop | `python3 test_simulation.py` |
| **16** | [`16_Duplicate-File-Cleaner`](./16_Duplicate-File-Cleaner) | Desktop Utility | `python3 clean.py` | หน้าต่างโปรแกรม Desktop | `python3 test_simulation.py` |
| **17** | [`17_Grade-Calculator-Python`](./17_Grade-Calculator-Python) | Educational Tools | `python3 cal.py` | หน้าต่างโปรแกรม Desktop | `python3 test_simulation.py` |
| **18** | [`18_Neo-Web-Chat`](./18_Neo-Web-Chat) | Web & Wireless | `open index.html` / `python3 app.py` | `index.html` | `python3 test_simulation.py` |

---

## การรันชุดทดสอบ

ในโฟลเดอร์หลักมีสคริปต์ [`run_all_tests.sh`](./run_all_tests.sh) สำหรับรัน Simulation Test ของทั้ง 18 โปรเจกต์ สามารถทดสอบได้ด้วยคำสั่ง:
```bash
./run_all_tests.sh
```

---

## รายละเอียดโปรเจกต์

---

### 1. [01_AI-WiFi-Sensing-Wall](./01_AI-WiFi-Sensing-Wall) — ระบบตรวจจับการเคลื่อนไหวผ่านสัญญาณ WiFi (CSI)

> **เทคโนโลยี:** ESP32, WiFi CSI, Scikit-Learn, Python, HTML5 Dashboard

#### ภาพรวมโครงการ (Project Overview)
ระบบตรวจจับการเคลื่อนไหวและการหกล้มของบุคคลผ่านการวิเคราะห์สัญญาณคลื่นวิทยุ WiFi CSI จากบอร์ด ESP32 โดยใช้โมเดล Machine Learning (Random Forest) จำแนกรูปแบบคลื่นสัญญาณที่เปลี่ยนไป (ห้องว่าง, มีคนเดิน, หกล้ม) และแสดงผลบนหน้าเว็บแดชบอร์ด

#### ตัวอย่างหน้าจอ (Screenshots)
![AI WiFi Wall Dashboard](./assets/real_web_01_wifiwall.png)

![Live Simulation Demo](./assets/demo_01_wifi_sensing.gif)

#### แผนภาพการทำงาน (Architecture)
```mermaid
flowchart TD
  A[ESP32 Transmitter] -->|สัญญาณ WiFi 2.4GHz| B[กำแพง / สิ่งกีดขวาง]
  B --> C[การเคลื่อนไหวของบุคคล]
  C -->|คลื่นเกิดการกระเจิง| D[ESP32 Receiver]
  D -->|สกัดสัญญาณ CSI| E[Python UDP Collector]
  E -->|คำนวณ Amplitude & Phase| F[Random Forest Classifier]
  F -->|จำแนกผลลัพธ์| G{สถานะการตรวจจับ}
  G -->|ไม่มีการเคลื่อนไหว| H[ห้องว่าง]
  G -->|เคลื่อนไหวต่อเนื่อง| I[กำลังเดิน]
  G -->|แอมพลิจูดตกวูบฉับพลัน| J[แจ้งเตือนคนหกล้ม]
  H & I & J --> K[Web Dashboard: ai_index.html]
```

#### วิธีรันระบบ (How to Run)
1. **ติดตั้ง Dependencies:**
  ```bash
  cd 01_AI-WiFi-Sensing-Wall
  pip install scikit-learn pandas numpy joblib
  ```
2. **รันโหมดทดสอบจำลอง (Simulation Mode):**
  ```bash
  python3 test_simulation.py
  ```
3. **เปิดหน้า Web Dashboard:**
  ```bash
  python3 ai_web_server.py
  ```
  เปิดเบราว์เซอร์ที่: `http://localhost:8050`

---

### 2. [02_Smart-Doc-AI](./02_Smart-Doc-AI) — เครื่องมือค้นคว้าข้อมูลและร่างเอกสาร Word

> **เทคโนโลยี:** React, Tailwind CSS, Vite, FastAPI, Wikipedia API, DuckDuckGo, ArXiv API, python-docx, Docker

#### ภาพรวมโครงการ (Project Overview)
ระบบช่วยรวบรวมข้อมูลตามหัวข้อที่ต้องการจากแหล่งข้อมูลออนไลน์ (Wikipedia, ArXiv, Web Search) และจัดรูปแบบเป็นเอกสาร Word (.docx) พร้อมดาวน์โหลด

#### ตัวอย่างหน้าจอ (Screenshots)
![Smart Doc AI](./assets/real_web_02_smartdoc.png)

![Live Simulation Demo](./assets/demo_02_smart_doc.gif)

#### แผนภาพการทำงาน (Architecture)
```mermaid
flowchart LR
  A[ผู้ใช้กรอกหัวข้อ] --> B[React UI]
  B -->|REST API| C[FastAPI Backend]
  subgraph Data_Retrieval [ค้นคว้าข้อมูล]
    C --> D[Wikipedia API]
    C --> E[DuckDuckGo Search]
    C --> F[ArXiv API]
  end
  D & E & F --> G[Text Synthesis]
  G --> H[python-docx Formatter]
  H --> I[ไฟล์ Word .docx]
```

#### วิธีรันระบบ (How to Run)
* **รันผ่าน Docker Compose:**
  ```bash
  cd 02_Smart-Doc-AI
  docker compose up -d
  ```
  เปิดเบราว์เซอร์ที่: `http://localhost:5173`
* **รันแบบ Manual:**
  * Backend: `cd 02_Smart-Doc-AI/app && pip install -r requirements.txt && uvicorn main:app --reload --port 8000`
  * Frontend: `cd 02_Smart-Doc-AI/frontend && npm install && npm run dev`

---

### 3. [03_Tip-Desk-PromptPay](./03_Tip-Desk-PromptPay) — ระบบรับเงินบริจาค PromptPay พร้อมเสียงอ่านชื่อ

> **เทคโนโลยี:** React, TypeScript, Vite, FastAPI, SQLite, EMVCo QR Code, Web Speech API

#### ภาพรวมโครงการ (Project Overview)
ระบบรับบริจาค/ทิปผ่าน PromptPay QR Code ตามมาตรฐาน EMVCo รองรับการอัปเดตยอดเงินแบบเรียลไทม์ และอ่านชื่อผู้ส่งพร้อมข้อความผ่าน Text-to-Speech

#### ตัวอย่างหน้าจอ (Screenshots)
![Tip Desk](./assets/real_web_03_tipdesk.png)

![Live Simulation Demo](./assets/demo_03_tip_desk.gif)

#### แผนภาพการทำงาน (Architecture)
```mermaid
flowchart TD
  A[ผู้สนับสนุน] --> B[กรอกชื่อ + จำนวนเงิน + ข้อความ]
  B --> C[FastAPI Backend]
  C -->|คำนวณ Tag-Length-Value & CRC16| D[EMVCo PromptPay Payload]
  D --> E[สร้าง QR Code]
  E --> F[สแกนจ่ายเงินผ่านแอปธนาคาร]
  F --> G[บันทึกลง SQLite Database]
  G -->|Server-Sent Events| H[Live Donation Dashboard]
  H -->|Web Speech API| I[เสียงอ่านชื่อและข้อความ TTS]
```

#### วิธีรันระบบ (How to Run)
1. **Backend (FastAPI):**
  ```bash
  cd 03_Tip-Desk-PromptPay/backend
  pip install -r requirements.txt
  cp .env.example .env
  uvicorn main:app --reload --port 8000
  ```
2. **Frontend (React):**
  ```bash
  cd 03_Tip-Desk-PromptPay
  npm install
  npm run dev
  ```
  เปิดเบราว์เซอร์ที่: `http://localhost:5173`

---

### 4. [04_Club-Management-System](./04_Club-Management-System) — ระบบลงทะเบียนและเช็คชื่อสมาชิกชมรม

> **เทคโนโลยี:** Node.js, Express, SQLite, Tailwind CSS, JWT

#### ภาพรวมโครงการ (Project Overview)
เว็บแอปพลิเคชันสำหรับลงทะเบียนสมาชิกชมรม เช็คชื่อเข้าร่วมกิจกรรม และมีหน้าแอดมินสำหรับดูสถิติและรายชื่อสมาชิก

#### ตัวอย่างหน้าจอ (Screenshots)
| หน้าลงทะเบียน (`/register.html`) | หน้าเช็คชื่อ (`/attendance.html`) |
| :---: | :---: |
| ![Club Register UI](./assets/real_web_04_club_register.png) | ![Club Attendance UI](./assets/real_web_04_club_attendance.png) |


![Live Simulation Demo](./assets/demo_04_club_management.gif)

#### แผนภาพการทำงาน (Architecture)
```mermaid
flowchart TD
  A[สมาชิก] -->|กรอกข้อมูล| B[หน้าลงทะเบียน]
  B --> C[Express API]
  C -->|บันทึกข้อมูล| D[(SQLite Database)]
  E[ผู้ดูแลระบบ] -->|JWT Auth| F[หน้า Admin Panel]
  F --> G[เช็คชื่อ Attendance]
  G --> D
  F --> H[รายงานสถิติ]
```

#### วิธีรันระบบ (How to Run)
```bash
cd 04_Club-Management-System/backend
npm install
cp .env.example .env
node server.js
```
เปิดใช้งานที่พอร์ต `3000`:
* หน้าลงทะเบียน: `http://localhost:3000/register.html`
* หน้าเช็คชื่อ: `http://localhost:3000/attendance.html`
* หน้าแอดมิน: `http://localhost:3000/admin.html`

---

### 5. [05_ATM-YOLOv8-Detector](./05_ATM-YOLOv8-Detector) — ระบบตรวจจับบุคคลหน้าตู้ ATM ด้วย YOLOv8

> **เทคโนโลยี:** Python, OpenCV, YOLOv8

#### ภาพรวมโครงการ (Project Overview)
โปรแกรมตรวจจับบุคคลบริเวณหน้าตู้ ATM โดยใช้โมเดล YOLOv8 วิเคราะห์ภาพจากกล้องวงจรปิด บันทึกภาพ Snapshot เมื่อพบบุคคล และเก็บประวัติเวลาไว้ในไฟล์ JSON Log

#### ตัวอย่างหน้าจอ (Screenshots)
![Live Simulation Demo](./assets/demo_05_atm_detector.gif)

#### แผนภาพการทำงาน (Architecture)
```mermaid
flowchart LR
  A[กล้อง CCTV] -->|Video Stream| B[OpenCV Frame Capture]
  B --> C[YOLOv8 Neural Network]
  C -->|ตรวจจับ Class: Person| D{พบบุคคลในเฟรม?}
  D -->|ใช่| E[วาด Bounding Box & คำนวณพิกัด]
  E --> F[บันทึกภาพลง /snapshots]
  E --> G[บันทึก Timestamp ลง detection_log.json]
  D -->|ไม่ใช่| H[ประมวลผลเฟรมถัดไป]
```

#### วิธีรันระบบ (How to Run)
1. **ติดตั้ง Dependencies:**
  ```bash
  cd 05_ATM-YOLOv8-Detector
  pip install ultralytics opencv-python numpy
  ```
2. **รันผ่านกล้องเว็บแคม:**
  ```bash
  python3 person_detector.py
  ```
3. **หรือรันโหมดจำลอง (Simulation):**
  ```bash
  python3 test_simulation.py
  ```

---

### 6. [06_Karaoke-Streaming-System](./06_Karaoke-Streaming-System) — ระบบสตรีมมิ่งคาราโอเกะพร้อมรีโมตมือถือ

> **เทคโนโลยี:** FastAPI, yt-dlp, HTML5 Video, WebSocket, REST API

#### ภาพรวมโครงการ (Project Overview)
ระบบสตรีมมิ่งคาราโอเกะสำหรับเปิดเล่นเพลงบนหน้าจอหลัก และมีหน้ารีโมตผ่านเว็บสำหรับให้คนอื่นใช้มือถือค้นหาเพลงและจัดการคิวเพลงพร้อมกัน

#### ตัวอย่างหน้าจอ (Screenshots)
**1. หน้าจอหลักเล่นเพลง (`/index.html`):**
![Karaoke Player](./assets/real_web_06_karaoke_player.png)

**2. หน้ารีโมตควบคุมบนมือถือ (`/remote.html`):**
<p align="center">
  <img src="./assets/real_web_06_karaoke_remote.png" width="380" alt="Karaoke Remote UI" />
</p>


![Live Simulation Demo](./assets/demo_06_karaoke_streaming.gif)

#### แผนภาพการทำงาน (Architecture)
```mermaid
flowchart TD
  A[จอหลัก: /] -->|เล่นเพลงตามคิว| B[FastAPI Server]
  C[มือถือผู้ใช้ A: /remote] -->|ค้นหา & จองคิว| B
  D[มือถือผู้ใช้ B: /remote] -->|ค้นหา & แทรกคิว| B
  B -->|yt-dlp Engine| E[สตรีมมิ่งวิดีโอ]
  B -->|State Sync| A
  B -->|อัปเดตลำดับคิว| C & D
```

#### วิธีรันระบบ (How to Run)
1. **ติดตั้งและรันเซิร์ฟเวอร์:**
  ```bash
  cd 06_Karaoke-Streaming-System
  pip install fastapi uvicorn yt-dlp
  python3 main.py
  ```
2. **เปิดหน้าจอ:**
  * หน้าจอหลัก (Player): `http://localhost:8000`
  * หน้ารีโมตมือถือ (Remote): `http://localhost:8000/remote.html`

---

### 7. [07_AdGuard-Time-Portal](./07_AdGuard-Time-Portal) — ระบบจัดการเวลาอินเทอร์เน็ตผ่าน AdGuard Home API

> **เทคโนโลยี:** Node.js, Express, AdGuard Home REST API, SQLite, Node-Schedule

#### ภาพรวมโครงการ (Project Overview)
หน้าพอร์ทัลควบคุมการใช้งานอินเทอร์เน็ตของอุปกรณ์ในเครือข่าย โดยผู้ใช้กรอกรหัส PIN เพื่อเปิดใช้งานตามเวลาที่กำหนด และสั่งบล็อกระดับ DNS ผ่าน AdGuard Home API เมื่อหมดเวลา

#### ตัวอย่างหน้าจอ (Screenshots)
| หน้ากรอกรหัส PIN (`/index.html`) | หน้าแอดมินสร้างรหัส PIN (`/admin.html`) |
| :---: | :---: |
| ![AdGuard Portal Web UI](./assets/real_web_07_adguard_portal.png) | ![AdGuard Admin Web UI](./assets/real_web_07_adguard_admin.png) |


![Live Simulation Demo](./assets/demo_07_adguard_portal.gif)

#### แผนภาพการทำงาน (Architecture)
```mermaid
flowchart LR
  A[อุปกรณ์ในเครือข่าย] --> B[Time Portal Web Page]
  B -->|กรอกรหัส PIN| C[Express Server]
  C -->|ตรวจสอบรหัส| D[(SQLite Database)]
  C -->|Unblock IP| E[AdGuard Home DNS]
  E -->|เปิดใช้อินเทอร์เน็ต| A
  C -->|นับถอยหลัง| F{หมดเวลา?}
  F -->|ใช่| G[ส่งคำสั่ง Block IP]
```

#### วิธีรันระบบ (How to Run)
```bash
cd 07_AdGuard-Time-Portal
npm install
cp .env.example .env
node server.js
```
เปิดใช้งานที่พอร์ต `8080`:
* หน้ากรอก PIN: `http://localhost:8080/index.html`
* หน้าแอดมิน: `http://localhost:8080/admin.html`

---

### 8. [08_System-Monitor-Desktop-App](./08_System-Monitor-Desktop-App) — โปรแกรมมอนิเตอร์สถานะระบบคอมพิวเตอร์

> **เทคโนโลยี:** Node.js, Express, pkg

#### ภาพรวมโครงการ (Project Overview)
โปรแกรมมอนิเตอร์ทรัพยากรเครื่อง (CPU, RAM, Uptime) แสดงผลผ่านหน้าเว็บเบราว์เซอร์ โดยคอมไพล์เป็นไฟล์ .exe แบบ Standalone ใช้งานได้ทันทีโดยไม่ต้องติดตั้ง Node.js เพิ่มเติม

#### ตัวอย่างหน้าจอ (Screenshots)
![System Monitor Web UI](./assets/real_web_08_sysmonitor.png)


![Live Simulation Demo](./assets/demo_08_sys_monitor.gif)

#### แผนภาพการทำงาน (Architecture)
```mermaid
flowchart LR
  A[เปิดไฟล์ .exe] --> B[Node.js Standalone Runtime]
  B -->|อ่านค่า CPU, RAM, Uptime| C[System Metrics]
  B -->|เปิด Local Web Server| D[Localhost Web UI]
  D -->|แสดงผล Gauge และตัวเลข| E[ผู้ใช้งาน]
```

#### วิธีรันระบบ (How to Run)
* **บน Windows:**
  ดับเบิลคลิกไฟล์ `sys-monitor-app-win-x64.exe` ได้ทันที
* **บน macOS / Linux:**
  ```bash
  cd 08_System-Monitor-Desktop-App
  npm install
  node server.js
  ```
  เปิดเบราว์เซอร์ที่: `http://localhost:3000`

---

### 9. [09_HomeServer-Infrastructure](./09_HomeServer-Infrastructure) — HomeServer Services & Network Scanner

> **เทคโนโลยี:** Go, SQLite, React, Tailwind CSS, Docker

#### ภาพรวมโครงการ (Project Overview)
แดชบอร์ดรวบรวมทางเข้าบริการต่างๆ ในบ้าน และมีเครื่องมือสแกนหา IP อุปกรณ์ในเครือข่าย:
1. **Services Hub:** หน้ารวมทางเข้าและเช็กสถานะการทำงานของบริการภายในบ้าน เช่น Immich, Jellyfin, FileBrowser, Bitwarden, Memos
2. **Network Scanner:** ค้นหา IP และอุปกรณ์ที่เชื่อมต่ออยู่ในวง LAN เดียวกัน หรือระบุ Subnet เพื่อค้นหาข้ามวง VLAN พร้อมเช็กพอร์ตพื้นฐานที่เปิดอยู่ และบันทึกผลลง SQLite

#### ตัวอย่างหน้าจอ (Screenshots)
| Services Hub | Network Scanner |
| :---: | :---: |
| ![HomeServer Services Hub](./assets/real_web_09_homeserver.png) | ![Cross-VLAN Network Scanner](./assets/real_web_09_scanner.png) |


![Live Simulation Demo](./assets/demo_09_homeserver_scanner.gif)

#### แผนภาพการทำงาน (Architecture)
```mermaid
flowchart TD
  User[ผู้ใช้งานผ่านหน้าเว็บ] -->|REST API| GoServer[Go Backend Server: 8001]
  GoServer -->|Query / Save| DB[(SQLite Database)]
  
  subgraph Engine_Features [Go Backend Engine]
    GoServer -->|Goroutines| Scanner[Network Scanner]
    GoServer -->|Health Check| ServiceHub[Services Monitor]
  end

  Scanner -->|TCP Probe| Subnets[Subnets & VLANs]
  Subnets -->|Discovered Nodes| Scanner
  Scanner -->|Save Discovered Nodes| DB
```

#### วิธีรันระบบ (How to Run)
1. **Backend (Go):**
  ```bash
  cd 09_HomeServer-Infrastructure/backend
  go run .
  ```
2. **Frontend (React + Tailwind):**
  ```bash
  cd 09_HomeServer-Infrastructure/frontend
  npm install
  npm run dev
  ```
  *(หรือรันผ่าน Docker: `docker compose up -d --build`)*
  เปิดเบราว์เซอร์ที่: `http://localhost:8001`

---

### 10. [10_Music-Shuffle-AI](./10_Music-Shuffle-AI) — โปรแกรมเล่นเพลงเดสก์ท็อปพร้อมระบบค้นหาด้วยเสียงผ่าน AI (Whisper)

* **หมวดหมู่:** Desktop Application & AI Audio
* **เทคโนโลยี:** Python, PyQt6, faster-whisper, mutagen, yt-dlp

#### สรุปโปรเจกต์
โปรแกรมเล่นเพลงบนระบบปฏิบัติการเดสก์ท็อปที่พัฒนาด้วย PyQt6 เชื่อมต่อโมเดล faster-whisper เพื่อให้สามารถรับคำสั่งเสียงพูด (Speech-to-Text) ภาษาไทยและภาษาอังกฤษเพื่อค้นหาเพลงในคลังได้โดยตรงบนเครื่อง ตัวโปรแกรมรองรับการสร้างเพลย์ลิสต์ รายการโปรด การแสดงเนื้อเพลงแบบคาราโอเกะ (LRC Sync) และมีเครื่องมือค้นหาและฝังภาพปกเพลงอัตโนมัติผ่าน iTunes API และ YouTube

![Music Shuffle Desktop GUI](./assets/real_app_10_music_shuffle.png)


![Live Simulation Demo](./assets/demo_10_music_shuffle.gif)

#### สถาปัตยกรรมระบบ
```mermaid
graph TD
  User([User / Microphone]) -->|Voice Command| Whisper[faster-whisper Engine]
  Whisper -->|Transcribed Text| SearchEngine[Music Search Thread]
  SearchEngine -->|Matched Audio| Player[QMediaPlayer & QAudioOutput]
  Player -->|Playback Timing| LyricSync[LRC Lyric Sync]
  MetadataScraper[fetch_covers Pipeline] -->|ID3 APIC / covr| Player
```

#### วิธีรันระบบ (How to Run)
```bash
cd 10_Music-Shuffle-AI
pip install -r requirements.txt
python3 main.py
```

โหมดทดสอบด่วน (Quick Test):
```bash
python3 test_simulation.py
```

---

### 11. [11_Bottle-Can-Sorter](./11_Bottle-Can-Sorter) — เครื่องคัดแยกขวดพลาสติกและกระป๋องโลหะอัตโนมัติ

* **หมวดหมู่:** Embedded Systems & Robotics / Waste Management
* **เทคโนโลยี:** Arduino Uno, C++, Stepper Motor, Servo Motor, HX711 Load Cell, Inductive Sensor, Ultrasonic Sensor, I2C LCD

#### สรุปโปรเจกต์
ระบบคัดแยกขยะรีไซเคิลอัตโนมัติสำหรับขวดพลาสติกและกระป๋องเครื่องดื่มอลูมิเนียม ควบคุมด้วยบอร์ด Arduino Uno เซนเซอร์อัลตราโซนิกตรวจจับการเข้าใกล้เพื่อเปิดฝาถังอัตโนมัติ เซนเซอร์ตรวจจับโลหะแบบเหนี่ยวนำ (Inductive Proximity Sensor) จำแนกกระป๋องโลหะ และโหลดเซลล์ HX711 ตรวจสอบน้ำหนัก ขับเคลื่อนถาดคัดแยกสองทิศทางด้วย Stepper Motor และแสดงปริมาณขยะพร้อมแจ้งเตือนสถานะถังเต็มบนจอ LCD I2C 16x2

![Bottle Can Sorter Simulation](./assets/real_hw_11_bottle_sorter.png)

![Live Simulation Demo](./assets/demo_11_bottle_sorter.gif)

#### เอกสารประกอบโครงงาน
* รายงานโครงงานฉบับสมบูรณ์ (83 หน้า): [11_Bottle-Can-Sorter/docs/project_report_full.pdf](./11_Bottle-Can-Sorter/docs/project_report_full.pdf)
* แบบประเมินโครงงาน ทค.3 / ทค.5 และใบรับรอง: [11_Bottle-Can-Sorter/docs/](./11_Bottle-Can-Sorter/docs/)

#### วิธีรันระบบ (How to Run)
1. อัปโหลดเฟิร์มแวร์เข้าสู่ Arduino Uno:
   ```bash
   arduino-cli compile --fqbn arduino:avr:uno 11_Bottle-Can-Sorter/arduino/bottle_can_sorter.ino
   ```
2. รันโหมดทดสอบจำลอง (Simulation Mode):
   ```bash
   python3 11_Bottle-Can-Sorter/test_simulation.py
   ```

---

### 12. [12_Smart-Plant-Watering](./12_Smart-Plant-Watering) — เครื่องรดน้ำต้นไม้อัตโนมัติควบคุมระยะไกลด้วยมือถือ

* **หมวดหมู่:** IoT & Smart Agriculture
* **เทคโนโลยี:** ESP8266 NodeMCU, C++, Blynk IoT Platform, Soil Moisture Sensor, 4-Channel Relay, Solenoid Valve

#### สรุปโปรเจกต์
ระบบรดน้ำต้นไม้อัจฉริยะสำหรับแปลงเกษตรและอาคารที่อยู่อาศัย ควบคุมผ่านไมโครคอนโทรลเลอร์ NodeMCU ESP8266 และแอปพลิเคชัน Blynk บนสมาร์ตโฟน ตรวจวัดระดับความชื้นในดินแบบเรียลไทม์ และสั่งการเปิด-ปิดโซลินอยด์วาล์วน้ำผ่านโมดูลรีเลย์ 4 ช่อง พร้อมระบบตัดน้ำฉุกเฉินเมื่อรดน้ำต่อเนื่องเกินเวลาที่กำหนด

![Smart Plant Watering Simulation](./assets/real_hw_12_smart_plant.png)

![Live Simulation Demo](./assets/demo_12_smart_plant.gif)

#### เอกสารประกอบโครงงาน
* รายงานโครงงานฉบับสมบูรณ์ (99 หน้า): [12_Smart-Plant-Watering/docs/project_report_full.pdf](./12_Smart-Plant-Watering/docs/project_report_full.pdf)

#### วิธีรันระบบ (How to Run)
1. อัปโหลดเฟิร์มแวร์เข้าสู่ NodeMCU ESP8266:
   ```bash
   arduino-cli compile --fqbn esp8266:esp8266:nodemcuv2 12_Smart-Plant-Watering/arduino/blynk_valve_control.ino
   ```
2. รันโหมดทดสอบจำลอง (Simulation Mode):
   ```bash
   python3 12_Smart-Plant-Watering/test_simulation.py
   ```

---

### 13. [13_General-Education-Web](./13_General-Education-Web) — เว็บไซต์แนะนำการศึกษาประเภทวิชาสามัญ (Seniormath)

* **หมวดหมู่:** Web Application & Educational Technology
* **เทคโนโลยี:** HTML5, CSS3, JavaScript (ES6), Glassmorphism UI, MediaStream

#### สรุปโปรเจกต์
เว็บพอร์ทัลสื่อการเรียนรู้แบบตอบสนองสำหรับกลุ่มสาระวิชาสามัญ ครอบคลุมวิชาคณิตศาสตร์ ฟิสิกส์ ไฟฟ้าอิเล็กทรอนิกส์ และระบบเลขฐานคอมพิวเตอร์ มาพร้อมระบบแปลงเลขฐาน เครื่องคิดเลขวิทยาศาสตร์แบบกระจกฝ้า (Glassmorphism Calculator) และวิดีโอประกอบการเรียนรู้ในแต่ละหมวดวิชา

![General Education Web Portal](./assets/real_hw_13_education_web.png)

![Live Simulation Demo](./assets/demo_13_education_web.gif)

#### เอกสารหลักสูตรและเนื้อหา
* เอกสารหลักสูตรวิชาสามัญ: [13_General-Education-Web/docs/](./13_General-Education-Web/docs/)

#### วิธีรันระบบ (How to Run)
เปิดใช้งานผ่านเว็บเบราว์เซอร์:
```bash
open 13_General-Education-Web/index.html
```
รันชุดทดสอบความสมบูรณ์ของโครงสร้างเว็บ:
```bash
python3 13_General-Education-Web/test_simulation.py
```

---

### 14. [14_Computer-Quiz-System](./14_Computer-Quiz-System) — เว็บไซต์ทำแบบทดสอบพื้นฐานคอมพิวเตอร์

* **หมวดหมู่:** Web Application & Educational Assessment
* **เทคโนโลยี:** Vanilla HTML5, CSS3, JavaScript, JSON Database

#### สรุปโปรเจกต์
ระบบแบบทดสอบออนไลน์วิชาพื้นฐานคอมพิวเตอร์ เชื่อมต่อคลังข้อสอบแบบ JSON จำนวน 400 ข้อ ครอบคลุมทั้งฮาร์ดแวร์ ซอฟต์แวร์ เครือข่าย และความปลอดภัย มีระบบบันทึกและตรวจสอบข้อมูลผู้สอบ ระบบป้องกันการคัดลอกข้อความ และโมดัลประเมินผลคะแนนคำนวณร้อยละและคะแนนตัดเกรดอัตโนมัติ

![Computer Quiz System](./assets/real_hw_14_computer_quiz.png)

![Live Simulation Demo](./assets/demo_14_computer_quiz.gif)

#### เอกสารคลังข้อสอบ
* เอกสารคลังข้อสอบ 400 ข้อ: [14_Computer-Quiz-System/docs/quiz_question_bank_summary.md](./14_Computer-Quiz-System/docs/quiz_question_bank_summary.md)

#### วิธีรันระบบ (How to Run)
เปิดใช้งานผ่านเว็บเบราว์เซอร์:
```bash
open 14_Computer-Quiz-System/index.html
```
รันชุดทดสอบคลังข้อสอบและการคำนวณคะแนน:
```bash
python3 14_Computer-Quiz-System/test_simulation.py
```

---

### 15. [15_SD-Calculator-Python](./15_SD-Calculator-Python) — โปรแกรมคำนวณค่า S.D. ด้วย Python

* **หมวดหมู่:** Desktop Application & Statistics
* **เทคโนโลยี:** Python 3, Tkinter, ttk, NumPy, PyInstaller

#### สรุปโปรเจกต์
โปรแกรมประยุกต์บนเดสก์ท็อปสำหรับประมวลผลข้อมูลแบบสอบถามและแบบประเมินความพึงพอใจการใช้งาน ผู้ใช้สามารถกำหนดจำนวนกลุ่มตัวอย่างและจำนวนข้อคำถามเพื่อสร้างตารางกรอกคะแนนแบบไดนามิก โปรแกรมประมวลผลคะแนนรวม ค่าเฉลี่ย ส่วนเบี่ยงเบนมาตรฐาน (S.D.) และสัมประสิทธิ์การแปรผัน (C.V. %) แสดงผลบนตาราง Treeview

![SD Calculator Desktop GUI](./assets/real_hw_15_sd_calculator.png)

![Live Simulation Demo](./assets/demo_15_sd_calculator.gif)

#### เอกสารคู่มือทางสถิติ
* คู่มือสูตรการคำนวณทางสถิติ: [15_SD-Calculator-Python/docs/statistics_formula_manual.md](./15_SD-Calculator-Python/docs/statistics_formula_manual.md)

#### วิธีรันระบบ (How to Run)
```bash
python3 15_SD-Calculator-Python/sd.py
```
รันชุดทดสอบการประมวลผลสถิติ:
```bash
python3 15_SD-Calculator-Python/test_simulation.py
```

---

### 16. [16_Duplicate-File-Cleaner](./16_Duplicate-File-Cleaner) — โปรแกรมค้นหาและลบไฟล์ซ้ำ ด้วย Python

* **หมวดหมู่:** Desktop Application & Storage Optimizer
* **เทคโนโลยี:** Python 3, CustomTkinter, hashlib (SHA-256), Dark Mode

#### สรุปโปรเจกต์
โปรแกรมยูทิลิตี้สำหรับค้นหาและกำจัดไฟล์ซ้ำซ้อนภายในเครื่องคอมพิวเตอร์ ใช้สถาปัตยกรรมคัดกรอง 2 ชั้น โดยตรวจสอบขนาดไฟล์ก่อน แล้วจึงคำนวณแฮช SHA-256 แบบแบ่งบล็อก 64 KB เพื่อความเร็วสูงสุดและประหยัดแรม ผู้ใช้สามารถเลือกไฟล์ที่ต้องการลบผ่าน Checkbox พร้อมระบบยืนยันความปลอดภัยก่อนลบข้อมูล

![Duplicate File Cleaner GUI](./assets/real_hw_16_duplicate_cleaner.png)

![Live Simulation Demo](./assets/demo_16_duplicate_cleaner.gif)

#### เอกสารสถาปัตยกรรม
* รายละเอียดขั้นตอนวิธีตรวจจับไฟล์ซ้ำ: [16_Duplicate-File-Cleaner/docs/duplicate_detection_algorithm.md](./16_Duplicate-File-Cleaner/docs/duplicate_detection_algorithm.md)

#### วิธีรันระบบ (How to Run)
```bash
python3 16_Duplicate-File-Cleaner/clean.py
```
รันชุดทดสอบการจำลองค้นหาและลบไฟล์ซ้ำ:
```bash
python3 16_Duplicate-File-Cleaner/test_simulation.py
```

---

### 17. [17_Grade-Calculator-Python](./17_Grade-Calculator-Python) — โปรแกรมคำนวณเกรด ด้วย Python (GPA & GPAX)

* **หมวดหมู่:** Desktop Application & Educational Utilities
* **เทคโนโลยี:** Python 3, CustomTkinter, Weighted Average Algorithm

#### สรุปโปรเจกต์
โปรแกรมคำนวณแต้มคะแนนเฉลี่ยรายภาคเรียน (GPA) และผลการเรียนเฉลี่ยสะสมทุกภาคเรียน (GPAX) พัฒนาด้วย CustomTkinter ในธีมสีมืด แปลงคะแนนดิบ 0-100 เป็นเกรด 8 ระดับตามมาตรฐานการศึกษา พร้อมระบบเพิ่มรายวิชาแบบไดนามิกและการตรวจสอบความถูกต้องของข้อมูล

![Grade Calculator Desktop GUI](./assets/real_hw_17_grade_calculator.png)

![Live Simulation Demo](./assets/demo_17_grade_calculator.gif)

#### เอกสารคู่มือเกณฑ์การตัดเกรด
* คู่มือเกณฑ์มาตรฐานการคำนวณเกรด: [17_Grade-Calculator-Python/docs/grading_system_manual.md](./17_Grade-Calculator-Python/docs/grading_system_manual.md)

#### วิธีรันระบบ (How to Run)
```bash
python3 17_Grade-Calculator-Python/cal.py
```
รันชุดทดสอบการตัดเกรดและสูตรคำนวณ:
```bash
python3 17_Grade-Calculator-Python/test_simulation.py
```

---

### 18. [18_Neo-Web-Chat](./18_Neo-Web-Chat) — เว็บไซต์คุยแชทออนไลน์ และระบบแชทออฟไลน์ BLE

* **หมวดหมู่:** Web Application & Wireless Networking
* **เทคโนโลยี:** HTML5, Tailwind CSS, JavaScript, Firebase Realtime Database, Web Bluetooth API, Python, Bleak, asyncio

#### สรุปโปรเจกต์
ระบบส่งข้อความสื่อสารสองโหมด ประกอบด้วยเว็บแอปพลิเคชันสไตล์ Neo-Brutalism รองรับการส่งข้อความผ่าน Wi-Fi คลาวด์แบบเรียลไทม์ และการสลับเป็นโหมดออฟไลน์เพื่อสื่อสารผ่านคลื่นสัญญาณ Bluetooth Low Energy (BLE) กับไมโครคอนโทรลเลอร์ ESP32 ในระยะใกล้ พร้อมด้วยไคลเอนต์เดสก์ท็อป Python ควบคุมการเชื่อมต่อแบบอะซิงโครนัส

![Neo Web Chat](./assets/real_hw_18_web_chat.png)

![Live Simulation Demo](./assets/demo_18_web_chat.gif)

#### เอกสารสถาปัตยกรรมและโปรโตคอล
* รายละเอียดสถาปัตยกรรมและ GATT Profile: [18_Neo-Web-Chat/docs/chat_architecture_and_protocol.md](./18_Neo-Web-Chat/docs/chat_architecture_and_protocol.md)

#### วิธีรันระบบ (How to Run)
เปิดเว็บแอปพลิเคชัน:
```bash
open 18_Neo-Web-Chat/index.html
```
รันไคลเอนต์เดสก์ท็อป Bluetooth:
```bash
python3 18_Neo-Web-Chat/app.py
```
รันชุดทดสอบโครงสร้างระบบแชทและโปรโตคอล BLE:
```bash
python3 18_Neo-Web-Chat/test_simulation.py
```

---

## ข้อมูลผู้พัฒนา
* **ชื่อ-นามสกุล:** Phakhaphon Sukmee
* **GitHub:** [@FANG9356](https://github.com/FANG9356)
* **Repository:** [https://github.com/FANG9356/MyProject](https://github.com/FANG9356/MyProject)

