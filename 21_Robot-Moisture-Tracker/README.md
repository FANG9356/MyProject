# 21_Robot-Moisture-Tracker

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
