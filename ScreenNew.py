# -*- coding: utf-8 -*-
import time
import tkinter as tk
from datetime import datetime

import pandas as pd
import pygame
from PIL import Image, ImageTk
import Settings as s
from Audio import say
import random
import math
from gtts import gTTS
import os
import playsound  # You can use other libraries for playing the speech, like pygame or pyaudio
import pyttsx3





class Screen(tk.Tk):
    def __init__(self):
        print("screen start")
        tk.Tk.__init__(self, className='Gymmy')
        self._frame = None
        self["bg"]="#F3FCFB"


    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            if hasattr(self._frame, 'background_label'):
                self._frame.background_label.destroy()
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

    def wait_until_waving(self):
        s.req_exercise = "hello_waving"
        while not s.waved_has_tool:
            time.sleep(0.00000001)

    def quit(self):
        self.destroy()


def add_daytime(to_say):
    hour = datetime.now().hour
    print(hour)

    if (22 <= hour <= 23) or (0 <= hour <= 5):
        to_say += "לילה טוב!"

    if (6 <= hour <= 10):
        to_say += "בוקר טוב!"

    if (11 <= hour <= 14):
        to_say += "צהריים טובים!"

    if (15 <= hour <= 18):
        to_say += "אחר צהריים טובים!"

    if (19 <= hour <= 21):
        to_say += "ערב טוב!"

    return to_say


def text_to_speech(text, lang='iw', slow=False):
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save("output.mp3")

    # Initialize pygame mixer
    pygame.mixer.init()

    # Load and play the audio file
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()

    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Clean up
    pygame.mixer.quit()


def text_to_speech2():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print(voice, voice.id)
        engine.setProperty('voice', voice.id)
        engine.setProperty('rate', 120)
        engine.say("hello")
        engine.runAndWait()
        engine.stop()


class ID_patient_fill_page(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//IDFillPage.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        self.user_id_entry_patient = tk.Entry(self, font=('Arial', 14), width=20)
        self.user_id_entry_patient.place(x=400, y=250)
        # Button to retrieve information from the Entry widget
        submit_button = tk.Button(self, text="היכנס", command=self.on_submit_patient)
        submit_button.place(x=450, y=300)  # Adjust x and y coordinates as needed

    def on_submit_patient(self):
        user_id = self.user_id_entry_patient.get()
        print(f"User ID entered: {user_id}")
        # Add your logic here to handle the user ID, e.g., store it in a variable or perform an action.
        if user_id != "":
            excel_file_path = "Patients.xlsx"
            df = pd.read_excel(excel_file_path)

            # Convert the first column to string for comparison
            df.iloc[:, 0] = df.iloc[:, 0].astype(str)

            # Convert the user_id to string and remove leading/trailing spaces for comparison
            user_id_cleaned = str(user_id).strip()

            # Filter rows based on the condition
            row_of_patient = df[df.iloc[:, 0] == user_id_cleaned]

            if row_of_patient is None:
                self.label = tk.Label(self, text="תעודת זהות לא שמורה במערכת, אנא פנה לנציג או הכנס תז חדשה")
                self.label.place(x=450, y=350)

            else:
                ezer=row_of_patient.iloc[0, 2]

                if ezer==0:
                    self.label = tk.Label(self, text="אין תרגילים שמורים למשתמש, אנא פנה לנציג")
                    self.label.place(x=450, y=350)

                else:
                    s.ex_in_training=[]
                    num_columns= df.shape[1]

                    for i in range (4,num_columns):
                        if row_of_patient.iloc[0,i]=="Y":
                            s.ex_in_training.append(df.columns[i])

                    print(s.ex_in_training)
                    to_say="היי "+row_of_patient.iloc[0,1]+". "
                    to_say=add_daytime(to_say)
                    text_to_speech(to_say)
                    #text_to_speech2()

        else:
            self.label = tk.Label(self, text="לא הוכנסה תעודת זהות")
            self.label.place(x=450, y=350)







class ID_physiotherapist_fill_page(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//IDFillPage.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        self.user_id_entry_physio= tk.Entry(self, font=('Arial', 14), width=20)
        self.user_id_entry_physio.place(x=400, y=250)
        # Button to retrieve information from the Entry widget
        submit_button = tk.Button(self, text="היכנס", command=self.on_submit_physio)
        submit_button.place(x=450, y=300)  # Adjust x and y coordinates as needed

    def on_submit_physio(self):
        user_id = self.user_id_entry_physio.get()
        print(f"User ID entered: {user_id}")
        # Add your logic here to handle the user ID, e.g., store it in a variable or perform an action.

        if user_id != "":
            excel_file_path = "Physiotherapists.xlsx"
            df = pd.read_excel(excel_file_path)

            # Convert the first column to string for comparison
            df.iloc[:, 0] = df.iloc[:, 0].astype(str)

            # Convert the user_id to string and remove leading/trailing spaces for comparison
            user_id_cleaned = str(user_id).strip()

            # Filter rows based on the condition
            row_of_patient = df[df.iloc[:, 0] == user_id_cleaned]

            if row_of_patient is None:
                self.label = tk.Label(self, text="תעודת זהות לא שמורה במערכת, אנא פנה לנציג או הכנס תז חדשה")
                self.label.place(x=450, y=350)

            else:
                    to_say = "היי " + row_of_patient.iloc[0, 1] + ", "
                    to_say = add_daytime(to_say)
                    text_to_speech(to_say)
                    self.text_to_speech(to_say)

                    self.label = tk.Label(self, text="לא הוכנסה תעודת זהות")
                    self.label.place(x=450, y=350)


        else:
            self.label = tk.Label(self, text="לא הוכנסה תעודת זהות")
            self.label.place(x=450, y=350)
class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)

    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom


if __name__ == "__main__":
    s.audio_path = 'audio files/Hebrew/Male/'
    s.screen = Screen()
    s.screen.switch_frame(ID_patient_fill_page)
    app = FullScreenApp(s.screen)
    s.screen.mainloop()