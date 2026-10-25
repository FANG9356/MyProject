#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h> // เปลี่ยนมาใช้ Library สำหรับ BMP280

const char* ssid = "S20 FE Galax";       // ใส่ชื่อ WiFi ของคุณ
const char* password = "11111111"; // ใส่รหัสผ่าน WiFi

const char* mqtt_server = "10.249.89.113"; // IP ของ Server ที่รัน MQTT Broker
const int mqtt_port = 1883;                    // Port มาตรฐานของ MQTT
const char* mqtt_topic = "naphat_skill";           // Topic ที่ต้องการส่งข้อมูลไป

WiFiClient espClient;
PubSubClient client(espClient);

/**
 * ฟังก์ชันเชื่อมต่อ WiFi
 */
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

/**
 * ฟังก์ชันเชื่อมต่อ MQTT Broker
 */
void reconnect_mqtt() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000); // รอ 5 วินาทีก่อนลองใหม่
    }
  }
}

Adafruit_BMP280 bmp; // เปลี่ยนชื่อตัวแปรเป็น bmp เพื่อให้ตรงกับเซ็นเซอร์

unsigned long previousMillis = 0;
const long interval = 10000; // ส่งข้อมูลทุก 10 วินาที (10000 ms)



void setup() {
  Serial.begin(115200);
  Wire.begin(); // เริ่มต้น I2C (SDA=21, SCL=22 สำหรับ ESP32)

  setup_wifi(); // Begin using Wi-Fi
  client.setServer(mqtt_server, mqtt_port); // Begin using MQTT

  Serial.println(F("Initializing BMP280 sensor..."));
  
  if (!bmp.begin(0x76)) { 
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring!"));
    while (1) delay(10); // หยุดการทำงานถ้าไม่เจอ Sensor
  }
  
  Serial.println(F("Sensor found!"));
  Serial.println(F("------------------------------------"));
}

void loop() {
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop(); // MQTT client working

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {

    float temperature = bmp.readTemperature();       // องศาเซลเซียส
    float pressure = bmp.readPressure() / 100.0F;    // hPa

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
}