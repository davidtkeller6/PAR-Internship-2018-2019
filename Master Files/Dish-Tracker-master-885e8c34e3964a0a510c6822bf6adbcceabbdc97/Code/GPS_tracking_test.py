import time
import math
from geopy.distance import vincenty

def compute_azimuth(new_lon,new_lat,pos_lon, pos_lat):
    """Computes azimuth angle"""
    #compute lon components
    a = (0,pos_lon)
    b = (0,new_lon)
    x = vincenty(a, b).meters
    #compute lat components
    c = (pos_lat,0)
    d = (new_lat,0)
    y = vincenty(c, d).meters    
    azimuth = math.atan2(x,y)
    azimuth = azimuth * 57.9218
    #if(x < 0):
    #   azimuth = (math.atan2(x,y))   
    return azimuth

def compute_azimuth2(new_lon,new_lat,ref_lon, ref_lat): #same result as function above
    '''Compute azimuth angle'''
    x = float(new_lon)-ref_lon
    y = float(new_lat)-ref_lat
    azimuth = math.atan2(x,y)
    azimuth = azimuth * 57.9218
    #if(x < 0):
    #   azimuth = (math.atan2(x,y))   
    return azimuth

start = time.time()
time.sleep(1)
end = time.time()

print((end - start))

ref_lat = 43.035047
ref_lon = -75.647514
ref_alt = 0
start_time = 0

filename =  '/home/pgsc/Dish-Tracker/Goodbody/Alion_Data/drone_test1_c_band.csv'
gps_file = open(filename, "r")
#pos_lat, pos_lon = start_up() #read from Garmin module
gps_file = open(filename, "r")

count = 0
first_pass = True
for line in gps_file:
    data = line.split(',')
    hr = data[0]
    minute = data[1]
    sec = data[2]
    lat = data[3]
    lon = data[4]
    est_lat = data[5]
    est_lon = data[6]
    alt = data[7]
    yaw = data[8]
    pitch = data[9]
    roll = data[10]
    sync = data[11]
    freq_offset = data[12]
    payload_errors = data[13]
    rssi_1 = data[14]
    rssi_2 = data[15]
    delta = data[16]
    dist = data[17]
    az = data[18]
    alt_2 = data[19]
    if(first_pass is False):
        computed_az = compute_azimuth(float(lon),float(lat),ref_lon, ref_lat)
        if(computed_az < 0):
            computed_az = computed_az + 180
        print('Computed1:    ', computed_az, '| Actual:    ',az)
    first_pass = False
    if count == 500: #choose what points to look at
        break
    count+=1
gps_file.close()


