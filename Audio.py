import threading
import time
import pygame.mixer
import wave
import Settings as s

import random
import time
import wave  # To get the length of the audio file

class ContinuousAudio(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        random_number = random.randint(1, 6)
        self.file_name = f'song_{random_number}'
        self.current_volume = s.volume
        self.last_additional_audio_time = 0  # Track the last time additional audio played

    def run(self):
        while s.audio_path is None:
            time.sleep(1)

        # Calculate the total length of the audio file in seconds
        audio_path = 'audio files/Songs/' + self.file_name + '.wav'
        total_length = self.get_audio_length(audio_path)

        # Calculate the maximum starting point (30 minutes from the end)
        min_start_time = 0
        max_start_time = total_length - 30 * 60  # 30 minutes (in seconds) before the end

        if max_start_time < 0:
            max_start_time = 0  # If the file is shorter than 30 minutes, start from the beginning

        # Select a random start time
        start_time = random.uniform(min_start_time, max_start_time)

        # Load the audio file
        pygame.mixer.music.load(audio_path)

        # Set the initial volume before playing
        pygame.mixer.music.set_volume(s.volume)

        # Set the start position for the audio playback
        pygame.mixer.music.play(start=0)
        pygame.mixer.music.set_pos(start_time)  # Start from the random point

        # Continue playing the audio until the workout is finished
        while not s.finish_workout:
            current_time = time.time()

            # If additional audio is playing, lower the volume
            if s.additional_audio_playing:
                if s.volume>=0.1:
                    pygame.mixer.music.set_volume(0.1)  # Lower volume to 10%
                else:
                    pygame.mixer.music.set_volume(s.volume)
                self.last_additional_audio_time = current_time  # Update last play time
            else:
                # Restore the volume if at least 1 second has passed since the last additional audio
                if current_time - self.last_additional_audio_time >= 1:
                    if pygame.mixer.music.get_volume() != s.volume:
                        pygame.mixer.music.set_volume(s.volume)
                        self.current_volume = s.volume  # Update the stored volume

            # Dynamically update the volume to match the current `s.volume`
            if not s.additional_audio_playing:
                pygame.mixer.music.set_volume(s.volume)

            # Check if the music is still playing, and replay if necessary
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(start=0)
                pygame.mixer.music.set_pos(start_time)  # Optional replay logic here

            pygame.time.Clock().tick(10)

        # Stop the audio when the workout is finished
        pygame.mixer.music.stop()

    def stop(self):
        """
        Stop the audio playback and exit the loop.
        """
        s.finish_workout = True
        pygame.mixer.music.stop()

    def get_audio_length(self, file_path):
        """
        Get the length of the audio file in seconds.
        """
        with wave.open(file_path, 'rb') as audio_file:
            frames = audio_file.getnframes()
            rate = audio_file.getframerate()
            duration = frames / float(rate)
            return duration


class AdditionalAudio(threading.Thread):
    def __init__(self, file_name, is_explanation= False, is_effort = False):
        threading.Thread.__init__(self)
        self.file_name = file_name
        self.is_explanation = is_explanation
        self.is_effort = is_effort

    def run(self):
        # Indicate that additional audio is playing
        s.additional_audio_playing = True

        # Find an available channel for additional audio
        channel = pygame.mixer.find_channel()

        if channel:
            sound = pygame.mixer.Sound(s.audio_path + self.file_name + '.wav')
            channel.play(sound)

            # Wait until the additional sound finishes playing
            while channel.get_busy():
                if (self.is_explanation and s.explanation_over) or (self.is_effort and s.finished_effort):
                    channel.stop()  # Stop the sound playback

                pygame.time.Clock().tick(10)

        # Indicate that additional audio is finished playing
        s.additional_audio_playing = False
        time.sleep(5)

def say(str_to_say, is_explanation= False, is_effort= False):
    """
    This function triggers additional audio playback in parallel with any other sound.
    :param str_to_say: Name of the file (without .wav extension) to play.
    """
    additional_audio = AdditionalAudio(str_to_say, is_explanation, is_effort)
    additional_audio.start()

def get_wav_duration(str_to_say):
    str_with_path = s.audio_path + str_to_say + '.wav'
    with wave.open(str_with_path, 'rb') as wav_file:
        num_frames = wav_file.getnframes()
        frame_rate = wav_file.getframerate()
        duration = num_frames / float(frame_rate)
        return int(duration)

if __name__ == '__main__':
    language = 'Hebrew'
    gender = 'Male'
    s.audio_path = 'audio files/' + language + '/' + gender + '/'
    s.finish_workout= False
    s.additional_audio_playing= False
    s.volume = 0.5
    # Initialize pygame mixer globally (only once)
    pygame.mixer.init()
    s.req_exercise = "bbb"
    s.stop_song = False

    # Start continuous audio in a separate thread
    continuous_audio = ContinuousAudio()
    continuous_audio.start()

    # Allow some time for the continuous audio to play
    time.sleep(5)

    # Use the say() function to play additional audio while background audio is still running
    say("1")
    time.sleep(5)

    say("2")
    time.sleep(5)
    say("3")
    # # Stop the continuous audio after some time
    # continuous_audio.stop()
    # # Join the continuous audio thread
    # continuous_audio.join()
