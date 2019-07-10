#import qpt_v2
from qpt_v2 import*
import math
import time
import serial
from geopy.distance import vincenty


ref_gps_lat = 43.220735 # Latitude of the antenna, grab from germin gps
ref_gps_lon = -75.407593 # longitude of the antenna, grab from garmin gps
#lat_pointer = Latitude of antenna pointer
#lon_pointer = Longitude of antenna pointer
target_speed = 95  #meters per second for a U-27A
Current_Location = [0, 0] # GPS location of the target
ser = serial.Serial('/dev/ttyUSB0',9600)
qpt = serial.Serial(port='/dev/ttyUSB1',baudrate=9600,timeout=1)

#starting at 0,0
cur_azimuth = 0
cur_elevation = 0

def gps_to_degrees(lon2, lat2):
    """Converts GPS coordinates into the degrees (azimuth angle) """
    #x will be longitude of target and y will be latitude of target
    x = float(lon2)-ref_gps_lon 
    y = float(lat2)-ref_gps_lat
    az_deg = 0
    #print (x,y)
    if(x == 0 and y == 0):
        print ("Error, x and y value cannot be zero at the same time")
        #for testing purposes 
        x = float(input("Enter Longitude: "))
        y = float(input("Enter Latitude: "))
        #actual program will wait for another gps location to be transmitted 
        #return ("waiting for valid coordinates")
    else:
        print("Coordinates received")
    
    #each condition for the x and y using atan2(y,x) properties 
    if(x == 0 and y > 0):
        az_deg = math.degrees(0)       
    elif(x == 0 and y < 0):
        az_deg = math.degrees(math.pi) #or az_deg = math.degrees(-math.pi)
    elif(x < 0 and y == 0):
        az_deg = math.degrees((-math.pi)/2)
    elif(x > 0 and y == 0):
        az_deg = math.degrees((math.pi)/2)
    elif(x > 0 and y > 0): 
        val = y/x
        az_deg = math.degrees(math.atan(val))
    elif(x > 0 and y < 0):
        val = y/x
        az_deg = math.degrees((math.atan(val))+math.pi)
    elif(x < 0 and y > 0):
        val = y/x
        az_deg = math.degrees(math.atan(val)) - 360
    elif(x < 0 and y < 0):
        val = y/x
        az_deg = math.degrees((math.atan(val))-math.pi) + 360
    
    #print ("Latitude: " + str(lat2))
    #print ("Longitude: " + str(lon2))
    #print ("Azimuth: " + str(round(az_deg,2)))
    return az_deg
'''
Maybe a better way to find the azimuth angle (bearing) - Test out
-----------------------------------------------------------------------
def initial_bearing(pointA, pointB):

    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = radians(pointA[0])
    lat2 = radians(pointB[0])

    diffLong = radians(pointB[1] - pointA[1])

    x = sin(diffLong) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1)* cos(lat2) * cos(diffLong))

    initial_bearing = atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing
'''    
'''------------------------------------------------------------------------
Maybe need to find where the antenne is pointing and calculate rotation by finding degrees 'needed' to move in either direction. NOT only from the center as a reference. 
---------------------------------------------------------------------------
'''

def set_elevation(alt, latitude, longitude):
    """set altitude of the flight path"""
    #this will align with the altitude based on distance away and desired altitude. (Elevation angle)
    
    a = (ref_gps_lat,ref_gps_lon)
    b = (float(latitude),float(longitude))
    r_dis = vincenty(a, b).meters
    '''
    Harversine Calculation Method
    ----------------------------------------------------------------
    R = 6371 # average radius of the earth in km. Use 3956 for miles.
    x = float(longitude)-ref_gps_lon
    y = float(latitude)-ref_gps_lat
    #finding the difference between the 2 points
    diff_Lat = math.radians(x)
    diff_Lon = math.radians(y) 
    #implementation of haversine formula
    a = math.sin(diff_Lat/2)**2 + math.cos((math.radians(ref_gps_lat))) * math.cos(math.radians(float(latitude))) * math.sin(diff_Lon/2)**2
    print (a)
    c = 2 * (math.asin(math.sqrt(a))) #asin is the correct method but won't work for certain values 
    #distance in km of vector on x,y plane (2D)
    r_dis = R * c
    ''' 
    '''
    x1_km = abs((40075 * (math.cos(ref_gps_lon))) / 360) #convert longitude to km
    y1_km = abs((ref_gps_lat * 111.320)) #convert latitude to km
    x2_km =abs((40075 * (math.cos(float(longitude)))) / 360)
    y2_km = abs((float(latitude) * 111.320))
    #math.sqrt((x2_km - x1_km) + (y2_km - y1_km)) - alterantive for p_dis
    --------------------------------------------------------------
    '''
    #distance in m of vecter on x,y,z, plane (3D) at altitude
    p_dis = math.sqrt(r_dis**2 + float(alt)**2) 
    val1 = float(alt)/r_dis
    elevation = math.degrees((math.atan(val1))) #if it doesn't work try asin (another source)
    pointer_elevation = 90 - elevation #elevation of dish pointer is at 0 degrees when pointed directly up
    #print("Altitude: " + str(alt))
    #print("Distance in the x,y plane: " + str(round(r_dis,2)))
    #print("Distance in the x,y,z plane (at altitude): " + str(round(p_dis,2)))
    #print("Elevation: " + str(round(pointer_elevation,2)))
    return pointer_elevation, r_dis, p_dis



