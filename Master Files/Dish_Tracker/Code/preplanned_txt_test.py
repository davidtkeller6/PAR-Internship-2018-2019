'''
def preplaned_track():
    """Tracks based on constant speed and gps coordinates from a file"""
    filename = input('Enter the GPS file name: ')
    filename =  '/home/pgsc/Desktop/gpscoordinates.txt'
    gps_file = open(filename, "r")
    #pos_lat, pos_lon = start_up() #read from Garmin module
    pos_lat = 43.220735
    pos_lon = -75.407593
    time = 1 #not sure about this time piece yet
    i = file_len(filename)
    count_limit = i
    print(count_limit)
    count = 0
    while (count<count_limit):
        data_str = gps_file.readline() #reading depends on file format
        data = data_str.split(',')
        lat = data[0]
        lon = data[1]
        alt = data[2]
        speed = data[3]
        target_speed = data[3]
        print("lat is: ", data[0])
        print("lon is: ", data[1])
        print("alt is: ", data[2])
        print("speed is: ", data[3])
        
        count += 1
        
def file_len(filename):
    with open(filename) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
''' 
   
def preplaned_track():
    """Tracks based on constant speed and gps coordinates from a file"""
    filename = input('Enter the GPS file name: ')
    filename =  '/home/pgsc/Desktop/gpscoordinates.txt'
    gps_file = open(filename, "r")
    i = file_len(filename)
    count_limit = i
    count = 0
    start = True
    while (count < count_limit):
        if(start == True):
            #gps_file = open(filename, "r")
            data_str = gps_file.readline() #reading depends on file format
            data = data_str.split(',')
            lat1 = data[0]
            lon1= data[1]
            alt1 = data[2]
            speed1 = data[3]
            az1 = compute_azimuth(lon1, lat1, ref_lon, ref_lat)
            r_dis = compute_distance(ref_lat,ref_lon,lat1,lon1)
            el1 = compute_elevation(r_dis, alt)
            start = False
            count += 1
        else:
            data_str = gps_file.readline() #reading depends on file format
            data = data_str.split(',')
            lat2 = data[0]
            lon2= data[1]
            alt2 = data[2]
            speed2 = data[3]
            az2 = compute_azimuth(lon2, lat2, ref_lon, ref_lat)
            r_dis = compute_distance(ref_lat,ref_lon,lat2,lon2)
            el2 = compute_elevation(r_dis, alt)
            count += 1
            print("Previous Point Lat: ", lat1)
            print("Previous Point Lon: ", lon1)
            print("Previous Altitude: ", alt1)
            print("Previous Speed: ", speed1)
            print("Next Point Lat: ", lat2)
            print("Next Point Lon: ", lon2)
            print("Next Altitude: ", alt2)
            print("Next Speed: ", speed2)
            lat1 = lat2
            lon1 = lon2
            alt1 = alt2
            speed1 = speed2
    
     
     
def file_len(filename):
    #filename = input('Enter the GPS file name: ')
    #filename =  '/home/pgsc/Desktop/gpscoordinates.txt'
    #gps_file = open(filename, "r")
    with open(filename) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


        
preplaned_track()

