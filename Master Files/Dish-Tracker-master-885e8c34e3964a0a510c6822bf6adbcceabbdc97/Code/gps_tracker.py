from qpt_v2 import*
import math
import time
from geopy.distance import vincenty

#ser = serial.Serial('/dev/ttyUSB0',9600) #serial connection for the receiver module
Current_Location = [0,0]
#qpt = serial.Serial(port='/dev/ttyUSB1',baudrate=9600,timeout=1) ---> established in the qpt_v2 file that is imported



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
    '''Read GPS from arduino'''
    while (ser.inWaiting() >= 0):
        new_altitude = ser.readline().decode()
        for x in range(0, len(Current_Location)):
            Current_Location[x] = ser.readline().decode()
            new_target_lat = Current_Location[0]
            print("NEW TARGET LAT:", new_target_lat)
            new_target_lon = Current_Location[1]
            print("NEW TARGET LON:", new_target_lon)
        break
    print(new_target_lat,new_target_lon,new_altitude )
    return new_target_lat, new_target_lon, new_altitude
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
    azimuth = math.atan2(x,y)
    azimuth = azimuth * 57.9218
    #if(x < 0):
    #   azimuth = (math.atan2(x,y))    
    return azimuth
#======================================================================================================= 
def compute_elevation_angle( flat_dist , alt ):
    '''Compute elevation angle'''
    ''' ****important**** 
        currently im returning the negated number of pointer elevation.
        this is because on our current stand, when the tilt goes UP, it heads towards the south
        (positive numbers and when the tilt goes down, it heads to the north (negative tilt numbers)
        to revert to normal, just take the - sign out
    '''    
    # elev_dis is the distance from the stand to the point, including its elevation(its hypotneuse)
    # flat_dis is the distance from the stand to the point, in a straight line on the ground.
    # elev_dis should always be bigger than flat_dist, unless the altitude is 0
    #elev_dist = math.sqrt(flat_dist**2 + float(alt)**2)   
    val1 = float(alt)/flat_dist
    elevation = math.degrees((math.atan(val1))) #if it doesn't work try asin (another source)
    pointer_elevation = 90 - elevation
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
            if cur_pos_x <= az_pos:
                return True
            else: 
                return False    
        else:
            if cur_pos_x >= az_pos:
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
            if cur_pos_y <= el_pos:
                return True
            else: 
                return False    
        else:
            if cur_pos_y >= el_pos:
                return True  
            else: 
                return False    
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
     
    def to_angular_speed(el1 , el2 , az1 , az2 , tar_spd , dist_1_to_2 , alt_change):
           
            # Determines Clockwise or Counterclockwise for pan
            cw = False
            if(az1 < az2):
                cw = True      
            # Determines Speed stand needs to move during timeframe that it will take to move from point 1 to point 2     
            az_deg_change = az1 - az2
            time_az = dist_1_to_2/float(tar_spd)
            print("Time for azimuth change is:", time_az )
            angular_speed_az = abs(az_deg_change/time_az)          
           # Determines Up or Down for pan
           # Currently going down is into the negative degrees, but also in the northward direction(what we want)
           # going up is into the positive degrees, but southward direction.
            up = False
            if(el1 < el2):
                up = True
            
            # computes change in elevation angle for stand
            el_deg_change = el1 - el2
            # computes the distance between point 1 and 2, with their elevation included.
            elev_dist = math.sqrt(dist_1_to_2**2 + float(alt_change)**2)
            #print("Total Distance from p1 to p2 is: ", dist_1_to_2)
            #print("Total Distance including elevation is : ", elev_dist)
            #print("ALT CHANGE IS: ", alt_change)
            #print("tar_spd is: ", tar_spd)
            time_el = elev_dist/float(tar_spd)
            print("Time for elevation change is:", time_el )
            angular_speed_el = abs(el_deg_change/time_el)
            #print("ANGULAR SPEED FOR AZIMUTH TURNING IS:", angular_speed_az)
            #print("DIRECTION IS: ", cw)
            #print("ANGULAR SPEED FOR ELEVATION IS:", angular_speed_el)
            #print("DIRECTION IS: ", up)
            return angular_speed_az, cw, angular_speed_el, up
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #Adjust movement speed and create move message 
    def adjust_speed(r_el, n_el,r_az,n_az,tar_spd,dist_1_to_2,alt_change):
        
        #call to_angular_speed
        ang_target_speed_az , cw , ang_target_speed_el , up = to_angular_speed(r_el,n_el,r_az,n_az,tar_spd,dist_1_to_2,alt_change)

        #-------------------------------------------        
        #print(" cw is : ", cw)
        #print(" up is : ", up)
        if(cw is True):
        
            # Accomodates for huge speeds and adjusts to max speed for stand
            if ang_target_speed_az > 32:
                ang_target_speed_az = 32
            # Accomodates for very small speeds and adjust to min speed for stand
            elif ang_target_speed_az < 1:
                ang_target_speed_az = 1     
            speed_az = (2*(4*int(ang_target_speed_az)-1)+1)#clockwise message (odd number)
          
        else:
            if ang_target_speed_az > 32:
                ang_target_speed_az = 32      
            elif ang_target_speed_az < 1:
                ang_target_speed_az = 1        
            speed_az =(2*(4*int(ang_target_speed_az)-1)) #counter-clockwise message (even number)           
               
        #---------------------------------------------    
        if(up is True):
        
            # Accomodates for huge speeds and adjusts to max speed for stand
            if ang_target_speed_el < 32:
                ang_target_speed_el = 32
            # Accomodates for very small speeds and adjust to min speed for stand
            elif ang_target_speed_el > 1:
                ang_target_speed_el = 1
            speed_el = (2*(4*int(ang_target_speed_el)-1)+1)#clockwise message (odd number)
          
        else:
            # Accomodates for huge speeds and adjusts to max speed for stand
            if ang_target_speed_el > 32:
                ang_target_speed_el = 32
            # Accomodates for very small speeds and adjust to min speed for stand
            elif ang_target_speed_el < 1:
                ang_target_speed_el = 1  
            speed_el = (2*(4*int(ang_target_speed_el)-1)) #counter-clockwise message (even number)
            
        print(speed_az, speed_el)
        print(ang_target_speed_az,ang_target_speed_el)             
        return ( speed_az , speed_el , cw, up )         
        
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        
    def speed_msg( speed_az , speed_el , cw , up ):           
        #print("AZ SPEED IS: ",speed_az)
        #print("EL SPEED IS: ",speed_el)
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
        return (move_msg)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
  
    #call adjust speed to get the correct speed and move message
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

    while(pan_move and tilt_move):
        qpt.write(command)
        time.sleep(.01)
        current_az, current_el = get_degrees(command)
        pan_move = not_there_az(current_az , new_az , cw)
        tilt_move = not_there_el(current_el , new_el , up)  
                
    if(pan_move is False and tilt_move is True):
        #print("Pan stopping, tilt continuing")
        command = speed_msg( 0 , speed_el , cw , up )
        while(tilt_move):
            qpt.write(command)
            print(qpt.readline())
            #time.sleep(.01)
            current_az, current_el = get_degrees(command)
            tilt_move = not_there_el(current_el , new_el , up)
                          
    elif(pan_move is True and tilt_move is False):
        #print("Tilt stopping, pan continuing")
        command = speed_msg( speed_az , 0 , cw , up )
        while(pan_move):
            qpt.write(command)
            #time.sleep(.01)
            current_az, current_el = get_degrees(command)            
            pan_move = not_there_az(current_az , new_az , cw)
    
    stop_move() 
    
