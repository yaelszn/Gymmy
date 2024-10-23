import threading

import pygame

import Settings as s
from Audio import ContinuousAudio
from Camera import Camera
from Gymmy import Gymmy
from Realsense import Realsense
from TrainingNew import Training
from ScreenNew import Screen, FullScreenApp, EntrancePage



if __name__ == '__main__':
    s.camera_num = 1  # 0 - webcam, 2 - second USB in maya's computer


    s.additional_audio_playing = False
    s.volume = 0.6
    # Training variables initialization
    s.rep = 5
    s.req_exercise = ""
    s.audio_path = None
    s.finish_workout = False
    s.waved = False
    s.success_exercise = False
    s.calibration = False
    s.gymmy_done = False
    s.camera_done = False
    s.robot_count = False
    s.demo_finish= False
    s.ex_in_training=[]
    s.finish_program= False #will turn to true only when the user will press on the exit button
    #s.exercises_start=False
    s.waved_has_tool= True # True just in order to go through the loop in Gymmy
    s.finished_training_adding_to_excel= False
    # Excel variable
    ############################# להוריד את הסולמיות
    s.ex_list = {}
    s.starts_and_ends_of_stops =[]
    s.stop_requested = False
    s.is_second_repetition_or_more=False
    s.another_training_requested= False
    s.choose_continue_or_not= False
    s.did_training_paused= False
    s.rate= "moderate"
    # Create all components
    s.camera = Camera()
    s.training = Training()
    s.robot = Gymmy()


    pygame.mixer.init()
    s.stop_song = False
    # Start continuous audio in a separate thread
    s.continuous_audio = ContinuousAudio()
    s.continuous_audio.start()

    s.screen = Screen()
    #s.screen.switch_frame(HelloPage)

    # Start all threads
    s.camera.start()
    s.training.start()
    s.robot.start()


    s.screen.switch_frame(EntrancePage)
    app = FullScreenApp(s.screen)
    s.screen.mainloop()

