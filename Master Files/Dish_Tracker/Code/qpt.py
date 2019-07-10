import serial
import time

#open connection
qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=1)

#check connection
#print(qpt.isOpen())

def to_center():
    """Moves towards center position (0 deg, 0 deg)"""
    center_msg = b'\x02\x35\x35\x03'
    qpt.write(center_msg)
    feedback = qpt.readline()
    return feedback
    
def stop_move():
    """Stops current move"""
    stop_msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
    qpt.write(stop_msg)
    feedback = qpt.readline()
    return feedback

def move_cw():
    """Moves clockwise"""
    cw_msg = b'\x02\x31\x00\xA7\x00\x00\x00\x96\x03' #change value to knock down speed and step
    qpt.write(cw_msg)
    feedback = qpt.readline()
    return feedback

def move_ccw():
    """Moves counter clockwise """
    ccw_msg = b'\x02\x31\x00\x96\x00\x00\x00\xA7\x03'
    qpt.write(ccw_msg)
    feedback = qpt.readline()
    return feedback

def move_up():
    """Moves pointer up"""
    up_msg = b'\x02\x31\x00\x00\x65\x00\x00\x54\x03'
    qpt.write(up_msg)
    feedback = qpt.readline()
    return feedback

def move_down():
    """Moves pointer down"""
    down_msg = b'\x02\x31\x00\x00\x54\x00\x00\x65\x03'
    qpt.write(down_msg)
    feedback = qpt.readline()
    return feedback
    
def move_up_cw():
    """Moves pointer up and clockwise diagonally"""
    up_cw_msg = b'\x02\x31\x00\xFB\xF9\x00\x00\x33\x03'
    qpt.write(up_cw_msg)
    feedback = qpt.readline()
    return feedback
    
def move_down_cw():
    """Moves pointer down and clockwise diagonally"""
    down_cw_msg = b'\x02\x31\x00\xF3\xF6\x00\x00\x34\x03'
    qpt.write(down_cw_msg)
    feedback = qpt.readline()
    return feedback

def move_up_ccw():
    """Moves pointer up and counterclockwise diagonally"""
    up_ccw_msg = b'\x02\x31\x00\xF8\xF9\x00\x00\x30\x03'
    qpt.write(up_ccw_msg)
    feedback = qpt.readline()
    return feedback
    
def move_down_ccw():
    """Moves pointer down and counterclockwise diagonally"""
    down_ccw_msg = b'\x02\x31\x00\xFC\xFA\x00\x00\x37\x03'
    qpt.write(down_ccw_msg)
    feedback = qpt.readline()
    return feedback
    
def get_horizontal_degrees():
    """Returns vertical position degrees"""
    stop_msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03' #----don't always want to stop---
    qpt.write(stop_msg)
    pos_string = qpt.readline()
    #convert the hex value to degrees for horizontal position
    hor_deg = ((int(pos_string[3])*256) + (int(pos_string[2])))/10 #check hex location
    return hor_deg
    
def get_vertical_degrees():
    """Returns vertical position degrees"""
    stop_msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03' #----don't always want to stop---
    qpt.write(stop_msg)
    #write message come before the read message?
    pos_string = qpt.readline()
    #convert the hex value to degrees for vertical position
    ver_deg = ((int(pos_string[5])*256) + (int(pos_string[4])))/10 #check hex location
    return ver_deg
    
def get_position_bytes():
    """Returns the byte message of position"""
    stop_msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03' #----don't always want to stop---
    qpt.write(stop_msg)
    pos_string = qpt.readline()
    return pos_string
    
def return_to_center():
    """Repositions pointer to center"""
    current_pos = '\xAA\xBB\xCC\xDD'
    #run command until back to center (0,0)
    while True: #change the byte locations
        current_pos = to_center()
        print(current_pos)
        time.sleep(0.2) #check timing
        if((current_pos[1] == 0) and (current_pos[1] == 0)):
            break
    print('At center')

