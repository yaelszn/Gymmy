import os
import threading
import time
import re
from random import randint

import cv2
import pygame

from Camera import Camera
from Gymmy import Gymmy
from ScreenNew import Screen, FullScreenApp, Ball, Rubber_Band, Stick, NoTool, StartOfTraining, GoodbyePage, \
    EffortScale, EntrancePage, ExplanationPage, ExercisePage, Repeat_training_or_not, \
    Number_of_good_repetitions_page, ClappingPage, Weights
import Settings as s
import Excel
import random
from Audio import say, get_wav_duration, ContinuousAudio
from datetime import datetime
import Email



class Training(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while not s.finish_program:
            self.training_session()
            if s.finish_program:
                break

            self.finish_training()


    def training_session(self):
        while s.ex_in_training==[]:
            time.sleep(0.1)

            if s.finish_program:
                break

        time.sleep(1)

        if not s.finish_program:
            s.turn_camera_on= True
            s.starts_and_ends_of_stops= []
            s.stop_requested = False

            time.sleep(1) #wait another second so that s.ex_in_training will contain all of the exercises
            # הגדרת זוגות התרגילים
            exercise_pairs = [
                ("band_straighten_left_arm_elbows_bend_to_sides", "band_straighten_right_arm_elbows_bend_to_sides"),
                ("weights_right_hand_up_and_bend", "weights_left_hand_up_and_bend"),
                ("notool_right_hand_up_and_bend", "notool_left_hand_up_and_bend"),
                ("notool_right_bend_left_up_from_side", "notool_left_bend_right_up_from_side"),
            ]

            if not s.is_second_repetition_or_more and not s.finish_program:
                if len(s.ex_in_training) <= 10:
                    # אם מספר התרגילים קטן או שווה ל-10, כל התרגילים נכנסים
                    s.ex_in_training = s.ex_in_training
                else:
                    selected_exercises = []
                    exercise_counts = {"ball": 0, "weights": 0, "stick": 0, "band": 0,
                                       "notool": 0}  # ספירה של תרגילים לפי קטגוריות
                    pairs_selected = 0  # ספירת מספר הזוגות שנבחרו
                    used_pairs = set()  # סט למעקב אחר זוגות שכבר נבחרו
                    count = 10  # מספר מקסימלי של תרגילים

                    while len(selected_exercises) < count:
                        # בחירת תרגיל רנדומלי
                        exercise = random.choice(s.ex_in_training)

                        # מציאת הקטגוריה של התרגיל (המילה הראשונה)
                        category = next((key for key in exercise_counts.keys() if exercise.startswith(key)), None)

                        # בדיקה אם התרגיל כבר נבחר או אם עבר את המגבלה של 4 תרגילים באותה קטגוריה
                        if exercise not in selected_exercises and category and exercise_counts[category] < 4:
                            pair_found = False
                            for pair in exercise_pairs:
                                if exercise in pair:
                                    pair_found = True
                                    # מציאת בן הזוג
                                    partner = pair[0] if exercise == pair[1] else pair[1]

                                    # בדיקה אם בן הזוג כבר ברשימה או אם הזוג כבר נבחר
                                    if partner not in selected_exercises and pair not in used_pairs and pairs_selected < 1:
                                        # הוספת הזוג ונעילת הבחירה
                                        selected_exercises.append(exercise)
                                        selected_exercises.append(partner)
                                        exercise_counts[category] += 2  # עדכון הספירה לקטגוריה
                                        used_pairs.add(pair)
                                        pairs_selected += 1  # עדכון ספירת הזוגות
                                    break

                            # אם התרגיל אינו חלק מזוג או שהזוג כבר נבחר, הוספה של תרגיל יחיד
                            if not pair_found:
                                selected_exercises.append(exercise)
                                exercise_counts[category] += 1  # עדכון הספירה לקטגוריה

                    random.shuffle(selected_exercises)

                    # שמירת התרגילים שנבחרו
                    s.ex_in_training = selected_exercises

                    # הדפסת התרגילים שנבחרו
                    for item in selected_exercises:
                        print(item)

                while not s.explanation_over:
                    time.sleep(0.5)

            s.starts_and_ends_of_stops.append(datetime.now())

            categories = ["ball", "stick", "notool", "band", "weights"]
            random.shuffle(categories)

            Excel.create_workbook_for_training() #create workbook in excel for this session

            s.exercises_by_order=[]


            for i in categories:
                if s.stop_requested or s.finish_program:
                    break

                exercises_in_category = [category for category in s.ex_in_training if i in category] #search for the exercises that are in the specific category
                random.shuffle(exercises_in_category)
                s.waved_has_tool= False
                if exercises_in_category!=[]:
                    time.sleep(1)
                    self.show_screen_category(i)
                    while not s.waved_has_tool:
                         time.sleep(0.0001)

                    self.first_coordination_ex = True

                    for e in exercises_in_category:
                        s.skip = False
                        s.general_sayings = self.get_motivation_file_names()
                        s.exercises_by_order.append(e)
                        s.gymmy_done= False
                        s.camera_done= False
                        #s.demo_finish = False
                        exercise = e
                        s.number_of_repetitions_in_training =0
                        s.max_repetitions_in_training =0
                        time.sleep(1)
                        s.num_exercises_started +=1
                        self.run_exercise(e)

                        # if not (exercise == "notool_right_bend_left_up_from_side" or exercise == "notool_left_bend_right_up_from_side") or not self.first_coordination_ex:
                        #     self.end_exercise()
                        if exercise == "notool_right_bend_left_up_from_side" or exercise == "notool_left_bend_right_up_from_side":
                            if self.first_coordination_ex == True:
                                    self.first_coordination_ex = False
                            else:
                                self.first_coordination_ex = True

                        self.end_exercise()

                        # while (not s.gymmy_done) or (not s.camera_done):
                            #     # print("not done")
                            #     time.sleep(0.0001)
                            #     if s.stop_requested:
                            #         time.sleep(3)
                            #         break

                        if s.stop_requested or s.finish_program:
                            break

                        while not s.gymmy_done or not s.camera_done:
                            time.sleep(0.001)

                if s.stop_requested or s.finish_program:
                    break

    def show_screen_category(self, category):
        if category=="ball":
            s.screen.switch_frame(Ball)
        elif category=="stick":
            s.screen.switch_frame(Stick)
        elif category=="band":
            s.screen.switch_frame(Rubber_Band)
        elif category == "weights":
            s.screen.switch_frame(Weights)
        else:
            s.screen.switch_frame(NoTool)



    def get_motivation_file_names(self):
        """
        Retrieves all file names in a directory that:
        - Start with 'faster_' followed by a number.
        - Start with 'motivation_' followed by a number and optionally '_start', '_middle', '_end', or '_end_good'.

        Returns:
        - List[str]: A list of matching file names without extensions.
        """
        # Updated regex pattern
        pattern = r'^(faster_\d+|motivation_\d+_(start|middle|end|end_good))\.\w+$'

        # Initialize a list to store matching file names
        matching_file_names = []

        # Verify the directory exists
        if not os.path.exists(s.audio_path):
            print(f"Directory does not exist: {s.audio_path}")
            return matching_file_names

        # Check all files in the directory
        for file_name in os.listdir(s.audio_path):
            # Match the file name against the pattern
            if re.match(pattern, file_name):
                # Remove the file extension
                name_without_extension, _ = os.path.splitext(file_name)
                matching_file_names.append(name_without_extension)

        return matching_file_names

    def finish_training(self):
        #time.sleep(3)
        s.starts_and_ends_of_stops.append(datetime.now())

        s.finish_workout= True
        s.finished_effort= False
        s.list_effort_each_exercise= {}

        s.screen.switch_frame(EffortScale)


        while not s.finished_effort:
            time.sleep(0.0001)

        if not s.stop_requested:
            s.screen.switch_frame(Repeat_training_or_not)

            while not s.choose_continue_or_not:
                time.sleep(0.0001)

        else:
            s.screen.switch_frame(ClappingPage)



        if s.another_training_requested:
            Excel.find_and_add_training_to_patient()
            Excel.close_workbook()
            Email.email_to_patient()
            Email.email_to_physical_therapist()

            s.req_exercise = ""
            s.waved = False
            s.success_exercise = False
            s.calibration = False
            s.finish_workout = False
            s.gymmy_done = False
            s.camera_done = False
            s.robot_count = False
            # s.demo_finish = False
            # s.exercises_start=False
            s.waved_has_tool = True  # True just in order to go through the loop in Gymmy
            # Excel variable
            s.ex_list = {}
            s.stop_requested = False
            s.choose_continue_or_not= False
            s.another_training_requested= False
            s.is_second_repetition_or_more= True
            s.finished_effort= False
            s.effort= None
            s.patient_repetitions_counting_in_exercise=0
            s.number_of_repetitions_in_training=0
            s.did_training_paused= False
            s.starts_and_ends_of_stops= []
            s.general_sayings = ["", "", ""]
            s.num_exercises_started = 0
            s.number_of_pauses = 0
            s.needs_first_position = False
            s.exercises_skipped= {}
            s.skip = False

        else:
            Excel.find_and_add_training_to_patient()
            Excel.close_workbook()
            Email.email_to_patient()
            # self.check_points_and_send_email()
            Email.email_to_physical_therapist()
            print("TRAINING DONE")
            time.sleep(1)
            self.reset()


    def end_exercise(self):
        s.screen.switch_frame(Number_of_good_repetitions_page)
        time.sleep(get_wav_duration(f"{s.patient_repetitions_counting_in_exercise}_successful_rep"))
        time.sleep(2)



    def random_encouragement(self):
        enco = ["Well_done", "Very_good", "Excellent"]

        random_class_name = random.choice(enco)
        random_class = globals()[random_class_name]
        random_instance = random_class
        s.screen.switch_frame(random_instance)
        time.sleep(get_wav_duration(random_class_name)+1)


    def run_exercise(self, name):
        s.success_exercise = False
        s.patient_repetitions_counting_in_exercise = 0

        print("TRAINING: Exercise ", name, " start")
        s.explanation_over = False
        s.req_exercise = name

        if self.first_coordination_ex:
            s.screen.switch_frame(ExplanationPage, exercise= name)
            if name == "notool_right_bend_left_up_from_side" or name == "notool_left_bend_right_up_from_side":
                name = "notool_arm_bend_arm_up_from_side"
            # time.sleep(get_wav_duration(name)) #wait the time of the audio

            while not s.explanation_over or not s.gymmy_finished_demo:
                time.sleep(0.001)

            say(str(f'{s.rep}_times'))
            time.sleep(get_wav_duration(f'{str(s.rep)}_times')+1)

        else:
            say("notool_arm_bend_arm_up_from_side_continue")
            say(str(f'{s.rep}_times'))
            time.sleep(get_wav_duration(f'{str(s.rep)}_times')+1)
            s.explanation_over = True

        name = s.req_exercise
        s.screen.switch_frame(ExercisePage)
        while s.req_exercise == name:
            time.sleep(0.00000001)


        print("TRAINING: Exercise ", name, " done")
        s.gymmy_finished_demo = False
        time.sleep(3)
        # time.sleep(1)



    def get_video_duration(self, exercise):
        video_file = f'Videos//{exercise}_vid.mp4'
        video_path = os.path.join(os.getcwd(), video_file)
        self.cap = cv2.VideoCapture(video_path)

        fps = self.cap.get(cv2.CAP_PROP_FPS)  # Get the frame rate of the video
        total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)  # Get the total number of frames
        duration = total_frames / fps  # Duration in seconds

        return duration

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
        s.stop_requested = False
        s.choose_continue_or_not=False
        s.another_training_requested= False
        s.is_second_repetition_or_more= False
        s.finished_effort= False
        s.effort = None
        s.chosen_patient_ID = None
        s.patient_repetitions_counting_in_exercise=0
        s.number_of_repetitions_in_training=0
        s.did_training_paused= False
        s.starts_and_ends_of_stops= []
        time.sleep(2)
        s.general_sayings = ["", "", ""]
        s.num_exercises_started = 0
        s.dist_between_shoulders = 0
        s.number_of_pauses = 0
        s.needs_first_position = False
        s.exercises_skipped = {}
        s.screen.switch_frame(EntrancePage)
        s.skip = False


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
    s.gender= "Male"
    s.audio_path = f'audio files/Hebrew/{s.gender}/'
    general_sayings = Training.get_motivation_file_names(Training)

    current_time = datetime.now()
    s.participant_code = str(current_time.day) + "." + str(current_time.month) + " " + str(current_time.hour) + "." + \
                         str(current_time.minute) + "." + str(current_time.second)
    s.waved = False
    s.finish_workout = False
    #s.exercise_amount = 6
    s.finish_program= False
    s.asked_for_measurement= False
    s.rep = 5


    #s.ex_in_training =  ["ball_raise_arms_above_head"]
    s.ex_in_training = ["ball_bend_elbows"]
    # s.ex_in_training= ["band_open_arms", "band_open_arms_and_up", "band_up_and_lean", "band_straighten_left_arm_elbows_bend_to_sides", "band_straighten_right_arm_elbows_bend_to_sides"]
                    #"band_open_arms", "band_open_arms_and_up", "band_up_and_lean", "band_straighten_left_arm_elbows_bend_to_sides", "band_straighten_right_arm_elbows_bend_to_sides"
    #["ball_bend_elbows" , "ball_raise_arms_above_head","ball_switch" ,"ball_open_arms_and_forward" , "ball_open_arms_above_head"]
                    # "stick_bend_elbows", "stick_bend_elbows_and_up", "stick_raise_arms_above_head", "stick_switch", "stick_up_and_lean"
                    # weights_right_hand_up_and_bend, weights_left_hand_up_and_bend, weights_open_arms_and_forward, weights_abduction
    # notool_hands_behind_and_lean
    # notool_right_hand_up_and_bend
    # notool_left_hand_up_and_bend
    # notool_raising_hands_diagonally
    # notool_right_bend_left_up_from_side
    # notool_left_bend_right_up_from_side

    s.chosen_patient_ID="314808981"
    s.req_exercise=""
    s.ex_list = {}
    s.dist_between_shoulders = 280
    s.is_second_repetition_or_more =False
    #s.demo_finish = False

    s.did_training_paused = False
    s.volume = 0
    s.additional_audio_playing = False
    s.gymmy_finished_demo = False
    s.robot_counter = 0
    s.last_saying_time = datetime.now()
    s.rate= "moderate"
    s.num_exercises_started = 0
    pygame.mixer.init()
    s.full_name = "יעל שניידמן"
    s.stop_song = False
    s.explanation_over = False
    s.another_training_requested= False
    s.explanation_over = False
    s.choose_continue_or_not = False
    s.email_of_patient = "yaelszn@gmail.com"
    s.number_of_pauses=0
    # Start continuous audio in a separate thread
    s.screen = Screen()
    s.camera = Camera()
    s.training = Training()
    s.robot = Gymmy()
    s.camera.start()
    s.training.start()
    s.robot.start()
    s.continuous_audio = ContinuousAudio()
    s.continuous_audio.start()
    s.screen.switch_frame(StartOfTraining)
    app = FullScreenApp(s.screen)
    s.screen.mainloop()
