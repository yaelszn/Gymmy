
import threading
import random

import serial
from pypot.creatures import PoppyTorso
import time
import poppy_torso
from serial import Serial

import Settings as s
from Audio import say, get_wav_duration
import pypot.dynamixel.io
import logging, sys

from MP import MP
from ScreenNew import DemoPage, ExercisePage, Screen, EntrancePage, FullScreenApp


class poppy(threading.Thread):

    ################################################# INITIALIZATION ###########################################
    def __init__(self):
        threading.Thread.__init__(self)

        self.gymmy = PoppyTorso(camera="dummy", port= "COM3")  # for real robot
        #self.gymmy = PoppyTorso(simulator='vrep')  # for simulator
        print("ROBOT INITIALIZATION")
        #self.gymmy.abs_z.goto_position(0, 1, wait=True)

        #for m in self.gymmy.motors:  # motors need to be initialized, False=stiff, True=loose
         #   m.compliant = False

        #self.gymmy.r_shoulder_x.complient= False
        for m in self.gymmy.motors:  # motors need to be initialized, False=stiff, True=loose
            m.compliant = False



        # left hand
        self.gymmy.r_shoulder_y.goto_position(-30, 1, wait=False)
        self.gymmy.r_elbow_y.goto_position(-60, 1, wait=False)
        self.gymmy.l_shoulder_y.goto_position(-120, 1, wait=False)
        self.gymmy.l_arm_z.goto_position(-90, 1, wait=False)
        self.gymmy.abs_z.goto_position(-40, 1, wait=False)
        time.sleep(2)

        self.gymmy.r_shoulder_y.goto_position(0, 1, wait=False)
        self.gymmy.r_elbow_y.goto_position(0, 1, wait=False)
        self.gymmy.l_shoulder_y.goto_position(0, 1, wait=False)
        self.gymmy.l_arm_z.goto_position(0, 1, wait=False)
        self.gymmy.abs_z.goto_position(0, 1, wait=False)
        time.sleep(2)

        self.gymmy.l_shoulder_y.goto_position(-30, 1, wait=False)
        self.gymmy.l_elbow_y.goto_position(-60, 1, wait=False)
        self.gymmy.r_shoulder_y.goto_position(-120, 1, wait=False)
        self.gymmy.r_arm_z.goto_position(90, 1, wait=False)
        self.gymmy.abs_z.goto_position(40, 1, wait=False)
        time.sleep(2)

        self.gymmy.l_shoulder_y.goto_position(0, 1, wait=False)
        self.gymmy.l_elbow_y.goto_position(0, 1, wait=False)
        self.gymmy.r_shoulder_y.goto_position(0, 1, wait=False)
        self.gymmy.r_arm_z.goto_position(0, 1, wait=False)
        self.gymmy.abs_z.goto_position(0, 1, wait=False)
        time.sleep(2)


if __name__ == "__main__":
    robot = Gymmy()
    robot.start()
