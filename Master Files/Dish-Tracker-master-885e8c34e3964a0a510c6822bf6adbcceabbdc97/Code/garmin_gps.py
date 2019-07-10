import serial

#####FUNCTIONS#############################################
#initialize serial connection 
def init_serial():
    """Initializes a serial USB device for reading."""
    COMNUM = 4
    ser = serial.Serial()
    ser.baudrate = 4800
    ser.port = ('COM4')
    ser.port = '/dev/ttyUSB0'
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

def main( ser ):
    while 1:
        bytes = str(ser.readline())
        if 'GGA' in bytes:
            output = gga_to_dict( bytes )
            print( output )

if __name__ == '__main__':
    ser = init_serial()
    if ser is not None:
        main(ser)
    else:
        print( 'Could not open serial device.' )

