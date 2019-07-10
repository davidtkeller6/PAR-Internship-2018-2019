from qpt_v2 import*
import serial
import time
import math

min_cw_speed = b'\x02\x31\x00\x05\x00\x00\x00\x34\x03'
max_cw_speed = b'\x02\x31\x00\xFF\x00\x00\x00\xCE\x03'

min_cw_speed = b'\x02\x32\x00\x05\x00\x00\x00\x34\x03'
max_cw_speed = b'\x02\x32\x00\xFF\x00\x00\x00\xCE\x03'


STX = 0x02
ETX = 0x03
Cmd_Num = 0x32
lrc = msg_type^x_1^x_count^y_1^y_count

def cw_rotation_speed():

    x = 1
    
    ang_rotation = float(input("enter a degree per second rotation between 0 and 32 in increments of 0.25 degress"))
    if(ang_rotation < 0 or ang_rotation > 32):
        ang_rotation = float(input("Please enter and angle between 0 and 32 in increments of 0.25 degress"))
    else:
        y = ang_rotation/0.25
        y -= 1
        y*2
        x += y
        hex(x)
            
    
    move_msg = bytearray()
    move_msg.append(STX)
    move_msg.append(Cmd_Num)
    move_msg.append(0)
    move_msg.append(x)
    move_msg.append(0)
    move_msg.append(0)
    move_msg.append(0)
    move_msg.append(lrc)
    move_msg.append(ETX)
    
    qpt.write(move_msg)
    check_at_position()
    
