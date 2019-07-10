import threading
import serial, bluetooth
import time

#set up peices needed
event = threading.Event()
qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=.1)
print('Connecting...')
bd_addr = "00:21:13:02:59:1A"
port = 1
BT_sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
BT_sock.connect((bd_addr, port))
print ('Connected')
BT_sock.settimeout(20)


ccw_msg = b'\x02\x31\x00\x96\x00\x00\x00\xA7\x03'

def get_degrees(msg, sock):
    """returns current degrees of positioner"""
    """Returns both horizontal and vertical position in degrees"""
    #read input from positioner
    sock.flushInput()
    pos_string = b''
    comp = b''
    if(msg == 'default'):  
        msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
    while(len(pos_string) < 7):
        sock.write(msg)
        pos_string = sock.readline()
        if(pos_string[0] != 0x06):
            pos_string = b'\x00'
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
    
    
#==========================================================================================
#Threaded functions below
#==========================================================================================    
def joystick(num, sock, bt_s): 
    """function to print cube of given num """
    CW_MSG = b'\x02\x31\x00\xA7\x00\x00\x00\x96\x03'
    CCW_MSG = b'\x02\x31\x00\x96\x00\x00\x00\xA7\x03'
    UP_MSG = b'\x02\x31\x00\x00\x65\x00\x00\x54\x03'
    DOWN_MSG = b'\x02\x31\x00\x00\x54\x00\x00\x65\x03'
    UP_CW_MSG = b'\x02\x31\x00\xFB\xF9\x00\x00\x33\x03'
    DOWN_CW_MSG = b'\x02\x31\x00\xF3\xF6\x00\x00\x34\x03'
    UP_CCW_MSG = b'\x02\x31\x00\xF8\xF9\x00\x00\x30\x03'
    DOWN_CCW_MSG = b'\x02\x31\x00\xFC\xFA\x00\x00\x37\x03'
    STOP_MSG = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
    
    
    def read_value(bt):
        """read value from joystick via BT"""
        #sock.send('1')
        char = bt.recv(1).decode()
        return int(char)
    
    print("Cube: {}".format(num * num * num))
    while True:
        move('stop', sock)
        time.sleep(1)
        value = read_value(bt_s)
        if(value == 1):
            sock.write(UP_CCW_MSG)
            count = 0   #if move, reset count to zero
        elif(value == 2):
            sock.write(UP_CW_MSG)
            count = 0
        elif(value == 3):
            sock.write(DOWN_CCW_MSG)
            count = 0
        elif(value == 4):
            sock.write(DOWN_CW_MSG)
            count = 0
        elif(value == 5):
             sock.write(CCW_MSG)
            count = 0
        elif(value == 6):
            sock.write(CW_MSG)
            count = 0
        elif(value == 7):
            sock.write(UP_MSG)
            count = 0
        elif(value == 8):
            sock.write(DOWN_MSG)
            count = 0
        else:
            #move('stop', sock)
            count+=1 #count increases for doing nothing
            if(count > 50):#if do nothing for 10 count, then move on with point
                count = 0
                event.set()
            else:
                count+=1

def gps_track(num,sock, bt):
    """function to print square of given num """
    event.wait()
    print('JOYSTICK DONE')
    event.clear()
    event.wait()
    print("Square: {}".format(num * num))

  
if __name__ == "__main__": 
    # creating thread 
    t1 = threading.Thread(target=joystick, args=(10,qpt,BT_sock)) 
    t2 = threading.Thread(target=gps_track, args=(10,qpt,BT_sock,)) 
  
    # starting thread 1 
    t1.start() 
    # starting thread 2 
    t2.start() 
  
    # wait until thread 1 is completely executed 
    t1.join() 
    # wait until thread 2 is completely executed 
    t2.join() 
  
    # both threads completely executed 
    print("Path Complete!") 
    
