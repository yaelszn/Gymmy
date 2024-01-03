import threading
import wave

import Settings as s
import winsound
from pygame import mixer
import time


class Audio(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        print ("AUDIO INITIALIZATION")

    def run(self):
        while not s.finish_workout:
            if s.str_to_say!="":
                self.say_no_wait(s.str_to_say)
                print("tts says: ", s.str_to_say)
                s.str_to_say = ""
        print ("AUDIO DONE")

    def say1(self, str_to_say):
        if (str_to_say != ""):
            winsound.PlaySound(s.audio_path+str_to_say+'.wav', winsound.SND_FILENAME)


def say(str_to_say):
    '''
    str_to_say = the name of the file
    This function make the robot say whatever there is in the file - play the audio (paralelly)
    :return: audio
    '''
    mixer.init()
    mixer.music.load(s.audio_path+str_to_say+'.wav')
    mixer.music.play()

   # while mixer.music.get_busy():
    #    time.sleep(0.1)


def get_wav_duration(str_to_say):
    str_with_path= s.audio_path + str_to_say + '.wav'
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
    s.audio_path = 'audio files/' + language + '/'+gender+'/'

    # audio = Audio()
    # audio.say('raise arms forward')
    say("calibration")
    #time.sleep(5)
    say("hello_waving")
