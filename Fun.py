import threading
import random
from pypot.creatures import PoppyTorso
import time
import Settings as s
from Audio import say, get_wav_duration
from ScreenNew import ExercisePage, Screen, EntrancePage, FullScreenApp


class Gymmy(threading.Thread):

    ################################################# INITIALIZATION ###########################################
    def __init__(self):
        threading.Thread.__init__(self)

        #self.gymmy = PoppyTorso(camera="dummy", port= "COM3")  # for real robot
        self.gymmy = PoppyTorso(simulator='vrep')  # for simulator
        print("ROBOT INITIALIZATION")
        #self.gymmy.abs_z.goto_position(0, 1, wait=True)

        for m in self.gymmy.motors:  # motors need to be initialized, False=stiff, True=loose
            m.compliant = False
            time.sleep(0.1)

        self.init_robot()

    def init_robot(self):
        self.gymmy.l_shoulder_x.goto_position(10, 1.5, wait=True)
        self.gymmy.r_shoulder_x.goto_position(-10, 1.5, wait=True)

        for m in self.gymmy.motors:
            if not m.name == 'head_y' and not m.name == 'r_shoulder_x' and not m.name== 'l_shoulder_x':
                    m.goto_position(0, 1.5, wait=False)


        self.gymmy.head_y.goto_position(-20, 1.5, wait=False)

        time.sleep(1)

    ########################################################### RUN ##########################################
    def run(self):
        print("ROBOT START")

        self.exercise_demo()


        print("Robot Done")



    def exercise_demo(self):
