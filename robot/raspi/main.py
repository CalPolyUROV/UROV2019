# python3

# This is the python program is meant to run on the Raspberry Pi located on
# the robot. This program acts as a intermediary between the Raspberry Pi on
# the surface unit and the Arduino/Teensy on the robot. The scheduling module
# used in this program manages the serial and sockets connections to the
# Arduino/Teensy and topside raspberry Pi Currently, only serial communication
# to the Arduino/Teensy is present here. Sockets code will need to be merged
# into this program from the sockets_test file once it is stablized.

from time import sleep  # Temporary delay to not make things too fast during testing

# Scheduling imports
from schedule import Schedule
from schedule import Task
from schedule import TaskType
from schedule import TaskPriority

# Make a schedule object
# This also initializes the sockets/networking code
# Note: The sockets should not connect to the topside unit until after the 
# serial connection has been made. This is not an issue because the socket 
# client on the robot is initialized without communicating with the server
# (however the serial connection uses a handshake/"est_con")
s = Schedule()

s.schedule_initial_tasks()

terminate: bool = False  # Whether to exit main loop
while(not terminate):
    # Get new tasks if needed
    # TODO: Integrate this if statement into the get_new_tasks call or a check_for_new_tasks()
    if (not s.has_tasks()):
        s.get_new_tasks()

    # Get the next task to execute
    t = s.get_next_task()
    s.execute_task(t)
    sleep(2)  # Temporary delay to not make things too fast during testing

s.terminate()
