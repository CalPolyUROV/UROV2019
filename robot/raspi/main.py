#python3

# This is the python program is meant to run on the Raspberry Pi located on the robot.
# This program acts as a intermediary between the Raspberry Pi on the surface unit and the Arduino/Teensy on the robot.
# Currently, only serial communication to the Arduino/Teensy is present here. Sockets code will need to be merged into 
# this program from the sockets_test file once it is stablized.
# Send the initial packet to make contact with Arduino/Teensy
usb_serial.establish_contact()
print("Sent initial packet")

# loop()
while(True):
    # TODO: Send commands to Teensy (In final commands will come from sockets connection OR event loop will get updated values in an RTOS manner)
    # TODO: Write logic choosing a command to send (maybe use a queue)
    # send_packet()
    # Recieve a packet fromt eh Arduino/Teensy
    ack_packet = usb_serial.get_packet()
    if(ack_packet == None):
        print("Received an invalid packet")
    else:
        print(ack_packet)

