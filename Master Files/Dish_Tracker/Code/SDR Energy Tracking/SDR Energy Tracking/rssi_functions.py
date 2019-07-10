#!/usr/bin/env python3
import serial
import socket
from time import sleep
import time

# USING THIS FILE WITH ---"rssi.py"---
# Includes a whole bunch of info and functions needed to control the mount for
# the dish tracker. 

#open connection for mount
qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=.1)
print("\nChecking connection to Stand \n")
if (qpt.isOpen() == 1):
    print("Connection Successful!\n")
    
#==================================================================================================================================
#==================================================================================================================================    
#====================================        Software Radio Connections       =====================================================
#================================================================================================================================== 
#==================================================================================================================================  

#Establishes Connection to SDR
def create_socket(TCP_IP_ADDR,TCP_PORT):
    try:
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sock.bind((TCP_IP_ADDR,TCP_PORT));sock.listen(1)
        cli,addr=sock.accept()
        print("Connected.")
    except KeyboardInterrupt:
        sock.close()
        print("\n   Closing...\n\n")
        exit()
    except (socket.error,OSError):
        sock.close()
        print("\n   Check IP Address for TCP Socket.")
        print("   Expected IP is",TCP_IP_ADDR,"\n")
        exit()
    return(cli)

#Grabs dbm reading from horn and returns
def get_dbm(client):
    client.send('horn'.encode('utf-8'))
    rssi,addr2=client.recvfrom(7)
    rssi=rssi.decode('utf-8')
    rssi=float(rssi)
    #print("dBm: ",rssi)
    #sleep(.01) 
    return(rssi)
    
    
#==================================================================================================================================
#==================================================================================================================================    
#====================================              Stand Commands             =====================================================
#================================================================================================================================== 
#==================================================================================================================================
# Movement messages are byte arrays, passed to the mount as such.
# To change speed of any of these stand commands, change the hex value to a lower number, 
# but keeping it odd or even depending on what it currently is. The stand incrementes numbers
# by 4, starting at 4(min) for even and 5(min) for odd. So the next speed in the sequence would
# be 8 and 9 respectively all the way till 254 and 255. 
# ODD hex numbers = Clockwise for pan, Up for tilt
# EVEN hex numbers = Counter-Clockwise for pan, Down for tilt
# FORMAT: STX\CMD_NUM\00\PAN\TILT\00\00\LRC\ETX
# STX, CMD_NUM and ETX are constants (CMD_NUM changes for other commands)
# STX     = x02
# CMD_NUM = x31
# ETX     = x03
# LRS is the XOR of(CMD_NUM, PAN and TILT)

''' STAND COMMANDS'''
# Stop command never changes so we can just write it in.
stop_msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03' #stop/don't move

