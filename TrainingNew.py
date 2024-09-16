import threading
import time
from Camera import Camera
from Gymmy import Gymmy
from ScreenNew import Screen, FullScreenApp, Ball, Rubber_Band, Stick, NoTool, StartOfTraining, GoodbyePage, \
    EffortScale, EntrancePage, ExplanationPage, ExercisePage
import Settings as s
import Excel
import random
from Audio import say, get_wav_duration
from datetime import datetime
import Email



class Training(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            self.training_session()
            self.finish_training()

    def training_session(self):

        while s.ex_in_training==[]:
            time.sleep(1)

        print("Training: start exercises")
        s.start_time = time.time()

        categories = ["ball", "stick", "notool", "band"]
        random.shuffle(categories)

        Excel.create_workbook() #create workbook in excel for this session
        time.sleep(7)
        self.exercises_by_order=[]

        for i in categories:
            exercises_in_category = [category for category in s.ex_in_training if i in category] #search for the exercises that are in the specific category
            random.shuffle(exercises_in_category)
            s.waved_has_tool= False
            if exercises_in_category!=[]:
                #time.sleep(1)
                self.show_screen_category(i)
                while not s.waved_has_tool:
                    time.sleep(0.0001)

                for e in exercises_in_category:
                    self.exercises_by_order.append(e)
                    s.gymmy_done= False
                    s.camera_done= False
                    #s.demo_finish = False
                    s.number_of_repetitions_in_training =0
                    s.max_repetitions_in_training =0
                    time.sleep(1)
                    self.run_exercise(e)
                    while (not s.gymmy_done) or (not s.camera_done):
                        # print("not done")
                        time.sleep(0.0001)
                    time.sleep(3)

            time.sleep(1.5)

    def show_screen_category(self, category):
        if category=="ball":
            s.screen.switch_frame(Ball)
        elif category=="stick":
            s.screen.switch_frame(Stick)
        elif category=="band":
            s.screen.switch_frame(Rubber_Band)
        else:
            s.screen.switch_frame(NoTool)

    def finish_training(self):
        #time.sleep(3)
        s.time_in_training=time.time()-s.start_time
        s.finish_workout= True
        s.finished_effort= False
        s.list_effort_each_exercise= {}
        s.screen.switch_frame(EffortScale)

        while not s.finished_effort:
            time.sleep(0.0001)


        say('goodbye')
        s.screen.switch_frame(GoodbyePage)
        Excel.success_worksheet()
        Excel.find_and_add_training_to_patient()
        self.check_points_and_send_email()
        Excel.close_workbook()
        print("TRAINING DONE")
        self.reset()

    def run_exercise(self, name):
        time.sleep(0.1)  # wait between exercises
        s.success_exercise = False
        s.patient_repetitions_counting_in_exercise=0
        s.req_exercise = name
        print("TRAINING: Exercise ", name, " start")
        s.screen.switch_frame(ExplanationPage, exercise= name)
        time.sleep(5)
        s.screen.switch_frame(ExercisePage)
        while s.req_exercise == name:
            time.sleep(0.00000001)


        print("TRAINING: Exercise ", name, " done")
        time.sleep(3)
        # time.sleep(1)

    def reset(self):
        s.req_exercise = ""
        s.waved = False
        s.success_exercise = False
        s.calibration = False
        s.finish_workout = False
        s.gymmy_done = False
        s.camera_done = False
        s.robot_count = False
        #s.demo_finish = False
        s.list_effort_each_exercise = {}
        s.ex_in_training = []
        # s.exercises_start=False
        s.waved_has_tool = True  # True just in order to go through the loop in Gymmy
        # Excel variable
        s.ex_list = {}
        s.screen.switch_frame(EntrancePage)


    #A function that checks how many points did the patient get in the current level, and if he is progressing to the next level
    def check_points_and_send_email(self):
        time.sleep(1)
        level_up = False  #has the patient progressed to another level

        points_in_this_training = s.number_of_repetitions_in_training - 0.5 * (
                    s.max_repetitions_in_training - s.number_of_repetitions_in_training) #how many points the patient got on this training

        points_into_excel = 0 #varaible for points to put in excel

        if (s.points_in_current_level_before_training + points_in_this_training) < 100: #checks whether the sum of the points before the training and in it are less than 100
            points_into_excel = s.points_in_current_level_before_training + points_in_this_training #if less than 100, the points will stay as the sum

        elif 100 <= (s.points_in_current_level_before_training + points_in_this_training) < 200: #if the points are between 100 and 200
            s.current_level_of_patient += 1 #the level will increase in 1
            points_into_excel = s.points_in_current_level_before_training + points_in_this_training - 100 #if between 100 and 200, we will deduct 100 points (because the patient progressed in one level)
            level_up = True

        elif (s.number_of_repetitions_in_training + s.number_of_repetitions_in_current_level_before_training) >= 200: #if the points are more than 200
            s.current_level_of_patient += 2 #the level will increase in 2
            points_into_excel = s.points_in_current_level_before_training + points_in_this_training - 200 #if more than 200, we will deduct 200 points (because the patient progressed in two levels)
            level_up = True

        dict_new_values={"level": s.current_level_of_patient, "points in current level": points_into_excel}
        Excel.find_and_change_values_patients(dict_new_values)

        if level_up is True:
            Email.email_sending_level_up()
        else:
            Email.email_sending_not_level_up()

if __name__ == "__main__":
    s.audio_path = 'audio files/Hebrew/Male/'
    # s.picture_path = 'audio files/' + language + '/' + gender + '/'
    # s.str_to_say = ""
    current_time = datetime.now()
    s.participant_code = str(current_time.day) + "." + str(current_time.month) + " " + str(current_time.hour) + "." + \
                         str(current_time.minute) + "." + str(current_time.second)
    s.waved = False
    s.finish_workout = False
    #s.exercise_amount = 6
    s.finish_program= False
    s.rep = 8
    s.ex_in_training=["raising_hands_diagonally_notool"]
    s.chosen_patient_ID="1111"
    s.req_exercise=""
    s.ex_list = {}
    #s.demo_finish = False
    s.screen = Screen()
    s.camera = Camera()
    s.training = Training()
    s.robot= Gymmy()
    s.camera.start()
    s.training.start()
    s.robot.start()
    app = FullScreenApp(s.screen)
    s.screen.mainloop()
