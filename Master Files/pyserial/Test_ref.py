import time
import serial 
qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=1)
ard = serial.Serial(port='/dev/ttyACM0',baudrate=9600)

#1 directional moves
cw_msg = b'\x02\x31\x00\xA7\x00\x00\x00\x96\x03'
ccw_msg = b'\x02\x31\x00\x96\x00\x00\x00\xA7\x03'
up_msg = b'\x02\x31\x00\x00\x65\x00\x00\x54\x03'
down_msg = b'\x02\x31\x00\x00\x54\x00\x00\x65\x03'
#diagonal moves
up_cw_msg = b'\x02\x31\x00\xFB\xF9\x00\x00\x33\x03'
down_cw_msg = b'\x02\x31\x00\xF3\xF6\x00\x00\x34\x03'
up_ccw_msg = b'\x02\x31\x00\xF8\xF9\x00\x00\x30\x03'
down_ccw_msg = b'\x02\x31\x00\xFC\xFA\x00\x00\x37\x03'

stop_msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
#read from compass sensor
#determine which way to move bassed on the compass feedback

def read_compass_values():
    """Reads compass values"""
    values = 0
    return values #will probably be an array of numbers
print(ard.inWaiting())
while True:
    read_compass_values()
    num = ard.readline()
    print (num)
    #compare the compass values with "center" or "zero" values
    if():
        #move clockwise
        qpt.write(cw_msg)
    elif():
        #move counterclockwise
        qpt.write(ccw_msg)
    elif():
        #move up
        qpt.write(up_msg)
    elif():
        #move down
        qpt.write(down_msg)
    elif():
        #move clockwise and up
        qpt.write(cw_up_msg)
    elif():
        #move clockwise and down
        qpt.write(cw_down_msg)
    elif():
        #move counterclockwise and up
        qpt.write(ccw_up_msg)
    elif():
        #move counterclockwise and down
        qpt.write(ccw_down_msg)
    else:
        #do nothing / don't move
        qpt.write(stop_msg)
    feedback_msg = qpt.readline()
    #print(feedback)
