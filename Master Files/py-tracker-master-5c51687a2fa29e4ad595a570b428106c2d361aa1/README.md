py-tracker
==========

py-tracker is a small library for the iMARC tracking system. This particular version
contains the functions for controlling the Servo City belt-driven pan system. 

Hardware Platform
=================

This library is designed to only run on a Raspberry Pi. For the most processing capability,
a Raspberry Pi 2 B+ or better (RPi 3 B+ recommended) is required. This has been tested
on the Raspberry Pi 3 B+ extensively. 

Prerequisites
=============

### WiringPi w/ Python Support

To install wiringpi w/ python support, type the following command on a 
Raspberry Pi terminal that has internet access:

```
sudo pip install wiringpi
```

The sources can be found here:
https://projects.drogon.net/raspberry-pi/wiringpi/

### py-gaugette

This library is required for the ability to read the quadrature encoder used to determine
the current position of the belt-driven pan system. 

It can be installed via github at:
https://github.com/guyc/py-gaugette

Once you obtain the source files, install by typing:
```
sudo python setup.py install
```

Installation
============

The installation process is very simple. After installing the prerequisites, open a terminal
and type the following commands:
```
cd py-tracker/
sudo python setup.py install
```

Usage
=====

A sample usage file can be found in ~/examples/control_positioner.py

This will initialize the GPIO using wiringpi, and set up the ability
to read the quadrature motor encoder using the py-gaugette library.
It will then center the device using the find_zero function, prompt the 
user for an azimuth speed, then continuously prompt the user for an angle
to set the positioner to until the enter key is pressed with no input.

### NOTE
    Positive angles will be to the RIGHT of the zero point.
    Negative angles will be to the LEFT of the zero point.

The Positioner class has 5 main functions to initialize/control the device:
```
init_gpio() - Sets up the GPIO pins for PWM use to control the motor.
init_encoder() - Sets up the GPIO pins to read the quadrature encoder on the motor.
find_zero() - Moves the positioner until the zero switch is activated. 
set_angle(angle,encoder,result) - Will move the positioner to a specified angle.
set_speed() - Controls the azimuth speed of the positioner. 5 speed options are available.
```

Authors
=======
* **[Alan Street]** - *Systems Engineer* - CTR PGSC
* **[David Keller]** - *Engineering Intern* - CTR PGSC
