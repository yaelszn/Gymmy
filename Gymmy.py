import atexit
import threading
import signal
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
from ScreenNew import DemoPage, ExercisePage


class Gymmy(threading.Thread):

    ################################################# INITIALIZATION ###########################################
    def __init__(self):
        threading.Thread.__init__(self)

        #self.gymmy = PoppyTorso(camera="dummy", port= "COM3")  # for real robot
        self.gymmy = PoppyTorso(simulator='vrep')  # for simulator
        print("ROBOT INITIALIZATION")
        for m in self.gymmy.motors:  # motors need to be initialized, False=stiff, True=loose
            m.compliant = False
        #atexit.register(self.cleanup_func)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)  # Handle SIGINT (Ctrl+C)
        atexit.register(self.cleanup_func)
        self._stop_event = threading.Event()
        self.init_robot()

    def init_robot(self):
        #self.gymmy.bust_x.goto_position(0, 1, wait=True)
        #self.gymmy.bust_y.goto_position(0, 1, wait=True)


        for m in self.gymmy.motors:
            if not m.name == 'r_elbow_y' and not m.name == 'l_elbow_y' and not m.name == 'head_y' \
                and not m.name == 'abs_z' and not m.name == 'head_z':

                #and not m.name == 'head_z'):
               # and not m.name == 'bust_x' and not m.name == 'bust_y' :
                    m.goto_position(0, 1, wait=True)


                #and not m.name == 'r_arm_z' and not m.name == 'l_arm_z'):

       # self.gymmy.l_arm_z.goto_position(0, 0.5, wait=True)
        #self.gymmy.r_arm_z.goto_position(0, 0.5, wait=True)
        #self.gymmy.abs_z.goto_position(0, 0.5, wait=True)

        self.gymmy.abs_z.goto_position(-100, 1, wait=True)
        self.gymmy.head_y.goto_position(-20, 1, wait=True)
        self.gymmy.head_z.goto_position(20, 1, wait=True)
        self.gymmy.r_elbow_y.goto_position(90, 1, wait=True)
        self.gymmy.l_elbow_y.goto_position(90, 1, wait=True)


        time.sleep(1)



    def cleanup_func(self):
        self.init_robot()
        for m in self.gymmy.motors:  # motors need to be initialized, False=stiff, True=loose
            m.compliant = True
        self.gymmy.close()
        print("*************************************************************************")
        self._stop_event.set()
        s.finish_workout=True
    def signal_handler(self, sig, frame):
        print("###################################################################################")
        print("Received signal {}".format(sig))
        self.cleanup_func()



    ########################################################### RUN ##########################################
    def run(self):
        try:
            print("ROBOT START")
            while not s.finish_workout:
                time.sleep(0.00000001)  # Prevents the MP to stuck
                if s.req_exercise != "" and not s.req_exercise=="hello_waving":
                    ex = s.req_exercise
                    time.sleep(1)

                    print("ROBOT: Exercise ", ex, " start")
                    self.exercise_demo(ex)
                    print("ROBOT: Exercise ", ex, " done")


                    s.req_exercise = ""
                    s.gymmy_done = True

            print("Robot Done")

        except:
            self.cleanup_func()
        # time.sleep(3)
       # except SystemExit:
         # self.cleanup_func()

       # except KeyboardInterrupt:
        #  self.cleanup_func()






    def exercise_demo(self, ex):
        if ex == "hello_waving":
            s.demo_finish=True
            self.hello_waving()
        else:
            #dmonstration
            audio = s.req_exercise + '_' + str(s.rep) + '_times'
            say(audio)
            time.sleep(get_wav_duration(audio))
            s.screen.switch_frame(DemoPage)
            time.sleep(get_wav_duration('robot_demo'))
            getattr(self, ex)(0)
            time.sleep(1)
            s.screen.switch_frame(ExercisePage)
            say('start_ex')
            s.demo_finish = True
            self.faster_sayings = ['pick_up_pace', 'faster']
            said_faster= 0 #how many times the robot said faster encouragement
            for i in range(s.rep):
                getattr(self, ex)(i)
                print("robot count: "+str(i+1))
                if i-3>= s.patient_repititions_counting and said_faster==0:
                    self.random_faster()
                    said_faster+=1
                if i-6>=s.patient_repititions_counting and said_faster==1:
                    self.random_faster()
                    said_faster+=1
                if s.success_exercise:
                    break

    def random_faster(self):
        random_faster_name = random.choice(self.faster_sayings)
        self.faster_sayings.remove(random_faster_name)
        say(random_faster_name)


