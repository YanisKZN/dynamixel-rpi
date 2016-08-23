from Robot import *
import time

s = Robot()

s.getId()

center = 512
over = 562
less = 462
counter = 5

while counter != -1:
    for i in s.getId():
        if s.readPosition(i) < center:
            s.moveMotorReg(i, over, 90)
        else:
            s.moveMotorReg(i, less, 90)

    while s.isRobotMoving():
        pass
    s.RegAction()

    print("\rDancing. {0}".format(counter), end="")
    time.sleep(0.5)
    print("\rDancing.. {0}".format(counter), end="")
    time.sleep(0.5)
    print("\rDancing... {0}".format(counter), end="\n")

    counter -= 1
