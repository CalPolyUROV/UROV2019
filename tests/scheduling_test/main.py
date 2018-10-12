# Test code for on-robot scheduling system

from schedule import Schedule
from schedule import Task
from time import sleep

# Make a schedule object
s = Schedule()

# loop()
while(True):
    # Get tasks if needed
    if (not s.has_tasks()):
        s.get_new_tasks()
        
    # Get the next task to execute
    t = s.get_next_task()
    t.execute_task()
    #sleep(2)
    
s.socket_connection.close_socket()