################################################################ WAVING EXERCISES ###############################33
    def hello_waving(self):
        if not s.waved:
            self.gymmy.r_shoulder_x.goto_position(-90, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(-80, 1.5, wait=False)
            for i in range(3):
                self.gymmy.r_arm[3].goto_position(-35, 0.6, wait=True)
                self.gymmy.r_arm[3].goto_position(35, 0.6, wait=True)
            self.finish_waving()

    def finish_waving(self):
        self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)
        self.gymmy.r_elbow_y.goto_position(90, 1.5, wait=False)
        self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)


################################################### Physiotherapy exercises ##########################################################

# ----------------------------------------------------- ball exercises Video No 1 ------------------------------

    # EX1
    def bend_elbows_ball(self, i):
        if i==0:
            self.gymmy.l_shoulder_y.goto_position(-40, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-40, 1, wait=False)
            time.sleep(1)
            self.gymmy.l_shoulder_x.goto_position(-7, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(7, 1, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1, wait=False)
            time.sleep(1)


        self.gymmy.r_arm[3].goto_position(-60, 1.5, wait=False)
        self.gymmy.l_arm[3].goto_position(-60, 1.5, wait=False)
        time.sleep(2)
        self.gymmy.r_arm[3].goto_position(85, 1.5, wait=False)
        self.gymmy.l_arm[3].goto_position(85, 1.5, wait=False)
        time.sleep(2)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)
            time.sleep(1.5)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)



    # EX2
    def raise_arms_above_head_ball(self, i):
        if i==0:
            self.gymmy.r_shoulder_x.goto_position(-25, 2, wait=False)
            self.gymmy.l_shoulder_x.goto_position(25, 2, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 2, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 2, wait=False)
            self.gymmy.r_arm[3].goto_position(50, 2, wait=False)
            self.gymmy.l_arm[3].goto_position(50, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-45, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-45, 2, wait=False)
            time.sleep(3)

        self.gymmy.l_shoulder_y.goto_position(-180, 1.5, wait=False)
        self.gymmy.r_shoulder_y.goto_position(-180, 1.5, wait=False)
        self.gymmy.r_arm[3].goto_position(50, 1.5, wait=False)
        self.gymmy.l_arm[3].goto_position(50, 1.5, wait=False)
        self.gymmy.r_shoulder_x.goto_position(-25, 1.5, wait=False)
        self.gymmy.l_shoulder_x.goto_position(25, 1.5, wait=False)

        time.sleep(3)
        self.gymmy.l_shoulder_y.goto_position(-45, 1.5, wait=False)
        self.gymmy.r_shoulder_y.goto_position(-45, 1.5, wait=False)
        self.gymmy.r_arm[3].goto_position(80, 1.5, wait=False)
        self.gymmy.l_arm[3].goto_position(-80, 1.5, wait=False)
        self.gymmy.r_shoulder_x.goto_position(-5, 1.5, wait=False)
        self.gymmy.l_shoulder_x.goto_position(5, 1.5, wait=False)
        time.sleep(3)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_arm_z.goto_position(0, 2, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 2, wait=False)
            time.sleep(1)
            self.gymmy.l_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.l_shoulder_x.goto_position(0, 2, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 2, wait=False)



    # EX3
    def raise_arms_forward_turn_ball(self, i):
        if i==0:
            self.gymmy.l_shoulder_y.goto_position(-90, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-90, 1.5, wait=False)
            time.sleep(2)
        self.gymmy.abs_z.goto_position(-170, 1.5, wait=False)
        time.sleep(2)
        self.gymmy.abs_z.goto_position(-100, 1.5, wait=False)
        time.sleep(2)
        self.gymmy.abs_z.goto_position(-30, 1.5, wait=False)
        time.sleep(2)
        self.gymmy.abs_z.goto_position(-100, 1.5, wait=False)
        time.sleep(2)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_shoulder_y.goto_position(0, 3, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 3, wait=False)
            self.gymmy.abs_z.goto_position(-100, 2, wait=False)
            time.sleep(2)
            self.gymmy.l_shoulder_x.goto_position(0, 2, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 2, wait=False)



