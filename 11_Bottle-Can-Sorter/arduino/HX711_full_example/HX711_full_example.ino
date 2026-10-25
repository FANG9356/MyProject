#include "HX711.h"


const int LOADCELL_DOUT_PIN = A0;
const int LOADCELL_SCK_PIN = A1;

HX711 scale;

void setup() {
  Serial.begin(38400);
  Serial.println("HX711 Demo");

  Serial.println("Initializing the scale");


  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);

  Serial.println("Before setting up the scale:");
  Serial.print("read: \t\t");
  Serial.println(scale.read());

  Serial.print("read average: \t\t");
  Serial.println(scale.read_average(20));

  Serial.print("get value: \t\t");
  Serial.println(scale.get_value(5));

  Serial.print("get units: \t\t");
  Serial.println(scale.get_units(5), 1);

  scale.set_scale(2280.f);
  scale.tare();

  Serial.println("After setting up the scale:");

  Serial.print("read: \t\t");
  Serial.println(scale.read());

  Serial.print("read average: \t\t");
  Serial.println(scale.read_average(20));

  Serial.print("get value: \t\t");
  Serial.println(scale.get_value(5));

  Serial.print("get units: \t\t");
  Serial.println(scale.get_units(5), 1);

  Serial.println("Readings:");
}

void loop() {

  int units = static_cast<int>(scale.get_units());


  Serial.print("Weight (units): \t");
  Serial.println(units);

  scale.power_down();
  delay(500);
  scale.power_up();
}
