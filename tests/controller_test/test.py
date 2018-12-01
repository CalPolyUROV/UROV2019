from controller1 import Controller
from time import sleep

xbox_controller = Controller()

while True:
    print(xbox_controller.get_input())
    sleep(1)

xbox_controller.close()
