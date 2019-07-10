from qpt_v2 import*
import math
import time
from geopy.distance import vincenty
import sys
from socket import *
#import thread 

#ser = serial.Serial('/dev/ttyS0',9600,timeout=0.5) #serial connection for the receiver module
Current_Location = [0,0,0]
#datafile_name = input ('Enter in file name: ')
#f=open(datafile_name, "w")
qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=1)




#---------------------------------------------------------------------------
#---------------------Set up UDP Socket Connections-------------------------
#---------------------------------------------------------------------------
host = "127.0.0.1"       #match IP to host
port = 13000
addr = (host, port)
udp_sock = socket(AF_INET, SOCK_DGRAM)
buf = 1024

#---------------------------------------------------------------------------
#---------------------Functions---------------------------------------------

def send_data(a,e):
    send_str = str(a)+','+str(e)
    udp_sock.sendto(send_str.encode(), addr)


def compute_distance(ref_lat,ref_lon,tar_lat,tar_lon):
    '''Computes distance from pointer to target'''
    a = (ref_lat,ref_lon)
    b = (float(tar_lat),float(tar_lon))
    #print(tar_lat,tar_lon,ref_lat,ref_lon)
    dis = vincenty(a, b).meters
    return dis
#=======================================================================================================     
def compute_azimuth(new_lon,new_lat,ref_lon, ref_lat):
    '''Compute azimuth angle'''
    x = float(new_lon)-ref_lon
    y = float(new_lat)-ref_lat
    azimuth = math.degrees(math.atan2(x,y))
    #azimuth = math.atan2(x,y)
    #azimuth = azimuth * 57.2958
    #if(x < 0):
    #   azimuth = (math.atan2(x,y))    
    return azimuth
#======================================================================================================= 
def compute_elevation( flat_dist , alt ):
    '''Compute elevation angle'''
    ''' ****important**** 
        currently i'm returning the negated number of pointer elevation.
        this is because on our current stand, when the tilt goes UP, it heads towards the south
        (positive numbers and when the tilt goes down, it heads to the north (negative tilt numbers)
        to revert to normal, just take the - sign out
    '''    
    # elev_dis is the distance from the stand to the point, including its elevation(its hypotneuse)
    # flat_dis is the distance from the stand to the point, in a straight line on the ground.
    # elev_dis should always be bigger than flat_dist, unless the altitude is 0
    #elev_dist = math.sqrt(flat_dist**2 + float(alt)**2)   
    val1 = float(alt)/flat_dist
    elevation = math.degrees((math.atan(val1))) 
    pointer_elevation = 86 - elevation
    if (pointer_elevation < -86):
        
        return (86.0)
    elif(pointer_elevation > 86):
        
        return (-86.0)
    return (-pointer_elevation)   



def preplanned_track():
    """Tracks based on constant speed and gps coordinates from a file"""
    #filename = input('Enter the GPS file name: ')
    filename =  '/home/pgsc/Desktop/GPS_test_data.txt'
    #gps_file = open(filename, "r")
    #pos_lat, pos_lon = start_up() #read from Garmin module
    pos_lat = 43.220746
    pos_lon = -75.407512
    #h = 0
    #v = 0
    start = True
    gps_file = open(filename, "r")
    for line in gps_file:
     
        if start == True:
           data = line.split(',')
           lat_1 = data[0]
           lon_1 = data[1]
           alt_1 = data[2]
           dist_1 = compute_distance(pos_lat,pos_lon,lat_1,lon_1)
           el_1 = compute_elevation(dist_1, alt_1)           
           az_1 = compute_azimuth(lon_1,lat_1,pos_lon, pos_lat)          
           print('Lat: {} Lon: {} Alt: {} El: {} Az: {}'.format(lat_1,lon_1,alt_1,el_1,az_1))           
           #function call to move the antenna to first GPS location
           move_to_position(round(az_1,1),round(el_1,1))
           h,v = get_degrees('default')
           print('Pointing at Az: {} El: {}'.format(h,v))
           #gps_file = open(filename, "r")
           start = False        
        elif start == False:
            data = line.split(',')
            lat_2 = data[0]
            lon_2 = data[1]
            alt_2 = data[2]
            target_speed = 1
            #pos_az,pos_el = get_degrees('default')
            dist_2 = compute_distance(pos_lat,pos_lon,lat_2,lon_2)
            dist_1_to_2 = compute_distance(lat_1, lon_1,lat_2,lon_2)
            alt_diff = float(alt_1) - float(alt_2)           
            if alt_diff is 0:
                alt_diff = 1  
            el_2 = compute_elevation(dist_2, alt_2)
            el_1 = compute_elevation(dist_1, alt_1)
            az_1 = compute_azimuth(lon_1,lat_1,pos_lon,pos_lat)
            az_2 = compute_azimuth(lon_2,lat_2,pos_lon,pos_lat)  
            print('\nPoint 2 Data:')
            print('Lat: {}, Lon: {}, Alt: {}, Az: {}, El: {}'.format(lat_2,lon_2,alt_2,az_2,el_2))
            
            print('------------------------------------------------------------------------------------')
            move_to_position(round(az_2,1),round(el_2,1)) 
            
            h,v = get_degrees('default')    
            print('Pointing at Az: {} El: {}'.format(h,v))
            lat_1 = lat_2
            lon_1 = lon_2
            alt_1 = alt_2
            dist_1 = dist_2
            time.sleep(2)
preplanned_track()

