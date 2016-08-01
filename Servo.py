import os
#import dynamixel
from ax12 import *
import sys
#import subprocess
# import optparse
import json
import time
import jsonpickle
#from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread

# class Robot(QThread):
class Robot():
    '''
    Class to control robot
    :param port: The port usb2dynamixel is connected to, no port argument required for posix OS.
    :param minId: This int is used as an motor id to START searching in case there is no motorConfig file or resetId=True.
    :param minId: This int is used as an motor id to END searching in case there is no motorConfig file or resetId=True.
    :param resetId: If this arg is True, ignore motorConfig file and start searching motor.
    '''

    def __init__(self, minId=1, maxId=20, resetId=False):
        # super(Robot, self).__init__()

        # if port == None:
        #     if os.name == 'posix':
        #         try:
        #             self.port = '/dev/' + subprocess.check_output('ls /dev/ | grep -i usbserial', shell=True).split()[1].decode('utf-8')
        #         except subprocess.CalledProcessError:
        #             print('usb2dynamixel is not connected..')
        #     elif os.name == 'nt':
        #         print("Windows requires PORT..")
        #     else:
        #         print("doesn't support OS")
        # else:
        #     if os.name == 'nt':
        #         if 'COM' in port:
        #             self.port = port
        #         else:
        #             # need to throw error
        #             raise ValueError("port is wrong, please assign 'COMxx'..")

        # initialization
        # self.port = dynamixel.SerialStream(port=self.port, baudrate='1000000', timeout=1)
        # self.net = dynamixel.DynamixelNetwork(self.serial)

        self.servos = ax12.Ax12()

        # motorConfigPath = 'data/motorConfig.json'
        # motorList = None
        #
        # if not resetId:
        #     try:
        #         with open(motorConfigPath, 'r') as infile:
        #             motorList = json.loads(json.load(infile))
        #     except FileNotFoundError:
        #         print("Cannot find %s" % motorConfigPath)
        #
        # if motorList == None:
        #     self.scan(minId, maxId)
        #     with open(motorConfigPath, 'w') as outfile:
        #         json.dump(json.dumps(self.getId()), outfile)
        #     print("saved motor id to %s succesfully as:" % motorConfigPath)
        #     print(self.getId())
        # else:
        #     for i in motorList:
        #         temp = dynamixel.Dynamixel(i, self.net)
        #         self.net._dynamixel_map[i] = temp
        #     print("finished scanning..")

    # once we call start Alive is True
    # def start(self):
    #     self.alive = True

    # when delete this obj, will wait
    # def __del__(self):
    #     self.wait()

    # run as long as alive
    # def run(self):
    #     while self.alive:
    #         pass

    # def scan(self, minId=1, maxId=20):
    #     print('scanning motor...')
    #     self.net.scan(minId, maxId)
    #     print('scanning done.')

    def getId(self, minId=1, maxId=20):
        servoList = []
        for i in range(minId, maxId + 1):
            try :
                temp = self.ping(i)
                servoList.append(i)
                if verbose: print "Found servo #" + str(i)
                time.sleep(0.1)

            except Exception, detail:
                if verbose : print "Error pinging servo #" + str(i) + ': ' + str(detail)
                pass
        return servoList

    def readPosition(self, id):
        return self.servos.readPosition(id)

    def getCurrentPosition(self):
        return {i : self.readPosition(i) for i in self.getId()}

    def setTorque(self, val=True):
        for i in self.net.get_dynamixels():
            i.torque_enable = val

    def moveMotor(self, servoId=1, val=512, spd=120):
        for i in self.net.get_dynamixels():
            if i.id == servoId:
                toMove = i
        toMove.goal_position = val
        toMove.moving_speed = spd
        self.net.synchronize()

#     @pyqtSlot("pyqt_PyObject")
    def doAction(self, toBeDoneAction):
        for step in toBeDoneAction.action:
            if step.nth <= len(toBeDoneAction.action):
                while self.isRobotMoving():
                    waiting = True
                for servoId, servoPos in step.pos.items():
                    for servo in self.net.get_dynamixels():
                        if servo.id == int(servoId):
                            servo.goal_position = int(servoPos)
                            servo.moving_speed = int(step.speed)
                    self.net.synchronize()
                print("moving step", step.nth)

    def isRobotMoving(self):
        for i in self.net.get_dynamixels():
            if i.moving == True:
                return True
        return False

    def createAction(self, actionName=None):
        if actionName == None:
            return -1

        self.setTorque(False)
        stepList = []
        ans = None
        currentStep = 1
        while ans != 'd':
            speed = input("speed for step%i:" % currentStep)
            timegap = 0

            ans = input("Adjust motor for step %i: press enter to proceed to next step: " % currentStep)

            stepList.append(Step(self.getCurrentPosition(), int(speed), timegap, currentStep))

            currentStep += 1
            ans = input("type 'd' if finished.")

        return Action(stepList, actionName=actionName)


class Step:
    '''
    Class of step of action for robot
    :param pos: Dictionary of MOTORID as KEY and its POSITION as VALUE.
    :param speed: Speed to move motors in this step (int 1-255).
    :param timegap: Time to let motor move for this step [DEPRECATED].
    :param nth: Label of order of this step, doAction plays from min to max.
    '''

    def __init__(self, pos, speed, timegap, nth):
        self.pos = pos
        self.speed = speed
        self.timegap = timegap
        self.nth = nth


class Action:
    '''
    Class of action for robot
    :param actionName: Name of this action.
    :param listOfSteps: List of steps for this action.
    '''

    def __init__(self, listOfSteps, actionName=None):
        self.actionName = actionName
        self.action = listOfSteps


class ActionList:
    '''
    Class of action lists for robot
    :param listOfActions: List of actions fot the robot class.
    '''

    def __init__(self, listOfActions=None):
        if listOfActions != None:
            self.actionCollection = {i.actionName : i for i in listOfActions}
        else:
            self.actionCollection = None

    def listAction(self):
        return list(self.actionCollection.keys())

    def getAction(self, actName):
        try:
            return self.actionCollection[actName]
        except KeyError:
            print("There is no action '%s'" % actName)

    def addAction(self, act):
        if isinstance(act, Action):
            self.actionCollection.update({act.actionName : act})
        else:
            print("Must be instance of class Action")

    def removeAction(self, actName):
        try:
            del self.actionCollection[actName]
        except KeyError:
            print("There is no action '%s', removed nothing.." % actName)

    def to_JSON(self, filename='data/fahsaiActions.json'):
        try:
            with open(filename, 'w') as outfile:
                json.dump(jsonpickle.encode(self), outfile)
        except FileNotFoundError:
            print("Cannot find %s" % filename)

    def from_JSON(self, filename='data/fahsaiActions.json'):
        try:
            with open(filename, 'r') as infile:
                self.actionCollection = jsonpickle.decode(json.load(infile)).actionCollection
        except FileNotFoundError:
            print("Cannot find %s" % filename)
