from qpt_v2 import*
import math
import time
from geopy.distance import vincenty
import sys
#import thread 

#ser = serial.Serial('/dev/ttyS0',9600,timeout=0.5) #serial connection for the receiver module
Current_Location = [0,0,0]
datafile_name = input ('Enter in file name: ')
f=open(datafile_name, "w")
qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=1)



#======================================================================================================= 
def start_up():
    #Read and return GPS from Garmin module for reference lat,lon
    def init_serial():
    
        """Initializes a serial USB device for reading."""
        COMNUM = 4
        ser = serial.Serial()
        ser.baudrate = 4800
        ser.port = '/dev/ttyUSB3' #serial port connection for Garmin module
        ser.timeout = 1
        ser.open()

        if ser.isOpen():
            print( 'Open: ' + ser.portstr )
            return ser
        else:
            return None

    def gga_to_dict( gga_str ):
        """Converts a GGA GPS string into a dictionary of values.
       Can return latitude, longitude, altitude, and number of satellites."""
       
        def getLon( val, direction=None ):
            """Returns longiude in degrees, negative for South"""
            degrees = float(val[:2])
            minutes = float(val[2:])
            ret = float( '%.6f'%(degrees+minutes/60) )
            if direction == 'S':
                ret *= -1
            return ret
    
        def getLat( val, direction=None ):
            """Returns latitude in degrees, negative for West"""
            degrees = float(val[:3])
            minutes = float(val[3:])
            ret = float( '%.6f'%(degrees+minutes/60) )
            if direction == 'W':
                ret *= -1
            return ret
    
        data = gga_str.split(',')
        output = {}
        output['longitude'] = getLon( data[2], data[3] )
        output['latitude'] = getLat( data[4], data[5] )
        try:
            output['altitude'] = float(data[9])
        except ValueError:
            output['altitude'] = float('nan')
        try:
            output['satellites'] = int(data[7])
        except ValueError:
            output['altitude'] = 0
        return output

    def run( ser ):
        while 1:
            bytes = str(ser.readline())
            if 'GGA' in bytes:
                output = gga_to_dict( bytes )
                reference_lat = output['latitude']
                reference_lon = output['longitude']

    ser = init_serial()
    if ser is not None:
        run(ser)
    else:
        print( 'Could not open serial device.' )
        reference_lat = 0
        reference_lon = 0
        
    return reference_lat, reference_lon
#======================================================================================================= 
def get_new_GPS():
    """Reads gps data from transmitter"""
   
    #def read_data():   
    while True:
        qpt.flushInput()
        c1 = qpt.read(1).decode()
        #print(c1)
        if c1 == 'A':
            c2 = ser.read(1).decode()
            if(c2 == 'A'):
                raw_data = qpt.readline().decode()
                data = raw_data.split(',') 
                lat = float(data[0])
                lon = float(data[1])
                alt = float(data[2])
                return lat, lon, alt
    #NOTE ===> make sure this is the correct return order
    #print(ser.inWaiting())
    
   
#======================================================================================================= 
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
    # elev_dis is the distance from the stand to the point, including its elevation(its hypotenuse)
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
#=======================================================================================================
#======================================================================================================= 
#=======================================================================================================  

def preplanned_track():
    """Tracks based on constant speed and gps coordinates from a file"""
    #filename = input('Enter the GPS file name: ')
    filename =  '/home/pi/Desktop/GPS_test_data.txt'
    gps_file = open(filename, "r")
    #pos_lat, pos_lon = start_up() #read from Garmin module
    pos_lat = 43.220746
    pos_lon = -75.407512
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
    gps_file.close()

