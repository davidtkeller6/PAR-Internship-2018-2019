from threading import Thread, Event, Lock
import serial, bluetooth, time, math
from geopy.distance import vincenty

class Joystick(Thread): #child class of thread
    def __init__(self, sock, bt):
        """Constructor"""
        Thread.__init__(self)
        self.sock = sock #socket connection to positioner
        self.bt = bt #socket connection to bluetooth
        self.CW_MSG = b'\x02\x31\x00\xA7\x00\x00\x00\x96\x03' # can substitude with making a dynamic message
        self.CCW_MSG = b'\x02\x31\x00\x96\x00\x00\x00\xA7\x03'
        self.UP_MSG = b'\x02\x31\x00\x00\x65\x00\x00\x54\x03'
        self.DOWN_MSG = b'\x02\x31\x00\x00\x54\x00\x00\x65\x03'
        self.UP_CW_MSG = b'\x02\x31\x00\xFB\xF9\x00\x00\x33\x03'
        self.DOWN_CW_MSG = b'\x02\x31\x00\xF3\xF6\x00\x00\x34\x03'
        self.UP_CCW_MSG = b'\x02\x31\x00\xF8\xF9\x00\x00\x30\x03'
        self.DOWN_CCW_MSG = b'\x02\x31\x00\xFC\xFA\x00\x00\x37\x03'
        self.STOP_MSG = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
        self.lock = Lock()
    
    def test_move(self):
        self.sock.write(self.CW_MSG)
        time.sleep(2)
        self.sock.write(self.STOP_MSG)
        print('Move Complete')        
        
    '''def read_value(self):
        """read value from joystick via BT"""
        #sock.send('1')
        char = self.bt.recv(1).decode()
        return int(char)'''
    
    def move(self):
        """Move positioner depending on joystick"""
        
        def read_value(self):
            """read value from joystick via BT"""
            char = self.bt.recv(1).decode()
            #print(char)
            return int(char)
        can_move = True #flag for joystick movement
        while True:
            if(can_move is True):
                self.lock.acquire()   # ask for lock, don't want joystick interupted
            else:
                self.lock.release()  #release lock
            value = read_value(self)
            if(value == 1 and can_move is True):
                self.sock.write(self.UP_CCW_MSG)
            elif(value == 2 and can_move is True):
                self.sock.write(self.UP_CW_MSG)
            elif(value == 3 and can_move is True):
                self.sock.write(self.DOWN_CCW_MSG)
            elif(value == 4 and can_move is True):
                self.sock.write(self.DOWN_CW_MSG)
            elif(value == 5 and can_move is True):
                self.sock.write(self.CCW_MSG)
            elif(value == 6 and can_move is True):
                self.sock.write(self.CW_MSG)
            elif(value == 7 and can_move is True):
                self.sock.write(self.UP_MSG)
            elif(value == 8 and can_move is True):
                self.sock.write(self.DOWN_MSG)
            elif(value == 9): #joystick no longer needed, break out of loop with button
                self.sock.write(self.STOP_MSG)
                if (can_move is False):
                    can_move = True
                    event.clear() #clear event flag, prevents further gps reading
                    print('joystick enabled')
                else:
                    print('Joystick disabled')
                    event.set() #set event flag, allow gps reading
                    can_move = False
                #break
            else:
                if(can_move is True):
                    self.sock.write(self.STOP_MSG)
            if(finished_event.is_set()):
                break
    
    def run(self):
        #print(self.sock, self.bt)
        self.move()
        #event.set() #set event flag for Telemetry tracker to move
        

