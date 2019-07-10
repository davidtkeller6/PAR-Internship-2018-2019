#!/usr/bin/env python
import os
import time
import wiringpi
import positioner.positioner as positioner

# Check for root access.
if(os.geteuid()!=0):
    print("\nPlease run as sudo!\n\n")
    exit()

# Initialize and Configure the Positioner / GPIO pins.
panunit=positioner.Positioner()
panunit.init_gpio()
panunit.find_zero()
encoder=panunit.init_encoder()
encoder_position=0
encoder_position,difftime=panunit.set_angle(0,encoder,encoder_position)

# Prompt user for desired azimuth speed.
#panunit.set_speed()

# Main Loop.
while True:
    try:
        angle=raw_input("\nPlease enter an angle (Leave blank to exit): ")
        if(angle==""):
            exit()
        else:
            angle=int(angle)
            encoder_position,difftime=panunit.set_angle(angle,encoder,encoder_position)
    except ValueError:
        print("   An invalid integer was entered. Please try again...\n")
    except KeyboardInterrupt:
        print("\n")
        exit()
