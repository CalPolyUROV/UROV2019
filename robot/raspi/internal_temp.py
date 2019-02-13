import os
import time

CMD = "vcgencmd measure_temp"
SLEEP_TIME_S = 2

def measure_temp():
	temp = os.popen(CMD).readline()
	return (temp.replace("temp=", ""))

while True:
	print(measure_temp())
	time.sleep(SLEEP_TIME_S)

