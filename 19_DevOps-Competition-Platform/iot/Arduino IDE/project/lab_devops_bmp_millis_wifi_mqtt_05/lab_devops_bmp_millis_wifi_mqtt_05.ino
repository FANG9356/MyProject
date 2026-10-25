#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>

const char* ssid = "S20 FE Galax";
const char* password = "11111111";

const char* mqtt_server = "10.249.89.113";
const int mqtt_port = 1883;
const char* mqtt_topic = "naphat_skill";

WiFiClient espClient;
PubSubClient client(espClient);


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
      delay(5000);
    }
  }
}

Adafruit_BMP280 bmp;

unsigned long previousMillis = 0;
const long interval = 10000;


void setup() {
  Serial.begin(115200);
  Wire.begin();

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);

  Serial.println(F("Initializing BMP280 sensor..."));

  if (!bmp.begin(0x76)) {
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring!"));
    while (1) delay(10);
  }

  Serial.println(F("Sensor found!"));
  Serial.println(F("------------------------------------"));
}

void loop() {
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop();

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {

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
}