# Defining Constants for Stand Command Input
stx = 0x02
cmd_num = 0x31
etx = 0x03
#These commands are created in byte arrays so that we can access their elements
# to change the speed of them if desired.
#============================================================
#up_ccw_msg = b'\x02\x31\x00\xFE\xFF\x00\x00\x30\x03' #up and counter clockwise
up_ccw_msg = bytearray()
up_ccw_msg.append(stx)
up_ccw_msg.append(cmd_num)
up_ccw_msg.append(0)
up_ccw_msg.append(0xFE)
up_ccw_msg.append(0xFF)
up_ccw_msg.append(0)
up_ccw_msg.append(0)
up_ccw_msg.append(0x30)
up_ccw_msg.append(etx)
#============================================================
#up_cw_msg = b'\x02\x31\x00\xFF\xFF\x00\x00\x31\x03' #up and clockwise 
up_cw_msg = bytearray()
up_cw_msg.append(stx)
up_cw_msg.append(cmd_num)
up_cw_msg.append(0)
up_cw_msg.append(0xFF)
up_cw_msg.append(0xFF)
up_cw_msg.append(0)
up_cw_msg.append(0)
up_cw_msg.append(0x31)
up_cw_msg.append(etx)
#============================================================
#down_ccw_msg = b'\x02\x31\x00\xFE\xFE\x00\x00\x31\x03' #down and counter clockwise
down_ccw_msg = bytearray()
down_ccw_msg.append(stx)
down_ccw_msg.append(cmd_num)
down_ccw_msg.append(0)
down_ccw_msg.append(0xFE)
down_ccw_msg.append(0xFE)
down_ccw_msg.append(0)
down_ccw_msg.append(0)
down_ccw_msg.append(0x31)
down_ccw_msg.append(etx)
#============================================================
#down_cw_msg = b'\x02\x31\x00\xFF\xFE\x00\x00\x30\x03' #down and clockwise
down_cw_msg = bytearray()
down_cw_msg.append(stx)
down_cw_msg.append(cmd_num)
down_cw_msg.append(0)
down_cw_msg.append(0xFF)
down_cw_msg.append(0xFE)
down_cw_msg.append(0)
down_cw_msg.append(0)
down_cw_msg.append(0x30)
down_cw_msg.append(etx)
#============================================================
#cw_msg = b'\x02\x31\x00\xFF\x00\x00\x00\xCE\x03' #clockwise
cw_msg = bytearray()
cw_msg.append(stx)
cw_msg.append(cmd_num)
cw_msg.append(0)
cw_msg.append(0xFF)
cw_msg.append(0)
cw_msg.append(0)
cw_msg.append(0)
cw_msg.append(0xCE)
cw_msg.append(etx)
#============================================================
#ccw_msg = b'\x02\x31\x00\xFE\x00\x00\x00\xCF\x03' #counter clockwise
ccw_msg = bytearray()
ccw_msg.append(stx)
ccw_msg.append(cmd_num)
ccw_msg.append(0)
ccw_msg.append(0xFE)
ccw_msg.append(0)
ccw_msg.append(0)
ccw_msg.append(0)
ccw_msg.append(0xCF)
ccw_msg.append(etx)
#============================================================
#up_msg = b'\x02\x31\x01\x00\xFF\x00\x00\xCE\x03' #up
up_msg = bytearray()
up_msg.append(stx)
up_msg.append(cmd_num)
up_msg.append(0)
up_msg.append(0)
up_msg.append(0xFF)
up_msg.append(0)
up_msg.append(0)
up_msg.append(0xCE)
up_msg.append(etx)
#============================================================
#down_msg = b'\x02\x31\x01\x00\xFE\x00\x00\xCF\x03' #down
down_msg = bytearray()
down_msg.append(stx)
down_msg.append(cmd_num)
down_msg.append(0)
down_msg.append(0)
down_msg.append(0xFE)
down_msg.append(0)
down_msg.append(0)
down_msg.append(0xCF)
down_msg.append(etx)
         
#==================================================================================================================================
# Moves stand Clockwise and Displays dbm Reading
def get_dbm_direction(client,delay,msg):
    move(msg)
    sleep(delay)
    #stop_move()
    client.send('horn'.encode('utf-8'))
    dbm,addr2=client.recvfrom(7)
    dbm=dbm.decode('utf-8')
    dbm = float(dbm)
    print("dBm : ",dbm)
    #sleep(delay) 
    return(dbm) 

#==================================================================================================================================  
# Loops as long as the dbm from previous reading is lower. Else they break out and return the value.
def dbm_loop_direction(dbm,cli,delay,msg):
    num_moves = 1
    dbm_dir = get_dbm_direction(cli,delay,msg)
    if(dbm_dir > dbm):
        while (dbm_dir > dbm):
            num_moves += 1 
            dbm = dbm_dir
            dbm_dir = get_dbm_direction(cli,delay,msg)           
        else:
            #stop_move()
            return(dbm_dir,num_moves)
    else:
        #stop_move()
        return(dbm,num_moves)  
#==================================================================================================================================
def hold_pos(dbm,cli,delay,hold_threshold):
    dbm_hold = get_dbm(cli)
    while (dbm <= (dbm_hold + hold_threshold)) and (dbm >= (dbm_hold - hold_threshold)): 
        dbm_hold = get_dbm(cli)
        print("HOLD DBM IS SITTING ON:  ", dbm_hold)
        stop_move()
    return(dbm_hold)     
