# Test code for on-robot scheduling system

from schedule import Schedule

# Make a schedule object
s = Schedule()

# loop()
while(True):
    # Get tasks if needed
    if (not s.has_tasks()):
        s.get_new_tasks()
        
    # Get the next task to execute
    current_task = s.get_next_task()
