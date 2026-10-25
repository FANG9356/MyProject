#define BLYNK_PRINT Serial
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <Servo.h>
#define BLYNK_TEMPLATE_ID "TMPL66T0DUYuF"
#define BLYNK_TEMPLATE_NAME "servo"
#define BLYNK_AUTH_TOKEN "YKPxUV6NXGpx_gIBb_uJFr3lsZiaqzF-"
Servo servo;

char auth[] = "YKPxUV6NXGpx_gIBb_uJFr3lsZiaqzF-"; //  your auth code 
char ssid[] = "H";  // ssid name 
char pass[] = "123456789"; // ssid password 

void setup()
{
  Serial.begin(9600);
  Blynk.begin(auth, ssid, pass);

  servo.attach(2); // NodeMCU D4 pin
  
 }
  
void loop()
{
  
  Blynk.run();
  
}
BLYNK_WRITE(V1)
{
   servo.write(param.asInt(60));
}