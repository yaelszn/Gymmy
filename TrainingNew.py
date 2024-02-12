import threading
import time
from Camera import Camera
from Gymmy import Gymmy
from ScreenNew import Screen, FullScreenApp, Ball, Rubber_Band, Stick, NoTool, StartingOfTraining, GoodbyePage, \
    EffortScale, EntrancePage
import Settings as s
import Excel
import random
from Audio import say, get_wav_duration
from datetime import datetime



class Training(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            self.training_session()
            self.finish_workout()


    def training_session(self):

        while s.ex_in_training==[]:
            time.sleep(0.0001)

        print("Training: start exercises")

        categories = ["ball", "stick", "notool", "band"]
        random.shuffle(categories)

        Excel.create_workbook() #create workbook in excel for this session
        time.sleep(7)
        self.exercises_by_order=[]

        for i in categories:
            exercises_in_category = [category for category in s.ex_in_training if i in category] #search for the exercises that are in the specific category
            random.shuffle(exercises_in_category)
            s.waved_has_tool=False
            if exercises_in_category!=[]:
                time.sleep(1)
                self.show_screen_category(i)

                while not s.waved_has_tool:
                    time.sleep(0.0001)

                for e in exercises_in_category:
                    self.exercises_by_order.append(e)
                    s.gymmy_done= False
                    s.camera_done= False
                    s.demo_finish = False
                    s.patient_repititions_counting=0
                    time.sleep(1)
                    self.run_exercise(e)
                    while (not s.gymmy_done) or (not s.camera_done):
                        # print("not done")
                        time.sleep(0.0001)
                    #s.gymmy_done = False
                    #s.camera_done = False
                    #s.demo_finish = False
                    time.sleep(3)

    def show_screen_category(self, category):
        if category=="ball":
            s.screen.switch_frame(Ball)
        elif category=="stick":
            s.screen.switch_frame(Stick)
        elif category=="band":
            s.screen.switch_frame(Rubber_Band)
        else:
            s.screen.switch_frame(NoTool)

    def finish_workout(self):
        time.sleep(3)
        s.finished_effort= False
        s.list_effort_each_exercise= {}
        s.screen.switch_frame(EffortScale, exercises=self.exercises_by_order)

        while not s.finished_effort:
            time.sleep(0.0001)

        say('goodbye')
        s.screen.switch_frame(GoodbyePage)
        Excel.success_worksheet()
        Excel.effort_worksheet()
        Excel.close_workbook()
        time.sleep(8)
        print("TRAINING DONE")
        self.reset()

    def run_exercise(self, name):
        time.sleep(0.1)  # wait between exercises
        s.success_exercise = False
        s.req_exercise = name
        print("TRAINING: Exercise ", name, " start")

        while not s.demo_finish or s.req_exercise == name:
            time.sleep(0.00000001)


        print("TRAINING: Exercise ", name, " done")
        time.sleep(3)
        # time.sleep(1)

    def reset(self):
        s.rep = 10
        s.req_exercise = ""
        s.finish_workout = False
        s.waved = False
        s.success_exercise = False
        s.calibration = False
        s.training_done = False
        s.gymmy_done = False
        s.camera_done = False
        s.robot_count = False
        s.demo_finish = False
        s.list_effort_each_exercise = {}
        s.ex_in_training = []
        # s.exercises_start=False
        s.waved_has_tool = True  # True just in order to go through the loop in Gymmy
        # Excel variable
        ############################# להוריד את הסולמיות
        s.ex_list = {}
        s.screen.switch_frame(EntrancePage)


if __name__ == "__main__":
    s.audio_path = 'audio files/Hebrew/Male/'
    # s.picture_path = 'audio files/' + language + '/' + gender + '/'
    # s.str_to_say = ""
    current_time = datetime.now()
    s.participant_code = str(current_time.day) + "." + str(current_time.month) + " " + str(current_time.hour) + "." + \
                         str(current_time.minute) + "." + str(current_time.second)
    s.waved = False
    s.finish_workout = False
    s.exercise_amount = 6
    s.rep = 10
    s.ex_in_training=["bend_elbows_ball", "arms_up_and_down_stick"]
    s.chosen_patient_ID="314808981"
    s.req_exercise=""
    s.demo_finish = False
    s.screen = Screen()
    s.camera = Camera()
    s.training = Training()
    s.robot= Gymmy()
    s.camera.start()
    s.training.start()
    s.robot.start()
    app = FullScreenApp(s.screen)
    s.screen.mainloop()
