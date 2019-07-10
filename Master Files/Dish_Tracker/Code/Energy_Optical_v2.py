from threading import Thread, Event, Lock
import serial, bluetooth, time, socket


class optical(Thread):
    def __init__(self, sock, ard, bt):
        """Constructor"""
        Thread.__init__(self)
        self.sock = sock
        self.ard = ard
        self.bt = bt
        self.lock = Lock()
        self.UP = b'\x02\x31\x00\xFE\xFF\x00\x00\x30\x03'
        self.DOWN = b'\x02\x31\x01\x00\xFE\x00\x00\xCF\x03'
        self.CW = b'\x02\x31\x00\xFF\x00\x00\x00\xCE\x03'
        self.CCW = b'\x02\x31\x00\xFE\x00\x00\x00\xCF\x03'
        self.STOP = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
      
    def read_compass_values(self):
        """Reads compass values of positioner"""
        pos_az = 0
        pos_el = 0
        self.ard.flushInput() #flush input of data throwing off the sync
        time.sleep(.2)
        #if(ard.inWaiting() > 0):
        #x_raw = ard.readline()
        start_time = time.time()
        az_raw = self.ard.readline()
        print(az_raw)
        read_time = time.time()
        #el_raw = ard.readline()
        #pos_x = int(x_raw)
        try:
            pos_az = float(az_raw)
            #pos_el = float(el_raw)
        except ValueError: #usually doesnt error twice
            ard.flushInput()
            time.sleep(.2)
            az_raw = ard.readline()
            pos_az = float(az_raw)
        return(pos_az, pos_el)  


    def read_scope_compass_values(self):
        """Read compass values from scope via bluetooth"""
        print("Reading values babye")
        char = ''
        msg_ar = [0,0]
        msg = ''
        temp_msg = ''
        i=0
        nothing=0
        islocked = False
        self.bt.send('1')
        while True:
            start_time = time.time()
            char = self.bt.recv(1).decode()
            read_time = time.time()
            if(read_time-start_time < 1):
                event.clear() #if message start getting received, move with optical and block energy
                if islocked is False:
                    #self.lock.acquire()
                    islocked = True
            else:
                if islocked is True:
                    #self.lock.release()
                    islocked = False
                event.set()             
              
            if(str(char) == '\r'):
                pass
            elif(str(char) == 'N'):
                pass
            elif(str(char) == '\n'):
                #msg_ar[i] = int(temp_msg)
                try:
                    msg = float(temp_msg)
                    temp_msg = ''
                    i+=1
                except ValueError: #------------------------------------------------------Somehow must prevent from continous reading-----------------------------------------------------
                    #pass                #----------------------------------------------------make read non-blocking to the rest of program------------------------------------------------
                    msg = '999.0'    #-----------------------------------------------------------TRY THIS--------------------------------------------------------------------------------
            else:
                temp_msg = temp_msg + str(char)
            if(i == 1):
                i=0
                #print(msg[0], msg[1], msg[2])
                break
        print('Scope: ' ,msg)
        return msg


    def compare_values(self,p_az, p_el, s_az, s_el):
        """compares the values of scope with positioner"""
        az_diff = p_az - s_az  
        el_diff = p_el - s_el
  
        #print('Difference' , az_diff,el_diff)
        return az_diff, el_diff

    def active_move(self,positioner_az, positioner_el, scope_az, scope_el):
        """Moves with jog commands"""
        az_diff = abs(scope_az - positioner_az)
        #if(az_diff > 220):
        #    az_diff = az_diff - 360
        az_neg = (scope_az < positioner_az)
        el_diff = scope_el - positioner_el
        if(az_neg is True and az_diff > 180):
            self.sock.write(self.CW)
        elif(az_neg is True and (az_diff > 4)):
            self.sock.write(self.CCW)
        elif(az_neg is False and az_diff > 180):
            self.sock.write(self.CCW)
        elif((az_neg is False) and (az_diff > 4)):
            self.sock.write(self.CW)
        else:
            self.sock.write(self.STOP)
        return az_diff


    def optical_control(self):
        """Preforms optical control tracking"""
        l = 45
        z = 0
        move_az=0
        move_el = 37
        while True:
            #print('----------------------------------')
            pos_az, pos_el = self.read_compass_values()
            scp_az = self.read_scope_compass_values()
            if(scp_az == 999.0):
                pass #---------------------------------------------------TRY THIS--------------------------------------------
            else:
                scp_el = 0
                el_change = 45
                self.active_move(pos_az, pos_el, scp_az, scp_el)
        """a_d, az_change = move_size(pos_az, pos_el, scp_az, scp_el)
        if(can_move(a_d, el_change)):
            move_to_position(int(az_change), -37)
        #time.sleep(1)"""
      
      
    def run(self):
        """Run class functions"""
        self.optical_control()


