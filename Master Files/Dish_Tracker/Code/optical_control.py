import bluetooth
import time
import serial
import sys
from qpt_v2 import*

qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=1)
ard = serial.Serial(port='/dev/ttyACM1',baudrate=9600)
bd_addr = "00:21:13:02:4B:BD"
port = 1
sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((bd_addr, port))
print ('Connected')
sock.settimeout(20.0)

def read_compass_values():
    """Reads compass values from positioner"""
    pos_az = 0
    pos_el = 0
    ard.flushInput() #flush input of data throwing off the sync
    time.sleep(.2)
    #if(ard.inWaiting() > 0): 
       #x_raw = ard.readline()
    az_raw = ard.readline()
        #el_raw = ard.readline()
        #pos_x = int(x_raw)
    try:
        pos_az = float(az_raw)
        #pos_el = float(el_raw)
    except ValueError: #usually doesnt error twice
        ard.flushInput()
        time.sleep(.2)
        az_raw = ard.readline()
        pos_az = float(az_raw)
        
        #print(pos_x, pos_y, pos_z)
    print('Tracker:', pos_az)#, pos_el)
    return pos_az, pos_el

def read_scope_compass_values():
    char = ''
    msg_ar = [0,0]
    msg = ''
    temp_msg = ''
    i=0
    nothing=0
    sock.send('1')
    while True:
        char = sock.recv(1).decode()
        if(str(char) == '\r'):
            k=0
        elif(str(char) == '\n'):
            #msg_ar[i] = int(temp_msg)
            msg = float(temp_msg)
            temp_msg = ''
            i+=1
        else:
            temp_msg = temp_msg + str(char)
        if(i == 1):
            i=0
            #print(msg[0], msg[1], msg[2])
            break
    print('Scope: ' ,msg)
    return msg

def compare_values(p_az, p_el, s_az, s_el):
    """compares the values of scope with positioner"""
    az_diff = p_az - s_az    
    el_diff = p_el - s_el
    
    #print('Difference' , az_diff,el_diff)
    return az_diff, el_diff
    
def active_move(positioner_az, positioner_el, scope_az, scope_el):
    az_diff = abs(scope_az - positioner_az)
    #if(az_diff > 220):
        #az_diff = az_diff - 360
    az_neg = (scope_az < positioner_az)
    el_diff = scope_el - positioner_el
    if(az_neg is True and az_diff > 180):
        move(cw_msg)
    elif(az_neg is True and (az_diff > 4)):
        move(ccw_msg)
    elif(az_neg is False and az_diff > 180):
        move(ccw_msg)
    elif((az_neg is False) and (az_diff > 4)):
        move(cw_msg)
    else:
        stop_move()
    return az_diff


def move_size(positioner_az, positioner_el, scope_az, scope_el):
    az_diff = abs(scope_az - positioner_az)
    if(az_diff > 220):
        az_diff = az_diff - 360
    az_neg = (scope_az < positioner_az)
    el_diff = scope_el - positioner_el
    current_az , current_el = get_degrees('default')
    if(az_neg):
        move_az = current_az - az_diff
    else:
        move_az = current_az + az_diff
    print('Move to: ' , move_az)
    return az_diff , move_az


def can_move(d_az, d_el):
    """can move if there is more than a 10 degrees difference in position
        and within the range of the positioner"""
    A = (abs(d_az > 4) and (abs(d_el > 4)))
    B = (abs(d_az < 220)) and (abs(d_el < 84))
    return (A and B)
    
def optical_control():
    l = 45
    z = 0
    move_az=0
    move_el = 37
    while True:
       #print('----------------------------------')
        pos_az, pos_el = read_compass_values()
        scp_az = read_scope_compass_values()
        scp_el = 0
        el_change = 45
        active_move(pos_az, pos_el, scp_az, scp_el)
        """a_d, az_change = move_size(pos_az, pos_el, scp_az, scp_el)
        if(can_move(a_d, el_change)): 
            move_to_position(int(az_change), -37)
        #time.sleep(1)
        """

def main():    
    optical_control()
  

if __name__ == '__main__':
    main()
