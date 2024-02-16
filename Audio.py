import threading
import wave
import time
import pygame.mixer

import Settings as s

class Audio(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        print("AUDIO INITIALIZATION")

    def run(self):
        while not s.finish_workout:
            if s.str_to_say != "":
                self.say_no_wait(s.str_to_say)
                print("tts says: ", s.str_to_say)
                s.str_to_say = ""
        print("AUDIO DONE")

    def say1(self, str_to_say):
        if str_to_say != "":
            pygame.mixer.music.load(s.audio_path + str_to_say + '.wav')
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

def say(str_to_say):
    '''
    str_to_say = the name of the file
    This function make the robot say whatever there is in the file - play the audio (paralelly)
    :return: audio
    '''
    pygame.mixer.init()
    pygame.mixer.music.load(s.audio_path + str_to_say + '.wav')
    pygame.mixer.music.play()

def get_wav_duration(str_to_say):
    str_with_path = s.audio_path + str_to_say + '.wav'
    with wave.open(str_with_path, 'rb') as wav_file:
        # Get the number of frames and the frame rate
        num_frames = wav_file.getnframes()
        frame_rate = wav_file.getframerate()

        # Calculate the duration in seconds
        duration = num_frames / float(frame_rate)

        return duration

if __name__ == '__main__':
    language = 'Hebrew'
    gender = 'Male'
    s.audio_path = 'audio files/' + language + '/' + gender + '/'

    # Initialize pygame mixer
    pygame.mixer.init()

    # Use the say function to play audio
    say("calibration")
    # Sleep for a while to allow the first audio to play
    time.sleep(5)
    say("hello_waving")