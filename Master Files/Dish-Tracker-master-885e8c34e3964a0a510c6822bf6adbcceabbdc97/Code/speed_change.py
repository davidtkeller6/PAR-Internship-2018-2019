import serial
import time

qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=.1)

stop_msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'

pan_ang_speed = input('Enter pan speed: ')
tilt_ang_speed = input('Enter tilt speed: ')

cw_ccw = input('Enter cw or ccw: ')

if (cw_ccw == 'cw'):
    cw = True
else:
    cw = False

up_down = input('Enter up or down: ')

if (up_down == 'up'):
    up = True
else:
    up = False

if(cw is True):
    pan_speed = int(2*(4*float(pan_ang_speed)-1)+1)#clockwise message (odd number)
else:
    pan_speed = int(2*(4*float(pan_ang_speed)-1)) #counter-clockwise message (even number)

if(up is True):
    tilt_speed = int(2*(4*float(tilt_ang_speed)-1)+1)#clockwise message (odd number)
else:
    tilt_speed = int(2*(4*float(tilt_ang_speed)-1)) #counter-clockwise message (even number)
    
STX = 0x02
msg_type = 0x31
ETX = 0x03
lrc = msg_type^pan_speed^tilt_speed
move_msg = bytearray()
move_msg.append(STX)
move_msg.append(msg_type)
move_msg.append(0)
move_msg.append(pan_speed)
move_msg.append(tilt_speed)
move_msg.append(0)
move_msg.append(0)
move_msg.append(lrc)
move_msg.append(ETX)


qpt.write(move_msg)
time.sleep(5)
qpt.write(stop_msg)
        
qpt.close()
