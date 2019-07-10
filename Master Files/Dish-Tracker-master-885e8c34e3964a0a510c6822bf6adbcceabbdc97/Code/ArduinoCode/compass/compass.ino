#include <Wire.h>
#include "Adafruit_LSM303_U.h"
#include "Adafruit_Sensor.h"

Adafruit_LSM303_Accel_Unified accel = Adafruit_LSM303_Accel_Unified(54321);
Adafruit_LSM303_Mag_Unified mag = Adafruit_LSM303_Mag_Unified(12345);
const float Pi = 3.14159;
String x_val = "";
String y_val = "";
String z_val = "";
String msg = "";
void displaySensorDetails(void)
{
  sensor_t sensor;
  mag.getSensor(&sensor);
  delay(500);
}

void setup(void)
{
#ifndef ESP8266
  while (!Serial);     // will pause Zero, Leonardo, etc until serial console opens
#endif
  Serial.begin(9600);
  mag.enableAutoRange(true);
  if(!mag.begin())
  {
    Serial.println("Ooops, no LSM303 detected ... Check your wiring!");
    while(1);
  }
  displaySensorDetails();
}

void loop(void)
{
  /* Get new sensor events */
  sensors_event_t event;
  mag.getEvent(&event);
  sensors_event_t accevent;
  sensors_event_t magevent;
  accel.getEvent(&accevent);
  mag.getEvent(&magevent);

  /* Calculate the angle of the vector y,x */
  float heading = (atan2(magevent.magnetic.y,magevent.magnetic.x) * 180) / Pi;  // Normalize to 0-360 
  if (heading < 0)
  {
      heading = 360 + heading;
  }
  //Serial.println("%d,%d,%d",mag.raw.x, mag.raw.y, mag.raw.z);
  Serial.println(heading);
  //Serial.println("-------------------------------");
  //Serial.print("x: ");
  //Serial.print(magevent.magnetic.x); 
  //Serial.print(" ");
  //Serial.print(magevent.magnetic.y);
  //Serial.print(" ");
  //Serial.println(magevent.magnetic.z);
  delay(500);
}
