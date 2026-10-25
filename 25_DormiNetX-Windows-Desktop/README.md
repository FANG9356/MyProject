# 25_DormiNetX-Windows-Desktop
[![Download Folder](https://img.shields.io/badge/Download-ZIP_Folder-238636?style=for-the-badge&logo=github)](https://download-directory.github.io/?url=https://github.com/FANG9356/MyProject/tree/main/25_DormiNetX-Windows-Desktop)
*ดาวน์โหลดเฉพาะโฟลเดอร์นี้เป็นไฟล์ ZIP (หรือ [ดาวน์โหลดผ่าน DownGit](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/FANG9356/MyProject/tree/main/25_DormiNetX-Windows-Desktop))*

ระบบบริหารจัดการหอพักแบบ Standalone สำหรับ Windows Desktop รวมเซิร์ฟเวอร์ Go และ UI บน Wails v2 พร้อมระบบคำนวณมิเตอร์น้ำ-ไฟและออกใบเสร็จแบบออฟไลน์

## ภาพถ่ายหน้าจอการทำงานจริง (Screenshot)
![DormiNetX Desktop Standalone](../assets/real_app_25_dorminetx.png)

## ภาพเคลื่อนไหวสาธิตการทำงาน (Demonstration)
![DormiNetX Desktop Demo](../assets/demo_25_dorminetx.gif)

## ผู้พัฒนา
Phakhaphon Sukmee

## คุณสมบัติหลัก
- ทำงานแบบ Standalone Executable บน Windows 10/11 x64 โดยไม่ต้องติดตั้ง Node.js หรือซอฟต์แวร์เสริม
- รันเซิร์ฟเวอร์ Go HTTP และฐานข้อมูล SQLite ฝังตัวในโปรแกรมเดียวแบบออฟไลน์ 100%
- รองรับโหมด Host Server (เครื่องแม่ข่าย) และ Client Terminal (เครื่องลูกข่ายค้นหา IP อัตโนมัติในวงแลน)
- ระบบคำนวณมิเตอร์น้ำ-ไฟและพิมพ์ใบแจ้งหนี้/ใบเสร็จรับเงินผ่าน Wails IPC PrintHtml
- ระบบสำรองและกู้คืนฐานข้อมูล SQLite Snapshot
- มีทั้งไฟล์รันเดี่ยว (Portable DormiNetX.exe) และตัวติดตั้งมาตรฐาน (DormiNetX-Installer.exe)

## โครงสร้างไฟล์สำคัญ
- `bin/DormiNetX.exe`: ไฟล์ปฏิบัติการแบบ Portable สำหรับ Windows x64 (30 MB)
- `bin/DormiNetX-Installer.exe`: ตัวติดตั้งโปรแกรมมาตรฐาน Windows NSIS Installer (13 MB)
- `wails_app/`: ซอร์สโค้ดโปรแกรม Desktop Native (Wails v2 + React Frontend)
- `backend-dorm/`: ซอร์สโค้ดเซิร์ฟเวอร์ Go และฐานข้อมูล SQLite
- `standalone_demo.html`: ตัวอย่างการใช้งานและจำลองหน้าต่างโปรแกรมแบบ Interactive
- `test_simulation.js`: สคริปต์ทดสอบการทำงานและคำนวณบิลของระบบ

## วิธีการทดสอบ
```bash
node test_simulation.js
```
