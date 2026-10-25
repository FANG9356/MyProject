#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <Stepper.h>
#include "HX711.h"

// ตัวแปรเดิม (คงไว้เหมือนเดิม)
int motorSpeed = 10;
int stepsRight = 512;
int stepsLeft = 512;

Stepper myStepper(2048, 8, 10, 9, 11);
LiquidCrystal_I2C lcd(0x27, 16, 2);

unsigned long lastDetectionTime_sen = 0;
unsigned long lastDetectionTime_pox = 0;
const unsigned long detectionDelay = 1000;
const unsigned long checkDelay = 3000;

int pox = 5;
int sen = 6;

int mea = 1;
int mea_previousState = LOW; // เก็บสถานะก่อนหน้าของ mea

const int trigPin = A0;
const int echoPin = A1;
long duration;
int distance;

const int LOADCELL_DOUT_PIN = A2;
const int LOADCELL_SCK_PIN = A3;
HX711 scale;

int count_sen = 0;
int count_pox = 0;
int count_wei = 0;
int count_total = 0;

bool sen_previousState = LOW;
bool pox_previousState = LOW;
bool wei_previousState = LOW;

unsigned long lastUltrasonicActivityTime = 0;
const unsigned long ultrasonicInactivityThreshold = 1000000;

Servo myServo;
Servo myServo2;
bool isServoMoving = false;
unsigned long servoMoveTime = 0;

void setup() {
  Serial.begin(38400);
  myStepper.setSpeed(motorSpeed); 

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  pinMode(sen, INPUT);
  pinMode(pox, INPUT);

  pinMode(mea, INPUT);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Plastic :");
  lcd.setCursor(0, 1);
  lcd.print("Metal   :");
  lcd.setCursor(10, 0);
  lcd.print("0");
  lcd.setCursor(10, 1);
  lcd.print("0");

  myServo.attach(3);
  myServo.write(0);
  
  myServo2.attach(7); // เซอร์โวที่สอง
  myServo2.write(0); // หมุนไปที่ 0 องศาเริ่มต้น

  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale(2280.f); 
  scale.tare(); 
}

void loop() {
  // อ่านสถานะของเซ็นเซอร์
  bool sen_currentState = digitalRead(sen);
  bool pox_currentState = digitalRead(pox);
  int mea_currentState = digitalRead(mea);
  
  unsigned long currentMillis = millis();
    
  // ตรวจสอบการเปลี่ยนแปลงของ mea
  if (mea_previousState != mea_currentState) { 
    // เมื่อขา mea เปลี่ยนสถานะ
    count_sen = 0;
    count_pox = 0;
    count_wei = 0;
    // ล้างข้อความ "FULL" และรีเซ็ตหน้าจอ LCD
    lcd.setCursor(10, 0);
    lcd.print("0        ");
    lcd.setCursor(10, 1);
    lcd.print("0        ");
   //lcd.print(count_total); // แสดงผลรวมบน LCD
  }
  mea_previousState = mea_currentState; // อัปเดตสถานะของ mea

  // โค้ดตรวจจับ sen และ pox (คงเดิม)
  if (sen_previousState == 1 && sen_currentState == 0) {
    delay(checkDelay);
    bool updatedPoxState = digitalRead(pox);

    if (updatedPoxState == 1) {
      lcd.setCursor(0, 0);
      lcd.print("Plastic :");
      count_sen++;
      myStepper.step(0);
      delay(1000);
      myStepper.step(-stepsLeft);
      delay(1000);
      myStepper.step(stepsLeft);
      delay(100);

      if (count_sen >= 10) {
        count_sen = 10;
        lcd.setCursor(10, 0);
        lcd.print("FULL    ");
      } else {
        lcd.setCursor(10, 0);
        lcd.print(count_sen);
        lcd.print("        ");
      }
    } else if (updatedPoxState == 0) {
      lcd.setCursor(0, 1);
      lcd.print("Metal   :");
      count_pox++;
      myStepper.step(0);
      delay(1000);
      myStepper.step(stepsRight);
      delay(1000);
      myStepper.step(-stepsRight);
      delay(100);

      if (count_pox >= 10) {
        count_pox = 10;
        lcd.setCursor(10, 1);
        lcd.print("FULL    ");
      } else {
        lcd.setCursor(10, 1);
        lcd.print(count_pox);
        lcd.print("        ");
      }
    }
  }

  // บันทึกสถานะล่าสุดของเซ็นเซอร์
  sen_previousState = sen_currentState;
  pox_previousState = pox_currentState;

  // ส่วนโค้ดอัลตราโซนิกและเซอร์โว (ปรับปรุง)
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = (duration * 0.034) / 2;

  // ตรวจสอบระยะและหมุนเซอร์โวเมื่อระยะ < 70
  if (distance > 0 && distance < 70 && !isServoMoving) {
    Serial.print("Distance: ");
    Serial.println(distance);  // ตรวจสอบระยะใน Serial Monitor

    lastUltrasonicActivityTime = millis();
    lcd.backlight();

    isServoMoving = true;
    myServo.write(180);  // หมุนเซอร์โวไปที่มุม 180
    servoMoveTime = millis();
  }

  // รีเซ็ตเซอร์โวหลังจากหมุนไป 3 วินาที
  if (isServoMoving && millis() - servoMoveTime >= 3000) {
    myServo.write(0);  // หมุนกลับไปที่มุม 0
    isServoMoving = false;
  }

  // ปิดไฟหน้าจอ LCD เมื่อไม่ได้ใช้งานอัลตราโซนิก
  if (millis() - lastUltrasonicActivityTime > ultrasonicInactivityThreshold) {
    lcd.noBacklight();
  }

  // การอ่านค่าจาก load cell
  float currentReading = scale.get_units();
  if (currentReading < 0) {
    currentReading = 0; 
  }

  // Serial.print("one reading:\t");
  // Serial.print(currentReading, 1);
  // Serial.print("\t| average:\t");
  float averageReading = scale.get_units(10);
  if (averageReading < 0) {
    averageReading = 0; 
  }
  // Serial.print(averageReading, 1);

  // เพิ่มเงื่อนไขการแสดงผล
  if (averageReading > 10) {
   
   lcd.setCursor(0, 0);
   lcd.print("Wei     :");
    myStepper.step(0);
      delay(1000);
      myStepper.step(stepsRight);
      delay(1000);
      myStepper.step(-stepsRight);
      delay(100);
    myServo2.write(180);  // หมุนไปที่ 180 องศา
    delay(4000);           // รอ 4 วินาที
    myServo2.write(0);     // กลับมาที่ 0 องศา
    count_wei++;
    //Serial.print("\t | binary     1"); 
    if (count_wei >= 10) {
      count_wei = 10;
      lcd.setCursor(10, 0);
      lcd.print("FULL    ");
  } else {
    //Serial.print("\t | binary     0"); 
    lcd.setCursor(10, 0);
    lcd.print(count_wei);
    lcd.print("        ");
  }
    
  // count_total  = count_sen +  count_pox  +  count_wei; // คำนวณผลรวม
  // lcd.setCursor(0, 1);
  // lcd.print("Total   :");
  // lcd.print(count_total); // แสดงผลรวมบน LCD

  Serial.println();
  scale.power_down(); 
  delay(1000);
  scale.power_up();
  }
}
