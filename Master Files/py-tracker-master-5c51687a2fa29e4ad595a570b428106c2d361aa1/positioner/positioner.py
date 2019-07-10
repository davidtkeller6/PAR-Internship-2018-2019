#------------------------------------------------------------------
# Name: positioner.py
# Tracker Class for the Heavy Duty Azimuth Positioning System.
# Author: Alan Street / PGSC
# Created: January 14th, 2018
# Description: Controls the hardware for the heavy duty
#       azimuth positioning system.
#       Includes the following features:
#           Setting up the GPIO on the Raspberry Pi,
#           Configuring the TReX motor controller,
#           Moving the positioner,
#           Reading the magnetic sensor to determine home position,
#           Reading the quadrature encoder to determine the
#               current position of the device.
# Required Libraries:
#           py-gaugette
#           time
#           wiringpi
# py-gaugette can be obtained at:
#   https://github.com/guyc/py-gaugette
# wiringpi can be obtained at:
#   https://git.drogon.net/ (do NOT use the version on GITHUB!)
# OR by typing in "sudo pip install wiringpi" while having
#   a working internet connection.
# The time library should be installed by default with the OS.
# NOTE: Raspberry Pi GPIO pin numbers use the BCM # system.
# NOTE: PWM Values and the corresponding speeds and directions
#       are included below:
#   PWM of 15: Stops Tracker / Stand Still.
#   PWM of 16-20: Moves Tracker RIGHT at ~5.3 to ~34 degrees/sec.
#   PWM of 10-14: Moves Tracker LEFT at ~5.3 to ~34 degrees/sec.
#   Negative angles are to the LEFT of the home position.
#   Positive angles are to the RIGHT of the home position.
#   Tracker Speeds (Note that these numbers are not offical.
#   They were measured using the time.time() function in python)
#   PWM of 15: Tracker moves so fast you can't see it moving.
#   PWM of 14 or 16: Moves Tracker @ ~5.3 degrees per second.
#   PWM of 13 or 17: Moves Tracker @ ~13 degrees per second.
#   PWM of 12 or 18: Moves Tracker @ ~20.6 degrees per second.
#   PWM of 11 or 19: Moves Tracker @ ~28.2 degrees per second.
#   PWM of 10 or 20: Moves Tracker @ ~34 degrees per second.
#
# Raspberry Pi GPIO Connection Configuration:
#   GPIO 18 (Pin 12) - TReX Ch. 1 PWM
#   GPIO 7 (Pin 26) - Motor Encoder Ch. A (Yellow Wire)
#   GPIO 9 (Pin 21) - Motor Encoder Ch. B (Brown Wire)
#   5V DC (Pin 2 or 4) - Motor Encoder Power (Orange Wire)
#   GND(Pins 6,9,14,20,25,30,34,39) - Motor Encoder GND (Green Wire)
#   5V DC - Home Sensor 5V (Red Wire)
#   GND - Home Sensor GND (Black Wire)
#   GPIO 27 (Pin 13) - Home Sensor Signal Wire (Green Wire) 
#
# NOTE: A driver program for this class is included in the source
#       code package (py-tracker/examples/control_positioner.py). 
#--------------------------------------------------------------------
import time
import gaugette.gpio
import gaugette.rotary_encoder
import wiringpi

