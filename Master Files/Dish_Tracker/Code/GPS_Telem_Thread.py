from qpt_v2 import*
import math
import time
from geopy.distance import vincenty
import sys
import threading

ser = serial.Serial('/dev/ttyS0',9600,timeout=0.5) #serial connection for the receiver module
Current_Location = [0,0,0]
datafile_name = input ('Enter in file name: ')
f=open(datafile_name, "w")
#qpt = serial.Serial(port='/dev/ttyUSB1',baudrate=9600,timeout=1) ---> established in the qpt_v2 file that is imported

def get_new_GPS():
    """Reads gps data from transmitter"""
   
    #def read_data():   
    while True:
        ser.flushInput()
        c1 = ser.read(1).decode()
        #print(c1)
        if c1 == 'A':
            c2 = ser.read(1).decode()
            if(c2 == 'A'):
                raw_data = ser.readline().decode()
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
#=======================================================================================================
#======================================================================================================= 
#=======================================================================================================  

def move_pointer(tar_spd , ref_az , new_az , dist_1_to_2 , ref_el , new_el , alt_change):  

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
     
    def not_there_az(cur_pos_x , az_pos , cw):
      
        # To deal with random error from get_degrees() sending values in the 6000's
        if cur_pos_x > 360 or cur_pos_x < -360:
            return False
        # Continues to loop as long as stand needs to rotate to get to new azimuth angle  
        if cw is True:
            if cur_pos_x < az_pos:
                return True
            else: 
                return False    
        else:
            if cur_pos_x > az_pos:
                return True 
            else:
                return False     
            
            
    def not_there_el(cur_pos_y , el_pos , up):
        #print("Current position is:",cur_pos_y,"Desired position is: ",el_pos)        
        # To deal with random error from get_degrees() sending values in the 6000's
        if cur_pos_y > 90 or cur_pos_y < -90:
            return False
        # Continues to loop as long as stand needs to rotate to get to the new elevation angle  
        if up is True:
            if cur_pos_y < el_pos:
                return True
            else: 
                return False    
        else:
            if cur_pos_y > el_pos:
                return True  
            else: 
                return False    
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
     
    def to_angular_speed(el1 , el2 , az1 , az2 , tar_spd , dist_1_to_2 , alt_change):
           
            # Determines Clockwise or Counterclockwise for pan
            cw = False
            if(az1 < az2):
                cw = True      
            # Determines Up or Down for tilt
            up = False
            if(el1 < el2):
                up = True
            
            # Determines Speed stand needs to move during timeframe that it will take to move from point 1 to point 2   
            # computes change in azimuth angle for stand  
            az_deg_change = az1 - az2
            time_az = 0.1 #hard coded because the GPS coordinates are received every tenth of a second
            angular_speed_az = abs(az_deg_change/time_az)          
            # Currently going down is into the negative degrees, but also in the northward direction(what we want)
            # going up is into the positive degrees, but southward direction.

            # computes change in elevation angle for stand
            el_deg_change = el1 - el2
            time_el = 0.1 #hard coded because the GPS coordinates are received every tenth of a second
            angular_speed_el = abs(el_deg_change/time_el)
            
            return  cw,  up, angular_speed_az, angular_speed_el
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #Adjust movement speed and create move message 
    def adjust_speed(r_el, n_el,r_az,n_az,tar_spd,dist_1_to_2,alt_change):
        
        #call to_angular_speed
        cw , up, angular_speed_az, angular_speed_el = to_angular_speed(r_el,n_el,r_az,n_az,tar_spd,dist_1_to_2,alt_change)
        
        

        #-------------------------------------------                
        
        if(cw is True):
        
            # Accomodates for huge speeds and adjusts to max speed for stand
            if angular_speed_az > 32:
                angular_speed_az = 32
            # Accomodates for very small speeds and adjust to min speed for stand
            elif angular_speed_az < 1:
                angular_speed_az = 1     
            speed_az = (2*(4*int(angular_speed_az)-1)+1)#clockwise message (odd number)
          
        else:
            if angular_speed_az > 32:
                angular_speed_az = 32      
            elif angular_speed_az < 1:
                angular_speed_az = 1        
            speed_az =(2*(4*int(angular_speed_az)-1)) #counter-clockwise message (even number)           
               
        #---------------------------------------------    
        if(up is True):
        
            # Accomodates for huge speeds and adjusts to max speed for stand
            if angular_speed_el > 32:
                angular_speed_el = 32
            # Accomodates for very small speeds and adjust to min speed for stand
            elif angular_speed_el < 1:
                angular_speed_el = 1
            speed_el = (2*(4*int(angular_speed_el)-1)+1)#up message (odd number)
          
        else:
            # Accomodates for huge speeds and adjusts to max speed for stand
            if angular_speed_el > 32:
                angular_speed_el = 32
            # Accomodates for very small speeds and adjust to min speed for stand
            elif angular_speed_el < 1:
                angular_speed_el = 1  
            speed_el = (2*(4*int(angular_speed_el)-1)) #down message (even number)
            
        print(speed_az, speed_el)
        #print(angular_speed_az,angular_speed_el)             
        return ( speed_az , speed_el , cw, up )         

        
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        
    def speed_msg( speed_az , speed_el , cw , up ):  
        #generates the move message for the stand. The azimuth and eleveation numbers in the message controls the speed at which it moves in tilt
        #or pan
        STX = 0x02
        msg_type = 0x31
        ETX = 0x03
        lrc = msg_type^speed_az^speed_el
        move_msg = bytearray()
        move_msg.append(STX)
        move_msg.append(msg_type)
        move_msg.append(0)
        move_msg.append(speed_az) #az speed
        move_msg.append(speed_el) #el speed
        move_msg.append(0)
        move_msg.append(0)
        move_msg.append(lrc)
        move_msg.append(ETX)
        '''
        test_az, test_el = get_degrees(move_msg)
        if(test_az == 999):
            lrc = msg_type^speed_az^speed_el
            move_msg = bytearray()
            move_msg.append(STX)
            move_msg.append(msg_type)
            move_msg.append(0)
            move_msg.append(speed_az) #az speed
            move_msg.append(0x1B)
            move_msg.append(speed_el) #el speed
            move_msg.append(0)
            move_msg.append(0)
            move_msg.append(lrc)
            move_msg.append(ETX)
        '''
        #print(move_msg)
        #print(move_msg[0],move_msg[1],move_msg[2],move_msg[3],move_msg[4],move_msg[5],move_msg[6],move_msg[7],move_msg[8])
        return (move_msg)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    #call adjust_speed and speed_msg to get the correct speed and move message
    speed_az , speed_el , cw , up = adjust_speed(ref_el,new_el,ref_az,new_az,tar_spd,dist_1_to_2,alt_change)
    command = speed_msg( speed_az , speed_el , cw , up )
    current_az = ref_az
    current_el = ref_el
    
    # Returns a bool for pan_move and tilt_move. If one of these becomes false, then it has reached
    # Its desired angle for that movement(up, down or cw,ccw). It will then stop that movement, but if
    # The other movement is not done yet, it will continue that one. For example, if the stand needs to
    # go up and to the left, it will do so, and if it needs to go up less that it needs to go to the left,
    # It will get to the stop going up first. Therefore we want to stop the stand from going up anymore, but
    # keep it going left until it reaches its destination left. 
    pan_move = not_there_az(current_az , new_az , cw)
    tilt_move = not_there_el(current_el , new_el , up)

    #if(pan_move is True and tilt_move is True):
    while(pan_move and tilt_move):
        qpt.write(command)
        #print("move msg: ", command)
        #print("diff msg: ", qpt.readline())
        #time.sleep(.01)
        current_az, current_el = get_degrees(command)
        pan_move = not_there_az(current_az , new_az , cw)
        tilt_move = not_there_el(current_el , new_el , up)  
        signal.alarm(0)        
    if(pan_move is False and tilt_move is True):
        #print("Pan stopping, tilt continuing")
        command = speed_msg( 0 , speed_el , cw , up )
        while(tilt_move):
            qpt.write(command)
            #print(qpt.readline())
            #time.sleep(.01)
            current_az, current_el = get_degrees(command)
            tilt_move = not_there_el(current_el , new_el , up)
            signal.alarm(0)           
    elif(pan_move is True and tilt_move is False):
        #print("Tilt stopping, pan continuing")
        command = speed_msg( speed_az , 0 , cw , up )
        while(pan_move):
            qpt.write(command)
            #print(qpt.readline())
            #time.sleep(.01)
            current_az, current_el = get_degrees(command)            
            pan_move = not_there_az(current_az , new_az , cw)
            signal.alarm(0)     
    stop_move() 


