#python3

# This is the python program is meant to run on the Raspberry Pi located on the robot.
# This program acts as a intermediary between the Raspberry Pi on the surface unit and the Arduino/Teensy on the robot.
# Currently, only serial communication to the Arduino/Teensy is present here. Sockets code will need to be merged into 
# this program from the sockets_test file once it is stablized.

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

# Create the serial connection object with the specified port    
usb_serial = SerialConnection(port)

# Send the initial packet to make contact with Arduino/Teensy
usb_serial.establish_contact()
print("Sent initial packet")

# loop()
while(True):
    # send_packet()
    # Recieve a packet fromt eh Arduino/Teensy
    ack_packet = usb_serial.get_packet()
    if(ack_packet == None):
        print("Received an invalid packet")
    else:
        print(ack_packet)

