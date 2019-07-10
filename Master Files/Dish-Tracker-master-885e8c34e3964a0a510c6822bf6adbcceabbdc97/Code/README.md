## Guide to using functions to move dish with qpt_v2.py:

The azimuth range of the dish poniter is -221 to 221 degrees- not a full 360 range in one direction. The elevation (tilt) range is -87 to 84 degrees. The main functions that will be used in other programs are the get_degrees and move_to_position functions. First, you must download the program and import it into the current script.

To import the qpt_v2.py library type:
```python
from qpt_v2 import \*
```

The python program communicates to the dish pointer over a serial port connection. Double check the serial connection and edit the line below if needed
```python
qpt = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=1)
```

#### Functions

```python
def to_center():
```
The to_center function will put the dish at the center position (azimuth=0, elevation=0)


```python
def stop_move():
    return feedback
```
The stop_move function will stop any current motion of the dish pointer. Will return a raw feedback message containing position (in bytes).

```python
def move(msg):
    return feedback
```
The move function will move the dish pointer in a direction specified by one of the byte message (can be seen at bottom of this file). Note that the dish pointer will continue to move in the specified direction until the stop_move() or move(stop_message) is called, or if the dish pointer reaches the limit of its motion. Will return a raw feedback message containing position (in bytes).

```python
def validate(hp, xo, vp, yo):
    return #either a True of False depending on logic outcome
```
This function is used in the move_to_position function to preform logic.

```python
def get_degrees():
    return hor_deg, ver_deg
```
The get_degrees function will return the current azimuth and elevation (tilt) position of the dish pointer. An example of how to get position would be as shown directly below:
```python
azimuth , elevation = get_degrees()
```

```python
def get_position_bytes():
    return pos_string
```
The get_position_bytes function will return the position of the dish pointer in the raw bytes format. 

```python
def move_to_position(x_origional, y_origional):
    return h_pos, v_pos
```
The move_to_position function takes in an azimuth degrees and elevation degrees to move to. The dish pointer will then move to the entered position. After moving, it will then return the current position of the dish pointer (which should be the coordinates that were entered). An example of how to run this function can be seen below:
```python
current_azimuth, current_elevation = move_to_position(azimuth_degrees, elevation_degrees)
```

```python
def shut_down():
```
The shut_down function stops the motion of the dish pointer and closes the serial port connection.


#### Byte Message
The message below are the ones needed in the move function. 

```python
cw_msg = b'\x02\x31\x00\xA7\x00\x00\x00\x96\x03' #clockwise
ccw_msg = b'\x02\x31\x00\x96\x00\x00\x00\xA7\x03' #counter clockwise
up_msg = b'\x02\x31\x00\x00\x65\x00\x00\x54\x03' #up
down_msg = b'\x02\x31\x00\x00\x54\x00\x00\x65\x03' #down
up_cw_msg = b'\x02\x31\x00\xFB\xF9\x00\x00\x33\x03' #up and clockwise
down_cw_msg = b'\x02\x31\x00\xF3\xF6\x00\x00\x34\x03' #down and clockwise
up_ccw_msg = b'\x02\x31\x00\xF8\xF9\x00\x00\x30\x03' #up and counter clockwise
down_ccw_msg = b'\x02\x31\x00\xFC\xFA\x00\x00\x37\x03' #down and counter clockwise
stop_msg = b'\x02\x31\x00\x00\x00\x00\x00\x31\x03' #stop/don't move
```