def set_speed(): 
#make set speed set the rotation speed of the positioner with byte message
    """Sets the speed of the motors on dish pointer"""
    time = 1
    while (ser.inWaiting() >= 0):
        
            
            new_altitude = ser.readline().decode()
   
            for x in range(0, len(Current_Location)):
        
                Current_Location[x] = ser.readline().decode()
                new_target_lat = Current_Location[0]
                new_target_lon = Current_Location[1]
            break 
    
    target_azimuth = gps_to_degrees(new_target_lon,new_target_lat)
    target_elevation, t_dis, q_dis = set_elevation(new_altitude, new_target_lat, new_target_lon)
   
    '''
    old method - called function instead 
    ---------------------------------------------------------------------
    x_new = float(new_target_lon)-ref_gps_lon 
    y_new = float(new_target_lat)-ref_gps_lat
    new_az_deg = 0
    #print (x,y)
    if(x_new == 0 and y_new == 0):
        print ("Error, x and y value cannot be zero at the same time")
        #for testing purposes 
        x_new = float(input("Enter Longitude: "))
        y_new = float(input("Enter Latitude: "))
        #actual program will wait for another gps location to be transmitted 
        #return ("waiting for valid coordinates")
    else:
        print("Coordinates received")
    #each condition for the x and y using atan2(y,x) properties 
    if(x_new == 0 and y_new > 0):
        new_az_deg = math.degrees(0)
    elif(x_new == 0 and y_new < 0):
        new_az_deg = math.degrees(math.pi) 
    elif(x_new < 0 and y_new == 0):
        new_az_deg = math.degrees((3*math.pi)/2)
    elif(x_new > 0 and y_new == 0):
        new_az_deg = math.degrees((math.pi)/2)
    elif(x_new > 0 and y_new > 0): 
        val = y_new/x_new
        new_az_deg = math.degrees(math.atan(val))
    elif(x_new > 0 and y_new < 0):
        val = y_new/x_new
        new_az_deg = math.degrees((math.atan(val))+math.pi)
    elif(x_new < 0 and y_new > 0):
        val = y_new/x_new
        new_az_deg = math.degrees(math.atan(val)) + 360
    elif(x_new < 0 and y_new < 0):
        val = y_new/x_new
        new_az_deg = math.degrees((math.atan(val))-math.pi) + 360
    -----------------------------------------------------------------------
    '''
    #pointer_az = 0
    #pointer_el = 0
    pointer_az, pointer_el = get_degrees()   
    print  (pointer_az, pointer_el)
    
    '''
    if (target_azimuth > 180):
        az_deg_change = (target_azimuth - pointer_az) - 360
    else:
        az_deg_change = target_azimuth - pointer_az
    '''
    el_deg_change = target_elevation - pointer_el
    az_deg_change = target_azimuth - pointer_az
    '''
    old method - called function instead 
    ----------------------------------------------------------
    a_new = (ref_gps_lat,ref_gps_lon)
    b_new = (float(new_target_lat),float(new_target_lon))
    t_dis = vincenty(a_new, b_new).meters
    q_dis = math.sqrt(t_dis**2 + float(new_altitude)**2) #math.sqrt((x2_km - x1_km) + (y2_km - y1_km)) - maybe try this one
    ----------------------------------------------------------
    '''
    '''
    Harversine Calculation Method
    ----------------------------------------------------------------
    #maybe use other formula 
    R = 6371 # average radius of the earth in km. Use 3956 for miles.
    x_hav = float(next_target_lon)-ref_gps_lon
    y_hav = float(next_target_lat)-ref_gps_lat
    #finding the difference between the 2 points
    new_diff_Lat = math.radians(x_hav) 
    new_diff_Lon = math.radians(y_hav) 
    #implementation of haversine formula
    a_new = math.sin(new_diff_Lat/2)**2 + math.cos((math.radians(current_target_lat))) * math.cos(math.radians(float(next_target_lat))) * math.sin(new_diff_Lon/2)**2
    c_new = 2 * math.asin(math.sqrt(a_new))
    #distance in km of vector on x,y plane (2D)
    t_dis = R * c_new
    --------------------------------------------------------------
    '''
    
    '''
    old method
    -------------------------------------------------------------------------------------------------------------- 
    val2 = float(current_altitude)/t_dis
    new_elevation = math.degrees((math.atan(val2))) #if it doesn't work try asin (another source)
    new_pointer_elevation = 90 - new_elevation #elevation of dish pointer is at 0 degrees when pointed directly up
    --------------------------------------------------------------------------------------------------------------
    '''
    
    
    #azimuth angular velocity of antenna (assuming speed is constant)
    '''
    old method
    ------------------------------------------------------
    #az_distance = math.sqrt(t_dis**2 - r_dis**2)
    current_pos = (current_target_lat, current_target_lon)
    new_pos = (new_target_lat, new_target_lon)
    az_distance = vincenty(current_pos,new_pos).meters
    time = az_distance/target_speed
    ang_vel_az = abs(az_deg_change/time)
    ------------------------------------------------------
    '''
    ang_vel_az = abs(az_deg_change/time)
    
    #elevation angular velocity of antenna (assuming speed is constant)
    '''
    old method
    --------------------------------------------------------------------------------------
    altitude_change = float(new_altitude) - float(current_altitude)
    el_distance = az_distance                              #math.sqrt(q_dis**2 - p_dis**2)
    time = el_distance/target_speed
    ang_vel_el = abs(az_deg_change/time)
    --------------------------------------------------------------------------------------
    '''
    ang_vel_el = abs(el_deg_change/time)
    
    print ("Latitude: ", new_target_lat)
    print ("Longitude: ", new_target_lon)
    print("Altitude: ", new_altitude)
    print ("Azimuth: ", round(target_azimuth,2))
    print("Elevation: ", round(target_elevation,2))
    print("Distance in the x,y plane: ", round(t_dis,2))
    print("Distance in the x,y,z plane (at altitude): ", round(q_dis,2))
    print("azimuth angluar velocity: ", ang_vel_az)
    print("elevation angular velocity: ", ang_vel_el) 
    print("elevation degree change: ", el_deg_change) 
    print("azimuth degree change:", az_deg_change)
    
    return ang_vel_az, ang_vel_el, el_deg_change, az_deg_change, target_azimuth, target_elevation
    
    
