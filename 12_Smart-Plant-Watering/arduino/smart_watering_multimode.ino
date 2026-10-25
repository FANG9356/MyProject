#define BLYNK_PRINT Serial
#define BLYNK_TEMPLATE_ID "TMPL6irqm_dWM"
#define BLYNK_TEMPLATE_NAME "skibidi"
#define BLYNK_AUTH_TOKEN "dziwUiXJ1qLKLJlSBIHsLXu0WLS3VGt4"
#include <Servo.h>
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>

char auth[] = "dziwUiXJ1qLKLJlSBIHsLXu0WLS3VGt4";
char ssid[] = "H";
char pass[] = "123456789";
Servo servo;
int servoPosition = 0;

void setup() {
  Blynk.begin(auth, ssid, pass);
  servo.attach(D5);
  servo.write(servoPosition);  // ไม่จำเป็นต้องใช้ myservo.write(servoPosition);
}

void loop() {
  Blynk.run();
}

BLYNK_WRITE(V1) {
  int servoPosition = param.asInt();
  servo.write(servoPosition);
}

BLYNK_WRITE(V2) {
  int buttonState = param.asInt();
  if (buttonState == 1) {
    servoPosition = 90;
    servo.write(servoPosition);
    delay(1000);
    
  }
  else{servoPosition = 0;
    servo.write(servoPosition);}
}
BLYNK_WRITE(V0) {
  int buttonState = param.asInt();
  if (buttonState == 1) {
    servoPosition = 180;
    servo.write(servoPosition);
    delay(1000);
    servoPosition = 0;
  servo.write(servoPosition);
  }
}
