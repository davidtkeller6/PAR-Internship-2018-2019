import serial


gps_rec = serial.Serial(port='/dev/ttyACM0',baudrate=9600,timeout=.1)

def read_new_gps():
     """Receive new GPS coordinates"""
    Current_Location = self.ser.readline().decode()
    new_target_lat = float(Current_Location.split(',')[0])
    new_target_lon = float(Current_Location.split(',')[1])
    new_altitude = float(Current_Location.split(',')[2])
    #print('Latitude:' + str(new_target_lat))
    #print('Longitude:' + str(new_target_lon))
     #print('Altitude:'+ str(new_altitude))
    #print(new_target_lat,new_target_lon,new_altitude )
    return new_target_lat, new_target_lon, new_altitude
    
    
while True:
    print(read_new_gps)