# ------------------------------------------------------ ball exercises Video No 2 ------------------------------------

    # EX4
    def open_arms_and_forward_ball(self, i):
        if i==0:
            self.gymmy.l_shoulder_x.goto_position(5, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-5, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-90, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-90, 2, wait=False)
            time.sleep(4)

        self.gymmy.r_shoulder_x.goto_position(-85, 2, wait=False)
        self.gymmy.l_shoulder_x.goto_position(95, 2, wait=False)
        time.sleep(3)
        self.gymmy.l_shoulder_x.goto_position(-10, 2, wait=False)
        self.gymmy.r_shoulder_x.goto_position(10, 2, wait=False)
        time.sleep(3)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)



    # EX5
    def open_arms_above_head_ball(self, i):
        self.gymmy.l_shoulder_y.goto_position(-90, 1.5, wait=False)
        self.gymmy.r_shoulder_y.goto_position(-90, 1.5, wait=False)
        self.gymmy.l_shoulder_x.goto_position(90, 1.5, wait=False)
        self.gymmy.r_shoulder_x.goto_position(-90, 1.5, wait=False)
        time.sleep(3)
        self.gymmy.r_shoulder_x.goto_position(-10, 2, wait=False)
        self.gymmy.l_shoulder_x.goto_position(10, 2, wait=False)
        self.gymmy.l_shoulder_y.goto_position(-170, 2, wait=False)
        self.gymmy.r_shoulder_y.goto_position(-180, 2, wait=False)
        time.sleep(3)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_shoulder_y.goto_position(0, 3, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 3, wait=False)
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)



