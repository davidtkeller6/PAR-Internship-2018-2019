import bluetooth
import sys
bd_addr = "00:21:13:02:4B:BD"

port = 1
sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((bd_addr, port))
print 'Connected'
#sock.settimeout(20.0)

#count = 0;
'''
while True: #(count < 10):
    data = sock.recv(1)
    print (data)

    #count += 1
'''
char = ''
msg = [0,0,0]
temp_msg = ''
i=0
k=0
while True:
    char = sock.recv(1).decode()
    if(char == '\r'):
        #do nothing
        k=0
    elif(char == '\n'):
        msg[i] = int(temp_msg)
        temp_msg = ''
        i+=1
    else:
        temp_msg = temp_msg + str(char)
    if(i == 3):
        i=0
        print((msg[0]), (msg[1]), (msg[2]))
sock.close()
