import threading
import random
from datetime import datetime

from pypot.creatures import PoppyTorso
import time
import Settings as s
from Audio import say, get_wav_duration
from ScreenNew import ExercisePage, Screen, EntrancePage, FullScreenApp


class Gymmy(threading.Thread):

    ################################################# INITIALIZATION ###########################################
    def __init__(self):
        threading.Thread.__init__(self)

        self.gymmy = PoppyTorso(camera="dummy", port= "COM4")  # for real robot
        #self.gymmy = PoppyTorso(simulator='vrep')  # for simulator
        print("ROBOT INITIALIZATION")
        #self.gymmy.abs_z.goto_position(0, 1, wait=True)

        for m in self.gymmy.motors:  # motors need to be initialized, False=stiff, True=loose
            m.compliant = False
            time.sleep(0.1)

        self.init_robot()

    def init_robot(self):
        self.gymmy.l_shoulder_x.goto_position(10, 2, wait=True)
        self.gymmy.r_shoulder_x.goto_position(-10, 2, wait=True)

        for m in self.gymmy.motors:
            if not m.name == 'head_y' and not m.name == 'r_shoulder_x' and not m.name== 'l_shoulder_x':
                    m.goto_position(0, 2, wait=False)


        self.gymmy.head_y.goto_position(-20, 2, wait=False)

        time.sleep(1)

    ########################################################### RUN ##########################################
    def run(self):
        print("ROBOT START")
        while not s.finish_program:
            while not s.finish_workout:
                time.sleep(0.00000001)  # Prevents the MP to stuck
                if s.req_exercise != "" and not s.req_exercise=="hello_waving":
                    ex = s.req_exercise
                    time.sleep(2)

                    print("ROBOT: Exercise ", ex, " start")
                    self.exercise_demo(ex)
                    print("ROBOT: Exercise ", ex, " done")


                    s.req_exercise = ""
                    s.gymmy_done = True

                elif s.finish_program:
                    break

                else:
                    time.sleep(2)  # Prevents the MP to stuck

        print("Robot Done")



    def exercise_demo(self, ex):
        if ex == "hello_waving":
            #s.demo_finish=True
            self.hello_waving()
        else:
            self.faster_sayings = ['pick_up_pace', 'faster']
            getattr(self, ex)("demo", "slow")
            time.sleep(3)
            s.gymmy_finished_demo = True

            random_number_for_faster_saying = random.randint(3, 6)

            for i in range(s.rep):
                if s.finish_program:
                    break

                while s.did_training_paused and not s.stop_requested:
                    time.sleep(0.01)

                if s.stop_requested:
                    self.init_robot()
                    break

                s.robot_counter = i

                getattr(self, ex)(i, s.rate)

                print("robot count: "+str(i+1))
                if i-random_number_for_faster_saying>= s.patient_repetitions_counting_in_exercise and i!=s.rep-1: #-1 because i starts from 0
                    self.random_faster()
                    s.last_saying_time = datetime.now()

                if s.success_exercise or s.stop_requested:
                    self.init_robot()
                    break

    def random_faster(self):
        print(" ")
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
                self.gymmy.r_arm[3].goto_position(-35, 0.6, wait=False)
                self.gymmy.r_arm[3].goto_position(35, 0.6, wait=False)
            self.finish_waving()

    def finish_waving(self):
        self.gymmy.r_shoulder_x.goto_position(0, 1.5, wait=False)
        self.gymmy.r_elbow_y.goto_position(90, 1.5, wait=False)
        self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)


################################################### Physiotherapy exercises ##########################################################