if __name__ == '__main__':
    #alt is given (for testing purposes) - maybe have it transmitted like the GPS coordinates for calulations in real time if decreasing or increasing in alt
    #put a check for negative altitudes unless the altitude of the antenna could possibly be higher than the target 
    #altitude = float(input('Enter the tracking altitude in km: '))
    #print (altitude)
    #receive GPS coordinates
    while True:
        
        #altitude = float(input('Enter the tracking altitude in km: '))
        '''
        while (ser.inWaiting() >= 0):
        
            
            current_altitude = ser.readline().decode()
   
            for x in range(0, len(Current_Location)):
        
                Current_Location[x] = ser.readline().decode()
                current_target_lat = Current_Location[0]
                current_target_lon = Current_Location[1]
            break 
        '''
        #az_deg = gps_to_degrees(current_target_lon, current_target_lat)
        
        #pointer_elevation, r_dis, p_dis = set_elevation(current_altitude, current_target_lat, current_target_lon)
        
        
        
        ang_vel_az, ang_vel_el, el_deg_change, az_deg_change, target_azimuth, target_elevation  = set_speed()
        
        #to_center()
        
        cur_azimuth, cur_elevation = move_to_position(target_azimuth, target_elevation)
    
        #time.sleep(.1)
    '''
    in order to turn the antenna the desired degrees - maybe? fix with if structures for quicker rotations (CW or CCW)
    ---------------------------
    current_deg = get_degrees()
    desired_deg = (az_deg - current_degree)
    ---------------------------
    '''
    #if (az_deg_change < 0):
        #antenna will move anticlockwise @ ang_vel
    #else:
        #antenna will move clockwise @ ang_vel
    #keep this in a loop

    
    

