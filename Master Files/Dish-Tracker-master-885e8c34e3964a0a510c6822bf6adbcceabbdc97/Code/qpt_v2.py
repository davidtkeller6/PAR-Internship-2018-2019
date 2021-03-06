import serial
import time

#open connection
qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=.1)

#check connection
#print(qpt.isOpen())

cw_msg = b'\x02\x31\x00\xA7\x00\x00\x00\x96\x03'
ccw_msg = b'\x02\x31\x00\x96\x00\x00\x00\xA7\x03'
up_msg = b'\x02\x31\x00\x00\x65\x00\x00\x54\x03'
down_msg = b'\x02\x31\x00\x00\x54\x00\x00\x65\x03'
up_cw_msg = b'\x02\x31\x00\xFB\xF9\x00\x00\x33\x03'
down_cw_msg = b'\x02\x31\x00\xF3\xF6\x00\x00\x34\x03'
up_ccw_msg = b'\x02\x31\x00\xF8\xF9\x00\x00\x30\x03'
down_ccw_msg = b'\x02\x31\x00\xFC\xFA\x00\x00\x37\x03'
stop_msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'

def to_center():
    """Moves towards center position (0 deg, 0 deg)"""
    center_msg = b'\x02\x35\x35\x03'
    #qpt.write(center_msg)
    #feedback = qpt.readline()
    move_to_position(0,0)
    #return feedback

def stop_move():
    """Stops current move"""
    stop_msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
    qpt.write(stop_msg)
    #feedback = qpt.readline()
    #return feedback

def move(msg):
    """Moves pointer down and counterclockwise diagonally"""
    qpt.write(msg)
    #feedback = qpt.readline()
    #return feedback

def get_degrees(msg):
    """Returns both horizontal and vertical position in degrees"""
    #read input from positioner
    qpt.flushInput()
    pos_string = b''
    comp = b''
    if(msg == 'default'):  
        msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
    while(len(pos_string) < 7):
        qpt.write(msg)
        pos_string = qpt.readline()
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

def get_position_bytes():
    """Returns the byte message of position"""
    stop_msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03' #----don't always want to stop---
    qpt.write(stop_msg)
    pos_string = qpt.readline()
    return pos_string
    
def return_to_center(): #ignore this for now, use move_to_position_(0,0)
    """Repositions pointer to center----------> currently ignore"""
    current_pos = '\xAA\xBB\xCC\xDD'
    #run command until back to center (0,0)
    while True: #change the byte locations
        current_pos = to_center()
        print(current_pos)
        time.sleep(0.2) #check timing
        if((current_pos[1] == 0) and (current_pos[1] == 0)):
            break
    print('At center')


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

def spiral_search():
    """Preforms a spiral search to find transmitter"""
    #spiral inward to outward making a larger circle each pass (currently squares)
    #------------check the RSSI readings as it spins------------------
    #replace max rssi with new largest and record degrees coordinates
    rssi_max = -120
    max_x = 0
    max_y = 0

    count = 0
    while (count < 5):
        move(ccw_msg)
        time.sleep((.1+count))
        move(up_ccw_msg)
        time.sleep((.05+count))
        move(up_msg)
        time.sleep((.05+count))
        move(up_cw_msg)
        time.sleep((.05+count))
        move(cw_msg)
        time.sleep(2*(.1+count))
        move(down_cw_msg)
        time.sleep((.05*count))
        move(down_msg)
        time.sleep(2*(.05+(.05*count)))
        move(down_ccw_msg)
        time.sleep(.05*count)
        count+=1
    #this method isn't really ideal with using timer to determine movement length

def shut_down():
    """closed connections when program done"""
    #return_to_center()
    stop_move()
    qpt.close()

#---------------------testing fucntions-----------------------------

if __name__ == '__main__': 
    
    count = 0
    while (count < 1000):
        move(cw_msg)
        h_pos = get_horizontal_degrees()
        print(h_pos)
        time.sleep(0.1)
        count+=1
    stop_move()

    #spiral_search()
    #print(get_horizontal_degrees())
    #diagonal_test()
    #move_to_position(50,179)
    #scan_cw_ccw_test()
    #scan_up_down_test()
    #to_center()

    shut_down()
    

    
    
    
