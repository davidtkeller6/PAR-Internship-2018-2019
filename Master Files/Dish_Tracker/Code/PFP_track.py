from qpt_v2 import*
import math
import time

ref_gps_lat = 43.220735
ref_gps_lon = 75.407593
altitude = 10 #currently a static value, in meters, needs to change
speed = 95  #meters per second for a U-27A

def file_len(fname):
    """Finds number of lines in file (# gps coordinates)"""
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def set_speed(target_speed, lat1, lon1, lat2, lon2, new_az): #make set speed set the rotation speed of the positioner with byte message
    """Sets the speed of the motors on dish pointer"""
    current_az, current_el = 0
    x = float(lon2)-lon1
    y = float(lat2)-lat1
    x_dist = x*float(0.011/0.0001)
    y_dist = y*float(0.008/0.0001)
    distance = math.sqrt((math.pow(x_dist,2) + math.pow(y_dist,2)))*3280.84 #distance in feet
    time = (distance/3.28084)/target_speed #want distance in meters since target speed is meters per second
    current_az, current_el = get_degrees()
    angle = new_az - current_az #degrees needed to move from current position to new position
    rotate_speed = angle/time #in degrees per second
    return rotate_speed

def set_elevation(alt, latitude, longitude):
    """set altitude of the flight path"""
    #this will align with the altitude based on distance away and desired altitude
    x = float(longitude)-ref_gps_lon 
    y = float(latitude)-ref_gps_lat
    x_dist = x*float(0.011/0.0001)
    y_dist = y*float(0.008/0.0001)
    distance = math.sqrt((math.pow(x_dist,2) + math.pow(y_dist,2)))*1000.0 #distance in meters --> use 3280.84 for feet
    elevation = ((math.atan2(alt,distance)*360)/(2*math.pi))
    pointer_elevation = 90 - elevation #elevation of dish pointer is at 0 degrees when pointed directly up
    print(pointer_elevation)
    return pointer_elevation
    
def gps_to_degrees(lat,lon):
    """Converts GPS coordinates into the degrees that needs to be moved"""
    #x will be azimuth in degrees and y will be elevation in degrees
    x = 0
    y = 0
    #print(lat,lon)
    x = float(lon)-ref_gps_lon 
    y = float(lat)-ref_gps_lat
    val = y/x
    az_deg = (math.atan(val) * 180) / (2*math.pi)
    return az_deg
    
if __name__ == '__main__': 
    altitude = input('Enter the tracking altitude: ')
    filename = input('Enter the GPS file name: ')
    #filename = '/home/pgsc/Desktop/Dish Pointer Stuffs/sample_file.txt'
    filename =  '/home/pgsc/Dish-Tracker/Dish-Tracker/Code/test_gps_data.txt'
    #open file in read only --> file contains GPS and altitude coordinates
    gps_file = open(filename, "r")
    az = 0
    el = 0
    count_limit = file_len(filename)
    print(count_limit)
    count = 0
    while (count<count_limit):
        lat = gps_file.readline(9)
        space = gps_file.readline(1)
        lon = gps_file.readline(10) #currerntly doesnt deal with negatives, so will only work in north america
        az = gps_to_degrees(lat,lon) #lat and lon in decimal representation
        el = set_elevation(400, lat, lon) #altitude in feet, lat and lon in decimal representation
        print(az, el)
        count+=1
        #set_speed(speed, lat1, lon1, lat2, lon2, az) #---------needs two lat and lon poisitions which means make file line count 1 less
        move_to_position(az, el)
        time.sleep(3)
        #need to figure out the delay time in between points
    gps_file.close()
    
    
    