class Positioner:
    # Class Variables.
    def __init__(self):
        self.LOW_PWM=10
        self.HIGH_PWM=20
        self.STOP=15
        self.A_PIN=7
        self.B_PIN=9
        self.HOME_PIN=17
        self.PAN_PIN=18
        self.DEBUG=1
        self.ZERO_SPEED=18
        self.INVERTED_ENCODER=0

    # Function to configure the GPIO pins on the Raspberry Pi 3 Model B+.
    # This will also work on the Model B+, 2 B+ and 3.
    def init_gpio(self):
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(self.PAN_PIN,wiringpi.GPIO.PWM_OUTPUT)
        wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
        wiringpi.pwmSetClock(1920)
        wiringpi.pwmSetRange(200)
        wiringpi.pinMode(self.HOME_PIN,0)

    # Function to initialize the GPIO to read the quadrature encoder.
    # NOTE: Call this function only after the next function. See below.
    # Returns the encoder object.
    def init_encoder(self):
        gpio = gaugette.gpio.GPIO()
        self.encoder = gaugette.rotary_encoder.RotaryEncoder(gpio,self.A_PIN,self.B_PIN)
        self.encoder.start()

    # Function that will zero the tracker above the magnetic sensor.
    # NOTE: This function must be called prior to calling the function
    #       init_encoder or set_angle. If init_encoder is called
    #       before this function, it will mess up the encoder reading.
    def find_zero(self):
        time.sleep(.5)
        wiringpi.pwmWrite(self.PAN_PIN,self.STOP)
        time.sleep(.5)
        wiringpi.pullUpDnControl(self.HOME_PIN,wiringpi.PUD_UP)
        wiringpi.pwmWrite(self.PAN_PIN,self.ZERO_SPEED)
        pin_value=wiringpi.digitalRead(self.HOME_PIN)
        count=0
        while(pin_value!=0 and count!=10):
            wiringpi.pwmWrite(self.PAN_PIN,18)
            pin_value=wiringpi.digitalRead(self.HOME_PIN)
            time.sleep(.05)
            if(pin_value==0):
                count=count+1
        wiringpi.pwmWrite(self.PAN_PIN,self.STOP)

    # Function that will move the positioner to a specified angle.
    # NOTE: Angles over 180 degrees can be considered negative angles
    #   (to the left = negative angle) and will be converted.
    def set_angle(self, angle, encoder, result):
        if(self.DEBUG==1):
            print("Input Angle is: %d"%angle)
        if(angle>360):
            angle=angle-360
        elif(angle<-360):
            angle=angle+360
        if(angle>180):
            angle=angle-360
        desired_result=angle*-52.7456
        if(self.DEBUG==1):
            print("Current Result is %f" % result)
            print("Desired Result is: %f" % desired_result)
        current_angle=int(result/-52.7456)
        if(self.DEBUG==1):
            print("Current Angle is: %f" % current_angle)
        if(angle>=current_angle):
            if(current_angle>=0 and angle>=0):
                pulse=self.HIGH_PWM
                time1=time.time()
                while(result > desired_result):
                    delta=self.encoder.get_cycles()
                    wiringpi.pwmWrite(self.PAN_PIN,pulse)
                    if delta!=0:
                        result=result+delta
                        if(self.DEBUG==1):
                            print("rotate %d" % delta)
                    else:
                        time.sleep(.0001)
            elif(current_angle<0 and angle>=0):
                zero_result=(abs(0-angle))+abs(0+current_angle)
                if(self.DEBUG==1):
                    print("\n   Zero_Result is: %d"%zero_result)
                oneighty_result=(abs(-180-current_angle))+(180-angle)
                if(self.DEBUG==1):
                    print("\n   180_Result is: %d"%oneighty_result)
                if(zero_result<=oneighty_result):
                    pulse=self.HIGH_PWM
                    time1=time.time()
                    while(result > desired_result):
                        delta=self.encoder.get_cycles()
                        wiringpi.pwmWrite(self.PAN_PIN,pulse)
                        if delta!=0:
                            result=result+delta
                            if(self.DEBUG==1):
                                print("rotate %d" % delta)
                        else:
                            time.sleep(.0001)
                elif(oneighty_result<zero_result):
                    desired=desired_result
                    desired_result=(9494.208+desired_result)+result
                    desired_result=(9494.208-result)+desired_result
                    if(self.DEBUG==1):
                        print('\n   New Desired Result is %d'%desired_result)
                    desired_result=desired_result
                    pulse=self.LOW_PWM
                    time1=time.time()
                    while(result < desired_result):
                        delta=self.encoder.get_cycles()
                        wiringpi.pwmWrite(self.PAN_PIN,pulse)
                        if delta!=0:
                            result=result+delta
                            if(self.DEBUG==1):
                                print("rotate %d" % delta)
                        else:
                            time.sleep(.0001)
                    result=desired
                    if(self.DEBUG==1):
                        print('\n   New Result is %d'%result)
            elif(current_angle<0 and angle<0):
                pulse=self.HIGH_PWM
                time1=time.time()
                while(result > desired_result):
                    delta=self.encoder.get_cycles()
                    wiringpi.pwmWrite(self.PAN_PIN,pulse)
                    if delta!=0:
                        result=result+delta
                        if(self.DEBUG==1):
                            print("rotate %d" % delta)
                    else:
                        time.sleep(.0001)
        elif(angle<current_angle):
            if(current_angle>=0 and angle>=0):
                pulse=self.LOW_PWM
                time1=time.time()
                while(result < desired_result):
                    delta=self.encoder.get_cycles()
                    wiringpi.pwmWrite(self.PAN_PIN,pulse)
                    if delta!=0:
                        result=result+delta
                        if(self.DEBUG==1):
                            print("rotate %d" % delta)
                    else:
                        time.sleep(.0001)
            elif(current_angle>=0 and angle<0):
                zero_result=(abs(0-current_angle))+abs(0+angle)
                if(self.DEBUG==1):
                    print("\n   Zero_Result is: %d"%zero_result)
                oneighty_result=(abs(-180-angle))+(180-current_angle)
                if(self.DEBUG==1):
                    print("\n   180_Result is: %d"%oneighty_result)
                if(zero_result<=oneighty_result):
                    pulse=self.LOW_PWM
                    time1=time.time()
                    while(result < desired_result):
                        delta=self.encoder.get_cycles()
                        wiringpi.pwmWrite(self.PAN_PIN,pulse)
                        if delta!=0:
                            result=result+delta
                            if(self.DEBUG==1):
                                print("rotate %d" % delta)
                        else:
                            time.sleep(.0001)
                elif(oneighty_result<zero_result):
                    desired=desired_result
                    desired_result=(360+angle)*-52.7456
                    if(self.DEBUG==1):
                        print('\n   New Desired Result is %d'%desired_result)
                    pulse=self.HIGH_PWM
                    time1=time.time()
                    while(result > desired_result):
                        delta=self.encoder.get_cycles()
                        wiringpi.pwmWrite(self.PAN_PIN,pulse)
                        if delta!=0:
                            result=result+delta
                            if(self.DEBUG==1):
                                print("rotate %d" % delta)
                        else:
                            time.sleep(.0001)
                    result=desired
            elif(current_angle<0 and angle<0):
                pulse=self.LOW_PWM
                time1=time.time()
                while(result < desired_result):
                    delta=self.encoder.get_cycles()
                    wiringpi.pwmWrite(self.PAN_PIN,pulse)
                    if delta!=0:
                        result=result+delta
                        if(self.DEBUG==1):
                            print("rotate %d" % delta)
                    else:
                        time.sleep(.0001)
        wiringpi.pwmWrite(self.PAN_PIN,self.STOP)
        time.sleep(.02)
        wiringpi.pwmWrite(self.PAN_PIN,self.STOP)
        time.sleep(.02)
        wiringpi.pwmWrite(self.PAN_PIN,self.STOP)
        difftime=time.time()-time1
        return(result,difftime)

    # Function that will prompt user to change the tracking speed of the 
    #   positioner. Speeds were measured using python and time.time()
    def set_speed(self):
        print("\nPossible speed settings for the positioner:")
        print("(1) PWM of 14/16 - ~5 Degrees per Second")
        print("(2) PWM of 13/17 - ~13 Degrees per Second (Default Speed)")
        print("(3) PWM of 12/18 - ~21 Degrees per Second")
        print("(4) PWM of 11/19 - ~28 Degrees per Second")
        print("(5) PWM of 10/20 - ~34 Degrees per Second")
        option=raw_input("\nPlease enter your desired azimuth speed option: ")
        if(option=='1'):
            self.LOW_PWM=14;self.HIGH_PWM=16
        elif(option=='2' or option==''):
            self.LOW_PWM=13;self.HIGH_PWM=17
        elif(option=='3'):
            self.LOW_PWM=12;self.HIGH_PWM=18
        elif(option=='4'):
            self.LOW_PWM=11;self.HIGH_PWM=19
        elif(option=='5'):
            self.LOW_PWM=10;self.HIGH_PWM=20
        else:
            print("\nERROR: Invalid option. Using the previous value of %d/%d."%(self.LOW_PWM,self.HIGH_PWM))
    
    # Experimental function to determine if the Ch A and Ch B wires for the encoder
    #   are properly connected. NOT COMPLETED!!!        
    def calc_encoder_dir(self):
        print("\nDetermining encoder directions...")
        # Move Left and measure result.
        wiringpi.pwmWrite(self.PAN_PIN,self.LOW_PWM)
        count=0
        while count<10:
            delta=self.encoder.get_cycles()
            #if(delta!=0 and delta<=1):
                    