#==================================================================================================================================     
# Stops current stand movement
def stop_move():
    qpt.write(stop_msg)
    #feedback = qpt.readline()
    #return feedback  
#==================================================================================================================================          
# Moves in direction of inputted command    
def move(msg):
    qpt.write(msg)
    #feedback = qpt.readline()
    #return feedback 

#==================================================================================================================================
#==================================================================================================================================      
#==================================================================================================================================     
def get_degrees(msg):
    """Returns both horizontal and vertical position in degrees"""
    #read input from positioner
    qpt.flushInput()
    if( msg == 'default'):
        msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
    pos_string = b''
    comp = b''
    while(len(pos_string) < 7):
        qpt.write(msg)
        pos_string = qpt.readline()
        #if(pos_string[0] != 0x06):
        #    pos_string = b'\x00'
            #should make it re-read string, will go back to start of while loop
    #convert the hex value to degrees for horizontal position
    if(pos_string[2] == 0x1B and pos_string[4] == 0x1B):
        #2 1b for x
        hor_deg = (((int(pos_string[5]-128))*256) + (int(pos_string[3])-128))/10
        if(pos_string[6] == 0x1B and pos_string[8] == 0x1B):
            #2 for y
            ver_deg = ((int(pos_string[9]-128)*256) + (int(pos_string[7]-128)))/10
        elif(pos_string[7] == 0x1B):
            #1 for y
            ver_deg = ((int(pos_string[8]-128)*256) + (int(pos_string[6])))/10
        elif(pos_string[6] == 0x1B):
            #1 for y, different location
            ver_deg = ((int(pos_string[8])*256) + (int(pos_string[6]-128)))/10
        else:
            #none for y
            ver_deg = ((int(pos_string[7])*256) + (int(pos_string[6])))/10
        #make correction for negative value
        if(ver_deg > 360):
            #y negative, do backwards
            ver_deg = (-1)*(65535 - ver_deg*10)/10
            
    elif(pos_string[3] == 0x1B):
        #1 for x
        hor_deg = (((int(pos_string[4])-128)*256) + (int(pos_string[2])))/10
        if(pos_string[5] == 0x1B and pos_string[7] == 0x1B):
            #2 for y
            ver_deg = ((int(pos_string[8]-128)*256) + (int(pos_string[6]-128)))/10
        elif(pos_string[6] == 0x1B):
            #1 for y
            ver_deg = ((int(pos_string[7]-128)*256) + (int(pos_string[5])))/10
        elif(pos_string[5] == 0x1B):
            #1 for y, different location
            ver_deg = ((int(pos_string[7])*256) + (int(pos_string[6]-128)))/10
        else:
            #none for y
            ver_deg = ((int(pos_string[6])*256) + (int(pos_string[5])))/10
        #make correction for negative value
        if(ver_deg > 360):
                ver_deg = (-1)*(65535 - ver_deg*10)/10
    
    elif(pos_string[2] == 0x1B):
        #1b in first location
        hor_deg = (((int(pos_string[4]))*256) + (int(pos_string[3]-128)))/10
        if(pos_string[5] == 0x1B and pos_string[7] == 0x1B):
            #2 for y
            ver_deg = ((int(pos_string[8]-128)*256) + (int(pos_string[6]-128)))/10
        elif(pos_string[6] == 0x1B):
            #1 for y
            ver_deg = ((int(pos_string[7]-128)*256) + (int(pos_string[5])))/10
        elif(pos_string[5] == 0x1B):
            #1 for y in different location
            ver_deg = ((int(pos_string[7])*256) + (int(pos_string[6]-128)))/10
            
        else:
            #none for y
            ver_deg = ((int(pos_string[6])*256) + (int(pos_string[5])))/10
        #make correction for negative value
        if(ver_deg > 360):
            #y negative, do backwards
            ver_deg = (-1)*(65535 - ver_deg*10)/10
                   
    else:
        #none for x
        hor_deg = ((int(pos_string[3])*256) + (int(pos_string[2])))/10
        if(pos_string[4] == 0x1B and pos_string[6] == 0x1B):
            #2 for y
            ver_deg = ((int(pos_string[7]-128)*256) + (int(pos_string[5]-128)))/10
        elif(pos_string[5] == 0x1B):
            #1 for y
            ver_deg = ((int(pos_string[6]-128)*256) + (int(pos_string[4])))/10
        elif(pos_string[4] == 0x1B):
            #1 for y, different location
            ver_deg = ((int(pos_string[6])*256) + (int(pos_string[5]-128)))/10
        else:
            #none for y
            ver_deg = ((int(pos_string[5])*256) + (int(pos_string[4])))/10
        #make correction for negative value
        if(ver_deg > 360):
            #y negative, do backwards
            ver_deg = (-1)*(65535 - ver_deg*10)/10

    if(hor_deg > 360):
        #rewrite for negative x
        hor_deg = (-1)*(65535 - hor_deg*10)/10

    print('At: ', hor_deg, ver_deg)
    print(pos_string)
    print(pos_string[0],pos_string[1],pos_string[2],pos_string[3],pos_string[4],)
    print(' ')
    return hor_deg, ver_deg   
