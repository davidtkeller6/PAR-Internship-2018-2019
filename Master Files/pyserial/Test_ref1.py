import time
import serial 
#qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=1)
ard = serial.Serial(port='/dev/ttyACM0',baudrate=9600)
print(ard.inWaiting())
while True:
    num = ard.readline()
    print (float(num))


