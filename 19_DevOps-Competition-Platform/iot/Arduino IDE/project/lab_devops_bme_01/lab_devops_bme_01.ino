#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

Adafruit_BME280 bme; // ใช้งาน I2C

void setup() {
  Serial.begin(115200);
  Wire.begin(); // เริ่มต้น I2C (SDA=21, SCL=22 สำหรับ ESP32)

  Serial.println(F("Initializing BME/BMP280 sensor..."));
  
  if (!bme.begin(0x76)) { 
    Serial.println(F("Could not find a valid BME/BMP280 sensor, check wiring!"));
    while (1) delay(10); // หยุดการทำงานถ้าไม่เจอ Sensor
  }
  
  Serial.println(F("Sensor found!"));
  Serial.println(F("------------------------------------"));
}

void loop() {
  float temperature = bme.readTemperature();       // องศาเซลเซียส
  float humidity = bme.readHumidity();             // %RH
  float pressure = bme.readPressure() / 100.0F;    // hPa

  if (isnan(temperature) || isnan(pressure)) {
    Serial.println(F("Failed to read from BME/BMP sensor!"));
  } else {
    if (isnan(humidity)) {
      humidity = 0.0; 
    }

    Serial.print(F("Temperature = "));
    Serial.print(temperature);
    Serial.println(F(" *C"));

    Serial.print(F("Humidity    = "));
    Serial.print(humidity);
    Serial.println(F(" %RH"));

    Serial.print(F("Pressure    = "));
    Serial.print(pressure);
    Serial.println(F(" hPa"));
    Serial.println(F("------------------------------------"));
  }

  delay(2000); 
}