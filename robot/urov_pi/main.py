#python3

import serial
import serial.tools.list_ports
import serial_finder

ports = serial_finder.serial_ports()
print("Found ports:")
for p in ports
    print("{}".format(s))
port = serial_finder.find_port(ports)
if(port == None)
    print("No port found.")
    sys.exit(-1)
print("Using port: {}".format(port))
    
outbound = serial.Serial(
    port=port,
    baudrate=9600,
    parity=serial.PARITY_NONE,   # parity is error checking, odd means the message should have an odd number of 1 bits
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,   # eight bits of information per pulse/packet
    timeout=0.1
)

while(True):
	received = (outbound.read()).decode("utf-8")
	if(received != ""):		
		print(received)