def move_to_position(x,y):
    """Move to a selected position"""
    #convert x degrees to bytes
    x_deg = hex(10*x)
    #convert y degrees to bytes
    y_deg = hex(10*y)
    #construct byte message
    #send byte message
    header1 = 0x02
    header2 = 0x33
    x_1 = 10*x
    x_count = 0
    while True:
        x_1 = x_1 - 256
        x_count +=1
        if(x_1 < 0):
            x_1 = x_1 +256
            x_count-=1
            break
    #x_move = b"".join([bytes(hex(x_1), 'utf-8'), bytes(hex(x_count), 'utf-8')])
    #3print(bytes(hex(x_1), 'utf-8'))
    #print(bytes(hex(x_count), 'utf-8'))
    #print(x_move.decode())
    y_1 = 10*y
    y_count = 0
    while True:
        y_1 = y_1 - 256
        y_count +=1
        if(y_1 < 0):
            y_1 = y_1 +256
            y_count-=1
            break    
    end1 = x_1+y_count+y_1+y_count+0x11
    print('End1 = ' + str(end1))
    end2 = 0x03
    #move_msg = b"".join([header,x_move,y_move,end])
    move_msg = bytearray()
    move_msg.append(header1)
    move_msg.append(header2)
    move_msg.append(x_1)
    move_msg.append(x_count)
    move_msg.append(y_1)
    move_msg.append(y_count)
    move_msg.append(end1)
    move_msg.append(end2)
    print(move_msg)
    count=0
    while count < 10:
        qpt.write(move_msg)
        feedback = qpt.read()
        time.sleep(3)
        count+=1
    print('Moving to position: ' + x_deg + ', ' + y_deg)

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
        move_ccw()
        time.sleep((.1+count))
        move_up_ccw()
        time.sleep((.05+count))
        move_up()
        time.sleep((.05+count))
        move_up_cw()
        time.sleep((.05+count))
        move_cw()
        time.sleep(2*(.1+count))
        move_down_cw()
        time.sleep((.05*count))
        move_down()
        time.sleep(2*(.05+(.05*count)))
        move_down_ccw()
        time.sleep(.05*count)
        count+=1
    #this method isn't really ideal with using timer to determine movement length

def path_prediction_search():
    """Searches for transmitter using a predicted path of its movement"""
    #look at last few degrees readings of the arm when RSSI was high
    #create projected path based on data points
    #move to next point predicted and check RSSI
    #keep moving to next projected points until find Tx

def shut_down():
    """closed connections when program done"""
    #return_to_center()
    stop_move()
    qpt.close()

#---------------------testing fucntions-----------------------------

def scan_cw_ccw_test():
    """scans cw and ccw for test"""
    count = 0
    while (count < 10):
        move_cw()
        time.sleep(1)
        print(get_horizontal_degrees())
        print(get_position_bytes())
        count += 1
    count = 0    
    while (count < 20):
        move_ccw()
        time.sleep(1)
        print(get_horizontal_degrees())
        print(get_position_bytes())
        count += 1
    stop_move()
    print('Cw-Ccw scan complete')
    
def scan_up_down_test():
    """scans cw and ccw for test"""
    count = 0
    while (count < 10):
        move_up()
        time.sleep(1)
        print(get_vertical_degrees())
        print(get_position_bytes())
        count += 1
    count = 0
    while (count < 10):
        move_down()
        time.sleep(1)
        print(get_vertical_degrees())
        print(get_position_bytes())
        count += 1
    stop_move()
    print('Up-Down scan complete')
    
def feedback_test():
    """Tests continuous feedback""" #--------test worked--------
    count = 0
    while (count < 5):
        pos_string = move_cw()
        time.sleep(1)
        hor_deg = ((int(pos_string[3])*256) + (int(pos_string[2])))/10
        print(hor_deg)
        pos_string = move_cw()
        time.sleep(1)
        hor_deg = ((int(pos_string[3])*256) + (int(pos_string[2])))/10
        print(hor_deg)
        count += 1
    stop_move()

def diagonal_test():
    """Testing diagonal functions"""
    move_up_cw()
    time.sleep(2)
    print('up cw')
    stop_move()
    move_down_cw()
    time.sleep(2)
    print('down cw')
    stop_move()
    move_up_ccw()
    time.sleep(2)
    print('up ccw')
    stop_move()
    move_down_ccw()
    time.sleep(2)
    print('down ccw')
    stop_move()

if __name__ == '__main__': 
    to_center()
    to_center()
    to_center()
    to_center()
    to_center()
    to_center()
    to_center()
    to_center()
    #move_cw()
    #time.sleep(2)
    #stop_move()
    #spiral_search()
    #print(get_horizontal_degrees())
    #diagonal_test()
    #move_to_position(50,179)
    scan_cw_ccw_test()
    print('-----------------------------------------')
    scan_up_down_test()
    #to_center()

    shut_down()
    

    
    
    