# -------------------------------------- Rubber band exercises --------------------------------------

    # EX6
    def open_arms_with_rubber_band(self, i):
        self.gymmy.l_shoulder_y.goto_position(-95, 1.5, wait=False)
        self.gymmy.r_shoulder_y.goto_position(-95, 1.5, wait=False)

        if i==0:
            self.gymmy.l_shoulder_x.goto_position(5, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-5, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.l_arm_z.goto_position(-80, 2, wait=False)
            self.gymmy.r_arm_z.goto_position(80, 2, wait=False)


        self.gymmy.l_shoulder_x.goto_position(-7, 1.5, wait=False)
        self.gymmy.r_shoulder_x.goto_position(7, 1.5, wait=False)
        time.sleep(3)
        self.gymmy.r_shoulder_x.goto_position(-20, 2, wait=False)
        self.gymmy.l_shoulder_x.goto_position(20, 2, wait=False)
        time.sleep(3)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)


    # EX7
    def open_arms_and_up_with_rubber_band(self, i):
        self.gymmy.l_shoulder_y.goto_position(-90, 1.5, wait=False)
        self.gymmy.r_shoulder_y.goto_position(-90, 1.5, wait=False)

        if i==0:
            self.gymmy.l_shoulder_x.goto_position(5, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-5, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.l_arm_z.goto_position(-80, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(80, 1.5, wait=False)
            time.sleep(0.5)

        self.gymmy.l_shoulder_x.goto_position(-5, 1, wait=False)
        self.gymmy.r_shoulder_x.goto_position(5, 1, wait=False)
        time.sleep(2)
        self.gymmy.l_shoulder_x.goto_position(25, 1, wait=False)
        self.gymmy.r_shoulder_x.goto_position(-25, 1, wait=False)
        time.sleep(2)
        self.gymmy.l_shoulder_y.goto_position(-180, 1.5, wait=False)
        self.gymmy.r_shoulder_y.goto_position(-180, 1.5, wait=False)
        time.sleep(2)
        self.gymmy.l_shoulder_y.goto_position(-90, 1.5, wait=False)
        self.gymmy.r_shoulder_y.goto_position(-90, 1.5, wait=False)
        time.sleep(2)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)


    # EX8
    def up_with_rubber_band_and_lean_both_sides(self, i):
        if i == 0:
            self.gymmy.l_shoulder_y.goto_position(-90, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-90, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(5, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-5, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.l_arm_z.goto_position(-80, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(80, 1.5, wait=False)
            time.sleep(1)
            self.gymmy.l_shoulder_x.goto_position(25, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-25, 1.5, wait=True)
            self.gymmy.l_shoulder_y.goto_position(-180, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-180, 1.5, wait=False)

        #time.sleep(1)
        self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
        time.sleep(3)
        self.gymmy.bust_x.goto_position(-30, 1.5, wait=False)
        time.sleep(3)
        self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
        time.sleep(3)
        self.gymmy.bust_x.goto_position(30, 1.5, wait=False)
        time.sleep(3)
        self.gymmy.bust_x.goto_position(0, 1.5, wait=False)

        if i == (s.rep - 1):
            # init
            self.gymmy.bust_x.goto_position(0, 1.5, wait=True)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=True)
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)



# -------------------------------------- Stick exercises ------------------------------------------------------------------

    # EX9
    def bend_elbows_stick(self, i):
        if i==0:
            self.gymmy.l_shoulder_y.goto_position(-40, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-40, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=True)
            time.sleep(2)

        self.gymmy.r_arm[3].goto_position(-60, 1.5, wait=False)
        self.gymmy.l_arm[3].goto_position(-60, 1.5, wait=False)
        time.sleep(2.5)
        self.gymmy.r_arm[3].goto_position(85, 1.5, wait=False)
        self.gymmy.l_arm[3].goto_position(85, 1.5, wait=False)
        time.sleep(2.5)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)


    # EX10
    def bend_elbows_and_up_stick(self, i):
        self.gymmy.l_shoulder_y.goto_position(-25, 1.5, wait=False)
        self.gymmy.r_shoulder_y.goto_position(-25, 1.5, wait=False)
        self.gymmy.r_arm[3].goto_position(-40, 1.5, wait=False)
        self.gymmy.l_arm[3].goto_position(-40, 1.5, wait=False)
        self.gymmy.r_shoulder_x.goto_position(-5, 1.5, wait=False)
        self.gymmy.l_shoulder_x.goto_position(5, 1.5, wait=True)
        time.sleep(1)
       # self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)
        #self.gymmy.l_shoulder_x.goto_position(10, 1, wait=True)
        self.gymmy.r_arm[3].goto_position(40, 1.5, wait=False)
        self.gymmy.l_arm[3].goto_position(40, 1, wait=False)
        self.gymmy.l_shoulder_y.goto_position(-140, 1.5, wait=False)
        self.gymmy.r_shoulder_y.goto_position(-140, 1.5, wait=False)
        self.gymmy.r_shoulder_x.goto_position(-10, 1.5, wait=False)
        self.gymmy.l_shoulder_x.goto_position(10, 1.5, wait=True)
       # self.gymmy.r_arm_z.goto_position(90, 1.5, wait=False)
        #self.gymmy.l_arm_z.goto_position(90, 1.5, wait=False)
        time.sleep(1)

        if i == (s.rep - 1):
            # init
            self.gymmy.r_arm[3].goto_position(90, 1.5, wait=False)
            self.gymmy.l_arm[3].goto_position(90, 1.5, wait=True)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)

    # EX11
    def arms_up_and_down_stick(self, i):
        if i==0:
            self.gymmy.r_shoulder_x.goto_position(-20, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(20, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(80, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-80, 1.5, wait=False)
            self.gymmy.r_arm[3].goto_position(90, 1.5, wait=False)
            self.gymmy.l_arm[3].goto_position(90, 1.5, wait=True)


        self.gymmy.r_shoulder_y.goto_position(-50, 1.5, wait=False)
        self.gymmy.l_shoulder_y.goto_position(-50, 1.5, wait=False)
        time.sleep(2.5)
        self.gymmy.r_shoulder_y.goto_position(-150, 1.5, wait=False)
        self.gymmy.l_shoulder_y.goto_position(-150, 1.5, wait=False)
        time.sleep(2.5)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)



    # EX12
    def switch_with_stick(self, i):
        if i==0:
            self.gymmy.r_arm_z.goto_position(80, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-80, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-15, 2, wait=False)
            self.gymmy.l_shoulder_x.goto_position(15, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-100, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-100, 2, wait=False)
            time.sleep(3)

        self.gymmy.abs_z.goto_position(-170, 1.5, wait=False)
        time.sleep(2)
        self.gymmy.abs_z.goto_position(-100, 1.5, wait=False)
        time.sleep(2)
        self.gymmy.abs_z.goto_position(-30, 1.5, wait=False)
        time.sleep(2)
        self.gymmy.abs_z.goto_position(-100, 1.5, wait=False)
        time.sleep(2)

        if i == (s.rep - 1):
            # init
            self.gymmy.abs_z.goto_position(-100, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=True)
            time.sleep(0.5)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)




