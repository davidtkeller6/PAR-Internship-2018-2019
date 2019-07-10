from qpt_v2 import *
from socket import *

#---------------------------------------------------------------------------
#---------------------Set up UDP Socket Connections-------------------------
#---------------------------------------------------------------------------

#Receiving port
host = ""
port = 13000
buf = 1024
addr = (host,port)
udp_sock = socket(AF_INET, SOCK_DGRAM)
udp_sock.bind(addr)

#---------------------------------------------------------------------------
#--------------------------------Functions----------------------------------
#---------------------------------------------------------------------------

def rx_data():
    """Receives data over ethernet connection"""
    raw_data = udp_sock.recvfrom(buf)
    data = raw_data[0].decode()
    data = data.split(',')
    print(data)
    az = data[0]
    el = data[1]
    return az, el
    #return 0,0
   
def main():
    #ask_for_data()
    azimuth, elevation = rx_data()
    move_to_position(azimuth,elevation)
   
   
while True:
    main()


