#!/usr/bin/env python3
import serial

''' 
    quick script to stop movement of stand in case it decides to go haywire during testing
    Normally if your code breaks in a way that the stand starts to rotate without stopping, it
    will rotate till it hits one of its limits, and obviously stop mechanically, but for some 
    reason in the software it will not accept any command after it hits its limit. Most likely 
    this is due to the code that broke it is still trying to be sent until it completes, so it 
    wont accept any new command until the previous one is fufilled. This little script stops it
    if it starts to go out of control.
'''

#open connection for mount
qpt = serial.Serial(port='/dev/ttyUSB1',baudrate=9600,timeout=.1)
print("\nChecking connection to Mount \n")
if (qpt.isOpen() == 1):
    print("Connection Successful, stopping this wackamole.\n")
    

    
def stop_move():
    stop_msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03' #stop/don't move
    qpt.write(stop_msg)
    
stop_move()    
