import bluetooth

target_name = "HC-05"
target_address = "00:21:13:02:4B:BD"
hostMACAddress = 'B4:D5:BD:5C:FD:22'
port = 3
backlog = 1
size = 1024

nearby_devices = bluetooth.discover_devices()

for bdaddr in nearby_devices:
    if target_name == bluetooth.lookup_name( bdaddr ):
        target_address = bdaddr
        break

if target_address is not None:
    print("found target bluetooth device with address ", target_address)
else:
    print("could not find target bluetooth device nearby")

s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
s.bind((hostMACAddress, port))
s.listen(backlog)
try:
    client, clientInfo = s.accept()
    while 1:
        data = client.recv(size)
        if data:
            print(data)
            client.send(data) # Echo back to client
except:   
    print("Closing socket")
    client.close()
    s.close()
