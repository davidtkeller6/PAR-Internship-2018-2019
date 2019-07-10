from qpt_v2 import *

#driver --> import functions from qpt.py

print('Enter following input in degrees')
az = input('Enter azimuth: ')
el = input('Enter elevation: ')

move_to_position(az, el)
#print(get_degrees())

shut_down()
