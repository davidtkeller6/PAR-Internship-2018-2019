# Arduino Code

### compass.ino
* This program is found in the Compass folder. It will allow the arduino to read compass values and prints them to the serial port. This is used to read the heading in degrees of the positioner and the values are grabbed through a serial interface with some of the Python programs. Make sure the correct serial port is being used in the python programs. Usually ttyACM0 or ttyACM1. Used in the optical_control.py program. Make sure all of the libraries and header files are properly downloaded and included for the compass module.

### BT_compass.ino
* This program is found in the BT_compass folder. It will pull compass values and send them to a device over a bluetooth connection. Make sure the correct bluetooth address is set up and that the module is properly bound to the device it is sending data to. This program is used to get values from the scope a few feet away from positioner. Used in the optical_control.py program. Make sure all of the libraries and header files are properly downloaded and included for the compass module.

### joystick_with_BT.ino
* This program is found in the BT Joystick folder. It reads the position of the joystick and sends a message containing its postion to a device over a bluetooth connection. Make sure the correct bluetooth address is set up and that the module is properly bound to the device it is sending data to. Used in the joystick_control.py program.

