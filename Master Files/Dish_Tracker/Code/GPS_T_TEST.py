from qpt_v2 import*
import math
import time
from geopy.distance import vincenty

ser = serial.Serial('/dev/ttyS0',9600) #serial connection for the receiver module
Current_Location = [0,0,0]
#qpt = serial.Serial(port='/dev/ttyUSB1',baudrate=9600,timeout=1) ---> established in the qpt_v2 file that is imported
#cw = False
#up = False

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
    '''Read GPS from pi'''
    '''
    while(ser.inWaiting() >= 0):
        for x in range(0, len(Current_Location)):
            Current_Location[x] = ser.readline().decode()
            new_target_lat = Current_Location[0]
            #print("NEW TARGET LAT:", new_target_lat)
            new_target_lon = Current_Location[1]
            #print("NEW TARGET LON:", new_target_lon)
            new_altitude = Current_Location[2]
        break
    '''
    #ser.flushInput()
    #time.sleep(0.5)
    
    Current_Location = ser.readline().decode()
    print(Current_Location.split(',')[0])
    new_target_lat = float(Current_Location.split(',')[0])
    new_target_lon = float(Current_Location.split(',')[1])
    new_altitude = float(Current_Location.split(',')[2])
    #print('Latitude:' + str(new_target_lat))
    #print('Longitude:' + str(new_target_lon))
    #print('Altitude:'+ str(new_altitude))
    #print(new_target_lat,new_target_lon,new_altitude )
    return new_target_lat, new_target_lon, new_altitude
#=======================================================================================================
def compute_distance(ref_lat,ref_lon,tar_lat,tar_lon):
    """Computes distance from pointer to target"""
    a = (ref_lat,ref_lon)
    b = (float(tar_lat),float(tar_lon))
    #print(tar_lat,tar_lon,ref_lat,ref_lon)
    dis = vincenty(a, b).meters
    return dis
#=======================================================================================================    
def compute_azimuth(new_lon,new_lat,ref_lon, ref_lat):
    """Compute azimuth angle"""
    x = float(new_lon)-ref_lon
    y = float(new_lat)-ref_lat
    azimuth = math.atan2(x,y)
    azimuth = azimuth * 57.9218
    #if(x < 0):
    #   azimuth = (math.atan2(x,y))   
    return azimuth
#=======================================================================================================
def compute_elevation(r_dis, alt):
    """Compute elevation angle"""
    p_dis = math.sqrt(r_dis**2 + float(alt)**2)
    val1 = float(alt)/r_dis
    elevation = math.degrees((math.atan(val1))) #if it doesn't work try asin (another source)
    pointer_elevation = 90 - elevation
    return pointer_elevation
#=======================================================================================================

def move_pointer(tar_spd , ref_az , new_az , dist_1_to_2 , ref_el , new_el , alt_change):  
    
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
    
    def direction_speed(r_el, n_el,r_az,n_az,tar_spd,dist,alt_change):
        cw = False
        if(r_az < n_az):
            cw = True  
        
        up = False
        if(r_el < n_el):
            up = True                
        #Azimuth speed
        if(cw is True):
              speed_az = 5  
        else:
            speed_az = 4
        #Tilt speed
        if(up is True):
            speed_el = 5
        else:
            speed_el = 4
        return speed_az, speed_el, cw, up
    
    def speed_msg(speed_az, speed_el, cw, up):      
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
        print(move_msg)
        return move_msg
   
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
  
    #call adjust speed to get the correct speed and move message
    #cw, up = direction(az_1, az_2, el_1, el_2)
    speed_az, speed_el, cw, up = direction_speed(ref_el,new_el,ref_az,new_az,tar_spd,dist,alt_change)
    command = speed_msg(speed_az, speed_el, cw, up)

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
        #print("INSIDE PAN AND TILT LOOP")    
                
    if(pan_move is False and tilt_move is True):
        print("Pan stopping, tilt continuing")
        command = speed_msg( 0 , speed_el , cw , up )
        while(tilt_move):
            qpt.write(command)
            time.sleep(.01)
            current_az, current_el = get_degrees(command)
            tilt_move = not_there_el(current_el , new_el , up)
                          
    elif(pan_move is True and tilt_move is False):
        print("Tilt stopping, pan continuing")
        command = speed_msg( speed_az , 0 , cw , up )
        while(pan_move):
            print("in pan loop, tilt has stopped")
            qpt.write(command)
            time.sleep(.01)
            current_az, current_el = get_degrees(command)            
            pan_move = not_there_az(current_az , new_az , cw)
    
    stop_move()
     