#==================================================================================================================================    
#==================================================================================================================================
#==================================================================================================================================        
def move_to_position(x_origional,y_origional):
    
    def check_at_position():
        az1 = 1000
        el1 = 1000
        az2 = 2000
        el2 = 2000
        while True:
            time.sleep(0.2)
            az1 = az2
            el1 = el2
            az2, el2 = get_degrees('default')
            az_diff = abs(az1)-abs(az2)
            el_diff = abs(el1)-abs(el2)
            if( (abs(az_diff) < 1) and (abs(el_diff) < 1) ):
                print('At position!')
                break

    def validate(hp, xo, vp, yo):
        A = (int(hp) != int(xo))
        B = (int(hp) != int(float(xo)+0.5))
        C = (int(vp) != int(yo))
        D = (int(vp) != int(float(yo)+0.5))
        return ((A and B) or (C and D))
            
    """Move to a selected position"""
    x = float(x_origional)
    y = float(y_origional)
    x_neg = False
    y_neg = False
    if(x < 0):
        x_neg = True
    if(y < 0):
        y_neg = True
    x = abs(int(x))
    y = abs(int(y))
    #convert x degrees to bytes
    x_deg = hex(10*x)
    #convert y degrees to bytes
    y_deg = hex(10*y)
    #construct byte message
    header = 0x02
    msg_type = 0x33
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
    #print('LRC = ' + str(lrc))
    end = 0x03
    if(x_neg is True):
        #subtract from FF
        x_1 = 255-(int(x_1))
        x_count = 255-(int(x_count))
        print('x deg: ' , x_deg)
    if(y_neg is True):
        #subtract from FF
        y_1 = 255-(int(y_1))
        y_count = 255-(int(y_count))
    #move_msg = b"".join([header,x_move,y_move,end])
    move_msg = bytearray()
    move_msg.append(header)
    move_msg.append(msg_type)
    move_msg.append(x_1)
    if((x > 50) and (x < 110) and x_neg is False):
        esc_correct = 0x1B
        x_count = x_count + 128
        move_msg.append(esc_correct)
    move_msg.append(x_count)
    move_msg.append(y_1)
    if((y > 50) and (y < 110) and y_neg is False):
        esc_correct = 0x1B
        y_count = y_count + 128
        move_msg.append(esc_correct)
    move_msg.append(y_count)
    move_msg.append(lrc)
    move_msg.append(end)
    #print('move message created: ' , move_msg)
    h_pos = 1000
    v_pos = 1000
    qpt.write(move_msg)
    check_at_position()
    return x_origional, y_origional #returns entered position
#==================================================================================================================================
#==================================================================================================================================

