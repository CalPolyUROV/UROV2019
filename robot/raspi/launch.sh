#!/bin/bash

python3 main.py

# This script should be set to launch on boot

# Instructions: https://raspberrypi.stackexchange.com/questions/8734/execute-script-on-start-up
# "run when you boot into the LXDE environment"
# 1. Navigate to  "cd ~/.config/lxsession/LXDE-pi"
# 2. Open the autostart file in that folder:
# 3. "sudo vim autostart"
# 4. Add @midori on a new line. 
# 	If you want to run something like a python script, put something like @python mypython.py on a new line.
#	 Running a script file would be @./superscript, but for some reason the script runs in an infinite loop (perhaps this will stop that).
#		 (This continual restrting is actually exactly what we want)
# 5. Save and exit: Esc, then type :wq
# 6. Restart your Raspberry Pi into the LXDE environment.