#=========================================================================================== 
'''
def move_pointer2(tar_spd,ref_az,new_az,dist,ref_el,new_el,alt_diff): 
    
    def not_there(cur_pos_x, az_pos, cw, cur_pos_y, el_pos, up):
        """Checks to see if at position""" 
        # To deal with random error from get_degrees() sending values in the 6000's
        if cur_pos_x > 360 or cur_pos_x < -360:
            return True
        # Continues to loop as long as stand needs to rotate to get to new azimuth angle 
        if cw is True:
            if cur_pos_x <= az_pos:
                return True
        elif cw is False:
            if cur_pos_x >= az_pos:
                return True 
        else:
            return False
        # To deal with random error from get_degrees() sending values in the 6000's
        if cur_pos_y > 180 or cur_pos_y < -180:
            return True
        # Continues to loop as long as stand needs to rotate to get to the new elevation angle 
        if up is True:
            if cur_pos_y <= el_pos:
                return True
        elif up is False:
            if cur_pos_y >= el_pos:
                return True 
        else:
            return False
    #----------------------------------------------
    def adjust_move(r_el, n_el,r_az,n_az,tar_spd,dist,alt_diff):
        """Create move message"""
        #determining the direction of the antenna movement
        cw = False
        if(r_az < n_az):
            cw = True  
        
        up = False
        if(r_el < n_el):
            up = True                
        #Azimuth speed
        if(cw is True):
              speed_az = 5  
        else:
            speed_az = 4
        #Tilt speed
        if(up is True):
            speed_el = 5
        else:
            speed_el = 4
        
        #current_az, current_el = get_degrees()
        
        #if (current_az != n_az and current_el != n_el):
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
            print(move_msg)
        return move_msg ,cw, up
        
        elif(current_az = n_az and current_el != n_el):
            STX = 0x02
            msg_type = 0x31
            ETX = 0x03
            lrc = msg_type^speed_az^speed_el
            move_msg = bytearray()
            move_msg.append(STX)
            move_msg.append(msg_type)
            move_msg.append(0)
            move_msg.append(0)#az speed
            move_msg.append(speed_el) #el speed
            move_msg.append(0)
            move_msg.append(0)
            move_msg.append(lrc)
            move_msg.append(ETX)
        
 
    #call adjsut speed to get the correct speed and move message
    #print("ALT IN ORIGINAL FUNCTION IS: ", alt_diff)
    command , cw, up = adjust_move(ref_el,new_el,ref_az,new_az,tar_spd,dist,alt_diff)
    current_az = ref_az
    current_el = ref_el
    #qpt.write(command) 
    while(not_there(current_az,new_az,cw,current_el,new_el,up)):
        qpt.write(command)
        #time.sleep(.01)
        current_az, current_el = get_degrees(command)
    stop_move()
'''
#===========================================================================================
def telem_track():
    """Tracks based on constant GPS updates"""
    #pos_lat, pos_lon = start_up() #read from Garmin module
    pos_lat = 43.219409
    pos_lon = -75.408620
    start = True
    
     
    if start == True:
        lat_1, lon_1, alt_1 = get_new_GPS()
        target_speed = 1
        dist_1 = compute_distance(pos_lat,pos_lon,lat_1,lon_1)
        el_1 = compute_elevation(dist_1, alt_1) 
        #print("El_1 =", el_1)   
        az_1 = compute_azimuth(lon_1,lat_1,pos_lon, pos_lat)
        az_1 = float(az_1)
        el_1 = float(el_1)        
        print('Latitude:' + str(lat_1))
        print('Longitude:' + str(lon_1))
        print('Altitude:'+ str(alt_1))
        print("elevation: ", el_1,"azimuth: ", az_1, "distance 1: ",dist_1)
        move_to_position(az_1,el_1)
        start = False 
         
    if start == False:
        lat_2, lon_2, alt_2 = get_new_GPS()
        target_speed = 1    
        pos_az,pos_el = get_degrees('default')
        dist_2 = compute_distance(pos_lat,pos_lon,lat_2,lon_2)
        dist_1_to_2 = compute_distance(lat_1, lon_1,lat_2,lon_2)
        alt_diff = float(alt_1) - float(alt_2)           
        if alt_change is 0:
            alt_change = 1  
        el_2 = compute_elevation(dist_2, alt_2)
        el_1 = compute_elevation(dist_1, alt_1)
        az_1 = compute_azimuth(lon_1,lat_1,pos_lon,pos_lat)
        az_2 = compute_azimuth(lon_2,lat_2,pos_lon,pos_lat)         
        print("Azimuth 1: " + str(round(az_1)) + "Azimuth 2: " + str(round(az_2)))
        print("Elevation 1: " + str(round(el_1)) + "Elevation 2: " + str(round(el_2)))
        print("dis1: " + str(round(dist_1)))
        print("dist2: " + str(round(dist_2)))
        #print("dist between: " + str(round(dist_1_to_2)))
        #print("alt diff: " + str(round(alt_diff)))      
        
        
    if (az_1 != az_2 or el_1 != el_2):
        move_pointer(target_speed, az_1, az_2,dist_1_to_2, el_1, el_2, alt_change)
        
        
        print('Latitude1: ' + str(lat_1))
        print('Longitude1: ' + str(lon_1))
        print('Altitude1: '+ str(alt_1))
        print('Latitude2: ' + str(lat_2))
        print('Longitude2: ' + str(lon_2))
        print('Altitude2: '+ str(alt_2))


               
        
        lat_1 = lat_2
        lon_1 = lon_2
        alt_1 = alt_2
        dist_1 = dist_2
        #print("Latitude 1: ", lat_1,"Longitude 1: ",lon_1,"Latitude 2: ",lat_2,"Longitude 2: ", lon_2,"Altitude 1: " alt_1, "Altitude 2: ", alt_2)
   
def main():
    """Run tracker"""
    telem_track()
    #get_new_GPS()
if __name__ == '__main__':
    while True:
        try:
            main()
        except IndexError as e:
            print(e)
            time.sleep(.1)
        #ser.flushInput()
        #time.sleep(.1)