# ----------------------------------------------------- ball exercises Video No 1 ------------------------------

    # EX1
    def ball_bend_elbows(self, i, rate):
        if i=="demo":
            self.gymmy.l_shoulder_y.goto_position(-50, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-50, 1, wait=False)
            time.sleep(1)
            self.gymmy.l_shoulder_x.goto_position(5, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-5, 1, wait=False)
            time.sleep(1)

            while not s.explanation_over:
                self.gymmy.r_elbow_y.goto_position(-135, 1.75, wait=False)
                self.gymmy.l_elbow_y.goto_position(-135, 1.75, wait=True)
                time.sleep(0.75)
                self.gymmy.r_elbow_y.goto_position(0, 1.75, wait=False)
                self.gymmy.l_elbow_y.goto_position(0, 1.75, wait=True)
                time.sleep(0.75)

            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)
            time.sleep(1)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)


        else:
            if i==0:
                self.gymmy.l_shoulder_y.goto_position(-50, 1, wait=False)
                self.gymmy.r_shoulder_y.goto_position(-50, 1, wait=False)
                time.sleep(1)
                self.gymmy.l_shoulder_x.goto_position(5, 1, wait=False)
                self.gymmy.r_shoulder_x.goto_position(-5, 1, wait=False)
                time.sleep(1)


            if (rate=="fast"):
                self.gymmy.r_elbow_y.goto_position(-135, 1.25, wait=False)
                self.gymmy.l_elbow_y.goto_position(-135, 1.25, wait=True)
                time.sleep(0.25)
                self.gymmy.r_elbow_y.goto_position(0, 1.25, wait=False)
                self.gymmy.l_elbow_y.goto_position(0, 1.25, wait=True)
                time.sleep(0.25)

            elif (rate=="moderate"):
                self.gymmy.r_elbow_y.goto_position(-135, 1.5, wait=False)
                self.gymmy.l_elbow_y.goto_position(-135, 1.5, wait=True)
                time.sleep(0.5)
                self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
                self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=True)
                time.sleep(0.5)

            else:
                self.gymmy.r_elbow_y.goto_position(-135, 1.75, wait=False)
                self.gymmy.l_elbow_y.goto_position(-135, 1.75, wait=True)
                time.sleep(0.75)
                self.gymmy.r_elbow_y.goto_position(0, 1.75, wait=False)
                self.gymmy.l_elbow_y.goto_position(0, 1.75, wait=True)
                time.sleep(0.75)


            if i == (s.rep - 1):
                # init
                self.gymmy.l_shoulder_x.goto_position(10, 1, wait=False)
                self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)
                time.sleep(1)
                self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
                self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
                self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
                self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)




    # EX2
    def ball_raise_arms_above_head(self, i, rate):
        if i==0:
            self.gymmy.l_shoulder_y.goto_position(-55, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-55, 1, wait=False)
            time.sleep(1)
            self.gymmy.l_shoulder_x.goto_position(-15, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(15, 1, wait=False)

        if (rate=="fast"):
            self.gymmy.l_shoulder_y.goto_position(-75, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-75, 1.25, wait=False)
            self.gymmy.l_shoulder_x.goto_position(-15, 1.25, wait=False)
            self.gymmy.r_shoulder_x.goto_position(15, 1.25, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.25, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.25, wait=True)
            time.sleep(0.5)
            self.gymmy.l_arm_z.goto_position(30, 1.25, wait=False)
            self.gymmy.r_arm_z.goto_position(-30, 1.25, wait=False)
            self.gymmy.l_shoulder_x.goto_position(15, 1.25, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-15, 1.25, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.25, wait=True)
            time.sleep(0.5)

        elif (rate=="moderate"):
            self.gymmy.l_shoulder_y.goto_position(-75, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-75, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(-15, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(15, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=True)
            time.sleep(0.75)
            self.gymmy.l_arm_z.goto_position(30, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(-30, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(15, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-15, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.5, wait=True)
            time.sleep(0.75)

        else:
            self.gymmy.l_shoulder_y.goto_position(-75, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-75, 1.75, wait=False)
            self.gymmy.l_shoulder_x.goto_position(-15, 1.75, wait=False)
            self.gymmy.r_shoulder_x.goto_position(15, 1.75, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.75, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.l_arm_z.goto_position(30, 1.75, wait=False)
            self.gymmy.r_arm_z.goto_position(-30, 1.75, wait=False)
            self.gymmy.l_shoulder_x.goto_position(15, 1.75, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-15, 1.75, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.75, wait=True)
            time.sleep(1)



        if i == (s.rep - 1):
            # init
            self.gymmy.l_arm_z.goto_position(0, 2, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 2, wait=False)
            time.sleep(1)
            self.gymmy.l_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 2, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 2, wait=False)



    # EX3
    def ball_switch(self, i, rate):
        if i==0:
            self.gymmy.l_shoulder_y.goto_position(-100, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-100, 1.5, wait=False)
            time.sleep(2)
            self.gymmy.l_shoulder_x.goto_position(-10, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(10, 1, wait=False)
            time.sleep(2)

        if (rate=="fast"):
            self.gymmy.abs_z.goto_position(-60, 1, wait=True)
            time.sleep(0.75)
            self.gymmy.abs_z.goto_position(0, 1, wait=True)
            time.sleep(0.75)
            self.gymmy.abs_z.goto_position(60, 1, wait=True)
            time.sleep(0.75)
            self.gymmy.abs_z.goto_position(0, 1, wait=True)
            time.sleep(0.75)

        elif (rate=="moderate"):
            self.gymmy.abs_z.goto_position(-60, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(0, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(60, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(0, 1.25, wait=True)
            time.sleep(1)

        else:
            self.gymmy.abs_z.goto_position(-60, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(0, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(60, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(0, 1.75, wait=True)
            time.sleep(1)



        if i == (s.rep - 1):
            # init
            self.gymmy.l_shoulder_x.goto_position(10, 2, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 2, wait=False)
            time.sleep(2)
            self.gymmy.l_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.abs_z.goto_position(0, 2, wait=False)

    def ball_hands_up_and_bend_backwards(self, i, rate):
        if i == 0:
            self.gymmy.r_shoulder_y.goto_position(-165, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-165, 2, wait=False)
            time.sleep(2)

        if (rate == "fast"):
            self.gymmy.r_elbow_y.goto_position(-135, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-135, 1, wait=True)
            time.sleep(0.5)
            self.gymmy.r_elbow_y.goto_position(0, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.r_elbow_y.goto_position(-135, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-135, 1.5, wait=True)
            time.sleep(1)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=True)
            time.sleep(1)
        else:
            self.gymmy.r_elbow_y.goto_position(-135, 2, wait=False)
            self.gymmy.l_elbow_y.goto_position(-135, 2, wait=True)
            time.sleep(1.5)
            self.gymmy.r_elbow_y.goto_position(0, 2, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 2, wait=True)
            time.sleep(1.5)

        if i == (s.rep - 1):
            self.gymmy.r_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 2, wait=False)




# ------------------------------------------------------ ball exercises Video No 2 ------------------------------------

    # EX4
    def ball_open_arms_and_forward(self, i, rate):
        if i==0:
            self.gymmy.l_shoulder_y.goto_position(-100, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-100, 1.5, wait=False)
            time.sleep(1)
            self.gymmy.l_shoulder_x.goto_position(-10, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(10, 1, wait=False)
            time.sleep(2)

        if (rate=="fast"):
            self.gymmy.l_shoulder_x.goto_position(75, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-75, 1, wait=True)
            time.sleep(0.5)
            self.gymmy.l_shoulder_x.goto_position(-10, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(10, 1, wait=True)
            time.sleep(0.5)

        elif (rate=="moderate"):
            self.gymmy.l_shoulder_x.goto_position(75, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-75, 1.5, wait=True)
            time.sleep(1)
            self.gymmy.l_shoulder_x.goto_position(-10, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(10, 1.5, wait=True)
            time.sleep(1)

        else:
            self.gymmy.l_shoulder_x.goto_position(75, 2, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-75, 2, wait=True)
            time.sleep(1)
            self.gymmy.l_shoulder_x.goto_position(-10, 2, wait=False)
            self.gymmy.r_shoulder_x.goto_position(10, 2, wait=True)
            time.sleep(1)


        if i == (s.rep - 1):
            # init
            self.gymmy.l_shoulder_x.goto_position(10, 2, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 2, wait=False)
            time.sleep(2)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)



    # EX5
    def ball_open_arms_above_head(self, i, rate):
        if i==0:
            self.gymmy.r_shoulder_x.goto_position(-90, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(90, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-180, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-180, 1.5, wait=False)
            time.sleep(1)


        if (rate=="fast"):
            self.gymmy.r_shoulder_x.goto_position(-90, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(90, 1, wait=True)
            time.sleep(0.5)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.r_shoulder_x.goto_position(-90, 1.25, wait=False)
            self.gymmy.l_shoulder_x.goto_position(90, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.25, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.25, wait=True)
            time.sleep(1)

        else:
            self.gymmy.r_shoulder_x.goto_position(-90, 1.75, wait=False)
            self.gymmy.l_shoulder_x.goto_position(90, 1.75, wait=True)
            time.sleep(1.25)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.75, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.75, wait=True)
            time.sleep(1.25)




        if i == (s.rep - 1):
            self.gymmy.r_shoulder_x.goto_position(-90, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(90, 1, wait=False)
            time.sleep(2)
            # init
            self.gymmy.l_shoulder_y.goto_position(0, 3, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 3, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 2, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 2, wait=False)



# -------------------------------------- Rubber band exercises --------------------------------------

    # EX6
    def band_open_arms(self, i, rate):
        if i==0:
            self.gymmy.r_arm_z.goto_position(90, 0.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 0.5, wait=False)
            time.sleep(1)
            self.gymmy.l_shoulder_y.goto_position(-90, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-90, 1.5, wait=False)
            time.sleep(1)


        if (rate=="fast"):
            self.gymmy.l_shoulder_x.goto_position(-5, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(5, 1, wait=True)
            time.sleep(0.5)
            self.gymmy.l_shoulder_x.goto_position(20, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-20, 1, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.l_shoulder_x.goto_position(-5, 1.25, wait=False)
            self.gymmy.r_shoulder_x.goto_position(5, 1.25, wait=True)
            time.sleep(0.75)
            self.gymmy.l_shoulder_x.goto_position(20, 1.25, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-20, 1.25, wait=True)
            time.sleep(0.75)

        else:

            self.gymmy.l_shoulder_x.goto_position(-5, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(5, 1.5, wait=True)
            time.sleep(1)
            self.gymmy.l_shoulder_x.goto_position(20, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-20, 1.5, wait=True)
            time.sleep(1)


        if i == (s.rep - 1):
            # init
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 2, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 2, wait=False)


    # EX7
    def band_open_arms_and_up(self, i, rate):
        if i == 0:
            self.gymmy.l_shoulder_y.goto_position(-90, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-90, 1.5, wait=False)
            time.sleep(2)
            self.gymmy.l_shoulder_x.goto_position(-5, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(5, 1, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 0.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 0.5, wait=False)
            time.sleep(2)

        if (rate=="fast"):
            self.gymmy.l_shoulder_x.goto_position(30, 0.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-30, 0.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 0.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 0.5, wait=True)
            self.gymmy.l_shoulder_y.goto_position(-170, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1, wait=True)
            time.sleep(0.75)
            self.gymmy.l_shoulder_y.goto_position(-90, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-90, 1, wait=True)
            self.gymmy.l_shoulder_x.goto_position(-5, 0.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(5, 0.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 0.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0,0.5, wait=True)
            time.sleep(0.75)


        elif (rate == "moderate"):
            self.gymmy.l_shoulder_x.goto_position(30, 0.75, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-30, 0.75, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 0.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 0.75, wait=True)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.25, wait=True)
            time.sleep(1)

            self.gymmy.l_shoulder_y.goto_position(-90, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-90, 1.25, wait=True)
            self.gymmy.l_shoulder_x.goto_position(-5, 0.75, wait=False)
            self.gymmy.r_shoulder_x.goto_position(5, 0.75, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 0.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 0.75, wait=True)
            time.sleep(0.75)

        else:
            self.gymmy.l_shoulder_x.goto_position(30, 1.25, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-30, 1.25, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 1.25, wait=True)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.5, wait=True)
            time.sleep(1)

            self.gymmy.l_shoulder_y.goto_position(-90, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-90, 1.5, wait=True)
            self.gymmy.l_shoulder_x.goto_position(-5, 1.25, wait=False)
            self.gymmy.r_shoulder_x.goto_position(5, 1.25, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.25, wait=True)
            time.sleep(0.75)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.5, wait=False)
            time.sleep(2)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)



    # EX8
    def band_up_and_lean(self, i, rate):
        if i == 0:
            self.gymmy.l_shoulder_x.goto_position(30, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-30, 1, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 1, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 0.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 0.5, wait=False)
            time.sleep(1)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.5, wait=False)
            time.sleep(1.5)

        if (rate=="fast"):
            self.gymmy.bust_x.goto_position(0, 0.75, wait=True)
            time.sleep(0.75)
            self.gymmy.bust_x.goto_position(30, 0.75, wait=True)
            time.sleep(0.75)
            self.gymmy.bust_x.goto_position(0, 0.75, wait=True)
            time.sleep(0.75)
            self.gymmy.bust_x.goto_position(-30, 0.75, wait=True)
            time.sleep(0.75)


        elif (rate == "moderate"):
            self.gymmy.bust_x.goto_position(0, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.bust_x.goto_position(30, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.bust_x.goto_position(0, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.bust_x.goto_position(-30, 1.25, wait=True)
            time.sleep(1)

        else:
            self.gymmy.bust_x.goto_position(0, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.bust_x.goto_position(30, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.bust_x.goto_position(0, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.bust_x.goto_position(-30, 1.75, wait=True)
            time.sleep(1)

        if i == (s.rep - 1):
            # init
            self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)



# -------------------------------------- Stick exercises ------------------------------------------------------------------

    # EX9
    def stick_bend_elbows(self, i, rate):
        if i == 0:
            self.gymmy.l_shoulder_y.goto_position(-50, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-50, 1, wait=False)
            time.sleep(2)
            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=True)
            time.sleep(1)

        if (rate=="fast"):
            self.gymmy.r_elbow_y.goto_position(-135, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(-135, 1.25, wait=True)
            time.sleep(0.25)
            self.gymmy.r_elbow_y.goto_position(0, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.25, wait=True)
            time.sleep(0.25)

        elif (rate=="moderate"):
            self.gymmy.r_elbow_y.goto_position(-135, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-135, 1.5, wait=True)
            time.sleep(0.5)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=True)
            time.sleep(0.5)

        else:
            self.gymmy.r_elbow_y.goto_position(-135, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(-135, 1.75, wait=True)
            time.sleep(0.75)
            self.gymmy.r_elbow_y.goto_position(0, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.75, wait=True)
            time.sleep(0.75)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)
            time.sleep(1)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)


    # EX10
    def stick_bend_elbows_and_up(self, i, rate):

        if (rate=="fast"):
            self.gymmy.r_elbow_y.goto_position(-120, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-120, 1, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-20, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-20, 1, wait=True)
            time.sleep(0.5)

            self.gymmy.r_elbow_y.goto_position(-10, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-10, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(20, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-20, 1, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-160, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-160, 1, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.r_elbow_y.goto_position(-120, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-120, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-20, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-20, 1.5, wait=True)
            time.sleep(0.5)

            self.gymmy.r_elbow_y.goto_position(-10, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-10, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(20, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-20, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-160, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-160, 1.5, wait=True)
            time.sleep(0.5)

        else:
            self.gymmy.r_elbow_y.goto_position(-120, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(-120, 1.75, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-20, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-20, 1.75, wait=True)
            time.sleep(0.75)

            self.gymmy.r_elbow_y.goto_position(-10, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(-10, 1.75, wait=False)
            self.gymmy.l_shoulder_x.goto_position(20, 1.75, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-20, 1.75, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-160, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-160, 1.75, wait=True)
            time.sleep(0.75)


        if i == (s.rep - 1):
            # init
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)

    # EX11
    def stick_raise_arms_above_head(self, i, rate):
        if i==0:
            self.gymmy.l_arm_z.goto_position(-90, 1, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(30, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-30, 1, wait=False)

        if (rate=="fast"):
            self.gymmy.l_shoulder_y.goto_position(-50, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-50, 1.25, wait=True)
            time.sleep(0.5)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.25, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.l_shoulder_y.goto_position(-50, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-50, 1.5, wait=True)
            time.sleep(0.75)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.5, wait=True)
            time.sleep(0.75)

        else:
            self.gymmy.l_shoulder_y.goto_position(-50, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-50, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.75, wait=True)
            time.sleep(1)



        if i == (s.rep - 1):
            # init
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            time.sleep(1)
            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)



    # EX12
    def stick_switch(self, i, rate):
        if i==0:
            self.gymmy.l_shoulder_y.goto_position(-100, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-100, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 1, wait=False)
            time.sleep(2)

        if (rate=="fast"):
            self.gymmy.abs_z.goto_position(-60, 1, wait=True)
            time.sleep(0.75)
            self.gymmy.abs_z.goto_position(0, 1, wait=True)
            time.sleep(0.75)
            self.gymmy.abs_z.goto_position(60, 1, wait=True)
            time.sleep(0.75)
            self.gymmy.abs_z.goto_position(0, 1, wait=True)
            time.sleep(0.75)

        elif (rate == "moderate"):
            self.gymmy.abs_z.goto_position(-60, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(0, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(60, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(0, 1.25, wait=True)
            time.sleep(1)

        else:
            self.gymmy.abs_z.goto_position(-60, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(0, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(60, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(0, 1.75, wait=True)
            time.sleep(1)


        if i == (s.rep - 1):
            # init
            self.gymmy.abs_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)

    def stick_bending_forward(self, i, rate):
        if i == 0:
            self.gymmy.r_arm_z.goto_position(90, 1, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1, wait=True)
            time.sleep(1)

        if (rate == "fast"):
            self.gymmy.bust_y.goto_position(25, 1, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-100, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-100, 1, wait=True)
            time.sleep(0.75)

            self.gymmy.bust_y.goto_position(0, 1, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.bust_y.goto_position(25, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-100, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-100, 1.5, wait=True)
            time.sleep(1)

            self.gymmy.bust_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 2, wait=True)
            time.sleep(0.75)

        else:
            self.gymmy.bust_y.goto_position(25, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-100, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-100, 2, wait=True)
            time.sleep(1)

            self.gymmy.bust_y.goto_position(0, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 2, wait=True)
            time.sleep(1)

        if i == (s.rep - 1):
            self.gymmy.r_arm_z.goto_position(0, 1, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1, wait=True)

    # -------------------------------------- No equipment exercises ------------------------------------------------------------------

    # EX13 - Hands behind the head and bend to each side
    def notool_hands_behind_and_lean(self, i, rate):
        if i == 0:
            self.gymmy.l_arm_z.goto_position(85, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(-85, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(120, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-120, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-120, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(-120, 1.5, wait=False)

        if (rate=="fast"):
            self.gymmy.bust_x.goto_position(0, 0.75, wait=True)
            time.sleep(0.75)
            self.gymmy.bust_x.goto_position(30, 0.75, wait=True)
            time.sleep(0.75)
            self.gymmy.bust_x.goto_position(0, 0.75, wait=True)
            time.sleep(0.75)
            self.gymmy.bust_x.goto_position(-30, 0.75, wait=True)
            time.sleep(0.75)

        elif (rate == "moderate"):
            self.gymmy.bust_x.goto_position(0, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.bust_x.goto_position(30, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.bust_x.goto_position(0, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.bust_x.goto_position(-30, 1.25, wait=True)
            time.sleep(1)


        else:
            self.gymmy.bust_x.goto_position(0, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.bust_x.goto_position(30, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.bust_x.goto_position(0, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.bust_x.goto_position(-30, 1.75, wait=True)
            time.sleep(1)


        if i == (s.rep - 1):
            # init
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
            time.sleep(2)
            self.gymmy.l_shoulder_x.goto_position(10, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)


    # EX14 - Right Hand up and bend to the left
    def notool_right_hand_up_and_bend(self, i, rate):
        if i==0:
            self.gymmy.l_arm_z.goto_position(85, 1, wait=False)

        if (rate=="fast"):
            self.gymmy.r_shoulder_x.goto_position(-60, 0.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(-60, 0.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(160, 1, wait=False)
            self.gymmy.bust_x.goto_position(50, 1, wait=True)
            time.sleep(0.5)

            self.gymmy.l_shoulder_x.goto_position(20, 1, wait=False)
            self.gymmy.bust_x.goto_position(0, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1, wait=False)
            time.sleep(0.5)
            self.gymmy.r_elbow_y.goto_position(0, 1, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.r_shoulder_x.goto_position(-60, 1, wait=False)
            self.gymmy.r_elbow_y.goto_position(-60, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(160, 1.5, wait=False)
            self.gymmy.bust_x.goto_position(50, 1.5, wait=True)
            time.sleep(1)

            self.gymmy.l_shoulder_x.goto_position(20, 1.5, wait=False)
            self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=True)
            time.sleep(1)

        else:
            self.gymmy.r_shoulder_x.goto_position(-60, 1, wait=False)
            self.gymmy.r_elbow_y.goto_position(-60, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 1.75, wait=False)
            self.gymmy.l_shoulder_x.goto_position(160, 1.75, wait=False)
            self.gymmy.bust_x.goto_position(50, 1.75, wait=True)
            time.sleep(1.5)

            self.gymmy.l_shoulder_x.goto_position(20, 1.75, wait=False)
            self.gymmy.bust_x.goto_position(0, 1.75, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.75, wait=False)
            time.sleep(0.5)
            self.gymmy.r_elbow_y.goto_position(0, 1.75, wait=True)
            time.sleep(1.5)




        if i == (s.rep - 1):
            # init
            self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)




    # EX15 - Left Hand up and bend to the right
    def notool_left_hand_up_and_bend(self, i, rate):
        if i == 0:
            self.gymmy.r_arm_z.goto_position(-85, 1, wait=False)

        if (rate=="fast"):
            self.gymmy.l_shoulder_x.goto_position(60, 0.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-60, 0.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-160, 1, wait=False)
            self.gymmy.bust_x.goto_position(-50, 1, wait=True)
            time.sleep(0.5)

            self.gymmy.r_shoulder_x.goto_position(-20, 1, wait=False)
            self.gymmy.bust_x.goto_position(0, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1, wait=False)
            time.sleep(0.5)
            self.gymmy.l_elbow_y.goto_position(0, 1, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.l_shoulder_x.goto_position(60, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-60, 1, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-160, 1.5, wait=False)
            self.gymmy.bust_x.goto_position(-50, 1.5, wait=True)
            time.sleep(1)

            self.gymmy.r_shoulder_x.goto_position(-20, 1.5, wait=False)
            self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=True)
            time.sleep(1)

        else:
            self.gymmy.l_shoulder_x.goto_position(60, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-60, 1, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 1.75, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-160, 1.75, wait=False)
            self.gymmy.bust_x.goto_position(-50, 1.75, wait=True)
            time.sleep(1.5)

            self.gymmy.r_shoulder_x.goto_position(-20, 1.75, wait=False)
            self.gymmy.bust_x.goto_position(0, 1.75, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.75, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.75, wait=False)
            time.sleep(0.5)
            self.gymmy.l_elbow_y.goto_position(0, 1.75, wait=True)
            time.sleep(1.5)



        if i == (s.rep - 1):
            # init
            self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)


    # EX 16 - Hand up diagonaly and turn, both hands
    def notool_raising_hands_diagonally(self, i, rate):

        if (rate=="fast"):
            self.gymmy.abs_z.goto_position(0, 1.25, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.25, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.25, wait=True)
            time.sleep(0.25)

            # left hand
            self.gymmy.r_shoulder_y.goto_position(-30, 1.25, wait=False)
            self.gymmy.r_elbow_y.goto_position(-30, 1.25, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-150, 1.25, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.25, wait=False)
            self.gymmy.abs_z.goto_position(-40, 1.25, wait=True)
            time.sleep(0.25)

            self.gymmy.abs_z.goto_position(0, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.25, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.25, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.25, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.25, wait=True)
            time.sleep(0.25)


            self.gymmy.l_shoulder_y.goto_position(-30, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(-30, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-150, 1.25, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 1.25, wait=False)
            self.gymmy.abs_z.goto_position(40, 1.25, wait=True)
            time.sleep(0.25)


        elif (rate=="moderate"):
            self.gymmy.abs_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=True)
            time.sleep(0.75)

            # left hand
            self.gymmy.r_shoulder_y.goto_position(-30, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(-30, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-150, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.abs_z.goto_position(-40, 1.5, wait=True)
            time.sleep(0.75)

            self.gymmy.abs_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=True)
            time.sleep(0.75)

            self.gymmy.l_shoulder_y.goto_position(-30, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-30, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-150, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 1.5, wait=False)
            self.gymmy.abs_z.goto_position(40, 1.5, wait=True)
            time.sleep(0.75)

        else:
            self.gymmy.abs_z.goto_position(0, 1.75, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.75, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.75, wait=True)
            time.sleep(1)

            # left hand
            self.gymmy.r_shoulder_y.goto_position(-30, 1.75, wait=False)
            self.gymmy.r_elbow_y.goto_position(-30, 1.75, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-150, 1.75, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.75, wait=False)
            self.gymmy.abs_z.goto_position(-40, 1.75, wait=True)
            time.sleep(1)

            self.gymmy.abs_z.goto_position(0, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.75, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.75, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.75, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.75, wait=True)
            time.sleep(1)

            self.gymmy.l_shoulder_y.goto_position(-30, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(-30, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-150, 1.75, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 1.75, wait=False)
            self.gymmy.abs_z.goto_position(40, 1.75, wait=True)
            time.sleep(1)


        if i == (s.rep - 1):
            self.gymmy.abs_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=True)






    def weights_bending_forward(self, i, rate):
        if i == 0:
            self.gymmy.r_arm_z.goto_position(90, 1, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1, wait=True)
            time.sleep(1)

        if (rate == "fast"):
            self.gymmy.bust_y.goto_position(25, 1, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-100, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-100, 1, wait=True)
            time.sleep(0.75)

            self.gymmy.bust_y.goto_position(0, 1, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.bust_y.goto_position(25, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-100, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-100, 1.5, wait=True)
            time.sleep(1)

            self.gymmy.bust_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 2, wait=True)
            time.sleep(0.75)

        else:
            self.gymmy.bust_y.goto_position(25, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-100, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-100, 2, wait=True)
            time.sleep(1)

            self.gymmy.bust_y.goto_position(0, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 2, wait=True)
            time.sleep(1)

        if i == (s.rep - 1):
            self.gymmy.r_arm_z.goto_position(0, 1, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1, wait=True)




    def weights_right_hand_to_side_left_up(self, i, rate):
        if i == 0:
            self.gymmy.l_shoulder_y.goto_position(-165, 2, wait=False)
            time.sleep(2)

        self.gymmy.r_shoulder_x.goto_position(-100, 2, wait=False)
        self.gymmy.l_elbow_y.goto_position(-90, 2, wait=False)

    def weights_hands_up_and_bend_backwards(self, i, rate):
        if i == 0:
            self.gymmy.r_shoulder_y.goto_position(-165, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-165, 2, wait=False)
            time.sleep(2)

        if (rate=="fast"):
            self.gymmy.r_elbow_y.goto_position(-135, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-135, 1, wait=True)
            time.sleep(0.5)
            self.gymmy.r_elbow_y.goto_position(0, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1, wait=True)
            time.sleep(0.5)

        elif (rate=="moderate"):
            self.gymmy.r_elbow_y.goto_position(-135, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-135, 1.5, wait=True)
            time.sleep(1)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=True)
            time.sleep(1)
        else:
            self.gymmy.r_elbow_y.goto_position(-135, 2, wait=False)
            self.gymmy.l_elbow_y.goto_position(-135, 2, wait=True)
            time.sleep(1.5)
            self.gymmy.r_elbow_y.goto_position(0, 2, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 2, wait=True)
            time.sleep(1.5)

        if i == (s.rep - 1):
            self.gymmy.r_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 2, wait=False)




    def pronation_supination_notool(self, i, rate):
        if i == 0:
            self.gymmy.r_shoulder_y.goto_position(-100, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-100, 2, wait=True)
            time.sleep(1)

        if (rate == "fast"):

            self.gymmy.r_arm_z.goto_position(90, 1, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1, wait=True)
            time.sleep(0.25)

            self.gymmy.r_arm_z.goto_position(-90, 1, wait=False)
            self.gymmy.l_arm_z.goto_position(90, 1, wait=True)
            time.sleep(0.25)

        elif (rate=="moderate"):

            self.gymmy.r_arm_z.goto_position(90, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1.5, wait=True)
            time.sleep(0.25)

            self.gymmy.r_arm_z.goto_position(-90, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(90, 1.5, wait=True)
            time.sleep(0.25)

        else:

            self.gymmy.r_arm_z.goto_position(90, 2, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 2, wait=True)
            time.sleep(0.5)

            self.gymmy.r_arm_z.goto_position(-90, 2, wait=False)
            self.gymmy.l_arm_z.goto_position(90, 2, wait=True)
            time.sleep(0.5)


        if i == (s.rep - 1):
            self.gymmy.r_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 2, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 2, wait=True)



    def pronation_supination_weights(self, i, rate):
        if i == 0:
            self.gymmy.r_shoulder_y.goto_position(-100, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-100, 2, wait=True)
            time.sleep(1)

        if (rate == "fast"):

            self.gymmy.r_arm_z.goto_position(90, 1, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1, wait=True)
            time.sleep(0.25)

            self.gymmy.r_arm_z.goto_position(-90, 1, wait=False)
            self.gymmy.l_arm_z.goto_position(90, 1, wait=True)
            time.sleep(0.25)

        elif (rate == "moderate"):

            self.gymmy.r_arm_z.goto_position(90, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1.5, wait=True)
            time.sleep(0.25)

            self.gymmy.r_arm_z.goto_position(-90, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(90, 1.5, wait=True)
            time.sleep(0.25)

        else:

            self.gymmy.r_arm_z.goto_position(90, 2, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 2, wait=True)
            time.sleep(0.5)

            self.gymmy.r_arm_z.goto_position(-90, 2, wait=False)
            self.gymmy.l_arm_z.goto_position(90, 2, wait=True)
            time.sleep(0.5)

        if i == (s.rep - 1):
            self.gymmy.r_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 2, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 2, wait=True)


    def raise_arms_above_head_weights(self, i, rate):
        if i == 0:
            self.gymmy.l_arm_z.goto_position(-90, 1, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(30, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-30, 1, wait=False)

        if (rate == "fast"):
            self.gymmy.l_shoulder_y.goto_position(-50, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-50, 1.25, wait=True)
            time.sleep(0.5)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.25, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.l_shoulder_y.goto_position(-50, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-50, 1.5, wait=True)
            time.sleep(0.75)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.5, wait=True)
            time.sleep(0.75)

        else:
            self.gymmy.l_shoulder_y.goto_position(-50, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-50, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.75, wait=True)
            time.sleep(1)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            time.sleep(1)
            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)






    def hands_up_to_sides_notool (self, i, rate):
        robot.gymmy.l_shoulder_x.goto_position(100, 1, wait=False)
        robot.gymmy.r_shoulder_x.goto_position(-100, 1, wait=True)
        time.sleep(1)

        robot.gymmy.l_shoulder_x.goto_position(10, 1, wait=False)
        robot.gymmy.r_shoulder_x.goto_position(-10, 1, wait=True)
        time.sleep(1)

    def help (self, i, rate):
        if i == 0:
            robot.gymmy.l_shoulder_x.goto_position(100, 1, wait=False)
            robot.gymmy.r_shoulder_x.goto_position(-100, 1, wait=False)
            self.gymmy.r_arm_z.goto_position(-90, 2, wait=False)
            self.gymmy.l_arm_z.goto_position(90, 2, wait=True)
            time.sleep(1)

        self.gymmy.r_elbow_y.goto_position(-135, 2, wait=True)
        time.sleep(1)
        self.gymmy.r_elbow_y.goto_position(0, 2, wait=True)
        time.sleep(1)
        self.gymmy.l_elbow_y.goto_position(-135, 2, wait=True)
        time.sleep(1)
        self.gymmy.l_elbow_y.goto_position(0, 2, wait=True)
        time.sleep(1)

    def bend_elbows_weights(self, i, rate):
        if i == 0:
            self.gymmy.l_shoulder_y.goto_position(-50, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-50, 1, wait=False)
            time.sleep(1)
            self.gymmy.l_shoulder_x.goto_position(5, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-5, 1, wait=False)
            time.sleep(1)

        if (rate == "fast"):
            self.gymmy.r_elbow_y.goto_position(-135, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(-135, 1.25, wait=True)
            time.sleep(0.25)
            self.gymmy.r_elbow_y.goto_position(0, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.25, wait=True)
            time.sleep(0.25)

        elif (rate == "moderate"):
            self.gymmy.r_elbow_y.goto_position(-135, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-135, 1.5, wait=True)
            time.sleep(0.5)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=True)
            time.sleep(0.5)

        else:
            self.gymmy.r_elbow_y.goto_position(-135, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(-135, 1.75, wait=True)
            time.sleep(0.75)
            self.gymmy.r_elbow_y.goto_position(0, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.75, wait=True)
            time.sleep(0.75)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)
            time.sleep(1)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)


    def switch_with_weights(self, i, rate):
        if i==0:
            self.gymmy.l_shoulder_y.goto_position(-100, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-100, 1.5, wait=False)
            time.sleep(2)
            self.gymmy.l_shoulder_x.goto_position(-10, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(10, 1, wait=False)
            time.sleep(2)

        if (rate=="fast"):
            self.gymmy.abs_z.goto_position(-60, 1, wait=True)
            time.sleep(0.75)
            self.gymmy.abs_z.goto_position(0, 1, wait=True)
            time.sleep(0.75)
            self.gymmy.abs_z.goto_position(60, 1, wait=True)
            time.sleep(0.75)
            self.gymmy.abs_z.goto_position(0, 1, wait=True)
            time.sleep(0.75)

        elif (rate=="moderate"):
            self.gymmy.abs_z.goto_position(-60, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(0, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(60, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(0, 1.25, wait=True)
            time.sleep(1)

        else:
            self.gymmy.abs_z.goto_position(-60, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(0, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(60, 1.75, wait=True)
            time.sleep(1)
            self.gymmy.abs_z.goto_position(0, 1.75, wait=True)
            time.sleep(1)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_shoulder_x.goto_position(10, 2, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 2, wait=False)
            time.sleep(2)
            self.gymmy.l_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 2, wait=False)
            self.gymmy.abs_z.goto_position(0, 2, wait=False)


    def open_arms_and_forward_weights(self, i, rate):
            if i==0:
                self.gymmy.l_shoulder_y.goto_position(-100, 1.5, wait=False)
                self.gymmy.r_shoulder_y.goto_position(-100, 1.5, wait=False)
                time.sleep(1)
                self.gymmy.l_shoulder_x.goto_position(-10, 1, wait=False)
                self.gymmy.r_shoulder_x.goto_position(10, 1, wait=False)
                time.sleep(2)

            if (rate=="fast"):
                self.gymmy.l_shoulder_x.goto_position(75, 1, wait=False)
                self.gymmy.r_shoulder_x.goto_position(-75, 1, wait=True)
                time.sleep(0.5)
                self.gymmy.l_shoulder_x.goto_position(-10, 1, wait=False)
                self.gymmy.r_shoulder_x.goto_position(10, 1, wait=True)
                time.sleep(0.5)

            elif (rate=="moderate"):
                self.gymmy.l_shoulder_x.goto_position(75, 1.5, wait=False)
                self.gymmy.r_shoulder_x.goto_position(-75, 1.5, wait=True)
                time.sleep(1)
                self.gymmy.l_shoulder_x.goto_position(-10, 1.5, wait=False)
                self.gymmy.r_shoulder_x.goto_position(10, 1.5, wait=True)
                time.sleep(1)

            else:
                self.gymmy.l_shoulder_x.goto_position(75, 2, wait=False)
                self.gymmy.r_shoulder_x.goto_position(-75, 2, wait=True)
                time.sleep(1)
                self.gymmy.l_shoulder_x.goto_position(-10, 2, wait=False)
                self.gymmy.r_shoulder_x.goto_position(10, 2, wait=True)
                time.sleep(1)


            if i == (s.rep - 1):
                # init
                self.gymmy.l_shoulder_x.goto_position(10, 2, wait=False)
                self.gymmy.r_shoulder_x.goto_position(-10, 2, wait=False)
                time.sleep(2)
                self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
                self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)

    def open_arms_above_head_weights(self, i, rate):
        if i == 0:
            self.gymmy.r_shoulder_x.goto_position(-90, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(90, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-180, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-180, 1.5, wait=False)
            time.sleep(1)

        if (rate == "fast"):
            self.gymmy.r_shoulder_x.goto_position(-90, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(90, 1, wait=True)
            time.sleep(0.5)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.r_shoulder_x.goto_position(-90, 1.25, wait=False)
            self.gymmy.l_shoulder_x.goto_position(90, 1.25, wait=True)
            time.sleep(1)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.25, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.25, wait=True)
            time.sleep(1)

        else:
            self.gymmy.r_shoulder_x.goto_position(-90, 1.75, wait=False)
            self.gymmy.l_shoulder_x.goto_position(90, 1.75, wait=True)
            time.sleep(1.25)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.75, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.75, wait=True)
            time.sleep(1.25)

        if i == (s.rep - 1):
            self.gymmy.r_shoulder_x.goto_position(-90, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(90, 1, wait=False)
            time.sleep(2)
            # init
            self.gymmy.l_shoulder_y.goto_position(0, 3, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 3, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 2, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 2, wait=False)

    def open_arms_and_up_with_weights(self, i, rate):
        if i == 0:
            self.gymmy.l_shoulder_y.goto_position(-90, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-90, 1.5, wait=False)
            time.sleep(2)
            self.gymmy.l_shoulder_x.goto_position(-5, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(5, 1, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 0.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 0.5, wait=False)
            time.sleep(2)

        if (rate == "fast"):
            self.gymmy.l_shoulder_x.goto_position(30, 0.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-30, 0.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 0.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 0.5, wait=True)
            self.gymmy.l_shoulder_y.goto_position(-170, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1, wait=True)
            time.sleep(0.75)
            self.gymmy.l_shoulder_y.goto_position(-90, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-90, 1, wait=True)
            self.gymmy.l_shoulder_x.goto_position(-5, 0.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(5, 0.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 0.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 0.5, wait=True)
            time.sleep(0.75)


        elif (rate == "moderate"):
            self.gymmy.l_shoulder_x.goto_position(30, 0.75, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-30, 0.75, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 0.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 0.75, wait=True)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.25, wait=True)
            time.sleep(1)

            self.gymmy.l_shoulder_y.goto_position(-90, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-90, 1.25, wait=True)
            self.gymmy.l_shoulder_x.goto_position(-5, 0.75, wait=False)
            self.gymmy.r_shoulder_x.goto_position(5, 0.75, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 0.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 0.75, wait=True)
            time.sleep(0.75)

        else:
            self.gymmy.l_shoulder_x.goto_position(30, 1.25, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-30, 1.25, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 1.25, wait=True)
            self.gymmy.l_shoulder_y.goto_position(-170, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-170, 1.5, wait=True)
            time.sleep(1)

            self.gymmy.l_shoulder_y.goto_position(-90, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-90, 1.5, wait=True)
            self.gymmy.l_shoulder_x.goto_position(-5, 1.25, wait=False)
            self.gymmy.r_shoulder_x.goto_position(5, 1.25, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.25, wait=True)
            time.sleep(0.75)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.5, wait=False)
            time.sleep(2)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)

    def bend_elbows_and_up_weights(self, i, rate):

        if (rate == "fast"):
            self.gymmy.r_elbow_y.goto_position(-120, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-120, 1, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-20, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-20, 1, wait=True)
            time.sleep(0.5)

            self.gymmy.r_elbow_y.goto_position(-10, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-10, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(20, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-20, 1, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-160, 1, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-160, 1, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.r_elbow_y.goto_position(-120, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-120, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-20, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-20, 1.5, wait=True)
            time.sleep(0.5)

            self.gymmy.r_elbow_y.goto_position(-10, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-10, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(20, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-20, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-160, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-160, 1.5, wait=True)
            time.sleep(0.5)

        else:
            self.gymmy.r_elbow_y.goto_position(-120, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(-120, 1.75, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-20, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-20, 1.75, wait=True)
            time.sleep(0.75)

            self.gymmy.r_elbow_y.goto_position(-10, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(-10, 1.75, wait=False)
            self.gymmy.l_shoulder_x.goto_position(20, 1.75, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-20, 1.75, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-160, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-160, 1.75, wait=True)
            time.sleep(0.75)

        if i == (s.rep - 1):
            # init
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)

    def right_hand_up_and_bend_weights(self, i, rate):
        if i == 0:
            self.gymmy.l_arm_z.goto_position(85, 1, wait=False)

        if (rate == "fast"):
            self.gymmy.r_shoulder_x.goto_position(-60, 0.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(-60, 0.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(160, 1, wait=False)
            self.gymmy.bust_x.goto_position(50, 1, wait=True)
            time.sleep(0.5)

            self.gymmy.l_shoulder_x.goto_position(20, 1, wait=False)
            self.gymmy.bust_x.goto_position(0, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1, wait=False)
            time.sleep(0.5)
            self.gymmy.r_elbow_y.goto_position(0, 1, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.r_shoulder_x.goto_position(-60, 1, wait=False)
            self.gymmy.r_elbow_y.goto_position(-60, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(160, 1.5, wait=False)
            self.gymmy.bust_x.goto_position(50, 1.5, wait=True)
            time.sleep(1)

            self.gymmy.l_shoulder_x.goto_position(20, 1.5, wait=False)
            self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=True)
            time.sleep(1)

        else:
            self.gymmy.r_shoulder_x.goto_position(-60, 1, wait=False)
            self.gymmy.r_elbow_y.goto_position(-60, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-20, 1.75, wait=False)
            self.gymmy.l_shoulder_x.goto_position(160, 1.75, wait=False)
            self.gymmy.bust_x.goto_position(50, 1.75, wait=True)
            time.sleep(1.5)

            self.gymmy.l_shoulder_x.goto_position(20, 1.75, wait=False)
            self.gymmy.bust_x.goto_position(0, 1.75, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.75, wait=False)
            time.sleep(0.5)
            self.gymmy.r_elbow_y.goto_position(0, 1.75, wait=True)
            time.sleep(1.5)

        if i == (s.rep - 1):
            # init
            self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-10, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=False)


    def left_hand_up_and_bend_weights(self, i, rate):
        if i == 0:
            self.gymmy.r_arm_z.goto_position(-85, 1, wait=False)

        if (rate=="fast"):
            self.gymmy.l_shoulder_x.goto_position(60, 0.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-60, 0.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 1, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-160, 1, wait=False)
            self.gymmy.bust_x.goto_position(-50, 1, wait=True)
            time.sleep(0.5)

            self.gymmy.r_shoulder_x.goto_position(-20, 1, wait=False)
            self.gymmy.bust_x.goto_position(0, 1, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1, wait=False)
            time.sleep(0.5)
            self.gymmy.l_elbow_y.goto_position(0, 1, wait=True)
            time.sleep(0.5)

        elif (rate == "moderate"):
            self.gymmy.l_shoulder_x.goto_position(60, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-60, 1, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 1.5, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-160, 1.5, wait=False)
            self.gymmy.bust_x.goto_position(-50, 1.5, wait=True)
            time.sleep(1)

            self.gymmy.r_shoulder_x.goto_position(-20, 1.5, wait=False)
            self.gymmy.bust_x.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            time.sleep(0.5)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=True)
            time.sleep(1)

        else:
            self.gymmy.l_shoulder_x.goto_position(60, 1, wait=False)
            self.gymmy.l_elbow_y.goto_position(-60, 1, wait=False)
            self.gymmy.r_elbow_y.goto_position(-20, 1.75, wait=False)
            self.gymmy.r_shoulder_x.goto_position(-160, 1.75, wait=False)
            self.gymmy.bust_x.goto_position(-50, 1.75, wait=True)
            time.sleep(1.5)

            self.gymmy.r_shoulder_x.goto_position(-20, 1.75, wait=False)
            self.gymmy.bust_x.goto_position(0, 1.75, wait=False)
            self.gymmy.l_shoulder_x.goto_position(10, 1.75, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.75, wait=False)
            time.sleep(0.5)
            self.gymmy.l_elbow_y.goto_position(0, 1.75, wait=True)
            time.sleep(1.5)


    def raising_hands_diagonally_weights(self, i, rate):

        if (rate=="fast"):
            self.gymmy.abs_z.goto_position(0, 1.25, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.25, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.25, wait=True)
            time.sleep(0.25)

            # left hand
            self.gymmy.r_shoulder_y.goto_position(-30, 1.25, wait=False)
            self.gymmy.r_elbow_y.goto_position(-30, 1.25, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-150, 1.25, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.25, wait=False)
            self.gymmy.abs_z.goto_position(-40, 1.25, wait=True)
            time.sleep(0.25)

            self.gymmy.abs_z.goto_position(0, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.25, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.25, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.25, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.25, wait=True)
            time.sleep(0.25)


            self.gymmy.l_shoulder_y.goto_position(-30, 1.25, wait=False)
            self.gymmy.l_elbow_y.goto_position(-30, 1.25, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-150, 1.25, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 1.25, wait=False)
            self.gymmy.abs_z.goto_position(40, 1.25, wait=True)
            time.sleep(0.25)


        elif (rate=="moderate"):
            self.gymmy.abs_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=True)
            time.sleep(0.75)

            # left hand
            self.gymmy.r_shoulder_y.goto_position(-30, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(-30, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-150, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.abs_z.goto_position(-40, 1.5, wait=True)
            time.sleep(0.75)

            self.gymmy.abs_z.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.5, wait=True)
            time.sleep(0.75)

            self.gymmy.l_shoulder_y.goto_position(-30, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(-30, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-150, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 1.5, wait=False)
            self.gymmy.abs_z.goto_position(40, 1.5, wait=True)
            time.sleep(0.75)

        else:
            self.gymmy.abs_z.goto_position(0, 1.75, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.75, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.75, wait=True)
            time.sleep(1)

            # left hand
            self.gymmy.r_shoulder_y.goto_position(-30, 1.75, wait=False)
            self.gymmy.r_elbow_y.goto_position(-30, 1.75, wait=False)
            self.gymmy.l_shoulder_y.goto_position(-150, 1.75, wait=False)
            self.gymmy.l_arm_z.goto_position(-90, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.75, wait=False)
            self.gymmy.abs_z.goto_position(-40, 1.75, wait=True)
            time.sleep(1)

            self.gymmy.abs_z.goto_position(0, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.75, wait=False)
            self.gymmy.r_elbow_y.goto_position(0, 1.75, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.75, wait=False)
            self.gymmy.l_arm_z.goto_position(0, 1.75, wait=True)
            time.sleep(1)

            self.gymmy.l_shoulder_y.goto_position(-30, 1.75, wait=False)
            self.gymmy.l_elbow_y.goto_position(-30, 1.75, wait=False)
            self.gymmy.r_shoulder_y.goto_position(-150, 1.75, wait=False)
            self.gymmy.r_arm_z.goto_position(90, 1.75, wait=False)
            self.gymmy.abs_z.goto_position(40, 1.75, wait=True)
            time.sleep(1)


        if i == (s.rep - 1):
            self.gymmy.abs_z.goto_position(0, 1.5, wait=False)
            self.gymmy.l_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.l_elbow_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_shoulder_y.goto_position(0, 1.5, wait=False)
            self.gymmy.r_arm_z.goto_position(0, 1.5, wait=True)




if __name__ == "__main__":
    s.rep = 7
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
    s.did_training_paused=False
    s.stop_requested=False
    s.rate="slow"
    #######################################################################
    #s.req_exercise ="bend_elbows_ball"
    #s.req_exercise = "raise_arms_above_head_ball"
    #s.req_exercise = "raise_arms_forward_turn_ball"
    #s.req_exercise = "open_arms_and_forward_ball"
    #s.req_exercise = "open_arms_above_head_ball"
    #s.req_exercise = "open_arms_with_band"
    #s.req_exercise = "open_arms_and_up_with_band"
    #s.req_exercise = "up_with_band_and_lean"
    #s.req_exercise = "bend_elbows_stick"
    #s.req_exercise = "bend_elbows_and_up_stick"
    #s.req_exercise = "arms_up_and_down_stick"
    #s.req_exercise = "switch_with_stick"
    #s.req_exercise = "hands_behind_and_lean_notool"
    #s.req_exercise="right_hand_up_and_bend_notool"
    #s.req_exercise = "left_hand_up_and_bend_notool"
    #s.req_exercise = "raising_hands_diagonally_notool"
    #s.req_exercise = "notool_bending_forward"
    #s.req_exercise = "weights_hands_up_and_bend_backwards"
    s.req_exercise = "weights_right_hand_to_side_left_up"

    s.rate="moderate"


    robot = Gymmy()
    s.patient_repetitions_counting_in_exercise=0
    s.finish_program= False
    #mp=MP()
    #mp.start()
    robot.start()
    s.screen = Screen()


    app = FullScreenApp(s.screen)
    s.screen.mainloop()




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

    #sys.exit()