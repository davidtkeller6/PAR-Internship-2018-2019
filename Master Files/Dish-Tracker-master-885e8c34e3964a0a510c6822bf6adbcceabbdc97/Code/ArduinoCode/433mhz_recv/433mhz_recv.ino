#include <SoftwareSerial.h>

#define Rx 2
#define Tx 3

#define pinRx 0
#define pinTx 1

SoftwareSerial mySerial(Rx,Tx);
/*
float altitude = 2100;
float GPS [] = {43.210630,-75.33652};
float x = -75.407593 + random(-10,10)/10000000.000000 ;
float y = 43.220735 + random(-10,10)/10000000.000000;
float GPS [] = {y,x};
float altitude = random(0, 3000);
*/
String read_str = " ";
char c = ' ';
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  mySerial.begin(9600);
  delay(100);
}

void loop() {
  Serial.print("In looooop");
 
 while (Serial.available()) {
    delay(100);  //delay to allow buffer to fill
    //Serial.println("Atempted");
    c = Serial.read();
    read_str = read_str + c;
    if(c == '\n'){
      Serial.println(read_str);
      read_str = " ";
    }
    delay(100);
  }
  Serial.println("No rx");
  //delay(100);
 
}
