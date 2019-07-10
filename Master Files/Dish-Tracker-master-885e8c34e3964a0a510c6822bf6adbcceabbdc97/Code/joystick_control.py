import bluetooth
import time
import serial
import sys
import qpt_v2


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
    while True:
        value = read_value()
        if(value == 1):
            qpt_v2.move(qpt_v2.up_ccw_msg)
        elif(value == 2):
            qpt_v2.move(qpt_v2.up_cw_msg)
        elif(value == 3):
            qpt_v2.move(qpt_v2.down_ccw_msg)
        elif(value == 4):
            qpt_v2.move(qpt_v2.down_cw_msg)
        elif(value == 5):
            qpt_v2.move(qpt_v2.ccw_msg)
        elif(value == 6):
            qpt_v2.move(qpt_v2.cw_msg)
        elif(value == 7):
            qpt_v2.move(qpt_v2.up_msg)
        elif(value == 8):
            qpt_v2.move(qpt_v2.down_msg)
        elif(value == 9):
            print ('At: {}'.format(qpt_v2.get_degrees('default')))
        else:
            qpt_v2.stop_move()
            

def quit_option():
    option = input()
    if(option == 'q' or option == 'Q'):
        print('Program Terminated')
        value[0] = 1
        exit()
    
def main():    
    joystick_control()
  

if __name__ == '__main__':
    main()
    