# -------------------------------------- No equipment exercises ------------------------------------------------------------------

    # EX13 - Hands behind the head and bend to each side
    def hands_behind_and_lean_notool(self, i):
        if i == 0:
            self.gymmy.head_z.goto_position(20, 1, wait=True)
            self.gymmy.r_shoulder_x.goto_position(-40, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(40, 1.5, wait=True)
            self.gymmy.r_shoulder_y.goto_position(-180, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-180, 1.5, wait=True)
            self.gymmy.r_arm_z.goto_position(80, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-80, 1.5, wait=True)
            self.gymmy.r_arm[3].goto_position(-60, 1.5, wait=False)
            self.gymmy.l_arm[3].goto_position(-60, 1.5, wait=True)


        self.gymmy.bust_x.goto_position(-30, 1.5, wait=False)
        time.sleep(2.5)
        self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
        time.sleep(2.5)
        self.gymmy.bust_x.goto_position(30, 1.5, wait=False)
        time.sleep(2.5)
        self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
        time.sleep(2.5)

        if i == (s.rep - 1):
            # init
            self.gymmy.bust_x.goto_position(0, 1.5, wait=True)
            self.gymmy.r_arm[3].goto_position(90, 1.5, wait=False)
            self.gymmy.l_arm[3].goto_position(90, 1.5, wait=True)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=True)
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=True)


    # EX14 - Hands behind the head and turn to each side
    def hands_behind_and_turn_both_sides_notool(self, i):
        if i==0:
            self.gymmy.r_shoulder_x.goto_position(-40, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(40, 1.5, wait=True)
            self.gymmy.r_shoulder_y.goto_position(-180, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-180, 1.5, wait=True)
            self.gymmy.r_arm_z.goto_position(80, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-80, 1.5, wait=True)
            self.gymmy.r_arm[3].goto_position(-60, 1.5, wait=False)
            self.gymmy.l_arm[3].goto_position(-60, 1.5, wait=True)

        self.gymmy.abs_z.goto_position(-180, 2, wait=False)
        time.sleep(3)
        self.gymmy.abs_z.goto_position(-100, 2, wait=False)
        time.sleep(3)
        self.gymmy.abs_z.goto_position(-20, 2, wait=False)
        time.sleep(3)
        self.gymmy.abs_z.goto_position(-100, 2, wait=False)
        time.sleep(3)


        if i == (s.rep - 1):
            # init
            self.gymmy.abs_z.goto_position(-100, 1.5, wait=False)
            self.gymmy.r_arm[3].goto_position(90, 1.5, wait=False)
            self.gymmy.l_arm[3].goto_position(90, 1.5, wait=True)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=True)
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=True)


    # EX15 - Right Hand up and bend to the left
    def right_hand_up_and_bend_notool(self, i):
        if i==0:
            self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(5, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=True)
            self.gymmy.r_arm_z.goto_position(80, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-25, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-180, 1.5, wait=False)
            self.gymmy.r_arm[3].goto_position(60, 1.5, wait=False)
            time.sleep(1)


        self.gymmy.l_shoulder_x.goto_position(50, 1.5, wait=False)
        self.gymmy.l_shoulder_y.goto_position(5, 1.5, wait=False)
       # self.gymmy.l_arm[3].goto_position(40, 1.5, wait=False)
        self.gymmy.bust_x.goto_position(-40, 1.5, wait=True)
        time.sleep(2)
        self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
        self.gymmy.l_shoulder_x.goto_position(5, 1.5, wait=False)
        self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=True)
        time.sleep(2)

        if i == (s.rep - 1):
            # init
            self.gymmy.bust_x.goto_position(0, 1.5, wait=True)
            self.gymmy.l_arm[3].goto_position(90, 1.5, wait=True)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm[3].goto_position(90, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=True)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)

    # EX16 - Left Hand up and bend to the right
    def left_hand_up_and_bend_notool(self, i):
        if i==0:
            self.gymmy.l_arm_z.goto_position(-80, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(25, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-180, 1.5, wait=False)
            self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-5, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=True)
            self.gymmy.l_arm[3].goto_position(60, 1.5, wait=False)
            time.sleep(1)


        self.gymmy.r_shoulder_x.goto_position(-50, 1.5, wait=False)
        self.gymmy.r_shoulder_y.goto_position(5, 1.5, wait=False)
        #self.gymmy.r_arm[3].goto_position(50, 1.5, wait=False)
        self.gymmy.bust_x.goto_position(40, 1.5, wait=True)
        time.sleep(2)
        self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
        self.gymmy.r_shoulder_x.goto_position(-5, 1.5, wait=False)
        self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=True)
        time.sleep(2)

        if i == (s.rep - 1):
            # init
            self.gymmy.bust_x.goto_position(0, 1.5, wait=True)
            self.gymmy.l_arm[3].goto_position(90, 1.5, wait=True)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm[3].goto_position(90, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=True)
            self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)


    # EX 17
    def raising_right_and_left_hand_alternately(self, i):
        # left hand
        self.gymmy.l_shoulder_x.goto_position(10, 1.5, wait=False)
        #self.gymmy.l_shoulder_y.goto_position(-30, 1.5, wait=False)
       # self.gymmy.l_arm[3].goto_position(-25, 2, wait=False)
        self.gymmy.r_arm[3].goto_position(35, 1.5, wait=False)
        #self.gymmy.l_arm[3].goto_position(90, 2, wait=False)
        self.gymmy.l_shoulder_y.goto_position(-130, 1.5, wait=True)
        #time.sleep(0.2)
        self.gymmy.abs_z.goto_position(-170, 1.5, wait=False)
        time.sleep(2)

        # back to middle\init
        self.gymmy.abs_z.goto_position(-100, 1.5, wait=False)
        time.sleep(0.2)
        self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
        self.gymmy.l_shoulder_x.goto_position(0, 1.5, wait=False)
        self.gymmy.r_arm[3].goto_position(90, 1.5, wait=False)
        self.gymmy.l_arm[3].goto_position(90, 1.5, wait=False)
        time.sleep(2)

        # right hand
        self.gymmy.r_shoulder_x.goto_position(-10, 1.5, wait=False)
       # self.gymmy.r_shoulder_y.goto_position(-30, 1.5, wait=False)
       # self.gymmy.r_arm[3].goto_position(-25, 2, wait=False)
        self.gymmy.l_arm[3].goto_position(35, 1.5, wait=False)
        #self.gymmy.r_arm[3].goto_position(90, 2, wait=False)
        self.gymmy.r_shoulder_y.goto_position(-130, 1.5, wait=True)
        #time.sleep(0.2)
        self.gymmy.abs_z.goto_position(-30, 1.5, wait=False)
        time.sleep(2)

        # back to middle\init
        self.gymmy.abs_z.goto_position(-100, 1.5, wait=False)
        time.sleep(0.2)
        self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
        self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)
        self.gymmy.l_arm[3].goto_position(90, 1.5, wait=False)
        self.gymmy.r_arm[3].goto_position(90, 1.5, wait=False)
        time.sleep(2)





