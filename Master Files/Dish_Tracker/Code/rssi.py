#!/usr/bin/env python3
import socket
import serial
from time import sleep
from rssi_functions import *\

#STAND MESSAGES FROM rssi_functions FILE
# up_msg        - Up.... duh
# down_msg      - Down
# cw_msg        - Clockwise
# ccw_msg       - Counter-Clockwise
# up_cw_msg     - Up and Clockwise
# up_ccw_msg    - Up and Counter-Clockwise
# down_cw_msg   - Down and Clockwise
# down_ccw_msg  - Down and Counter-Clockwise

# Information for connection to USPR
TCP_IP_ADDR = "127.0.0.1"
TCP_PORT = 12345

# Defining Constands for Stand Limits(how far left, right, up and down i want it to go)
CCW_LIMIT = -210
CW_LIMIT = 210
UP_LIMIT = 85
DOWN_LIMIT = -85
     
'''  
======================================================== Testing ==========================================================================
======================================================== Testing ==========================================================================
======================================================== Testing ==========================================================================    
'''

#If the stand hits a soft limit, this will jog it in ech direction to unstick it.
#move(up_msg)
#sleep(.2)
#move(down_msg)
#sleep(.2)
#move(ccw_msg)
#sleep(.2)
#move(cw_msg)
#sleep(.2)
#stop_move()

def move_to_start():
    # Moves to starting point
    input_x = 2
    input_y = -65
    rec_x,rec_y = get_degrees('default')
    while (rec_x != input_x and rec_y != input_y):
        move_to_position(input_x,input_y)
        rec_x,rec_y = get_degrees('default')
    
# Function to establish connection to SDR      
cli = create_socket(TCP_IP_ADDR,TCP_PORT)

# List of messages
message = [up_msg,cw_msg,down_msg,ccw_msg] 

#Dictionary for dBm readings
dbm = get_dbm(cli)
print("STARTING DBM IS: ", dbm)
  
  
def track_energy():   
    ''' Main Loop '''
    move_to_start()
    threshold = .5
    delay = .5
    speed = 1
    for k in range(1,10000):
     
        for num in range(0,len(message)):
            dbm,num_of_loops = dbm_loop_direction(dbm,cli,delay,message[num])
            dbm = hold_pos(dbm,cli,delay,threshold)
     
            #if num_of_loops > 1:
            #    temp_msg = []
            #    count = 0
            #    while num < 4:
            #        temp_msg.append(message[num])
            #        num += 1
            #        count += 1
            #    num = 0
            #    while count < 4:
            #        temp_msg.append(message[num])
            #        count += 1
            #        num += 1
            #    message = temp_msg
            #    break
            
        # Stops stand if it approaches one of its limits.
        rec_x,rec_y = get_degrees('default')
        if(((rec_x + 1) > CW_LIMIT) or ((rec_x - 1) < CCW_LIMIT)):
            stop_move()
            print("*************  HORIZONTAL LIMIT APPROACHING, STOPPING   ***********")
            break
        if (((rec_y + 1) > UP_LIMIT) or ((rec_y -1) < DOWN_LIMIT)):
            stop_move()
            print("*************  VERTICAL LIMIT APPROACHING, STOPPING     ***********")
            break
    

def main():    
    track_energy
  

if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
     
