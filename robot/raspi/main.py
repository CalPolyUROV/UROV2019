#python3

import sys

import serial

import serial_finder
from serial_coms import SerialConnection

ports = serial_finder.serial_ports()
print("Found ports:")
for p in ports:
    print("{}".format(p))
port = serial_finder.find_port(ports)
if(port == None):
    print("No port found.")
    sys.exit(-1)
print("Using port: {}".format(port))
    
usb_serial = SerialConnection(port)

usb_serial.establish_contact()
print("Sent initial packet")

# loop()
while(True):
    # send_packet()
    ack_packet = usb_serial.get_packet()
    if(ack_packet == None):
        print("Received an invalid packet")
    else:
        print(ack_packet)

