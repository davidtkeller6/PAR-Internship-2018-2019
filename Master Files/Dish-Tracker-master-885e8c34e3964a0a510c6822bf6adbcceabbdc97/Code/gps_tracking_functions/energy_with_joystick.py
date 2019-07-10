#!/usr/bin/env python3
from threading import Thread, Event, Lock
import serial, bluetooth, time, socket

''' Prerequisites for running energy tracking with joystick control
    To run this code sucessfully, you will need to be connected to the
    positioner, USRP, and have the bluetooth arduino joystick turned on
    and within range. Also, the computer running this code will need
    to have the iMarc software installed.
   
    To begin: run "rssi_util usrp.json" from the command line.
    Make sure the usrp.json file is in the directory you are running from
    This begins initializing USRP for recieving transmission.
   
    Then run this code (make sure to use python 3)
   
    Clicking down on the Joystick will alternate it between joystick mode
    and energy tracking mode. 
'''
#==================================================================================================================================
#==================================================================================================================================   
#====================================              Joystick Thread            =====================================================
#==================================================================================================================================
#==================================================================================================================================

class Joystick(Thread): #child class of thread
    def __init__(self, sock, bt):
        """Constructor"""
        Thread.__init__(self)
        self.sock = sock #socket connection to positioner
        self.bt = bt #socket connection to bluetooth
        self.CW_MSG = b'\x02\x31\x00\xFF\x00\x00\x00\xCE\x03' #clockwise
        self.CCW_MSG = b'\x02\x31\x00\xFE\x00\x00\x00\xCF\x03' #counter clockwise
        self.UP_MSG = b'\x02\x31\x00\x00\xFF\x00\x00\xCE\x03' #up
        self.DOWN_MSG = b'\x02\x31\x00\x00\xFE\x00\x00\xCF\x03' #down
        self.UP_CW_MSG = b'\x02\x31\x00\xFF\xFF\x00\x00\x31\x03' #up and clockwise
        self.DOWN_CW_MSG = b'\x02\x31\x00\xFF\xFE\x00\x00\x30\x03' #down and clockwise
        self.UP_CCW_MSG = b'\x02\x31\x00\xFE\xFF\x00\x00\x30\x03' #up and counter clockwise
        self.DOWN_CCW_MSG = b'\x02\x31\x00\xFE\xFE\x00\x00\x31\x03' #down and counter clockwise
        self.STOP_MSG = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03'
        self.lock = Lock()     
      
    def move(self):
        """Move positioner depending on joystick"""
      
        def read_value(self):
            """Read value from joystick via BT"""
            char = self.bt.recv(1).decode()
            #print(char)
            return int(char)
           
        can_move = True #flag for joystick movement
        while True:
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
                    event.clear() #clear event flag, prevents energy tracking
                    print('Joystick enabled')
                else:
                    print('Joystick disabled')
                    event.set() #set event flag, allow energy tracking
                    can_move = False
            else:
                if(can_move is True):
                    self.sock.write(self.STOP_MSG)
  
    def run(self):
        """Run class functions"""
        self.move()

#==================================================================================================================================
#==================================================================================================================================   
#====================================          Energy Tracking Thread         =====================================================
#==================================================================================================================================
#==================================================================================================================================
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
        while True:
            event.wait()
            self.lock.acquire()
            self.track()
            self.lock.release()

#==================================================================================================================================
#==================================================================================================================================   
#====================================                    Main                 =====================================================
#==================================================================================================================================
#==================================================================================================================================
if __name__ == '__main__':
    #create events for communication between threads
    event = Event() # flag for whether or not joystick is active
 
    #set up positioner connection
    qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=.1)
    if qpt.isOpen() is True:
        print("\nConnected to Positioner\n")
   
    #set up bluetooth connections
    BT_ADDR = "00:21:13:02:59:1A"
    BT_PORT = 1
    BT_sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    BT_sock.connect((BT_ADDR, BT_PORT))
    print ("\nConnected to Bluetooth\n")
    BT_sock.settimeout(20)

    #set up USRP connection
    TCP_IP_ADDR = "127.0.0.1"
    TCP_PORT = 12345
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sock.bind((TCP_IP_ADDR,TCP_PORT));sock.listen(1)
    cli_TCP,addr=sock.accept()
    print("\nConnected to USRP.\n")

    #create class instances
    thread_joystick = Joystick(qpt, BT_sock)
    thread_energy = Energy_Track(qpt, cli_TCP)

    #start running threads
    thread_joystick.start()
    thread_energy.start()

    #wait for threads to finish
    thread_joystick.join()
    thread_energy.join()

    #all threads done
    print('Program Ended')
