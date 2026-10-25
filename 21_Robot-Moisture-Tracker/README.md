# 21_Robot-Moisture-Tracker
[![Download Folder](https://img.shields.io/badge/Download-ZIP_Folder-238636?style=for-the-badge&logo=github)](https://download-directory.github.io/?url=https://github.com/FANG9356/MyProject/tree/main/21_Robot-Moisture-Tracker)
*ดาวน์โหลดเฉพาะโฟลเดอร์นี้เป็นไฟล์ ZIP (หรือ [ดาวน์โหลดผ่าน DownGit](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/FANG9356/MyProject/tree/main/21_Robot-Moisture-Tracker))*

ระบบเว็บแอปพลิเคชันสำหรับติดตามพิกัดตำแหน่งหุ่นยนต์สำรวจดินและอ่านค่าความชื้นแบบเรียลไทม์ผ่านแผนที่ Leaflet

## ภาพถ่ายหน้าจอการทำงานจริง (Screenshot)
![Robot Moisture Map](../assets/real_hw_21_robot_moisture.png)

## ภาพเคลื่อนไหวสาธิตการทำงาน (Demonstration)
![Robot Moisture Tracker Demo](../assets/demo_21_robot_moisture.gif)

## ผู้พัฒนา
Phakhaphon Sukmee

## คุณสมบัติหลัก
- แสดงผลตำแหน่งพิกัด GPS หุ่นยนต์บนแผนที่โลกจริง OpenStreetMap
- แดชบอร์ดสรุปค่าพิกัด สถานะการทำงาน และระดับความชื้นในดิน
- รองรับการคลิกเลือกตำแหน่งเป้าหมายบนแผนที่เพื่อส่งคำสั่งพิกัดให้หุ่นยนต์เคลื่อนที่
- โครงสร้างข้อมูล JSON รองรับการซิงค์แบบเรียลไทม์กับ Firebase Realtime Database

## วิธีการทดสอบ
```bash
node test_simulation.js
```
