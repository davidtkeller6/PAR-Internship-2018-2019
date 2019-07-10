import sys
import serial
import time

ser = serial.Serial('/dev/ttyUSB0',9600)

while True:

    line = ser.readline().decode()
    print (line)


