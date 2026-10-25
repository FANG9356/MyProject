#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>

Adafruit_BMP280 bmp;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  Serial.println(F("Initializing BMP280 sensor..."));

  if (!bmp.begin(0x76)) {
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring!"));
    while (1) delay(10);
  }

  Serial.println(F("Sensor found!"));
  Serial.println(F("------------------------------------"));
}

void loop() {
  float temperature = bmp.readTemperature();
  float pressure = bmp.readPressure() / 100.0F;

  if (isnan(temperature) || isnan(pressure)) {
    Serial.println(F("Failed to read from BMP sensor!"));
  } else {
    Serial.print(F("Temperature = "));
    Serial.print(temperature);
    Serial.println(F(" *C"));

    Serial.print(F("Pressure    = "));
    Serial.print(pressure);
    Serial.println(F(" hPa"));
    Serial.println(F("------------------------------------"));
  }

  delay(2000);
}