def read_calculate_preplanned():
    
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
            start = False
            return az_1,el_1
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
            return az_2, el_2
            '''
            lat_1 = lat_2
            lon_1 = lon_2
            alt_1 = alt_2
            dist_1 = dist_2
            '''
def read_calculate_telem():
    
    #pos_lat, pos_lon = start_up() #read from Garmin module
    #position of antenna longitude and latitude taken from google maps for testing
    pos_lat = 43.220746
    pos_lon = -75.407512
    #pos_lat = 43.219409
    #pos_lon = -75.408620
    #pos_lat = 43.219511
    #pos_lon = -75.408899
    start = True
    
    while True:
    
        if (start == True):
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
            start = False
            return az_1, el_1
        elif (start == False):
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
            return az_2, el_2
            '''
            lat_1 = lat_2
            lon_1 = lon_2
            alt_1 = alt_2
            dist_1 = dist_2
            '''
def telem_track():
    """Tracks based on constant GPS updates"""
    start = True
    
    while True:
    
    #Method of start (true or false) so that first GPS coordinate received can be stored in the variables for the first point
    #second location can be stored in the variables for the seond point 
    #then both points can be used for calculations and comparisons 
        if (start == True):      
            az_1, el_1 = read_calculate_telem()
            move_to_position(az_1,el_1)
            h,v = get_degrees('default')
            print('Pointing at Az: {} El: {}'.format(h,v))
            f.write('\nPointing at Az: {} El: {}'.format(h,v))
            f.write('\n-------------------------------------------------------------------------------')
            start = False
        elif(start == False):      
            az_2, el_2 = read_calculate()
            move_to_position(round(az_2,1),round(el_2,1))
            #if (az_1 != az_2 or el_1 != el_2):
                #move_pointer(target_speed, az_1, az_2,dist_1_to_2, el_1, el_2, alt_change)
            h,v = get_degrees('default')
            print('Pointing at Az: {} El: {}'.format(h,v))
            f.write('\nPointing at Az: {} El: {}'.format(h,v))
            f.write('\n---------------------------------------------------------------------------------')
            print('------------------------------------------------------------------------------------')           
            #making the new position equal the old position for reference to the next calculation when the new coordinate is received     
            
            
if __name__ == "__main__": 
    # creating thread 
    t1 = threading.Thread(target=read_calculate_preplanned) 
    #t1 = threading.Thread(target=read_calculate_telem) 
    #t2 = threading.Thread(target=telem_track)
    t2 = threading.Thread(target=pre_planned)
    
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
