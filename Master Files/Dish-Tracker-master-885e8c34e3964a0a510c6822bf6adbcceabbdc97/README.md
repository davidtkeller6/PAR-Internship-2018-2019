# READ ME!!!

## Main Programs:

### qpt_v2.py
* This program holds the functions need to move to positioner and to grab its current position it is at. Directions how to impliment are found in the Code folder's README. There are still some errors that occur when reading back certian positions or moving to certian locations. These errors don't always occur and still need to be fixed.

### driver.py
* This program allows the positioner to be moved with the command line by entering in an azimuth and elevation (in degrees). It will also read back the current position after moving which should match the entered values.

### joystick_control.py
* This program uses the joystick and bluetooth module to control the positioner. Make sure that the bluetooth is correctly binded to the devices running the program and double check it has the correct MAC address in the code running.

### optical_control.py
* This program uses a compass on the positioner and compares the bearing with the compass on a scope that is sending its position back via bluetooth module. Make sure that the bluetooth is correctly binded to the devices running the program and double check it has the correct MAC address in the code running.

### PFP_track.py
* This program will track a target moving on a predetermined flight path. There is math that neeeds to be fixed; still in its early developement stages.

### garmin_gps.py
* This program interfaces with the Garmin GPS module and gets the latitude and longitude coordinates of the devices location.

### Arduino
* The programs that run on the arduinos can be found in the Code folder in ArduinoCode.