class gps_track(Thread): #child class of Thread
    def __init__(self, sock, rx):
        """Constructor"""
        Thread.__init__(self)
        self.sock = sock #socket connection to positioner
        self.rx = rx #socket connection for 433MHz receiver
        self.filename = " "
        self.CW_MSG = b'\x02\x31\x00\xA7\x00\x00\x00\x96\x03'
        self.CCW_MSG = b'\x02\x31\x00\x96\x00\x00\x00\xA7\x03'
        self.STOP_MSG = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
        self.lock = Lock()

    def test_move(self):
        """Test move function"""
        print('Entering test_move')
        self.sock.write(self.CW_MSG)
        time.sleep(2)
        self.sock.write(self.CCW_MSG)
        time.sleep(2)
        self.sock.write(self.STOP_MSG)
        print('Done Telem Test Move')

    def get_degrees(self, msg):
        """Returns both horizontal and vertical position in degrees"""
        #read input from positioner
        self.sock.flushInput()
        pos_string = b''
        comp = b''
        if(msg == 'default'):  
            msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
        while(len(pos_string) < 7):
            self.sock.write(msg)
            pos_string = self.sock.readline()
            if(pos_string[0] != 0x06):
                pos_string = b'\x00'
                #should make it re-read string, will go back to start of while loop
        #convert the hex value to degrees for horizontal position
        if(pos_string[2] == 0x1B and pos_string[4] == 0x1B):
            #2 1b for x
            hor_deg = (((int(pos_string[5]-128))*256) + (int(pos_string[3])-128))/10
            if(pos_string[6] == 0x1B and pos_string[8] == 0x1B):
                #2 for y
                ver_deg = ((int(pos_string[9]-128)*256) + (int(pos_string[7]-128)))/10
            elif(pos_string[7] == 0x1B):
                #1 for y
                ver_deg = ((int(pos_string[8]-128)*256) + (int(pos_string[6])))/10
            elif(pos_string[6] == 0x1B):
                #1 for y, different location
                ver_deg = ((int(pos_string[8])*256) + (int(pos_string[6]-128)))/10
            else:
                #none for y
                ver_deg = ((int(pos_string[7])*256) + (int(pos_string[6])))/10
            #make correction for negative value
            if(ver_deg > 360):
                #y negative, do backwards
                ver_deg = (-1)*(65535 - ver_deg*10)/10
            
        elif(pos_string[3] == 0x1B):
            #1 for x
            hor_deg = (((int(pos_string[4])-128)*256) + (int(pos_string[2])))/10
            if(pos_string[5] == 0x1B and pos_string[7] == 0x1B):
                #2 for y
                ver_deg = ((int(pos_string[8]-128)*256) + (int(pos_string[6]-128)))/10
            elif(pos_string[6] == 0x1B):
                #1 for y
                ver_deg = ((int(pos_string[7]-128)*256) + (int(pos_string[5])))/10
            elif(pos_string[5] == 0x1B):
                #1 for y, different location
                ver_deg = ((int(pos_string[7])*256) + (int(pos_string[6]-128)))/10
            else:
                #none for y
                ver_deg = ((int(pos_string[6])*256) + (int(pos_string[5])))/10
            #make correction for negative value
            if(ver_deg > 360):
                ver_deg = (-1)*(65535 - ver_deg*10)/10
    
        elif(pos_string[2] == 0x1B):
            #1b in first location
            hor_deg = (((int(pos_string[4]))*256) + (int(pos_string[3]-128)))/10
            if(pos_string[5] == 0x1B and pos_string[7] == 0x1B):
                #2 for y
                ver_deg = ((int(pos_string[8]-128)*256) + (int(pos_string[6]-128)))/10
            elif(pos_string[6] == 0x1B):
                #1 for y
                ver_deg = ((int(pos_string[7]-128)*256) + (int(pos_string[5])))/10
            elif(pos_string[5] == 0x1B):
                #1 for y in different location
                ver_deg = ((int(pos_string[7])*256) + (int(pos_string[6]-128)))/10
            
            else:
                #none for y
                ver_deg = ((int(pos_string[6])*256) + (int(pos_string[5])))/10
            #make correction for negative value
            if(ver_deg > 360):
                #y negative, do backwards
                ver_deg = (-1)*(65535 - ver_deg*10)/10
                   
        else:
            #none for x
            hor_deg = ((int(pos_string[3])*256) + (int(pos_string[2])))/10
            if(pos_string[4] == 0x1B and pos_string[6] == 0x1B):
                #2 for y
                ver_deg = ((int(pos_string[7]-128)*256) + (int(pos_string[5]-128)))/10
            elif(pos_string[5] == 0x1B):
                #1 for y
                ver_deg = ((int(pos_string[6]-128)*256) + (int(pos_string[4])))/10
            elif(pos_string[4] == 0x1B):
                #1 for y, different location
                ver_deg = ((int(pos_string[6])*256) + (int(pos_string[5]-128)))/10
            else:
                #none for y
                ver_deg = ((int(pos_string[5])*256) + (int(pos_string[4])))/10
            #make correction for negative value
            if(ver_deg > 360):
                #y negative, do backwards
                ver_deg = (-1)*(65535 - ver_deg*10)/10
        if(hor_deg > 360):
            #rewrite for negative x
            hor_deg = (-1)*(65535 - hor_deg*10)/10

        #print('At: ', hor_deg, ver_deg)
        #print(pos_string)
        #print(pos_string[0],pos_string[1],pos_string[2],pos_string[3],pos_string[4],)
        #print(' ')
        
        #return the final values of degrees
        return hor_deg, ver_deg

    def move_to_position(self, x_origional,y_origional):
        """Move to a specified position"""
        def check_at_position(self):
            az1 = 1000
            el1 = 1000
            az2 = 2000
            el2 = 2000
            while True:
                time.sleep(0.2)
                az1 = az2
                el1 = el2
                az2, el2 = self.get_degrees('default')
                az_diff = abs(az1)-abs(az2)
                el_diff = abs(el1)-abs(el2)
                if( (abs(az_diff) < 1) and (abs(el_diff) < 1) ):
                    print('At position!')
                    break

        def validate(hp, xo, vp, yo):
            A = (int(hp) != int(xo))
            B = (int(hp) != int(float(xo)+0.5))
            C = (int(vp) != int(yo))
            D = (int(vp) != int(float(yo)+0.5))
            return ((A and B) or (C and D))
            
        """Move to a selected position"""
        x = float(x_origional)
        y = float(y_origional)
        x_neg = False
        y_neg = False
        if(x < 0):
            x_neg = True
        if(y < 0):
            y_neg = True
        x = abs(int(x))
        y = abs(int(y))
        #convert x degrees to bytes
        x_deg = hex(10*x)
        #convert y degrees to bytes
        y_deg = hex(10*y)
        #construct byte message
        header = 0x02
        msg_type = 0x33
        x_1 = 10*x
        x_count = 0
        while True:
            x_1 = x_1 - 256
            x_count +=1
            if(x_1 < 0):
                x_1 = x_1 +256
                x_count-=1
                break
        y_1 = 10*y
        y_count = 0
        while True:
            y_1 = y_1 - 256
            y_count +=1
            if(y_1 < 0):
                y_1 = y_1 +256
                y_count-=1
                break    
        lrc = msg_type^x_1^x_count^y_1^y_count
        #print('LRC = ' + str(lrc))
        end = 0x03
        if(x_neg is True):
            #subtract from FF
            x_1 = 255-(int(x_1))
            x_count = 255-(int(x_count))
            print('x deg: ' , x_deg)
        if(y_neg is True):
            #subtract from FF
            y_1 = 255-(int(y_1))
            y_count = 255-(int(y_count))
        #move_msg = b"".join([header,x_move,y_move,end])
        move_msg = bytearray()
        move_msg.append(header)
        move_msg.append(msg_type)
        move_msg.append(x_1)
        if((x > 50) and (x < 110) and x_neg is False):
            esc_correct = 0x1B
            x_count = x_count + 128
            move_msg.append(esc_correct)
        move_msg.append(x_count)
        move_msg.append(y_1)
        if((y > 50) and (y < 110) and y_neg is False):
            esc_correct = 0x1B
            y_count = y_count + 128
            move_msg.append(esc_correct)
        move_msg.append(y_count)
        move_msg.append(lrc)
        move_msg.append(end)
        #print('move message created: ' , move_msg)
        h_pos = 1000
        v_pos = 1000
        self.sock.write(move_msg)
        check_at_position(self)
        return x_origional, y_origional #returns entered position


    def read_new_gps(self):
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
        
    def read_from_file(self,line):
        """Read coordinates from file""" #possibly add it into run function since only used there

        data = line.split(',')
        lat = data[0]
        lon = data[1]
        alt = data[2]
        speed = data[3]
        print(data)
        return (data)
        
    def compute_distance(self, ref_lat,ref_lon,tar_lat,tar_lon):
        """Computes distance from pointer to target"""
        a = (ref_lat,ref_lon)
        b = (float(tar_lat),float(tar_lon))
        #print(tar_lat,tar_lon,ref_lat,ref_lon)
        dis = vincenty(a, b).meters
        return dis
    
    def compute_azimuth(self,new_lon,new_lat,ref_lon, ref_lat):
        """Compute azimuth angle"""
        x = float(new_lon)-ref_lon
        y = float(new_lat)-ref_lat
        #azimuth = math.degrees(math.atan2(x,y))
        azimuth = math.atan2(x,y)
        azimuth = azimuth * 57.9218
        #if(x < 0):
        #   azimuth = (math.atan2(x,y))    
        return azimuth
        
    def compute_elevation_angle(self, flat_dist , alt ):
        """Compute elevation angle"""
        val1 = float(alt)/flat_dist
        elevation = math.degrees((math.atan(val1))) 
        pointer_elevation = 87 - elevation
        return (-pointer_elevation)
        
    def move_pointer(self, tar_spd , ref_az , new_az , dist_1_to_2 , ref_el , new_el , alt_change):  
        """Moves pointer the correct direction"""
        def not_there_az(self,cur_pos_x , az_pos , cw):
            """Checks azimuth position"""
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
                       
        def not_there_el(self, cur_pos_y , el_pos , up):
            """Checks elevation positioner"""       
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

        def to_angular_speed(self, el1 , el2 , az1 , az2 , tar_spd , dist_1_to_2 , alt_change):
            """Converts linear speed of target to angular speed of positioner"""
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
#============================================================================

        def adjust_speed(self, r_el, n_el,r_az,n_az,tar_spd,dist_1_to_2,alt_change):
        
            #call to_angular_speed
            ang_target_speed_az , cw , ang_target_speed_el , up = to_angular_speed(self,r_el,n_el,r_az,n_az,tar_spd,dist_1_to_2,alt_change)

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
            
            #print(speed_az, speed_el)
            #print(ang_target_speed_az,ang_target_speed_el)             
            return ( speed_az , speed_el , cw, up )         
