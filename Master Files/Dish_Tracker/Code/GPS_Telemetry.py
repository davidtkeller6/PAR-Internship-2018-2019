from qpt_v2 import*
import math
import time
from geopy.distance import vincenty

ser = serial.Serial('/dev/ttyACM0',9600) #serial connection for the receiver module
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
    """Read GPS from telemetry link with arduino"""
    data_raw = ser.readline().decode()
    data = data_raw.split(',')
    new_target_lat = data[0]
    new_target_lon = data[1]
    new_altitude = data[2]
    print(new_target_lat,new_target_lon,new_altitude )
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

def move_pointer(tar_spd,ref_az,new_az,dist,ref_el,new_el,alt_diff): 
    
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
        if(cw is True):
              speed_az = 5  
        else:
            speed_az = 4
        #Tilt speed
        if(up is True):
            speed_el = 5
        else:
            speed_el = 4

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
 
    #call adjsut speed to get the correct speed and move message
    print("ALT IN ORIGINAL FUNCTION IS: ", alt_diff)
    command , cw, up = adjust_speed(ref_el,new_el,ref_az,new_az,tar_spd,dist,alt_diff)
    current_az = ref_az
    current_el = ref_el
    #qpt.write(command) 
    while(not_there(current_az,new_az,cw,current_el,new_el,up)):
        qpt.write(command)
        #time.sleep(.01)
        current_az, current_el = get_degrees(command)
    stop_move()
 
#===========================================================================================
def telem_track():
    """Tracks based on constant speed and gps coordinates from a file"""
    #pos_lat, pos_lon = start_up() #read from Garmin module
    pos_lat = 43.219409
    pos_lon = -75.408620
    start = True
     
    if start == True:
        lat_1, lon_1, alt_1 = get_new_GPS()
        target_speed = 1
        dist_1 = compute_distance(pos_lat,pos_lon,lat_1,lon_1)
        el_1 = compute_elevation(dist_1, alt_1) 
        print("El_1 =", el_1)   
        az_1 = compute_azimuth(lon_1,lat_1,pos_lon, pos_lat)
        move_to_position(az_1,el_1)
        start = False 
         
    if start == False:
        lat_2, lon_2, alt_2 = get_new_GPS()
        target_speed = 1    
        pos_az,pos_el = get_degrees('default')
        dist_2 = compute_distance(pos_lat,pos_lon,lat_2,lon_2)
        dist_1_to_2 = compute_distance(lat_1, lon_1,lat_2,lon_2)
        alt_diff = float(alt_1) - float(alt_2)           
        if alt_diff is 0:
            alt_diff = 1  
        el_2 = compute_elevation(dist_2, alt_2)
        el_1 = compute_elevation(dist_1, alt_1)
        az_1 = compute_azimuth(lon_1,lat_1,pos_lon,pos_lat)
        az_2 = compute_azimuth(lon_2,lat_2,pos_lon,pos_lat)         
        print("Azimuth 1: ",az_1,"Azimuth 2: ",az_2)
        print("Elevation 1: ",el_1,"Elevation 2: ",el_2)
           
        if az_1 != az_2 or el_1 != el_2:
            move_pointer(target_speed, az_1, az_2,dist_1_to_2, el_1, el_2, alt_diff)
               
        print("Latitude 1: ", lat_1,"Longitude 1: ",lon_1,"Latitude 2: ",lat_2,"Longitude 2: ", lon_2,"Altitude 1: ", alt_1, "Altitude 2: ", alt_2)
        lat_1 = lat_2
        lon_1 = lon_2
        alt_1 = alt_2
        dist_1 = dist_2
        #print("Latitude 1: ", lat_1,"Longitude 1: ",lon_1,"Latitude 2: ",lat_2,"Longitude 2: ", lon_2,"Altitude 1: " alt_1, "Altitude 2: ", alt_2)
   
def main():
    """Run tracker"""
    telem_track()
    
if __name__ == '__main__':
    main()

