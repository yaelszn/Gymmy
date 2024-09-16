import Settings as s
from Camera import Camera
from Gymmy import Gymmy
from TrainingNew import Training
from ScreenNew import Screen, FullScreenApp, EntrancePage



def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hello, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
# TODO add more exercises
# TODO adaptive framework
# TODO GUI
# delay between exercises


if __name__ == '__main__':
    s.camera_num = 1  # 0 - webcam, 2 - second USB in maya's computer

    # Audio variables initialization
    language = 'Hebrew'
    gender = 'Male'
    s.audio_path = 'audio files/' + language + '/' + gender + '/'
    s.picture_path = 'audio files/' + language + '/' + gender + '/'


    # Training variables initialization
    s.rep = 10
    s.req_exercise = ""
    s.finish_workout = False
    s.waved = False
    s.success_exercise = False
    s.calibration = False
    s.gymmy_done = False
    s.camera_done = False
    s.robot_count = False
    s.demo_finish= False
    s.list_effort_each_exercise={}
    s.ex_in_training=[]
    s.finish_program= False #will turn to true only when the user will press on the exit button
    #s.exercises_start=False
    s.waved_has_tool= True # True just in order to go through the loop in Gymmy
    s.finished_training_adding_to_excel= False
    # Excel variable
    ############################# להוריד את הסולמיות
    s.ex_list = {}

    # Create all components
    s.camera = Camera()
    s.training = Training()
    s.robot = Gymmy()

    s.screen = Screen()
    #s.screen.switch_frame(HelloPage)


    # Start all threads
    s.camera.start()
    s.training.start()
    s.robot.start()


    s.screen.switch_frame(EntrancePage)
    app = FullScreenApp(s.screen)
    s.screen.mainloop()

