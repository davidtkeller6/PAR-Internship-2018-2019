import serial
import time

#open connection
qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=1)

msg = b'\x02\x33\x00\x02\x00\x00\x00\x31\x03'
qry = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'

def move_to_position(x,y):
    """Move to a selected position"""
    x = float(x)
    y = float(y)
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
    print('LRC = ' + str(lrc))
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
    move_msg.append(x_count)
    move_msg.append(y_1)
    move_msg.append(y_count)
    move_msg.append(lrc)
    move_msg.append(end)        
    print('move message created: ' , move_msg)
    h_pos = 1000
    v_pos = 1000
    qpt.write(move_msg)
    print(move_msg)
    while ((h_pos != x) or (v_pos != y)):
        time.sleep(.1)
        qpt.write(qry)
        print(qpt.readline())
        print(h_pos)
    print(h_pos)
    print(v_pos)
    print('Moved to position: ' + str(x) + ', ' + str(y))


test = input('Hit enter to begin')

move_to_position(27,21)

print('Test done')

    
    
    