if __name__ == "__main__":
    s.rep = 3
    s.success_exercise = False
    s.finish_workout = False

    #########################למחוק
    s.robot_count = False
    language = 'Hebrew'
    gender = 'Male'
    s.audio_path = 'audio files/' + language + '/' + gender + '/'
    #s.picture_path = 'audio files/' + language + '/' + gender + '/'
    ###########################################################
    s.waved=True
    s.finish_workout=False
    s.req_exercise="bend_elbows_ball"
    robot = Gymmy()
    #mp=MP()
    #mp.start()
    robot.start()
    #signal.signal(signal.SIGTERM, signal_handler)
    #signal.signal(signal.SIGINT, signal_handler)


    #robot.join()
    #robot.exercise_demo("bend_elbows_ball")

   # s.robot.exercise_demo("open_and_close_arms_90")
    #s.robot.exercise_demo("raise_arms_forward")
    # robot.start()
    #time.sleep(10)

    # robot.poppy.l_shoulder_y.goto_position(-90, 1.5, wait=False)
    # robot.poppy.r_shoulder_y.goto_position(-90, 1.5, wait=True)
    # robot.poppy.l_shoulder_x.goto_position(90, 1, wait=False)
    # # robot.poppy.r_shoulder_x.goto_position(-90, 1, wait=True)
    # robot.poppy.l_elbow_y.goto_position(0, 1.5, wait=False)
    # robot.poppy.r_elbow_y.goto_position(0, 1.5, wait=True)

    #robot.join()
    #time.sleep(5)
    #s.finish_workout=True
    while not s.finish_workout:
       time.sleep(1)
    #sys.exit()