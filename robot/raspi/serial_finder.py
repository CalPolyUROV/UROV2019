""" This module seaches the operating system for devices on serial ports
"""
# TODO: Find the origin of this code and give credit

import glob
import sys
import serial
from sys import platform

from debug import debug


def serial_ports() -> list:
    """ Finds all serial ports and returns a list containing them

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)                 # Try to open a port
            s.close()                               # Close the port if sucessful
            result.append(port)                     # Add to list of good ports
        except (OSError, serial.SerialException):   # If un sucessful
            pass
    return result


def find_port(ports) -> str or None:
    """ Finds a port in a list to use and returns itF
    """
    if platform == "linux" or platform == "linux2":
        debug("serial_finder", "Linux detected")
        for p in ports:
            # return '/dev/ttyS0'  # If using raspi GPIO for serial, just pick this port
            if "USB" in p:
                return p

    elif platform == "darwin":
        debug("serial_finder", "Darwin detected")
        return ports[0]

    elif platform == "win32":
        debug("serial_finder", "Windows detected")
        p = ""
        for p in ports:
            debug("serial_finder", p)
        return p

    else:
        return None
