import threading
import time
from Camera import Camera
from Screen import Screen, FullScreenApp, HelloPage, ChooseExercise, ExercisePage, GoodbyePage, CalibrationPage, \
    DemoPage
import Settings as s
import Excel
import random
from Audio import say, get_wav_duration
import datetime



class Training(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("TRAINING START")
        #print("start waving")
        #name="hello_waving"
        #s.req_exercise = name
        #s.screen.switch_frame(HelloPage)
        #time.sleep(3)  # Delay the robot movement after the audio is played
        #time.sleep(1)

        #while not s.waved:
        #    time.sleep(0.00000001)  # Prevents the MP to stuck
        #    continue
        #s.demo_finish = False
        #print("Training: finish waving")
        #print("Training: Calibration")
        #s.screen.switch_frame(CalibrationPage)
        #s.camera.init_position()
        #while not s.calibration:
        #    time.sleep(0.00000001)
        #    continue

        #s.demo_finish = False
        #time.sleep(3)
        #say('finish_calibration')
        #time.sleep(2)
        #say('start')
        #time.sleep(4)
        #s.gymmy_done = False # AFTER HELLO
        #s.camera_done = False # AFTER HELLO
        self.training_session()
        self.finish_workout()

    def training_session(self):
        print("Training: start exercises")
        categories=["ball", "stick","notool", "rubber_band"]

        s.ex_in_training=""
        #s.screen.switch_frame(ChooseExercise)

        while s.ex_in_training=="" or not s.waved_has_tool:
            time.sleep(0.00000001)

        s.exercise_amount=s.ex_in_training.__len__()
      #  while not s.exercises_start:
       #     time.sleep(0.00000001)


        #exercise_names = ["raise_arms_horizontally", "bend_elbows", "raise_arms_bend_elbows", "open_and_close_arms",
                        #  "open_and_close_arms_90", "raise_arms_forward"]
        #exercise_names = ["bend_elbows_ball"]

        for e in s.ex_in_training:
            #s.screen.switch_frame(ExercisePage)
            #time.sleep(2) # wait between exercises
            self.run_exercise(e)
            while (not s.gymmy_done) or (not s.camera_done):
                #print("not done")
                time.sleep(0.0001)
            s.gymmy_done = False
            s.camera_done = False
            s.demo_finish = False
            time.sleep(3)

    def finish_workout(self):
        time.sleep(3)
        say('goodbye')
        s.screen.switch_frame(GoodbyePage)
        s.finish_workout = True
        Excel.success_worksheet()
        Excel.close_workbook()
        time.sleep(10)
        s.screen.quit()
        print("TRAINING DONE")

    def run_exercise(self, name):
        time.sleep(2)  # wait between exercises
        s.success_exercise = False
        s.req_exercise = name
        print("TRAINING: Exercise ", name, " start")
        #while not s.demo_finish:
         #   time.sleep(0.00000001)
        #time.sleep(2) # wait between exercises
        #time.sleep(3)  # Delay the robot movement after the audio is played
        # time.sleep(1)
        #s.screen.switch_frame(ExercisePage)
        while s.req_exercise == name:
            time.sleep(0.001)  # Prevents the MP to stuck
        print("TRAINING: Exercise ", name, " done")
        #time.sleep(1)



if __name__ == "__main__":
    s.audio_path = 'audio files/Hebrew/Male/'
    # s.picture_path = 'audio files/' + language + '/' + gender + '/'
    # s.str_to_say = ""
    current_time = datetime.datetime.now()
    s.participant_code = str(current_time.day) + "." + str(current_time.month) + " " + str(current_time.hour) + "." + \
                         str(current_time.minute) + "." + str(current_time.second)
    s.waved=False
    s.finish_workout=False
    s.exercise_amount = 6
    s.rep = 8
    s.req_exercise = ""
    s.demo_finish= False
    s.screen = Screen()
    s.camera = Camera()
    s.training = Training()
    s.camera.start()
    s.training.start()
    app = FullScreenApp(s.screen)
    s.screen.mainloop()
