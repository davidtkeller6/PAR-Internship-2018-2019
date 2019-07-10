/*************************/
/* Connections to LM303  */
/* Arduino         LM303 */
/*  +3,3 VDC         Vcc   */
/*  GND            GND   */
/* Pin A4          SDA   */
/* Pin A5          SCL   */
/*************************/

#include <SoftwareSerial.h>
#include <Wire.h>
#include "Adafruit_Sensor.h"
#include "Adafruit_LSM303_U.h"
 
  #define RxD 10 // Receiver Pin for Arduino(Transmitter on HC-05)
  #define TxD 11 // Transmittor Pin for Arduino(Receiver on HC-05)
 
  /* Assign a unique ID to the tilt sensor at the same time */
  Adafruit_LSM303_Accel_Unified accel = Adafruit_LSM303_Accel_Unified(54321);
  Adafruit_LSM303_Mag_Unified mag = Adafruit_LSM303_Mag_Unified(12345);

  // Pi for calculations - not the raspberry type
const float Pi = 3.14159;
const int buttonPin = 2;
  //Sets the pins to Rx and TX software
  SoftwareSerial BTSerial(RxD, TxD);
String message = "-1";
int buttonState = 0;
// Display function -- Probably dont need  
void displaySensorDetails(void)
{
  sensor_t sensor;
  mag.getSensor(&sensor);
  delay(500);
}

 
  void setup()
  {
#ifndef ESP8266
  while (!Serial);     // will pause Zero, Leonardo, etc until serial console opens
#endif
   
    BTSerial.flush();
    delay(500);
    Serial.begin(9600);
   
    BTSerial.begin(9600);
    delay(100);

    /* Enable auto-gain */
    mag.enableAutoRange(true);

    /* Initialise the sensor */
    if(!mag.begin())
    {
     /* There was a problem detecting the LSM303 ... check your connections */
     Serial.println("Ooops, no LSM303 detected ... Check your wiring!");
     while(1);
    }

    /* Display some basic information on this sensor */
    displaySensorDetails();   
  }

void loop()
{
  buttonState = analogRead(buttonPin);
  //Serial.println(buttonState);
  if(buttonState > 1000){
    /* Get new sensor events */
    //sensors_event_t event;
    //mag.getEvent(&event);
    sensors_event_t accevent;
    sensors_event_t magevent;
    accel.getEvent(&accevent);
    mag.getEvent(&magevent);

    //Serial.print("Message is: ");
    //Serial.print(message);
    /*
    while(message == "-1")
    {
    message = BTSerial.read();
    delay(100);
    }   
    message = "-1";
    */
    float heading = (atan2(magevent.magnetic.y,magevent.magnetic.x) * 180) / Pi;  // Normalize to 0-360
   
    if (heading < 0)
    {
        heading = 360 + heading;
    }
    Serial.println(heading);
    BTSerial.println(heading);
    delay(500);
  }
  else{
    BTSerial.println("N");
  }
  
}

  
