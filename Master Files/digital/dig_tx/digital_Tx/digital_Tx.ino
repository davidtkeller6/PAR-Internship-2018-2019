
#define button 8
int buttonState = 0;

void setup() {
  pinMode(button, INPUT);
  Serial.begin(38400); // Default communication rate of the Bluetooth module
}

void loop() {
 delay(100);
 buttonState = digitalRead(button);
 if (buttonState == HIGH) {
   Serial.print('1'); // Sends '1' to serialout
 }
 else {
   Serial.print('0');
 }  
}
