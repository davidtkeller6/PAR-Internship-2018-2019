#!/usr/bin/python
from __future__ import print_function
import serial,os
from time import sleep

if(os.geteuid()!=0):
    print("   \n Please run as root.\n\n")
    exit()
nuc=serial.Serial('/dev/ttyS0',9600)

'''
python-serial must be installed for this to work. Use "sudo
   apt-get install python-serial" to install it if not installed.

/dev/ttyS0 is only used if you are using a Raspberry Pi 3.

For older versions, including RPi 2, use /dev/ttyAMA0 for the serial port.

You must enable the serial port in the Raspberry Pi Configuration by typing
   sudo raspi-config and finding serial and turning it on, then reboot.

You must also disable use of the serial port by the OS console on startup,
   otherwise this program will crash as both are using the serial port.
   This can be done by typing the following commands:
   sudo systemctl stop serial-getty@ttyS0.service
   sudo systemctl disable serial-getty@ttyS0.service 
   then reboot the system.

Note: The layout of the incoming string is:
    Time of GPS Transmission on NUC
    Aircraft Latitude
    Aircraft Longitude
    Aircraft Altitude
    Aircraft Heading
'''

while True:
    try:
        line=nuc.readline()
        lat=float(line.split(',')[1])
        lon=float(line.split(',')[2])
        alt=float(line.split(',')[3])
        heading=float(line.split(',')[4])
        print('\nLatitude:',lat)
        print('Longitude:',lon)
        print('Altitude:',alt)
        print('Heading:',heading)
    except IndexError:
        sleep(.1)
    except KeyboardInterrupt:
        nuc.close()
        exit()