def telem_track():
    """Tracks based on constant GPS updates"""
    #pos_lat, pos_lon = start_up() #read from Garmin module
    #position of antenna longitude and latitude taken from google maps for testing
    #pos_lat = 43.220746
    #pos_lon = -75.407512
    #pos_lat = 43.219409
    #pos_lon = -75.408620
    pos_lat = 43.219511
    pos_lon = -75.408899
    start = True
    
    while True:
    
    #Method of start (true or false) so that first GPS coordinate received can be stored in the variables for the first point
    #second location can be stored in the variables for the seond point 
    #then both points can be used for calculations and comparisons 
        if start == True:
            # First GPS location received in order -- Latitude, Longitude, Altitude
            lat_1, lon_1, alt_1 = get_new_GPS() 
            target_speed = 1 #can remove, was there for testing. 
            #computing the distance between the antenna and the target GPS location
            dist_1 = compute_distance(pos_lat,pos_lon,lat_1,lon_1)
            #computing the elevation angle 
            el_1 = compute_elevation(dist_1, alt_1)  
            #computing the azimuth angle
            az_1 = compute_azimuth(lon_1,lat_1,pos_lon, pos_lat)
            #casting to float to use in future calculations
            az_1 = float(az_1)
            el_1 = float(el_1)        
            print('Lat: {} Lon: {} Alt: {} El: {} Az: {}'.format(lat_1,lon_1,alt_1,el_1,az_1))
            f.write('\nLat: {} Lon: {} Alt: {} El: {} Az: {}'.format(lat_1,lon_1,alt_1,el_1,az_1))
            #function call to move the antenna to first GPS location
            move_to_position(az_1,el_1)
            h,v = get_degrees('default')
            print('Pointing at Az: {} El: {}'.format(h,v))
            f.write('\nPointing at Az: {} El: {}'.format(h,v))
            f.write('\n-------------------------------------------------------------------------------')
            start = False 
         
        elif start == False:
            #All other GPS locations are received in order -- Latitude, Longitude, Altitude
            lat_2, lon_2, alt_2 = get_new_GPS() 
            target_speed = 1  #can remove, was there for testing. 
            #function call from qpt_v2 to get the current azimuth and elevation of the antenna  
            pos_az,pos_el = get_degrees('default') 
            #computing the distance between the antenna and the target's second GPS location
            dist_2 = compute_distance(pos_lat,pos_lon,lat_2,lon_2)
            #computing the distance between the target's first and second GPS location
            dist_1_to_2 = compute_distance(lat_1, lon_1,lat_2,lon_2)
            #computing the altitude change
            alt_change = float(alt_1) - float(alt_2)   
            #condition needed for another calculation: if altitude change is zero, there will be an error for dividing by zero  
            if alt_change is 0:
                alt_change = 1  
            #computing the first and second elevation angles (can pull the first elevation angle from above)
            el_2 = compute_elevation(dist_2, alt_2)
            el_1 = compute_elevation(dist_1, alt_1)
            #computing the first and second azimuth angle (can pull the first azimuth angle from above)
            az_1 = compute_azimuth(lon_1,lat_1,pos_lon,pos_lat)
            az_2 = compute_azimuth(lon_2,lat_2,pos_lon,pos_lat)         
            print('\nPoint 2 Data:')
            print('Lat: {}, Lon: {}, Alt: {}, El: {}, Az: {}'.format(lat_2,lon_2,alt_2,el_2,az_2))
            f.write('\nLat: {} Lon: {} Alt: {} El: {} Az: {}'.format(lat_1,lon_1,alt_1,el_1,az_1))
            #condition to trigger the move pointer function
            move_to_position(round(az_2,1),round(el_2,1))
            h,v = get_degrees('default')
            print('Pointing at Az: {} El: {}'.format(h,v))
            f.write('\nPointing at Az: {} El: {}'.format(h,v))
            f.write('\n---------------------------------------------------------------------------------')
            print('------------------------------------------------------------------------------------')           
            #making the new position equal the old position for reference to the next calculation when the new coordinate is received     
            lat_1 = lat_2
            lon_1 = lon_2
            alt_1 = alt_2
            dist_1 = dist_2
   
def main():
    """Run tracker"""
    
    #Testing other move messages 
    '''
    STX = 0x02
    msg_type = 0x31
    ETX = 0x03
    lrc = msg_type^5^66
    move_msg = bytearray()
    move_msg.append(STX)
    move_msg.append(msg_type)
    move_msg.append(0)
    move_msg.append(5) #az speed
    move_msg.append(66) #el speed
    move_msg.append(0)
    move_msg.append(0)
    move_msg.append(lrc)
    move_msg.append(ETX)       
    qpt.write(move_msg)
    #stop_move()
    '''
    
    #funtion calls for antenna movement
    #move_to_position(110,50)
    telem_track()
    #preplanned_track()
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        #print("\nprogram interrupted, movement will be stopped")
        f.close()
        stop_move() 
