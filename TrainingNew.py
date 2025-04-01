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
    Number_of_good_repetitions_page, ClappingPage, Weights, CalibrationScreen
import Settings as s
import Excel
import random
from Audio import say, get_wav_duration, ContinuousAudio, AdditionalAudio
from datetime import datetime
import Email



class Training(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):

        while not s.finish_program:
            s.exercise_name_repeated_explanation = None

            self.training_session()
            if s.finish_program:
                break

            self.finish_training()

        print("Training Done")


    def select_exercises(self, ex_in_training, exercise_pairs, max_exercises=10, max_per_category=4):
        """
        Selects up to `max_exercises` exercises while ensuring:
        - If there are 10 or fewer exercises, all are included.
        - Exercises are categorized (ball, band, stick, weights, notool).
        - If an exercise is in a pair and there's room, it has a 50% chance to include its pair.
        - Maximum of 4 exercises per category unless only full categories remain.
        - If only exercise pairs remain and exactly one more is needed, one is chosen randomly.
        - The selected list is shuffled, but a specific pair remains together.
        """

        if len(ex_in_training) <= max_exercises:
            return ex_in_training  # If 10 or fewer exercises exist, use all

        selected_exercises = []
        exercise_counts = {category: 0 for category in ["ball", "band", "stick", "weights", "notool"]}
        used_pairs = set()

        while len(selected_exercises) < max_exercises:
            remaining_exercises = [ex for ex in ex_in_training if ex not in selected_exercises]
            if not remaining_exercises:
                break  # Stop if no exercises remain

            # Identify remaining pairs
            remaining_pairs = [pair for pair in exercise_pairs if pair[0] in remaining_exercises and pair[1] in remaining_exercises]
            only_pairs_left = len(remaining_pairs) > 0 and all(ex in sum(remaining_pairs, ()) for ex in remaining_exercises)

            # Select a random exercise
            exercise = random.choice(remaining_exercises)

            # Determine its category
            category = next((key for key in exercise_counts.keys() if exercise.startswith(key)), None)

            if category:
                pair_found = False
                for pair in exercise_pairs:
                    if exercise in pair:
                        partner = pair[0] if exercise == pair[1] else pair[1]

                        if partner in remaining_exercises and pair not in used_pairs:
                            # Randomly decide whether to include both or none if there's room
                            if len(selected_exercises) + 2 <= max_exercises and random.choice([True, False]):
                                selected_exercises.extend(pair)
                                exercise_counts[category] += 2
                                used_pairs.add(pair)
                            pair_found = True
                        break

                # If no pair was added and the category is not full, add a single exercise
                if not pair_found and exercise_counts[category] < max_per_category:
                    selected_exercises.append(exercise)
                    exercise_counts[category] += 1

            # If all available exercises belong to full categories, allow adding extra ones
            if len(selected_exercises) < max_exercises:
                remaining_exercises_no_limits = [ex for ex in ex_in_training if ex not in selected_exercises]
                if remaining_exercises_no_limits:
                    selected_exercises.append(random.choice(remaining_exercises_no_limits))

        # If only pairs remain and exactly one more exercise is needed, add one from a pair
        if len(selected_exercises) == max_exercises - 1 and only_pairs_left:
            random_pair = random.choice(remaining_pairs)
            selected_exercises.append(random.choice(random_pair))

        # **Shuffle but keep special pair together**
        special_pair = ("notool_right_bend_left_up_from_side", "notool_left_bend_right_up_from_side")

        if all(ex in selected_exercises for ex in special_pair):
            # Remove special pair from list before shuffling
            selected_exercises = [ex for ex in selected_exercises if ex not in special_pair]
            random.shuffle(selected_exercises)  # Shuffle the remaining exercises

            # Insert the special pair at a random position while keeping them together
            insert_index = random.randint(0, len(selected_exercises))
            selected_exercises[insert_index:insert_index] = list(special_pair)  # Insert the pair back together
        else:
            # If the special pair is not both present, just shuffle normally
            random.shuffle(selected_exercises)

        return selected_exercises


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

                selected_exercises= self.select_exercises(s.ex_in_training, exercise_pairs)

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


            s.req_exercise = "calibration"
            while not s.finished_calibration:
                time.sleep(0.0001)

                if s.stop_requested or s.finish_program:
                    break

            s.req_exercise = ""
            time.sleep(get_wav_duration("end_calibration"))


            for i in categories:
                if s.stop_requested or s.finish_program:
                    break

                self.exercises_in_category = [category for category in s.ex_in_training if i in category] #search for the exercises that are in the specific category
                random.shuffle(self.exercises_in_category)
                s.waved_has_tool= False
                if self.exercises_in_category!=[]:
                    self.show_screen_category(i)
                    while not s.waved_has_tool:
                         time.sleep(0.0001)

                    self.first_coordination_ex = True
                    j=0

                    while j < len(self.exercises_in_category):
                        s.skipped_exercise = False
                        s.last_entry_angles = None
                        s.hand_not_good = False
                        s.not_reached_max_limit_rest_rules_ok = False
                        s.reached_max_limit = False
                        s.all_rules_ok = False
                        s.was_in_first_condition = False
                        e = self.exercises_in_category[j]

                        # if not s.finished_calibration:
                        #     calibration_help_variable = True
                        #
                        # while not s.finished_calibration:
                        #     time.sleep(0.0001)
                        #
                        # if calibration_help_variable: #אם הייתה קליברציה
                        #     calibration_help_variable = False
                        #     time.sleep(get_wav_duration("welcome"))


                        # if s.try_again_calibration:
                        #     say("welcome")
                        #     time.sleep(get_wav_duration("welcome"))


                        s.was_in_first_condition = False
                        if e in ["band_straighten_left_arm_elbows_bend_to_sides", "band_straighten_right_arm_elbows_bend_to_sides"]:
                            s.zed_camera.set_detection_model_to_accurate()

                        s.direction = None
                        s.skip = False
                        s.general_sayings = self.get_motivation_file_names()
                        s.exercises_by_order.append(e)
                        s.gymmy_done= False
                        s.camera_done= False
                        #s.demo_finish = False
                        exercise = e
                        s.number_of_repetitions_in_training =0
                        s.max_repetitions_in_training =0
                        s.num_exercises_started +=1
                        self.run_exercise(e)

                        # if not (exercise == "notool_right_bend_left_up_from_side" or exercise == "notool_left_bend_right_up_from_side") or not self.first_coordination_ex:
                        #     self.end_exercise()
                        if exercise == "notool_right_bend_left_up_from_side" or exercise == "notool_left_bend_right_up_from_side":
                            if self.first_coordination_ex == True:
                                    self.first_coordination_ex = False
                            else:
                                self.first_coordination_ex = True


                        if e in ["band_straighten_left_arm_elbows_bend_to_sides", "band_straighten_right_arm_elbows_bend_to_sides"]:
                            s.zed_camera.set_detection_model_to_medium()


                        if not s.try_again_calibration and not s.repeat_explanation:
                            j+=1
                            self.end_exercise()

                        elif s.try_again_calibration:
                            say("try_again_calibration")
                            time.sleep(get_wav_duration("try_again_calibration"))
                            s.asked_for_measurement = True
                            s.screen_finished_counting = False
                            s.screen.switch_frame(CalibrationScreen)
                            s.num_exercises_started -= 1


                            while not s.finished_calibration:
                                time.sleep(0.0001)

                            time.sleep(get_wav_duration("end_calibration"))

                        elif s.repeat_explanation:
                            s.req_exercise = ""
                            s.num_exercises_started -= 1

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
            s.finished_calibration = True
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
            s.additional_audio_playing= False
            s.volume = 0.3
            s.play_song = False
            s.asked_for_measurement = False
            s.screen_finished_counting = True
            s.explanation_over = False
            s.gymmy_finished_demo = False
            s.last_saying_time = datetime.now()
            s.robot_counter= 0
            s.was_in_first_condition = False
            s.time_of_change_position = None
            s.try_again_calibration = False
            s.not_reached_max_limit_rest_rules_ok = False
            s.repeat_explanation = False
            s.shoulder_problem_calibration = False
            s.elbow_problem_calibration = False
            s.hand_not_good = False
            s.exercise_name_repeated_explanation = None
            s.suggest_repeat_explanation = False
            s.last_entry_angles = None
            s.skipped_exercise = False


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
        time.sleep(get_wav_duration(f"{s.patient_repetitions_counting_in_exercise}_successful_rep")+1)




    def run_exercise(self, name):
        s.robot_counter = 0
        s.success_exercise = False
        s.patient_repetitions_counting_in_exercise = 0

        print("TRAINING: Exercise ", name, " start")
        s.explanation_over = False
        s.req_exercise = name

        if self.first_coordination_ex:
            s.screen.switch_frame(ExplanationPage, exercise= name)
            # if name == "notool_right_bend_left_up_from_side" or name == "notool_left_bend_right_up_from_side":
            #     name = "notool_arm_bend_arm_up_from_side"
            # time.sleep(get_wav_duration(name)) #wait the time of the audio

            while not s.explanation_over or not s.gymmy_finished_demo:
                time.sleep(0.001)

            say(str(f'{s.rep}_times'))
            time.sleep(get_wav_duration(f'{str(s.rep)}_times')+0.5)
            # name = s.req_exercise
            #s.screen.switch_frame(ExercisePage)
            self.which_exercise_page()
        else:
            self.which_exercise_page()
            #s.screen.switch_frame(ExercisePage)
            say("notool_arm_bend_arm_up_from_side_continue")
            time.sleep(get_wav_duration("notool_arm_bend_arm_up_from_side_continue") + 0.5)
            # say(str(f'{s.rep}_times'))
            # time.sleep(get_wav_duration(f'{str(s.rep)}_times')+0.5)
            s.explanation_over = True


        while s.req_exercise == name and not s.try_again_calibration and not s.repeat_explanation and not s.skipped_exercise:
            time.sleep(0.00000001)

        if s.try_again_calibration:
            s.req_exercise = ""
            s.finished_calibration = False

        if s.skipped_exercise:
            s.req_exercise = ""



        print("TRAINING: Exercise ", name, " done")
        s.gymmy_finished_demo = False
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
        s.was_in_first_condition = False
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
        s.additional_audio_playing = False
        s.volume = 0.3
        s.play_song = False
        s.asked_for_measurement = True
        s.screen_finished_counting = True
        s.finished_calibration = False
        s.len_left_arm = None
        s.len_right_arm = None
        s.dist_between_wrists = None
        s.dist_between_shoulders = None
        s.time_of_change_position = None
        s.average_dist = None
        s.rep = 0
        s.audio_path = None
        s.rate = "moderate"
        s.explanation_over = False
        s.gymmy_finished_demo = False
        s.last_saying_time = datetime.now()
        s.robot_counter = 0
        s.try_again_calibration = False
        s.not_reached_max_limit_rest_rules_ok = False
        s.repeat_explanation = False
        s.shoulder_problem_calibration = False
        s.elbow_problem_calibration = False
        s.hand_not_good = False
        s.exercise_name_repeated_explanation = None
        s.suggest_repeat_explanation = False
        s.last_entry_angles = None
        s.skipped_exercise = False

    def which_exercise_page(self):

        average_len_arms = (s.len_left_arm + s.len_right_arm)/2

        if s.req_exercise in ["ball_bend_elbows", "stick_bend_elbows"]:
            s.screen.switch_frame(ExercisePage, exercise_type="wrist_height_y", reverse_color=True, reverse_bar=False, min_distance=0, max_distance= average_len_arms-150, which_side = "both")
        elif s.req_exercise in ["ball_raise_arms_above_head", "stick_raise_arms_above_head"]:
            s.screen.switch_frame(ExercisePage, exercise_type="wrist_height_y", reverse_color=True, reverse_bar=False, min_distance=-(average_len_arms), max_distance= average_len_arms/2, which_side = "both")
        elif s.req_exercise in ["ball_switch", "stick_switch"]:
            s.screen.switch_frame(ExercisePage, exercise_type="shoulders_distance_x", reverse_color=True, reverse_bar=False, min_distance=(s.dist_between_shoulders-s.dist_between_shoulders/4), max_distance= s.dist_between_shoulders)
        elif s.req_exercise in ["ball_open_arms_and_forward", "weights_open_arms_and_forward"]:
            s.screen.switch_frame(ExercisePage, exercise_type="wrist_distance_x", reverse_color=False, reverse_bar=False, min_distance=s.dist_between_shoulders, max_distance= s.dist_between_wrists-50)
        elif s.req_exercise in ["ball_open_arms_above_head", "stick_bend_elbows_and_up"]:
            s.screen.switch_frame(ExercisePage, exercise_type="wrist_height_y", reverse_color=True, reverse_bar=False, min_distance=-(average_len_arms-150), max_distance= 0, which_side = "both")
        elif s.req_exercise == "band_open_arms":
            s.screen.switch_frame(ExercisePage, exercise_type="wrist_distance_x", reverse_color=False, reverse_bar=False, min_distance=s.dist_between_shoulders, max_distance= 2 * s.dist_between_wrists/3)
        elif s.req_exercise == "band_open_arms_and_up":
            s.screen.switch_frame(ExercisePage, exercise_type="wrist_height_y_distance_x", reverse_color=False, reverse_bar=False, min_distance=-(average_len_arms-250), max_distance= 0, which_side = None, min_distance_x= s.dist_between_shoulders , max_distance_x=  s.dist_between_wrists/2)
        elif s.req_exercise in ["band_up_and_lean", "stick_up_and_lean", "notool_hands_behind_and_lean"]:
            s.screen.switch_frame(ExercisePage, exercise_type="shoulders_distance_x", reverse_color=True, reverse_bar=False, min_distance= s.dist_between_shoulders-50, max_distance= s.dist_between_shoulders)
        elif s.req_exercise in ["band_straighten_left_arm_elbows_bend_to_sides", "band_straighten_right_arm_elbows_bend_to_sides"]:
            s.screen.switch_frame(ExercisePage, exercise_type="wrist_distance_x", reverse_color=False, reverse_bar=False, min_distance= s.dist_between_shoulders+200, max_distance= s.dist_between_shoulders + average_len_arms - 100)
        elif s.req_exercise in ["notool_right_hand_up_and_bend", "notool_left_hand_up_and_bend"]:
            s.screen.switch_frame(ExercisePage, exercise_type="shoulders_distance_x", reverse_color=True, reverse_bar=False, min_distance= s.dist_between_shoulders-70, max_distance= s.dist_between_shoulders)
        elif s.req_exercise in ["weights_abduction"]:
            s.screen.switch_frame(ExercisePage, exercise_type="wrist_height_y", reverse_color=True, reverse_bar=False, min_distance=0, max_distance= (average_len_arms-40), which_side = "both")
        elif s.req_exercise in ["notool_right_bend_left_up_from_side"]:
            s.screen.switch_frame(ExercisePage, exercise_type="wrist_height_y", reverse_color=True, reverse_bar=False, min_distance = 0, max_distance= (average_len_arms-40), which_side = "left")
        elif s.req_exercise in ["notool_left_bend_right_up_from_side"]:
            s.screen.switch_frame(ExercisePage, exercise_type="wrist_height_y", reverse_color=True, reverse_bar=False, min_distance=0, max_distance=(average_len_arms - 40), which_side="right")
        elif s.req_exercise in ["notool_raising_hands_diagonally"]:
            s.screen.switch_frame(ExercisePage, exercise_type="wrist_height_y", reverse_color=True, reverse_bar=False, min_distance=-(average_len_arms - 250), max_distance=0, which_side="both")

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
    s.gender= "Female"
    s.audio_path = f'audio files/Hebrew/{s.gender}/'
    general_sayings = Training.get_motivation_file_names(Training)

    current_time = datetime.now()
    s.participant_code = str(current_time.day) + "." + str(current_time.month) + " " + str(current_time.hour) + "." + \
                         str(current_time.minute) + "." + str(current_time.second)
    s.waved = False
    s.finish_workout = False
    s.finish_program= False
    s.asked_for_measurement= False
    s.rep = 10
    s.time_of_change_position = None

    s.ex_in_training = ["notool_left_hand_up_and_bend", "notool_right_hand_up_and_bend"]
    s.skipped_exercise = False

        #,"ball_switch" ,"ball_open_arms_and_forward" , "ball_open_arms_above_head"] "ball_bend_elbows" ,
        # ["band_open_arms",  "band_up_and_lean", "band_open_arms_and_up"]
    #s.ex_in_training =  ["ball_raise_arms_above_head"]
    # s.ex_in_training = ["notool_right_bend_left_up_from_side", "notool_left_bend_right_up_from_side"]
    # s.ex_in_training= [, "band_open_arms_and_up", "band_up_and_lean", "band_straighten_left_arm_elbows_bend_to_sides", "band_straighten_right_arm_elbows_bend_to_sides"]
                    #"band_open_arms", "band_open_arms_and_up", "band_up_and_lean", "band_straighten_left_arm_elbows_bend_to_sides", "band_straighten_right_arm_elbows_bend_to_sides"
    #
                    # "stick_bend_elbows", "stick_bend_elbows_and_up", "stick_raise_arms_above_head", "stick_switch", "stick_up_and_lean"
                    # weights_right_hand_up_and_bend, weights_left_hand_up_and_bend, weights_open_arms_and_forward, weights_abduction
    # notool_hands_behind_and_lean
    # notool_right_hand_up_and_bend
    # notool_left_hand_up_and_bend
    # notool_raising_hands_diagonally
    # notool_right_bend_left_up_from_side
    # notool_left_bend_right_up_from_side
    s.direction = None
    s.chosen_patient_ID="3333"
    s.req_exercise=""
    s.ex_list = {}
    s.finished_calibration = False
    s.repeat_explanation = False
    s.last_entry_angles = None

    s.len_left_arm = None
    s.len_right_arm = None
    s.dist_between_wrists = None
    s.dist_between_shoulders = None
    s.len_left_upper_arm = None
    s.len_right_upper_arm = None
    s.shoulder_problem_calibration = False
    s.hand_not_good = False
    s.exercise_name_repeated_explanation = None

    s.was_in_first_condition = False
    s.screen_finished_counting = False
    s.is_second_repetition_or_more =False
    #s.demo_finish = False
    s.all_rules_ok = False
    s.reached_max_limit = False
    s.latest_keypoints = {}
    s.did_training_paused = False
    s.volume = 0
    s.additional_audio_playing = False
    s.gymmy_finished_demo = False
    s.robot_counter = 0
    s.last_saying_time = datetime.now()
    s.rate= "slow"
    s.num_exercises_started = 0
    s.asked_for_measurement = True
    pygame.mixer.init()
    s.full_name = "יעל שניידמן"
    s.play_song = False
    s.explanation_over = False
    s.suggest_repeat_explanation = False

    s.another_training_requested= False
    s.choose_continue_or_not = False
    s.email_of_patient = "yaelszn@gmail.com"
    s.try_again_calibration = False
    s.number_of_pauses=0
    # Start continuous audio in a separate thread
    s.screen = Screen()
    s.camera = Camera()
    s.training = Training()
    s.robot = Gymmy()
    s.camera.start()
    s.training.start()
    s.robot.start()
    s.audio_manager = AdditionalAudio()
    s.continuous_audio = ContinuousAudio()
    s.continuous_audio.start()
    s.screen.switch_frame(StartOfTraining)
    app = FullScreenApp(s.screen)
    s.screen.mainloop()
