#!/usr/bin/python
from qpt_v2 import *

def main():
    while True:
        print('Enter following input in degrees...or q to quit')
        az = input('Enter azimuth: ')
        el = input('Enter elevation: ')
        if (az == 'q' or el == 'q'):
            shut_down()
            print('Program Terminated')
            break
        else:
            move_to_position(az, el)


