import bluetooth
import time
import serial
import sys
import qpt_v2
from rssi import *
from rssi_functions import *


print('Connecting...')
bd_addr = "00:21:13:02:59:1A"
port = 1
sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((bd_addr, port))
print ('Connected')
sock.settimeout(20)

def read_value():
    #sock.send('1')
    char = sock.recv(1).decode()
    return int(char)
    
def joystick_control(): 
    energy_flag = False
    while True:
        value = read_value()
        if(value == 1 and energy_flag is False):
            qpt_v2.move(qpt_v2.up_ccw_msg)
        elif(value == 2 and energy_flag is False):
            qpt_v2.move(qpt_v2.up_cw_msg)
        elif(value == 3 and energy_flag is False):
            qpt_v2.move(qpt_v2.down_ccw_msg)
        elif(value == 4 and energy_flag is False):
            qpt_v2.move(qpt_v2.down_cw_msg)
        elif(value == 5 and energy_flag is False):
            qpt_v2.move(qpt_v2.ccw_msg)
        elif(value == 6 and energy_flag is False):
            qpt_v2.move(qpt_v2.cw_msg)
        elif(value == 7 and energy_flag is False):
            qpt_v2.move(qpt_v2.up_msg)
        elif(value == 8 and energy_flag is False):
            qpt_v2.move(qpt_v2.down_msg)
        elif(value == 9):
            print ('At: {}'.format(qpt_v2.get_degrees('default')))
            if energy_flag is False:
                energy_flag = True
            else:
                energy_flag = False                   
        else:
            qpt_v2.stop_move()
        if(energy_flag is True):
            #do energy loop contents
            track_energy()    
        
    
def main():    
    joystick_control()
  

if __name__ == '__main__':
    main()