#=======================================================================================================
#=======================================================================================================
#=======================================================================================================

def preplanned_track():
    
    """Tracks based on constant speed and gps coordinates from a file"""
    #filename = input('Enter the GPS file name: ')
    filename =  '/home/pgsc/Dish-Tracker/Dish-Tracker/Code/test_gps_data_2.txt'
    gps_file = open(filename, "r")
    #pos_lat, pos_lon = start_up() #read from Garmin module
    pos_lat = 43.219409
    pos_lon = -75.408620
    start = True
    gps_file = open(filename, "r")
    for line in gps_file:
      
        # Runs the first time, to position the stand towards the first lat and long point
        # data is being read from a csv file, with the format: latitude,longitude,elevation,speed
         
        if start == True:
            data = line.split(',')
            lat_1 = data[0]
            lon_1 = data[1]
            alt_1 = data[2]
            target_speed = data[3]
            dist_1 = compute_distance(pos_lat,pos_lon,lat_1,lon_1)
            el_1 = compute_elevation_angle(dist_1, alt_1)     
            az_1 = compute_azimuth(lon_1,lat_1,pos_lon, pos_lat)
            start_az, start_el = get_degrees('default')
            while (start_az != int(az_1) and start_el != int(el_1)):
                move_to_position(az_1,el_1)
                start_az, start_el = get_degrees('default')
            gps_file = open(filename, "r")
            start = False      
          
        # Main looping portion of preplanned pathing. Essentially this will take data from a csv file,
        # and calculate elevations, distances and azimuth headings from the stand, to the two points.
        # It then will move the stand to the desired azimuth heading, and tilt angle to keep the antenna, dish etc
        # alligned with whatever it is tracking on the preplanned path. 
        # Right now this code will run from point 1 to point 2, then after it is done moving from 1 to 2,
        # it sets point 2 as point 1, and reads from the file to get another point 2. So it reads points,
        # does the calculations, swaps the points, casting off the old point 1, and repeats for all points
        # in the file.
          
        if start == False:
            data = line.split(',')
            lat_2 = data[0]
            lon_2 = data[1]
            alt_2 = data[2]
            target_speed = data[3]
            pos_az,pos_el = get_degrees('default')
            dist_2 = compute_distance(pos_lat , pos_lon , lat_2 , lon_2)
            dist_1_to_2 = compute_distance(lat_1, lon_1 , lat_2 , lon_2)
            alt_change = float(alt_1) - float(alt_2)                               
            el_1 = compute_elevation_angle(dist_1, alt_1)
            el_2 = compute_elevation_angle(dist_2, alt_2) 
            az_1 = compute_azimuth(lon_1,lat_1,pos_lon,pos_lat)
            az_2 = compute_azimuth(lon_2,lat_2,pos_lon,pos_lat)          
            print("Azimuth Angle 1: ",az_1,"Azimuth Angle 2: ",az_2,"Elevation Angle 1: ",el_1,"Elevation Angle 2: ",el_2)
            
            if az_1 != az_2 or el_1 != el_2:
                move_pointer(target_speed, az_1, az_2,dist_1_to_2, el_1, el_2, alt_change)
                
            print("Latitude 1: ", lat_1,"Longitude 1: ",lon_1,"Latitude 2: ",lat_2,"Longitude 2: ", lon_2,"Altitude 1: ", alt_1, "Altitude 2: ", alt_2)
            lat_1 = lat_2
            lon_1 = lon_2
            alt_1 = alt_2
            dist_1 = dist_2
            
    gps_file.close()
    
    
#======================================================================================================= 
#======================================================================================================= 
#======================================================================================================= 

def main():
     
    preplanned_track()
        
if __name__ == '__main__':
    main()
    
    
    
