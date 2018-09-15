import socket   #for sockets connection to RPi
import sys  #for exit
from time import sleep #for waiting

import packet

__author__ = 'Spencer Shaw'

serial_coms = new SerialConnection()

serial_coms.establish_contact()
