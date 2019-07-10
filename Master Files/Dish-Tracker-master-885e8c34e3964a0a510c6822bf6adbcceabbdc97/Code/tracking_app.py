from tkinter import *
import os
import driver
import joystick_control

class Window(Frame):
    def __init__(self, master=None):        
        Frame.__init__(self, master)                  
        self.master = master
        self.init_window()

    def init_window(self):    
        self.master.title("Tracking Methods")
        self.pack(fill=BOTH, expand=1)

        command_Button = Button(self, text="Command Line",command=self.launch_command_line)
        command_Button.place(x=100, y=100)
        
        joystick_button = Button(self, text="Joystick", command=self.launch_joystick)
        joystick_button.place(x=100,y=150)

        optical_button = Button(self, text="Optical", command=self.launch_optical_tracking)
        optical_button.place(x=100,y=200)

        pfp_button = Button(self, text="Preplanned Flight Path Tracker", command=self.launch_pfp_track)
        pfp_button.place(x=100,y=250)
        
        telem_button = Button(self, text="Telemetry Tracking", command=self.launch_telem_track)
        telem_button.place(x=100,y=300)

        quitButton = Button(self, text="Exit",command=self.client_exit)
        quitButton.place(x=100, y=450)

    def client_exit(self):
        exit()

    def launch_command_line(self):
        os.system('clear')
        driver.main()
        self.current_method = 'driver.py'
                
    def launch_joystick(self):
        os.system('clear')
        joystick_control.main()
        self.current_method = 'joystick_control.py'
        
    def launch_optical_tracking(self):
        os.system('clear')
        os.system('python3 optical_control.py')
        self.current_method = 'optical_control.py'
        
    def launch_energy_tracking(self):
        os.system('clear')
        os.system('python3 energy_tracking.py')
        self.current_method = 'energy_tracking.py'
        
    def launch_pfp_track(self):
        os.system('clear')
        os.system('python3 gps_tracker.py')
        self.current_method = 'gps_tracker.py'
        
    def launch_telem_track(self):
        os.system('clear')
        os.system('python3 gps_tracking_functions/telemetry_tracking.py') #fix file name and location here
        self.current_method = 'gps_tracking_functions/telemetry_tracking.py'
        
    def change_method(self):
        """Kill current method process"""
        #kil the active thread
        print('Method Exited')


os.system('sudo service bluetooth start')      
root = Tk()
root.geometry("400x500")
app = Window(root)
root.mainloop() 



