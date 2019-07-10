from qpt_v2 import*
import serial
import time
import math

ser = serial.Serial('/dev/ttyUSB0',9600)
qpt = serial.Serial(port='/dev/ttyUSB1',baudrate=9600,timeout=1)

min_cw_speed = b'\x02\x31\x00\x05\x00\x00\x00\x34\x03'
max_cw_speed = b'\x02\x31\x00\xFF\x00\x00\x00\xCE\x03'

min_cw_speed = b'\x02\x32\x00\x05\x00\x00\x00\x34\x03'
max_cw_speed = b'\x02\x32\x00\xFF\x00\x00\x00\xCE\x03'


STX = 0x02
ETX = 0x03
Cmd_Num = 0x32
msg_type = 0x31


def cw_rotation_speed():

    ang_rotation = input("enter a degree per second rotation between 0 and 32 in increments of 0.25 degrees: ")      
    y = int(2*(4*float(ang_rotation)-1)+1)
    lrc = msg_type^y
    move_msg = bytearray()
    move_msg.append(STX)
    move_msg.append(msg_type)
    move_msg.append(0)
    move_msg.append(y)
    move_msg.append(0)
    move_msg.append(0)
    move_msg.append(0)
    move_msg.append(lrc)
    move_msg.append(ETX)
    
    
    print(move_msg)
    qpt.write(move_msg)
    time.sleep(1)
    stop_move()
    #check_at_position()
    
cw_rotation_speed()    
    
    
    
'''
    x_1 = 10*x
    x_count = 0
    while True:
        x_1 = x_1 - 256
        x_count +=1
        if(x_1 < 0):
            x_1 = x_1 +256
            x_count-=1
            break
    y_1 = 10*y
    y_count = 0
    while True:
        y_1 = y_1 - 256
        y_count +=1
        if(y_1 < 0):
            y_1 = y_1 +256
            y_count-=1
            break    
    lrc = msg_type^x_1^x_count^y_1^y_count
'''