#==================================================================================

        def speed_msg(self, speed_az , speed_el , cw , up ): 
            """Builds speed message"""         
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
            
        #call adjust speed to get the correct speed and move message
        speed_az , speed_el , cw , up = adjust_speed(self,ref_el,new_el,ref_az,new_az,tar_spd,dist_1_to_2,alt_change)
        command = speed_msg(self, speed_az , speed_el , cw , up )
        current_az = ref_az
        current_el = ref_el
    
        # Returns a bool for pan_move and tilt_move. If one of these becomes false, then it has reached
        # Its desired angle for that movement(up, down or cw,ccw). It will then stop that movement, but if
        # The other movement is not done yet, it will continue that one. For example, if the stand needs to
        # go up and to the left, it will do so, and if it needs to go up less that it needs to go to the left,
        # It will get to the stop going up first. Therefore we want to stop the stand from going up anymore, but
        # keep it going left until it reaches its destination left. 
        pan_move = not_there_az(self,current_az , new_az , cw)
        tilt_move = not_there_el(self,current_el , new_el , up)

        while(pan_move and tilt_move):
            self.sock.write(command)
            time.sleep(.01)
            current_az, current_el = self.get_degrees(command)
            pan_move = not_there_az(self,current_az , new_az , cw)
            tilt_move = not_there_el(self,current_el , new_el , up)
                
        if(pan_move is False and tilt_move is True):
            #print("Pan stopping, tilt continuing")
            command = speed_msg(self, 0 , speed_el , cw , up )
            while(tilt_move):
                self.sock.write(command)
                print(self.sock.readline())
                #time.sleep(.01)
                current_az, current_el = self.get_degrees(command)
                tilt_move = not_there_el(self,current_el , new_el , up)
                          
        elif(pan_move is True and tilt_move is False):
            #print("Tilt stopping, pan continuing")
            command = speed_msg(self, speed_az , 0 , cw , up )
            while(pan_move):
                self.sock.write(command)
                #time.sleep(.01)
                current_az, current_el = self.get_degrees(command)            
                pan_move = not_there_az(self,current_az , new_az , cw)
            self.sock.write(self.STOP_MSG) 

