
#define led 9

int data=0;
void setup() {
 
  pinMode(led,OUTPUT);
  Serial.begin(38400); // Default communication rate of the Bluetooth module
}

void loop() {
 if(Serial.available() > 0){ // Checks data is  from the serial port
 data = Serial.read(); // Reads the data from the serial port
 analogWrite(led,data);
 delay(10);
 
 }
}
