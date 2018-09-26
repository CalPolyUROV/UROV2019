#python3

# import sys

import serial

import serial_finder
from serial_coms import SerialConnection

port = None
while (port == None):
    # Get a list of all serial ports
    ports = serial_finder.serial_ports()
    print("Found ports:")
    for p in ports:
        print("{}".format(p))
    # Select the port
    port = serial_finder.find_port(ports)
    if(port == None):
        print("No port found, trying again.")
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