#=================================================================================


    def track(self, start, data, lat_1, lon_1, alt_1,dist_1): #get data from read_from_file in run, pass in start
        """Track based on telemetry""" 
        pos_lat = 43.219409
        pos_lon = -75.408620
 
        if start == True:
            lat_1 = data[0]
            lon_1 = data[1]
            alt_1 = data[2]
            target_speed = data[3]
            dist_1 = self.compute_distance(pos_lat,pos_lon,lat_1,lon_1)
            el_1 = self.compute_elevation_angle(dist_1, alt_1)
            az_1 = self.compute_azimuth(lon_1,lat_1,pos_lon, pos_lat)
            start_az, start_el = self.get_degrees('default')
            while (start_az != int(az_1) and start_el != int(el_1)):
                self.move_to_position(az_1,el_1)
                start_az, start_el = self.get_degrees('default')
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
            lat_2 = data[0]
            lon_2 = data[1]
            alt_2 = data[2]
            target_speed = data[3]
            pos_az,pos_el = self.get_degrees('default')
            dist_2 = self.compute_distance(pos_lat , pos_lon , lat_2 , lon_2)
            dist_1_to_2 = self.compute_distance(lat_1, lon_1 , lat_2 , lon_2)
            alt_change = float(alt_1) - float(alt_2)                               
            el_1 = self.compute_elevation_angle(dist_1, alt_1)
            el_2 = self.compute_elevation_angle(dist_2, alt_2) 
            az_1 = self.compute_azimuth(lon_1,lat_1,pos_lon,pos_lat)
            az_2 = self.compute_azimuth(lon_2,lat_2,pos_lon,pos_lat)          
            print("Azimuth Angle 1: ",az_1,"Azimuth Angle 2: ",az_2,"Elevation Angle 1: ",el_1,"Elevation Angle 2: ",el_2)
            
            if az_1 != az_2 or el_1 != el_2:
                self.move_pointer(target_speed, az_1, az_2,dist_1_to_2, el_1, el_2, alt_change)
                
            print("Latitude 1: ", lat_1,"Longitude 1: ",lon_1,"Latitude 2: ",lat_2,"Longitude 2: ", lon_2,"Altitude 1: ", alt_1, "Altitude 2: ", alt_2)
            lat_1 = lat_2
            lon_1 = lon_2
            alt_1 = alt_2
            dist_1 = dist_2
            
            return lat_1, lon_1, alt_1, dist_1
    
    def run(self):
        event.wait() #waits for event flag to get set by joystick
        #print(self.read_new_gps)
        #print (self.sock)
        #self.test_move()
        la1 = 0
        lo1 = 0
        al1 = 0
        di1 = 0
        self.filename = '/home/pgsc/Dish-Tracker/Dish-Tracker/Code/test_gps_data_2.txt'
        gps_file = open(self.filename, "r")
        first_pass = True #first pass is True going into loop, needed for track() fucntion
        for line in gps_file:
            self.lock.acquire() #request a loc before calling fucntions
            new_data = self.read_from_file(line)
            la1, lo1, al1, di1 = self.track(first_pass, new_data, la1, lo1, al1, di1)
            first_pass = False #no longer first pass
            self.lock.release() #release lock when no longer calling functions
            event.wait() #waits for event flag to get set by joystick
            #time.sleep(1)
            #print('HERE')
            #self.sock.write(self.CCW_MSG)
            #time.sleep(1)
            #self.test_move() #test moving after reading the file and see when the joystick takes over'''
            #print(self.get_degrees('default'))
        finished_event.set() #set flag to stop joystick when all gps points exhausted
        self.sock.write(self.STOP_MSG) #stop the last movement for sure

if __name__ == '__main__':
    #create events for communication between threads
    event = Event() # flag for whether or not joystick is active
    finished_event = Event() #flag for if gps coordinates are done
    #set up port connections
    qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=.1)
    print('Connecting...')
    bd_addr = "00:21:13:02:59:1A"
    port = 1
    BT_sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    BT_sock.connect((bd_addr, port))
    print ('Connected')
    BT_sock.settimeout(20)
    
    #create class instances
    thread1 = Joystick(qpt, BT_sock)
    thread2 = gps_track(qpt,'test')
    
    #start running threads
    thread1.start()
    thread2.start()
     
    #wait for threads to finish
    thread1.join()
    thread2.join()
    
    print('Program Ended')
    
    
