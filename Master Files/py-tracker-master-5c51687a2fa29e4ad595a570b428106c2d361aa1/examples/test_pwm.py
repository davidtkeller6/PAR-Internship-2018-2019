#!/usr/bin/env python
import wiringpi

# Set Up GPIO Pins.
wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(18,wiringpi.GPIO.PWM_OUTPUT)
wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
wiringpi.pwmSetClock(1920);wiringpi.pwmSetRange(200)

while True:
    try:
        pulse=input("\n   Enter a PWM: ")
        pulse=int(pulse)
        if(pulse>=10 and pulse<=20):
            wiringpi.pwmWrite(18,pulse)
        else:
            print("\n   Invalid value entered. Use any value from 10 to 20!")
    except KeyboardInterrupt:
        wiringpi.pwmWrite(18,15)
        exit()
