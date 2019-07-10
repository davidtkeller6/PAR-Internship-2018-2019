import bluetooth
import time
import serial
import sys

bd_addr = "00:21:13:02:4B:BD"
port = 1
sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((bd_addr, port))
print ('Connected')
#sock.settimeout(20.0)
#send begin message?

def read_scope_compass_values():
    char = ''
    msg = [0,0,0]
    temp_msg = ''
    i=0
    nothing=0
    while True:
        char = sock.recv(1).decode()
        if(str(char) == '\r'):
            k=0
        elif(str(char) == '\n'):
            msg[i] = int(temp_msg)
            temp_msg = ''
            i+=1
        else:
            temp_msg = temp_msg + str(char)
        if(i == 3):
            i=0
            #print(msg[0], msg[1], msg[2])
            break
    print('Scope:', msg[0], msg[1], msg[2])    
    return msg[0], msg[1], msg[2]
    
while True:
    read_scope_compass_values()
    
