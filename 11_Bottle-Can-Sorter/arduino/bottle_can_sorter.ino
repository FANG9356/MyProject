#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <Stepper.h>
#include "HX711.h"


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
int mea_previousState = LOW;

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

  myServo2.attach(7);
  myServo2.write(0);

  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale(2280.f);
  scale.tare();
}

void loop() {

  bool sen_currentState = digitalRead(sen);
  bool pox_currentState = digitalRead(pox);
  int mea_currentState = digitalRead(mea);

  unsigned long currentMillis = millis();


  if (mea_previousState != mea_currentState) {

    count_sen = 0;
    count_pox = 0;
    count_wei = 0;

    lcd.setCursor(10, 0);
    lcd.print("0        ");
    lcd.setCursor(10, 1);
    lcd.print("0        ");

  }
  mea_previousState = mea_currentState;


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


  sen_previousState = sen_currentState;
  pox_previousState = pox_currentState;


  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = (duration * 0.034) / 2;


  if (distance > 0 && distance < 70 && !isServoMoving) {
    Serial.print("Distance: ");
    Serial.println(distance);

    lastUltrasonicActivityTime = millis();
    lcd.backlight();

    isServoMoving = true;
    myServo.write(180);
    servoMoveTime = millis();
  }


  if (isServoMoving && millis() - servoMoveTime >= 3000) {
    myServo.write(0);
    isServoMoving = false;
  }


  if (millis() - lastUltrasonicActivityTime > ultrasonicInactivityThreshold) {
    lcd.noBacklight();
  }


  float currentReading = scale.get_units();
  if (currentReading < 0) {
    currentReading = 0;
  }


  float averageReading = scale.get_units(10);
  if (averageReading < 0) {
    averageReading = 0;
  }


  if (averageReading > 10) {

   lcd.setCursor(0, 0);
   lcd.print("Wei     :");
    myStepper.step(0);
      delay(1000);
      myStepper.step(stepsRight);
      delay(1000);
      myStepper.step(-stepsRight);
      delay(100);
    myServo2.write(180);
    delay(4000);
    myServo2.write(0);
    count_wei++;

    if (count_wei >= 10) {
      count_wei = 10;
      lcd.setCursor(10, 0);
      lcd.print("FULL    ");
  } else {

    lcd.setCursor(10, 0);
    lcd.print(count_wei);
    lcd.print("        ");
  }


  Serial.println();
  scale.power_down();
  delay(1000);
  scale.power_up();
  }
}
