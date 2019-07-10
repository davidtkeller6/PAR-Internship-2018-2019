#include <SoftwareSerial.h>

#define RxD 10 // Receiver Pin for Arduino(Transmitter on HC-05)
#define TxD 11 // Transmittor Pin for Arduino(Receiver on HC-05)

SoftwareSerial BTSerial(RxD, TxD);

String message = "-1";
int value1 = 0;
int value2 = 0;
int btn_value = 0;
int joypin1 = 0;
int joypin2 = 1;
int button_pin = 2;
int msg = 0;
String recv = "-1";
void setup()
{
  #ifndef ESP8266
  while (!Serial);     // will pause Zero, Leonardo, etc until serial console opens
  #endif
  BTSerial.flush();
  delay(500);
  Serial.begin(9600);   
  BTSerial.begin(9600);
  BTSerial.println("The controller has successfuly connected to the PC");
  delay(100); 
}

void loop()
{
  value1 = analogRead(joypin1);
  value2 = analogRead(joypin2);
  btn_value = analogRead(button_pin);
  Serial.println(value1);
  Serial.println(value2);
  Serial.println(btn_value);
  Serial.println("-----------------");
  if((value1 < 100) && (value2 < 100)){
    msg = 1;
  }
  else if((value1 > 800) && (value2 < 100)){
    msg = 2;
  }
  else if((value1 < 100) && (value2 > 800)){
    msg = 3;
  }
  else if((value1 > 800) && (value2 > 800)){
    msg = 4;
  }
  else if(value1 < 100){
    msg = 5;
  }
  else if(value1 > 800){
    msg = 6;
  }
  else if(value2 < 100){
    msg = 7;
  }
  else if(value2 > 800){
    msg = 8;
  }
  else if(btn_value == 0){
    msg = 9;
  }
  else{
    msg = 0;
  }
/*  
  while(recv == "-1")
  {
    recv = BTSerial.read();
    delay(100);
  }   
  recv = "-1";
*/
  BTSerial.print(msg);
  delay(100);

}