class Energy_Track(Thread):
    def __init__(self, sock, cli_TCP):
        """Constructor"""
        Thread.__init__(self)
        self.sock = sock #socket connection to positioner
        self.lock = Lock()
        self.dbm = 0
        self.cli_TCP = cli_TCP
        self.delay = 0.2 # time delay between movement commands in looping functions
        self.threshold = 0.5 # threshold for hold_position function.
        self.UP = b'\x02\x31\x00\x00\xFF\x00\x00\xCE\x03'
        self.DOWN = b'\x02\x31\x00\x00\xFE\x00\x00\xCF\x03'
        self.CW = b'\x02\x31\x00\xFF\x00\x00\x00\xCE\x03'
        self.CCW = b'\x02\x31\x00\xFE\x00\x00\x00\xCF\x03'
        self.STOP = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
        self.message = [self.UP,self.CW,self.DOWN,self.CCW]
    
    def get_first_dbm(self):
        self.cli_TCP.send('horn'.encode('utf-8'))
        rssi,addr2=self.cli_TCP.recvfrom(7)
        rssi=rssi.decode('utf-8')
        rssi=float(rssi)
        self.dbm = rssi
        return rssi
    
    def get_dbm(self):
        self.cli_TCP.send('horn'.encode('utf-8'))
        rssi,addr2=self.cli_TCP.recvfrom(7)
        rssi=rssi.decode('utf-8')
        rssi=float(rssi)
        return rssi
    
    def dbm_loop_direction(self,dbm,num):
     
        #==============================================
        def get_dbm_direction(self,msg):
            """Moves direction and get dbm"""
            self.sock.write(msg)
            time.sleep(self.delay)
            self.cli_TCP.send('horn'.encode('utf-8'))
            dbm,addr2=self.cli_TCP.recvfrom(7)
            dbm= dbm.decode('utf-8')
            dbm = float(dbm)
            print("dBm : ",dbm)
            return(dbm)
        #==============================================
    
        msg = self.message[num]
        dbm_dir = get_dbm_direction(self,msg)
        if(dbm_dir > dbm):
            while (dbm_dir > dbm):
                dbm = dbm_dir
                dbm_dir = get_dbm_direction(self,msg)
            else:
                return(dbm_dir)
        else:
            return(dbm)
 
    def hold_pos(self,dbm,hold_threshold):
        dbm_hold = self.get_dbm()
        while (dbm <= (dbm_hold + hold_threshold)) and (dbm >= (dbm_hold - hold_threshold)):
            dbm_hold = self.get_dbm()
            print("Within threshold of -/+",hold_threshold," dBm. DBM IS:  ", dbm_hold)
            self.sock.write(self.STOP)
        return(dbm_hold) 
    
    def track(self):
        """Preform energy tracking"""
        for num in range(0,len(self.message)):
            self.dbm = self.dbm_loop_direction(self.dbm,num)
            self.dbm = self.hold_pos(self.dbm,self.threshold)
 
    def run(self):
        """Run class functions"""
        self.get_first_dbm()
        event.clear() #start with event flag cleared
        while True:
            event.wait()
            #self.lock.acquire()
            self.track()
            #self.lock.release()

if __name__ == '__main__':
    #create events for communication between threads
    event = Event() # flag for whether or not joystick is active
  
    #set up positioner connection and arduino connection
    qpt = serial.Serial(port='/dev/ttyUSB1',baudrate=9600,timeout=.1)
    ard = serial.Serial(port='/dev/ttyACM0',baudrate=9600)
  
    #set up bluetooth connections
    bd_addr = "00:21:13:02:4B:BD"
    port = 1
    BT_sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    BT_sock.connect((bd_addr, port))
    print ('Connected To Bluetooth')
    BT_sock.settimeout(20)
  
    #set up USRP connection
    TCP_IP_ADDR = "127.0.0.1"
    TCP_PORT = 12345
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sock.bind((TCP_IP_ADDR,TCP_PORT));sock.listen(1)
    cli_TCP,addr=sock.accept()
    print("\nConnected to TCP.\n")
  
    #create class instances
    thread1 = optical(qpt, ard, BT_sock)
    thread2 = Energy_Track(qpt, cli_TCP)
  
    #start running threads
    thread1.start()
    thread2.start()
  
    #wait for threads to finish
    thread1.join()
    thread2.join()
  
    #all threads done
    print('Program Ended')
