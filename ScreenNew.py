# -*- coding: utf-8 -*-
import atexit
import queue
import threading
import time
import tkinter as tk
from datetime import datetime
from statistics import mean, stdev
from tkinter import ttk

import openpyxl
from gtts import gTTS
from gtts.tokenizer import Tokenizer
import os
import matplotlib
matplotlib.use('TkAgg')  # Use the TkAgg backend

import cv2
import pandas as pd
import pygame
from PIL import Image, ImageTk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkthemes import ThemedTk, ThemedStyle
import customtkinter



import Settings as s
from Audio import say
import random
import math
from gtts import gTTS
import os
import playsound  # You can use other libraries for playing the speech, like pygame or pyaudio
import pyttsx3
import Excel





class Screen(tk.Tk):
    def __init__(self):
        print("screen start")
        tk.Tk.__init__(self, className='Gymmy')
        self._frame = None
        self["bg"]="#F3FCFB"

    def switch_frame(self, frame_class, **kwargs):
        """Destroys all existing frames and creates a new one."""

        # Destroy all existing frames
        for widget in self.winfo_children():
            widget.destroy()

        # Create a new frame
        new_frame = frame_class(self, **kwargs)
        self._frame = new_frame
        self._frame.pack()

    def wait_until_waving(self):
        s.waved_has_tool = False
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



def text_to_speech2(language='iw'):
    text = "הרם את הידיים ב-90 מעלות"
    tts = gTTS(text=text, lang=language, slow=False, lang_check=False)
    tts.save("output.mp3")

    # Play the generated speech using a media player
    os.system("start output.mp3")






class EntrancePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image1 = Image.open('Pictures//background.jpg')
        self.photo_image1 = ImageTk.PhotoImage(image1)
        self.background_label = tk.Label(self, image=self.photo_image1)
        self.background_label.pack()  # Pack the background label here
        s.chosen_patient_ID = None

        # Load images for buttons
        therapist_image = Image.open("Pictures//therapist_enterence_button.jpg")  # Change path to your image file
        therapist_photo = ImageTk.PhotoImage(therapist_image)
        patient_image = Image.open("Pictures//patient_enterence_button.jpg")  # Change path to your image file
        patient_photo = ImageTk.PhotoImage(patient_image)

        # Create buttons with images
        enter_as_therapist_button = tk.Button(self, image=therapist_photo,
                                              command=lambda: self.on_click_therapist_chosen(),
                                              width=therapist_image.width, height=therapist_image.height,
                                              bg='#50a6ad', bd=0, highlightthickness=0)  # Set border width to 0 to remove button border
        enter_as_therapist_button.image = therapist_photo  # Store reference to image to prevent garbage collection
        enter_as_therapist_button.place(x=160, y=130)

        enter_as_patient_button = tk.Button(self, image=patient_photo,
                                            command=lambda: self.on_click_patient_chosen(),
                                            width=patient_image.width, height=patient_image.height,
                                            bg='#50a6ad', bd=0, highlightthickness=0)  # Set border width to 0 to remove button border
        enter_as_patient_button.image = patient_photo  # Store reference to image to prevent garbage collection
        enter_as_patient_button.place(x=540, y=130)
        s.ex_in_training = []


    def on_click_therapist_chosen(self):
        s.screen.switch_frame(ID_therapist_fill_page)


    def on_click_patient_chosen(self):
        s.screen.switch_frame(ID_patient_fill_page)


class ID_patient_fill_page(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//IDFillPage.jpg')
        self.photo_image = ImageTk.PhotoImage(image)  # self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image=self.photo_image).pack()
        self.user_id_entry_patient = tk.Entry(self, font=('Thaoma', 14), width=20)
        self.user_id_entry_patient.place(x=400, y=260)
        self.labels = []

        # Load image for the submit button
        submit_image = Image.open("Pictures//enter.jpg")  # Change path to your image file
        submit_photo = ImageTk.PhotoImage(submit_image)

        # Create button with image
        submit_button = tk.Button(self, image=submit_photo,
                                  command=lambda: self.on_submit_patient(),
                                  width=submit_image.width, height=submit_image.height,
                                  bg='#50a6ad', bd=0, highlightthickness=0)  # Set highlightthickness to 0
        submit_button.image = submit_photo  # Store reference to image to prevent garbage collection
        submit_button.place(x=460, y=300)  # Adjust x and y coordinates as needed




    def on_submit_patient(self):
        self.delete_all_labels()
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

            if row_of_patient.empty:
                # empty image as background for label
                back = Image.open('Pictures//id_not_in_system.jpg')
                background_img = ImageTk.PhotoImage(back)

                self.label = tk.Label(self, image=background_img, compound=tk.CENTER, highlightthickness=0)
                self.label.place(x=250, y=360)
                self.label.image = background_img
                self.labels.append(self.label)

            else:
                ezer=row_of_patient.iloc[0]["number of exercises"]

                if ezer==0:
                    # empty image as background for label
                    back = Image.open('Pictures//no_exercsies_for_patient.jpg')
                    background_img = ImageTk.PhotoImage(back)

                    self.label = tk.Label(self, image=background_img, compound=tk.CENTER, highlightthickness=0)
                    self.label.place(x=260, y=360)
                    self.label.image = background_img
                    self.labels.append(self.label)



                else:
                    s.chosen_patient_ID=user_id
                    s.ex_in_training=[]
                    num_columns= df.shape[1]

                    for i in range (5,num_columns): #including 0
                        if row_of_patient.iloc[0,i]==True:
                            s.ex_in_training.append(df.columns[i])

                    print(s.ex_in_training)
                    to_say="היי "+row_of_patient.iloc[0]["first name"]+". "
                    to_say=add_daytime(to_say)
                    #text_to_speech(to_say)
                    #text_to_speech2()
                    s.screen.switch_frame(StartingOfTraining)




        else:
            back = Image.open('Pictures//no_id.jpg')
            background_img = ImageTk.PhotoImage(back)

            self.label = tk.Label(self, image=background_img, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=320, y=360)
            self.label.image = background_img
            self.labels.append(self.label)

    def delete_all_labels(self):
        for label in self.labels:
            label.destroy()

        self.labels=[]

class ID_therapist_fill_page(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//IDFillPage.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        self.user_id_entry_physio= tk.Entry(self, font=('Thaoma', 14), width=20)
        self.user_id_entry_physio.place(x=400, y=260)
        self.labels=[]


        # Load image for the submit button
        submit_image = Image.open("Pictures//enter.jpg")  # Change path to your image file
        submit_photo = ImageTk.PhotoImage(submit_image)

        # Create button with image
        submit_button = tk.Button(self, image=submit_photo,
                                  command=lambda: self.on_submit_physio(),
                                  width=submit_image.width, height=submit_image.height,
                                  bg='#50a6ad', bd=0, highlightthickness=0)  # Set highlightthickness to 0
        submit_button.image = submit_photo  # Store reference to image to prevent garbage collection
        submit_button.place(x=460, y=300)  # Adjust x and y coordinates as needed


    def on_submit_physio(self):
        self.delete_all_labels()
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


            if row_of_patient.empty:
                back = Image.open('Pictures//id_not_in_system.jpg')
                background_img = ImageTk.PhotoImage(back)

                self.label = tk.Label(self, image=background_img, compound=tk.CENTER, highlightthickness=0)
                self.label.place(x=250, y=360)
                self.label.image = background_img
                self.labels.append(self.label)



            else:
                to_say = "היי " + row_of_patient.iloc[0]["first name"] + ". "
                to_say = add_daytime(to_say)
               # text_to_speech(to_say)
                s.screen.switch_frame(Choose_Action_Physio)


        else:
            back = Image.open('Pictures//no_id.jpg')
            background_img = ImageTk.PhotoImage(back)

            self.label = tk.Label(self, image=background_img, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=320, y=360)
            self.label.image = background_img
            self.labels.append(self.label)


    def delete_all_labels(self):
        for label in self.labels:
            label.destroy()

        self.labels = []

class Choose_Action_Physio(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//background.jpg')
        self.photo_image = ImageTk.PhotoImage(image)  # self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image=self.photo_image).pack()

        exit_button_img = Image.open("Pictures//exit_system.jpg")  # Change path to your image file
        exit_button_photo = ImageTk.PhotoImage(exit_button_img)

        exit_button = tk.Button(self, image=exit_button_photo, command=lambda: self.on_click_quit(),
                                              width=exit_button_img.width, height=exit_button_img.height, bd=0, highlightthickness=0)  # Set border width to 0 to remove button border
        exit_button.image = exit_button_photo  # Store reference to image to prevent garbage collection
        exit_button.place(x=30, y=30)



         # Load images for buttons
        therapist_register_button_img = Image.open("Pictures//add_physio.jpg")  # Change path to your image file
        therapist_register_button_photo = ImageTk.PhotoImage(therapist_register_button_img)
        patient_register_button_img = Image.open("Pictures//add_patient.jpg")  # Change path to your image file
        patient_register_button_photo = ImageTk.PhotoImage(patient_register_button_img)
        go_to_training_sessions_page_button_img = Image.open("Pictures//to_patients_list.jpg")  # Change path to your image file
        go_to_training_sessions_page_button_photo = ImageTk.PhotoImage(go_to_training_sessions_page_button_img)

        go_to_training_sessions_page_button = tk.Button(self, image=go_to_training_sessions_page_button_photo,
                                                        command=lambda: self.on_go_to_training_sessions_page_click(),
                                                        width=go_to_training_sessions_page_button_img.width,
                                                        height=go_to_training_sessions_page_button_img.height,
                                                        bg='#50a6ad', bd=0,
                                                        highlightthickness=0)  # Set border width to 0 to remove button border
        go_to_training_sessions_page_button.image = go_to_training_sessions_page_button_photo  # Store reference to image to prevent garbage collection
        go_to_training_sessions_page_button.place(x=225, y=120)

        # Create buttons with images
        therapist_register_button = tk.Button(self, image=therapist_register_button_photo,
                                              command=lambda: self.on_register_physio_click(),
                                              width=therapist_register_button_img.width, height=therapist_register_button_img.height,  bg='#50a6ad', bd=0,
                                              highlightthickness=0)  # Set border width to 0 to remove button border
        therapist_register_button.image = therapist_register_button_photo  # Store reference to image to prevent garbage collection
        therapist_register_button.place(x=535, y=310)

        patient_register_button = tk.Button(self, image=patient_register_button_photo,
                                            command=lambda: self.on_register_patient_click(),
                                            width=patient_register_button_img.width, height=patient_register_button_img.height,
                                            bg='#50a6ad', bd=0,
                                            highlightthickness=0)  # Set border width to 0 to remove button border
        patient_register_button.image = patient_register_button_photo  # Store reference to image to prevent garbage collection
        patient_register_button.place(x=225, y=310)




    def on_register_physio_click(self):
        s.screen.switch_frame(PhysioRegistration)

    def on_register_patient_click(self):
        s.screen.switch_frame(PatientRegistration)


    def on_go_to_training_sessions_page_click(self):
        s.screen.switch_frame(PatientDisplaying)

    def on_click_quit(self):
        s.screen.switch_frame(ID_therapist_fill_page)

class PhysioRegistration(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//physio_registration.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()

        back_button_img = Image.open("Pictures//back_to_menu.jpg")  # Change path to your image file
        back_button_photo = ImageTk.PhotoImage(back_button_img)

        back_button = tk.Button(self, image=back_button_photo, command=lambda: self.on_click_to_physio_menu(),
                                              width=back_button_img.width, height=back_button_img.height, bd=0, highlightthickness=0)  # Set border width to 0 to remove button border
        back_button.image = back_button_photo  # Store reference to image to prevent garbage collection
        back_button.place(x=30, y=30)



        self.first_name_entry = tk.Entry(self, font=('Thaoma', 14), width=20, justify='right')
        self.first_name_entry.place(x=370, y=190)
        self.last_name_entry = tk.Entry(self, font=('Thaoma', 14), width=20, justify='right')
        self.last_name_entry.place(x=370, y=250)
        self.id_entry = tk.Entry(self, font=('Thaoma', 14), width=20, justify='right')
        self.id_entry.place(x=370, y=310)

        add_physio_button_img = Image.open("Pictures//add.jpg")  # Change path to your image file
        add_physio_button_photo = ImageTk.PhotoImage(add_physio_button_img)

        add_physio_button = tk.Button(self, image=add_physio_button_photo, command=lambda: self.on_click_physio_registration(),
                                width=add_physio_button_img.width, height=add_physio_button_img.height, bd=0,
                                highlightthickness=0)  # Set border width to 0 to remove button border
        add_physio_button.image = add_physio_button_photo  # Store reference to image to prevent garbage collection
        add_physio_button.place(x=425, y=365)
        self.labels=[] #collect the labels that apear so that on a click on the button i can delete them


    def on_click_physio_registration(self):
        self.delete_all_labels()

        excel_file_path = "Physiotherapists.xlsx"
        df = pd.read_excel(excel_file_path)
        ID_entered=self.id_entry.get()
        is_in_ID = ID_entered in df['ID'].astype(str).values #chaeck if the ID that the user inserted is already in system



        if ID_entered=="":
            back = Image.open('Pictures//no_id.jpg')
            no_id_label = ImageTk.PhotoImage(back)
            self.label = tk.Label(self, image=no_id_label, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=290, y=425)
            self.label.image = no_id_label
            self.labels.append(self.label)

        elif is_in_ID is True:
            back = Image.open('Pictures//id_already_in_system.jpg')
            id_already_in_system = ImageTk.PhotoImage(back)
            self.label = tk.Label(self, image=id_already_in_system, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=220, y=425)
            self.label.image = id_already_in_system
            self.labels.append(self.label)


        else: #insret a new row to the physio excel
            df = pd.read_excel(excel_file_path)
            new_row_data = {'ID':ID_entered , 'first name': self.first_name_entry.get(), "last name": self.last_name_entry.get()}
            new_row_df = pd.DataFrame([new_row_data])
            df = pd.concat([df, new_row_df], ignore_index=True)
            df.to_excel(excel_file_path, index=False)

            back = Image.open('Pictures//successfully_added_physio.jpg')
            successfully_added_physio = ImageTk.PhotoImage(back)
            self.label = tk.Label(self, image=successfully_added_physio, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=280, y=425)
            self.label.image = successfully_added_physio
            self.first_name_entry.delete(0, tk.END)
            self.last_name_entry.delete(0, tk.END)
            self.id_entry.delete(0, tk.END)
            self.labels.append(self.label)


    def delete_all_labels(self):
        for label in self.labels:
            label.destroy()

        self.labels = []
    def on_click_to_physio_menu(self):  # go back to the physio menu page
        s.screen.switch_frame(Choose_Action_Physio)



class PatientRegistration(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//patient_registration.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()

        back_button_img = Image.open("Pictures//back_to_menu.jpg")  # Change path to your image file
        back_button_photo = ImageTk.PhotoImage(back_button_img)

        back_button = tk.Button(self, image=back_button_photo, command=lambda: self.on_click_to_physio_menu(),
                                width=back_button_img.width, height=back_button_img.height, bd=0,
                                highlightthickness=0)  # Set border width to 0 to remove button border
        back_button.image = back_button_photo  # Store reference to image to prevent garbage collection
        back_button.place(x=30, y=30)

        self.first_name_entry = tk.Entry(self, font=('Thaoma', 14), width=20, justify='right')
        self.first_name_entry.place(x=370, y=190)
        self.last_name_entry = tk.Entry(self, font=('Thaoma', 14), width=20, justify='right')
        self.last_name_entry.place(x=370, y=250)
        self.id_entry = tk.Entry(self, font=('Thaoma', 14), width=20, justify='right')
        self.id_entry.place(x=370, y=310)

        self.options = ["גבר", "אישה"]
        self.gender = 'Male'
        self.selected_option = tk.StringVar()
        self.selected_option.set(self.options[0])  # Set the default selected option

        # Create a custom style for the OptionMenu
        style = ttk.Style()
        style.theme_use('clam')  # Choose a theme (e.g., 'clam', 'default', 'alt', 'classic')

        # Configure the appearance of the OptionMenu
        style.configure('Custom.TMenubutton', font=('Arial', 12, 'bold'), background='lightgray', foreground='black',
                        anchor='e')
        style.configure('Custom.TMenubutton.TMenu', font=('Arial', 12, 'bold'), anchor='e')  # Bold font for the dropdown list

        # Create the OptionMenu with the custom style
        self.option_menu = ttk.OptionMenu(self, self.selected_option, self.selected_option.get(), *self.options,
                                          command=self.on_select_gender)
        self.option_menu['style'] = 'Custom.TMenubutton'  # Apply the custom style
        self.option_menu.config(width=6)  # Adjust the width of the grey place
        self.option_menu.place(x=440, y=365)



        add_patient_button_img = Image.open("Pictures//add.jpg")  # Change path to your image file
        add_patient_button_photo = ImageTk.PhotoImage(add_patient_button_img)

        add_patient_button = tk.Button(self, image=add_patient_button_photo,
                                      command=lambda: self.on_click_patient_registration(),
                                      width=add_patient_button_img.width, height=add_patient_button_img.height, bd=0,
                                      highlightthickness=0)  # Set border width to 0 to remove button border
        add_patient_button.image = add_patient_button_photo  # Store reference to image to prevent garbage collection
        add_patient_button.place(x=425, y=445)
        self.labels = []  # collect the labels that apear so that on a click on the button i can delete them

    def on_select_gender(self, option):
        if option=='אישה':
            self.gender='Female'

        else:
            self.gender='Male'

    def on_click_patient_registration(self):
        self.delete_all_labels()

        excel_file_path = "Patients.xlsx"
        df = pd.read_excel(excel_file_path)
        ID_entered=self.id_entry.get()
        is_in_ID = ID_entered in df['ID'].astype(str).values #chaeck if the ID that the user inserted is already in system



        if ID_entered=="":
            back = Image.open('Pictures//no_id.jpg')
            background_img = ImageTk.PhotoImage(back)

            self.label = tk.Label(self, image=background_img, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=310, y=500)
            self.label.image = background_img
            self.labels.append(self.label)


        elif is_in_ID is True:
            back = Image.open('Pictures//id_already_in_system.jpg')
            id_already_in_system = ImageTk.PhotoImage(back)
            self.label = tk.Label(self, image=id_already_in_system, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=220, y=500)
            self.label.image = id_already_in_system
            self.labels.append(self.label)



        else: #insret a new row to the physio excel
            df = pd.read_excel(excel_file_path)
            new_row_data = {column: False for column in df.columns}
            #modifying the columns that has other value than false
            new_row_data.update({
                'ID': ID_entered,
                'first name': self.first_name_entry.get(),
                'last name': self.last_name_entry.get(),
                'gender': self.gender,
                'number of exercises': 0
            })

            new_row_df = pd.DataFrame([new_row_data])
            df = pd.concat([df, new_row_df], ignore_index=True)
            df.to_excel(excel_file_path, index=False)

            back = Image.open('Pictures//successfully_added_patient.jpg')
            successfully_added_patient = ImageTk.PhotoImage(back)
            self.label = tk.Label(self, image=successfully_added_patient, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=280, y=500)
            self.label.image = successfully_added_patient
            self.first_name_entry.delete(0, tk.END)
            self.last_name_entry.delete(0, tk.END)
            self.id_entry.delete(0, tk.END)
            self.selected_option.set(self.options[0])
            self.gender='Male'
            self.labels.append(self.label)




    def delete_all_labels(self):
        for label in self.labels:
            label.destroy()

        self.labels = []
    def on_click_to_physio_menu(self):  # go back to the physio menu page
        s.screen.switch_frame(Choose_Action_Physio)

class PatientDisplaying(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        excel_file_path = "Patients.xlsx"
        df = pd.read_excel(excel_file_path, usecols=['ID', 'first name', 'last name'])
        new_headers = {'ID': 'תעודת זהות'[::-1], 'first name': 'שם פרטי'[::-1], 'last name': 'שם משפחה'[::-1]}
        df.rename(columns=new_headers, inplace=True)
        s.chosen_patient_ID=None
        s.excel_file_path_Patient=None

        for col in df.columns[1:3]:
            df[col] = df[col].apply(lambda x: x[::-1])

        # Load the background image
        image = Image.open('Pictures//Patient_list.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        # Create a label to display the background image
        self.background_label = tk.Label(self, image=self.photo_image)
        self.background_label.pack(fill="both", expand=True)

        # Display the DataFrame in a Treeview widget
        self.treeview = ttk.Treeview(self, style="Treeview", show="headings")
        self.treeview["columns"] = tuple(df.columns)

        # Set up a custom style for the Treeview
        style = ttk.Style(self)
        style.configure("Treeview", font=("Thaoma", 14, 'bold'), rowheight=30)  # Adjust the font size (16 in this case)

        # Add columns to the Treeview
        for col in df.columns:
            self.treeview.column(col, anchor="e", width=150)  # Set the anchor to "e" (east, or right-aligned)
            self.treeview.heading(col, text=col, anchor="e")

        # Insert data into the Treeview
        for index, row in df.iterrows():
            values = tuple(row)
            self.treeview.insert("", index, values=values, tags=(index,))

        # Set up event handling for row selection
        self.treeview.tag_configure("selected", background="lightblue")
        self.treeview.bind("<ButtonRelease-1>", self.on_treeview_click)
        self.treeview.config(height=10)

        # Pack the Treeview widget
        self.treeview.place(x=270, y=180)

        # Set up a vertical scrollbar
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(x=725, y=180, height=310)


        back_button_img = Image.open("Pictures//back_to_menu.jpg")  # Change path to your image file
        back_button_photo = ImageTk.PhotoImage(back_button_img)
        back_button = tk.Button(self, image=back_button_photo, command=lambda: self.on_click_to_physio_menu(),
                                width=back_button_img.width, height=back_button_img.height, bd=0,
                                highlightthickness=0)  # Set border width to 0 to remove button border
        back_button.image = back_button_photo  # Store reference to image to prevent garbage collection
        back_button.place(x=30, y=30)



    def on_click_to_physio_menu(self): #go back to the physio menu page
        s.screen.switch_frame(Choose_Action_Physio)

    def on_treeview_click(self, event):
        print("Clicked on a row!")
        # Get the selected item and tag (row index)
        item_id = self.treeview.identify_row(event.y)
        if item_id:
            # Update the color for the selected row
            self.treeview.tag_configure("selected", background="lightblue")

            # Deselect the previously selected row
            for item in self.treeview.get_children():
                self.treeview.tag_configure(item, background="white")

            # Get the selected row data
            selected_row = self.treeview.item(item_id, "values")
            print("Selected Row:", selected_row)

            s.chosen_patient_ID=selected_row[0]

            excel_file_path = "Patients.xlsx"
            df = pd.read_excel(excel_file_path)
            # Convert the first column to string for comparison
            df.iloc[:, 0] = df.iloc[:, 0].astype(str)
            # Convert the user_id to string and remove leading/trailing spaces for comparison
            user_id_cleaned = str(s.chosen_patient_ID).strip()
            # Filter rows based on the condition
            row_of_patient = df[df.iloc[:, 0] == user_id_cleaned]

            s.excel_file_path_Patient = s.chosen_patient_ID+"_Last.xlsx"
            s.screen.switch_frame(ChooseBallExercisesPage)



def show_graph(exercise, previous):
    # Call the Graph function with the exercise name
    s.screen.switch_frame(GraphPage, exercise=exercise, previous=previous)


def play_video(cap, label, exercise, previous, scale_factor=0.35, slow_factor=1):

    if previous is not None:
        def on_click(event):
            # Call the Graph function with the exercise name
            show_graph(exercise, previous)
            print("video clicked!")

    else:
        def on_click(event):
            print()

    ret, frame = cap.read()

    if ret:
        # Resize the frame
        frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)

        # Convert BGR to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image=Image.fromarray(image))

        label.config(image=photo)
        label.image = photo

        # Bind the click event to the label
        label.bind("<Button-1>", on_click)

        # Adjust the frame rate
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        adjusted_frame_rate = frame_rate * slow_factor
        delay = int(1200 / adjusted_frame_rate)  # Delay in milliseconds

        # Schedule the next frame update
        after_id = label.after(delay, lambda: play_video(cap, label, exercise, previous, scale_factor, slow_factor))
    else:
        # Video reached the end, reset the video capture to play again
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        after_id = label.after(25, lambda: play_video(cap, label, exercise, previous, scale_factor, slow_factor))

    # Return the after_id to have a reference for canceling the scheduled function
    return after_id

def ex_in_training_or_not(data_row, exercise):
    if data_row.iloc[0, data_row.columns.get_loc(exercise)] == True:
        return True
    else:
        return False

def get_row_of_patient():
    excel_file_path = "Patients.xlsx"
    df = pd.read_excel(excel_file_path)

    # Convert the first column to string for comparison
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)

    # Convert the user_id to string and remove leading/trailing spaces for comparison
    user_id_cleaned = str(s.chosen_patient_ID).strip()

    # Filter rows based on the condition
    row_of_patient = df[df.iloc[:, 0] == user_id_cleaned]

    return row_of_patient


class ChooseBallExercisesPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # Load background image
        background_image = Image.open('Pictures//background.jpg')
        self.background_photo = ImageTk.PhotoImage(background_image)
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.pack()

        forward_arrow_button_img = Image.open("Pictures//forward_arrow.jpg")
        forward_arrow_button_photo = ImageTk.PhotoImage(forward_arrow_button_img)
        forward_arrow_button = tk.Button(self, image=forward_arrow_button_photo, command=lambda: self.on_arrow_click(),
                                width=forward_arrow_button_img.width, height=forward_arrow_button_img.height, bd=0,
                                highlightthickness=0)
        forward_arrow_button.image = forward_arrow_button_photo
        forward_arrow_button.place(x=50, y=480)


        to_patients_list_button_img = Image.open("Pictures//back_to_patient_list.jpg")
        to_patients_list_button_photo = ImageTk.PhotoImage(to_patients_list_button_img)
        to_patients_list_button = tk.Button(self, image=to_patients_list_button_photo, command=lambda: self.to_patients_list_button_click(),
                                   width=to_patients_list_button_img.width, height=to_patients_list_button_img.height, bd=0,
                                   highlightthickness=0)  # Set border width to 0 to remove button border
        to_patients_list_button.image = to_patients_list_button_photo  # Store reference to image to prevent garbage collection
        to_patients_list_button.place(x=30, y=30)

        row_of_patient = get_row_of_patient()

        # Create labels for videos
        self.label1 = tk.Label(self)
        self.label1.place(x=30, y=100)  # Adjust x and y coordinates for the first video
        self.checkbox_var1 = tk.BooleanVar(value= ex_in_training_or_not(row_of_patient, "bend_elbows_ball"))
        self.checkbox1 = ttk.Checkbutton(self, variable= self.checkbox_var1)
        self.checkbox1.place(x=110, y=430)

        self.label2 = tk.Label(self)
        self.label2.place(x=230, y=100)  # Adjust x and y coordinates for the second video
        self.checkbox_var2 = tk.BooleanVar(value= ex_in_training_or_not(row_of_patient, "raise_arms_above_head_ball"))
        self.checkbox2 = ttk.Checkbutton(self, variable=self.checkbox_var2)
        self.checkbox2.place(x=310, y=430)

        self.label3 = tk.Label(self)
        self.label3.place(x=430, y=100)  # Adjust x and y coordinates for the third video
        self.checkbox_var3 = tk.BooleanVar(value= ex_in_training_or_not(row_of_patient, "raise_arms_forward_turn_ball"))
        self.checkbox3 = ttk.Checkbutton(self, variable=self.checkbox_var3)
        self.checkbox3.place(x=510, y=430)

        self.label4 = tk.Label(self)
        self.label4.place(x=630, y=100)  # Adjust x and y coordinates for the fourth video
        self.checkbox_var4 = tk.BooleanVar(value= ex_in_training_or_not(row_of_patient, "open_arms_and_forward_ball"))
        self.checkbox4 = ttk.Checkbutton(self, variable=self.checkbox_var4)
        self.checkbox4.place(x=710, y=430)

        self.label5 = tk.Label(self)
        self.label5.place(x=830, y=100)  # Adjust x and y coordinates for the fifth video
        self.checkbox_var5 = tk.BooleanVar(value= ex_in_training_or_not(row_of_patient, "open_arms_above_head_ball"))
        self.checkbox5 = ttk.Checkbutton(self, variable=self.checkbox_var5)
        self.checkbox5.place(x=910, y=430)

        # Video paths
        video_file1 = 'Videos//bend_elbows_ball_vid.mp4'
        video_path1 = os.path.join(os.getcwd(), video_file1)
        self.cap1 = cv2.VideoCapture(video_path1)

        video_file2 = 'Videos//raise_arms_above_head_ball_vid.mp4'
        video_path2 = os.path.join(os.getcwd(), video_file2)
        self.cap2 = cv2.VideoCapture(video_path2)

        video_file3 = 'Videos//raise_arms_forward_turn_ball_vid.mp4'
        video_path3 = os.path.join(os.getcwd(), video_file3)
        self.cap3 = cv2.VideoCapture(video_path3)

        video_file4 = 'Videos//open_arms_and_forward_ball_vid.mp4'
        video_path4 = os.path.join(os.getcwd(), video_file4)
        self.cap4 = cv2.VideoCapture(video_path4)

        video_file5 = 'Videos//open_arms_above_head_ball_vid.mp4'
        video_path5 = os.path.join(os.getcwd(), video_file5)
        self.cap5 = cv2.VideoCapture(video_path5)


        # Check if videos are opened successfully
        if not (self.cap1.isOpened() and self.cap2.isOpened() and self.cap3.isOpened() and self.cap4.isOpened() and self.cap5.isOpened()):
            print("Error opening video streams or files")

        else:
            # Play videos
            play_video(self.cap1, self.label1,"bend_elbows_ball", "ball")
            play_video(self.cap2, self.label2, "raise_arms_above_head_ball", "ball")  # Change "Page2" to the name of the page you want to switch to
            play_video(self.cap3, self.label3, "raise_arms_forward_turn_ball", "ball")  # Change "Page3" to the name of the page you want to switch to
            play_video(self.cap4, self.label4, "open_arms_and_forward_ball", "ball")  # Change "Page4" to the name of the page you want to switch to
            play_video(self.cap5, self.label5, "open_arms_above_head_ball", "ball")  # Change "Page5" to the name of the page you want to switch to


    def save_changes(self):
        new_values_ex_patient = {"bend_elbows_ball": bool(self.checkbox_var1.get()),
                                 "raise_arms_above_head_ball": bool(self.checkbox_var2.get()),
                                 "raise_arms_forward_turn_ball": bool(self.checkbox_var3.get()),
                                 "open_arms_and_forward_ball": bool(self.checkbox_var4.get()),
                                 "open_arms_above_head_ball": bool(self.checkbox_var5.get())}

        Excel.find_and_change_values_Patients(new_values_ex_patient)

    def on_arrow_click(self):
        self.save_changes()
        s.screen.switch_frame(ChooseRubberBandExercisesPage)

    def to_patients_list_button_click(self):
        self.save_changes()
        s.screen.switch_frame(PatientDisplaying)


class ChooseRubberBandExercisesPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # Load background image
        background_image = Image.open('Pictures//background.jpg')
        self.background_photo = ImageTk.PhotoImage(background_image)
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.pack()

        forward_arrow_button_img = Image.open("Pictures//forward_arrow.jpg")
        forward_arrow_button_photo = ImageTk.PhotoImage(forward_arrow_button_img)
        forward_arrow_button = tk.Button(self, image=forward_arrow_button_photo, command=lambda: self.on_arrow_click_forward(),
                                   width=forward_arrow_button_img.width, height=forward_arrow_button_img.height, bd=0,
                                   highlightthickness=0)
        forward_arrow_button.image = forward_arrow_button_photo
        forward_arrow_button.place(x=50, y=480)

        backward_arrow_button_img = Image.open("Pictures//previous_arrow.jpg")
        backward_arrow_button_photo = ImageTk.PhotoImage(backward_arrow_button_img)
        backward_arrow_button = tk.Button(self, image=backward_arrow_button_photo, command=lambda: self.on_arrow_click_back(),
                                   width=backward_arrow_button_img.width, height=backward_arrow_button_img.height, bd=0,
                                   highlightthickness=0)
        backward_arrow_button.image = backward_arrow_button_photo
        backward_arrow_button.place(x=913, y=480)

        to_patients_list_button_img = Image.open("Pictures//back_to_patient_list.jpg")
        to_patients_list_button_photo = ImageTk.PhotoImage(to_patients_list_button_img)
        to_patients_list_button = tk.Button(self, image=to_patients_list_button_photo,
                                   command=lambda: self.to_patients_list_button_click(),
                                   width=to_patients_list_button_img.width, height=to_patients_list_button_img.height,
                                   bd=0,
                                   highlightthickness=0)  # Set border width to 0 to remove button border
        to_patients_list_button.image = to_patients_list_button_photo  # Store reference to image to prevent garbage collection
        to_patients_list_button.place(x=30, y=30)

        row_of_patient = get_row_of_patient()

        # Create labels for videos
        self.label1 = tk.Label(self)
        self.label1.place(x=230, y=100)  # Adjust x and y coordinates for the first video
        self.checkbox_var1 = tk.BooleanVar(value=ex_in_training_or_not(row_of_patient, "open_arms_with_band"))
        self.checkbox1 = ttk.Checkbutton(self, variable=self.checkbox_var1)
        self.checkbox1.place(x=310, y=430)

        self.label2 = tk.Label(self)
        self.label2.place(x=430, y=100)  # Adjust x and y coordinates for the second video
        self.checkbox_var2 = tk.BooleanVar(value=ex_in_training_or_not(row_of_patient, "open_arms_and_up_with_band"))
        self.checkbox2 = ttk.Checkbutton(self, variable=self.checkbox_var2)
        self.checkbox2.place(x=510, y=430)

        self.label3 = tk.Label(self)
        self.label3.place(x=630, y=100)  # Adjust x and y coordinates for the third video
        self.checkbox_var3 = tk.BooleanVar(value=ex_in_training_or_not(row_of_patient, "up_with_band_and_lean"))
        self.checkbox3 = ttk.Checkbutton(self, variable=self.checkbox_var3)
        self.checkbox3.place(x=710, y=430)


        # Video paths
        video_file1 = 'Videos//open_arms_with_band_vid.mp4'
        video_path1 = os.path.join(os.getcwd(), video_file1)
        self.cap1 = cv2.VideoCapture(video_path1)

        video_file2 = 'Videos//open_arms_and_up_with_band_vid.mp4'
        video_path2 = os.path.join(os.getcwd(), video_file2)
        self.cap2 = cv2.VideoCapture(video_path2)

        video_file3 = 'Videos//up_with_band_and_lean_vid.mp4'
        video_path3 = os.path.join(os.getcwd(), video_file3)
        self.cap3 = cv2.VideoCapture(video_path3)



        # Check if videos are opened successfully
        if not (
                self.cap1.isOpened() and self.cap2.isOpened() and self.cap3.isOpened()):
            print("Error opening video streams or files")

        else:
            # Play videos
            play_video(self.cap1, self.label1, "open_arms_with_band", "band")
            play_video(self.cap2, self.label2,"open_arms_and_up_with_band", "band")  # Change "Page2" to the name of the page you want to switch to
            play_video(self.cap3, self.label3,"up_with_band_and_lean", "band")  # Change "Page3" to the name of the page you want to switch to


    def on_arrow_click_forward(self):
        self.save_changes()
        s.screen.switch_frame(ChooseStickExercisesPage)

    def on_arrow_click_back(self):
        self.save_changes()
        s.screen.switch_frame(ChooseBallExercisesPage)

    def to_patients_list_button_click(self):
        self.save_changes()
        s.screen.switch_frame(PatientDisplaying)


    def save_changes(self):
        new_values_ex_patient = {"open_arms_with_band": bool(self.checkbox_var1.get()),
                                 "open_arms_and_up_with_band": bool(self.checkbox_var2.get()),
                                 "up_with_band_and_lean": bool(self.checkbox_var3.get())}

        Excel.find_and_change_values_Patients(new_values_ex_patient)



class ChooseStickExercisesPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # Load background image
        background_image = Image.open('Pictures//background.jpg')
        self.background_photo = ImageTk.PhotoImage(background_image)
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.pack()

        forward_arrow_button_img = Image.open("Pictures//forward_arrow.jpg")
        forward_arrow_button_photo = ImageTk.PhotoImage(forward_arrow_button_img)
        forward_arrow_button = tk.Button(self, image=forward_arrow_button_photo,
                                         command=lambda: self.on_arrow_click_forward(),
                                         width=forward_arrow_button_img.width, height=forward_arrow_button_img.height,
                                         bd=0,
                                         highlightthickness=0)
        forward_arrow_button.image = forward_arrow_button_photo
        forward_arrow_button.place(x=50, y=480)

        backward_arrow_button_img = Image.open("Pictures//previous_arrow.jpg")
        backward_arrow_button_photo = ImageTk.PhotoImage(backward_arrow_button_img)
        backward_arrow_button = tk.Button(self, image=backward_arrow_button_photo,
                                          command=lambda: self.on_arrow_click_back(),
                                          width=backward_arrow_button_img.width,
                                          height=backward_arrow_button_img.height, bd=0,
                                          highlightthickness=0)
        backward_arrow_button.image = backward_arrow_button_photo
        backward_arrow_button.place(x=913, y=480)

        to_patients_list_button_img = Image.open("Pictures//back_to_patient_list.jpg")
        to_patients_list_button_photo = ImageTk.PhotoImage(to_patients_list_button_img)
        to_patients_list_button = tk.Button(self, image=to_patients_list_button_photo,
                                            command=lambda: self.to_patients_list_button_click(),
                                            width=to_patients_list_button_img.width,
                                            height=to_patients_list_button_img.height,
                                            bd=0,
                                            highlightthickness=0)  # Set border width to 0 to remove button border
        to_patients_list_button.image = to_patients_list_button_photo  # Store reference to image to prevent garbage collection
        to_patients_list_button.place(x=30, y=30)

        row_of_patient=get_row_of_patient()

        # Create labels for videos
        self.label1 = tk.Label(self)
        self.label1.place(x=125, y=100)  # Adjust x and y coordinates for the first video
        self.checkbox_var1 = tk.BooleanVar(value=ex_in_training_or_not(row_of_patient, "bend_elbows_stick"))
        self.checkbox1 = ttk.Checkbutton(self, variable=self.checkbox_var1)
        self.checkbox1.place(x=205, y=430)

        self.label2 = tk.Label(self)
        self.label2.place(x=325, y=100)  # Adjust x and y coordinates for the second video
        self.checkbox_var2 = tk.BooleanVar(value=ex_in_training_or_not(row_of_patient, "bend_elbows_and_up_stick"))
        self.checkbox2 = ttk.Checkbutton(self, variable=self.checkbox_var2)
        self.checkbox2.place(x=405, y=430)

        self.label3 = tk.Label(self)
        self.label3.place(x=525, y=100)  # Adjust x and y coordinates for the third video
        self.checkbox_var3 = tk.BooleanVar(value=ex_in_training_or_not(row_of_patient, "arms_up_and_down_stick"))
        self.checkbox3 = ttk.Checkbutton(self, variable=self.checkbox_var3)
        self.checkbox3.place(x=605, y=430)

        self.label4 = tk.Label(self)
        self.label4.place(x=725, y=100)  # Adjust x and y coordinates for the third video
        self.checkbox_var4 = tk.BooleanVar(value=ex_in_training_or_not(row_of_patient, "switch_with_stick"))
        self.checkbox4 = ttk.Checkbutton(self, variable=self.checkbox_var4)
        self.checkbox4.place(x=805, y=430)


        # Video paths
        video_file1 = 'Videos//bend_elbows_stick_vid.mp4'
        video_path1 = os.path.join(os.getcwd(), video_file1)
        self.cap1 = cv2.VideoCapture(video_path1)

        video_file2 = 'Videos//bend_elbows_and_up_stick_vid.mp4'
        video_path2 = os.path.join(os.getcwd(), video_file2)
        self.cap2 = cv2.VideoCapture(video_path2)

        video_file3 = 'Videos//arms_up_and_down_stick_vid.mp4'
        video_path3 = os.path.join(os.getcwd(), video_file3)
        self.cap3 = cv2.VideoCapture(video_path3)

        video_file4 = 'Videos//switch_with_stick_vid.mp4'
        video_path4 = os.path.join(os.getcwd(), video_file4)
        self.cap4 = cv2.VideoCapture(video_path4)



        # Check if videos are opened successfully
        if not (
                self.cap1.isOpened() and self.cap2.isOpened() and self.cap3.isOpened() and self.cap4.isOpened()):
            print("Error opening video streams or files")

        else:
            # Play videos
            play_video(self.cap1, self.label1, "bend_elbows_stick", "stick")
            play_video(self.cap2, self.label2,"bend_elbows_and_up_stick", "stick")
            play_video(self.cap3, self.label3,"arms_up_and_down_stick", "stick")
            play_video(self.cap4, self.label4,"switch_with_stick", "stick")


    def on_arrow_click_forward(self):
        self.save_changes()
        s.screen.switch_frame(ChooseNoToolExercisesPage)

    def on_arrow_click_back(self):
        self.save_changes()
        s.screen.switch_frame(ChooseRubberBandExercisesPage)

    def to_patients_list_button_click(self):
        self.save_changes()
        s.screen.switch_frame(PatientDisplaying)


    def save_changes(self):
        new_values_ex_patient = {"bend_elbows_stick": bool(self.checkbox_var1.get()),
                                 "bend_elbows_and_up_stick": bool(self.checkbox_var2.get()),
                                 "arms_up_and_down_stick": bool(self.checkbox_var3.get()),
                                 "switch_with_stick": bool(self.checkbox_var4.get())}

        Excel.find_and_change_values_Patients(new_values_ex_patient)



class ChooseNoToolExercisesPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # Load background image
        background_image = Image.open('Pictures//background.jpg')
        self.background_photo = ImageTk.PhotoImage(background_image)
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.pack()

        forward_arrow_button_img = Image.open("Pictures//forward_arrow.jpg")
        forward_arrow_button_photo = ImageTk.PhotoImage(forward_arrow_button_img)
        forward_arrow_button = tk.Button(self, image=forward_arrow_button_photo,
                                         command=lambda: self.on_arrow_click_forward(),
                                         width=forward_arrow_button_img.width, height=forward_arrow_button_img.height,
                                         bd=0,
                                         highlightthickness=0)
        forward_arrow_button.image = forward_arrow_button_photo
        forward_arrow_button.place(x=50, y=480)

        backward_arrow_button_img = Image.open("Pictures//previous_arrow.jpg")
        backward_arrow_button_photo = ImageTk.PhotoImage(backward_arrow_button_img)
        backward_arrow_button = tk.Button(self, image=backward_arrow_button_photo,
                                          command=lambda: self.on_arrow_click_back(),
                                          width=backward_arrow_button_img.width,
                                          height=backward_arrow_button_img.height, bd=0,
                                          highlightthickness=0)
        backward_arrow_button.image = backward_arrow_button_photo
        backward_arrow_button.place(x=913, y=480)

        to_patients_list_button_img = Image.open("Pictures//back_to_patient_list.jpg")
        to_patients_list_button_photo = ImageTk.PhotoImage(to_patients_list_button_img)
        to_patients_list_button = tk.Button(self, image=to_patients_list_button_photo,
                                            command=lambda: self.to_patients_list_button_click(),
                                            width=to_patients_list_button_img.width,
                                            height=to_patients_list_button_img.height,
                                            bd=0,
                                            highlightthickness=0)  # Set border width to 0 to remove button border
        to_patients_list_button.image = to_patients_list_button_photo  # Store reference to image to prevent garbage collection
        to_patients_list_button.place(x=30, y=30)

        row_of_patient=get_row_of_patient()

        # Create labels for videos
        self.label1 = tk.Label(self)
        self.label1.place(x=125, y=100)  # Adjust x and y coordinates for the first video
        self.checkbox_var1 = tk.BooleanVar(value=ex_in_training_or_not(row_of_patient, "hands_behind_and_lean_notool"))
        self.checkbox1 = ttk.Checkbutton(self, variable=self.checkbox_var1)
        self.checkbox1.place(x=205, y=430)

        self.label2 = tk.Label(self)
        self.label2.place(x=325, y=100)  # Adjust x and y coordinates for the second video
        self.checkbox_var2 = tk.BooleanVar(value=ex_in_training_or_not(row_of_patient, "right_hand_up_and_bend_notool"))
        self.checkbox2 = ttk.Checkbutton(self, variable=self.checkbox_var2)
        self.checkbox2.place(x=405, y=430)

        self.label3 = tk.Label(self)
        self.label3.place(x=525, y=100)  # Adjust x and y coordinates for the third video
        self.checkbox_var3 = tk.BooleanVar(value=ex_in_training_or_not(row_of_patient, "left_hand_up_and_bend_notool"))
        self.checkbox3 = ttk.Checkbutton(self, variable=self.checkbox_var3)
        self.checkbox3.place(x=605, y=430)

        self.label4 = tk.Label(self)
        self.label4.place(x=725, y=100)  # Adjust x and y coordinates for the third video
        self.checkbox_var4 = tk.BooleanVar(value=ex_in_training_or_not(row_of_patient, "raising_hands_diagonally_notool"))
        self.checkbox4 = ttk.Checkbutton(self, variable=self.checkbox_var4)
        self.checkbox4.place(x=805, y=430)


        # Video paths
        video_file1 = 'Videos//hands_behind_and_lean_notool_vid.mp4'
        video_path1 = os.path.join(os.getcwd(), video_file1)
        self.cap1 = cv2.VideoCapture(video_path1)

        video_file2 = 'Videos//right_hand_up_and_bend_notool_vid.mp4'
        video_path2 = os.path.join(os.getcwd(), video_file2)
        self.cap2 = cv2.VideoCapture(video_path2)

        video_file3 = 'Videos//left_hand_up_and_bend_notool_vid.mp4'
        video_path3 = os.path.join(os.getcwd(), video_file3)
        self.cap3 = cv2.VideoCapture(video_path3)

        video_file4 = 'Videos//raising_hands_diagonally_notool_vid.mp4'
        video_path4 = os.path.join(os.getcwd(), video_file4)
        self.cap4 = cv2.VideoCapture(video_path4)



        # Check if videos are opened successfully
        if not (
                self.cap1.isOpened() and self.cap2.isOpened() and self.cap3.isOpened() and self.cap4.isOpened()):
            print("Error opening video streams or files")
        else:
            # Play videos
            play_video(self.cap1, self.label1, "hands_behind_and_lean_notool", "no_tool")
            play_video(self.cap2, self.label2,"right_hand_up_and_bend_notool", "no_tool")
            play_video(self.cap3, self.label3,"left_hand_up_and_bend_notool", "no_tool")
            play_video(self.cap4, self.label4,"raising_hands_diagonally_notool", "no_tool")


    def on_end_click(self):
        self.save_changes()
        s.screen.switch_frame(PatientDisplaying)

    def on_arrow_click_back(self):
        self.save_changes()
        s.screen.switch_frame(ChooseStickExercisesPage)

    def to_patients_list_button_click(self):
        self.save_changes()
        s.screen.switch_frame(PatientDisplaying)


    def save_changes(self):
        new_values_ex_patient = {"hands_behind_and_lean_notool": bool(self.checkbox_var1.get()),
                                 "right_hand_up_and_bend_notool": bool(self.checkbox_var2.get()),
                                 "left_hand_up_and_bend_notool": bool(self.checkbox_var3.get()),
                                 "raising_hands_diagonally_notool": bool(self.checkbox_var4.get())}

        Excel.find_and_change_values_Patients(new_values_ex_patient)




class GraphPage(tk.Frame):
    def __init__(self, master, exercise, previous, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.queue = queue.Queue()
        self.exercise = exercise
        image = Image.open('Pictures//background.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()

        if previous=="ball":
            previous_page=ChooseBallExercisesPage
        elif previous=="band":
            previous_page=ChooseRubberBandExercisesPage
        elif previous=="stick":
            previous_page=ChooseStickExercisesPage
        elif previous=="no_tool":
            previous_page=ChooseNoToolExercisesPage

        previous_page_button_img = Image.open("Pictures//previous.jpg")
        previous_page_button_photo = ImageTk.PhotoImage(previous_page_button_img)
        previous_page_category = tk.Button(self, image=previous_page_button_photo,
                                          command=lambda: s.screen.switch_frame(previous_page),
                                          width=previous_page_button_img.width,
                                          height=previous_page_button_img.height, bd=0,
                                          highlightthickness=0)
        previous_page_category.image = previous_page_button_photo
        previous_page_category.place(x=30, y=30)





        success_flag = False

        back = Image.open('Pictures//empty.JPG')
        background_img = ImageTk.PhotoImage(back)


        try:
            df = pd.read_excel(s.excel_file_path_Patient, sheet_name=exercise)
            success_flag = True  # Set the flag to True if reading is successful

            if self.get_number_of_angles_in_exercise(exercise)==1:
                self.one_angle_graph(df)
            if self.get_number_of_angles_in_exercise(exercise)==2:
                self.two_angles_graph(df)
            if self.get_number_of_angles_in_exercise(exercise)==3:
                self.three_angles_graph(df)


            success_number= Excel.get_success_number(exercise)
            effort_number= Excel.get_effort_number(exercise)

            if success_number is not None:
                self.label = tk.Label(self, text=str(success_number)+ "מספר חזרות מוצלחות בביצוע האחרון: "[::-1] , image=background_img, compound=tk.CENTER, font=("Thaoma", 11, 'bold'), width=350, height=30)
                self.label.place(x=155, y=10)
                self.label.image = background_img

            if effort_number is not None:
                self.label = tk.Label(self, text=str(effort_number)+ "דירוג קושי התרגיל על ידי המתאמן בביצוע האחרון: "[::-1], image=background_img, compound=tk.CENTER, font=("Thaoma", 11, 'bold'), width=350, height=30)
                self.label.place(x=155, y=40)
                self.label.image = background_img


        except (pd.errors.ParserError, FileNotFoundError):
            # Handle the case where the sheet is not found
            pass  # Continue to the next iteration
        except ValueError as ve:
            # Handle other specific errors
            pass  # Continue to the next iteration

        # Check if any of the values were successful
        if success_flag:
            # Do something if at least one value was successful
            pass
        else:
            did_before = Image.open('Pictures//patient_didnt_do.jpg')
            self.did_before = ImageTk.PhotoImage(did_before)
            self.did_before_label = tk.Label(self, image=self.did_before, bd=0)
            self.did_before_label.place(x=270, y=75)


    def get_number_of_angles_in_exercise(self, exercise):
        try:
            # Load the workbook
            workbook = openpyxl.load_workbook("exercises_table.xlsx")

            # Select the desired sheet
            sheet = workbook[workbook.sheetnames[0]]

            # Iterate through rows starting from the specified row
            for row_number in range(1,sheet.max_row + 1):
                first_cell_value = sheet.cell(row=row_number, column=1).value

                if first_cell_value == exercise:
                    return sheet.cell(row=row_number, column=2).value


        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def three_angles_graph(self, df):
        first_graph_name = df.iloc[0, 0] + ", " + df.iloc[4, 0] + ", " + df.iloc[8, 0]
        y_values_1=df.iloc[72, :]
        y_values_1_float = y_values_1.astype(float)
        self.draw_graph(df.columns, y_values_1_float, first_graph_name, 20, 100, min(y_values_1_float), max(y_values_1_float), mean(y_values_1_float), stdev(y_values_1_float))

        second_graph_name = df.iloc[12, 0] + ", " + df.iloc[16, 0] + ", " + df.iloc[20, 0]
        y_values_2=df.iloc[73, :]
        y_values_2_float = y_values_2.astype(float)
        self.draw_graph(df.columns, y_values_2_float, second_graph_name, 20, 325, min(y_values_2_float), max(y_values_2_float), mean(y_values_2_float), stdev(y_values_2_float))

        second_graph_name = df.iloc[24, 0] + ", " + df.iloc[28, 0] + ", " + df.iloc[32, 0]
        y_values_3= df.iloc[74, :]
        y_values_3_float = y_values_3.astype(float)
        self.draw_graph(df.columns, y_values_3_float, second_graph_name, 350, 100, min(y_values_3_float), max(y_values_3_float), mean(y_values_3_float), stdev(y_values_3_float))

        second_graph_name = df.iloc[36, 0] + ", " + df.iloc[40, 0] + ", " + df.iloc[44, 0]
        y_values_4= df.iloc[75, :]
        y_values_4_float = y_values_4.astype(float)
        self.draw_graph(df.columns, y_values_4_float, second_graph_name, 350, 325, min(y_values_4_float), max(y_values_4_float), mean(y_values_4_float), stdev(y_values_4_float))

        second_graph_name = df.iloc[48, 0] + ", " + df.iloc[52, 0] + ", " + df.iloc[56, 0]
        y_values_5 = df.iloc[76, :]
        y_values_5_float = y_values_5.astype(float)
        self.draw_graph(df.columns, y_values_5_float, second_graph_name, 680, 100, min(y_values_5_float), max(y_values_5_float), mean(y_values_5_float), stdev(y_values_5_float))

        second_graph_name = df.iloc[60, 0] + ", " + df.iloc[64, 0] + ", " + df.iloc[68, 0]
        y_values_6 = df.iloc[77, :]
        y_values_6_float = y_values_6.astype(float)
        self.draw_graph(df.columns, y_values_6_float, second_graph_name, 680, 325, min(y_values_6_float), max(y_values_6_float), mean(y_values_6_float), stdev(y_values_6_float))


    def two_angles_graph(self, df):
        first_graph_name = df.iloc[0, 0] + ", " + df.iloc[4, 0] + ", " + df.iloc[8, 0]
        y_values_1=df.iloc[48, :]
        y_values_1_float = y_values_1.astype(float)
        self.draw_graph(df.columns, y_values_1_float, first_graph_name, 190, 100, min(y_values_1_float), max(y_values_1_float), mean(y_values_1_float), stdev(y_values_1_float))

        second_graph_name = df.iloc[12, 0] + ", " + df.iloc[16, 0] + ", " + df.iloc[20, 0]
        y_values_2=df.iloc[49, :]
        y_values_2_float = y_values_2.astype(float)
        self.draw_graph(df.columns, y_values_2_float, second_graph_name, 190, 325, min(y_values_2_float), max(y_values_2_float), mean(y_values_2_float), stdev(y_values_2_float))

        second_graph_name = df.iloc[24, 0] + ", " + df.iloc[28, 0] + ", " + df.iloc[32, 0]
        y_values_3= df.iloc[50, :]
        y_values_3_float = y_values_3.astype(float)
        self.draw_graph(df.columns, y_values_3_float, second_graph_name, 540, 100, min(y_values_3_float), max(y_values_3_float), mean(y_values_3_float), stdev(y_values_3_float))

        second_graph_name = df.iloc[36, 0] + ", " + df.iloc[40, 0] + ", " + df.iloc[44, 0]
        y_values_4= df.iloc[51, :]
        y_values_4_float = y_values_4.astype(float)
        self.draw_graph(df.columns, y_values_4_float, second_graph_name, 540, 325, min(y_values_4_float), max(y_values_4_float), mean(y_values_4_float), stdev(y_values_4_float))


    def one_angle_graph(self, df):
        first_graph_name = df.iloc[0, 0] + ", " + df.iloc[4, 0] + ", " + df.iloc[8, 0]
        y_values_1 = df.iloc[24, :]
        y_values_1_float = y_values_1.astype(float)
        self.draw_graph(df.columns, y_values_1_float, first_graph_name, 350, 100, min(y_values_1_float), max(y_values_1_float), mean(y_values_1_float), stdev(y_values_1_float))

        second_graph_name = df.iloc[12, 0] + ", " + df.iloc[16, 0] + ", " + df.iloc[20, 0]
        y_values_2 = df.iloc[25, :]
        y_values_2_float = y_values_2.astype(float)
        self.draw_graph(df.columns, y_values_2_float, second_graph_name, 350, 325, min(y_values_2_float), max(y_values_2_float),mean(y_values_2_float), stdev(y_values_2_float))




############################################### Exercises Pages ########################################################
class DemoPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//demo.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()
        say('robot_demo')


class ExercisePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//exercise.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        say("start_ex")



########################################### Encouragemennts Pages ######################################################

class Very_good(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//verygood.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()
        say('very_good')

class Excellent(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//excellent.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()
        say('excellent')

class Well_done(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//welldone.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()
        say('well_done')


class AlmostExcellent(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//almostexcellent.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()
        say('almostexcellent')


class Fail(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//fail.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()
        say('fail')


################################################# Categories Screens ##############################################
class StartingOfTraining(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//hello.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        say("welcome")

class Ball(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//ball.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        say("Ball")
        self.after(6000,lambda: master.wait_until_waving())


class Stick(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//stick.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        say("Stick")
        self.after(9000,lambda: master.wait_until_waving())


class Rubber_Band(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//rubber_band.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        say("Band")
        self.after(9000,lambda: master.wait_until_waving())


class NoTool(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//background.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        say("NoTool")
        self.after(9000,lambda: master.wait_until_waving())


######################################### Counting Pages #############################################################
class OnePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//1.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()


class TwoPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//2.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()


class ThreePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//3.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()


class FourPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//4.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()


class FivePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//5.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()


class SixPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//6.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()


class SevenPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//7.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()


class EightPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//8.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()


class NinePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//9.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()


class TenPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//10.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()


######################################################## Goodbbye Page #################################################
class GoodbyePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//goodbye.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()


######################################################## Effort scale Page #################################################
class EffortScale(tk.Frame):
    def __init__(self, master, exercises, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        if not exercises:
            s.finished_effort= True

        else:
            self.exercises= exercises
            image = Image.open('Pictures//background.jpg')
            self.photo_image = ImageTk.PhotoImage(image)
            self.background_label = tk.Label(self, image=self.photo_image)
            self.background_label.pack()
            self.chosen_effort= -1

            self.label = tk.Label(self)
            self.label.place(x=700, y=200)  # Adjust x and y coordinates for the fifth video
            # Video paths
            video_file = 'Videos//'+ exercises[0]+ '_vid.mp4'
            video_path = os.path.join(os.getcwd(), video_file)
            self.cap = cv2.VideoCapture(video_path)

            if not (self.cap.isOpened()):
                print("Error opening video streams or files")

                # Play videos
            play_video(self.cap, self.label, exercises[0], None)


            ## buttons to press for scale
            image0 = Image.open('Pictures//scale_0.jpg')
            resized_image0 = image0.resize((350, 40), Image.LANCZOS)
            self.photo_image0 = ImageTk.PhotoImage(resized_image0)
            button0= tk.Button(self,image=self.photo_image0, command=self.on_click_0)
            button0.place(height=40, width=350, x=100, y=100)

            image1 = Image.open('Pictures//scale_1.jpg')
            resized_image1 = image1.resize((350, 40), Image.LANCZOS)
            self.photo_image1 = ImageTk.PhotoImage(resized_image1)
            button1= tk.Button(self,image=self.photo_image1, command=self.on_click_1)
            button1.place(height=40, width=350, x=100, y=140)

            image2 = Image.open('Pictures//scale_2.jpg')
            resized_image2= image2.resize((350, 40), Image.LANCZOS)
            self.photo_image2 = ImageTk.PhotoImage(resized_image2)
            button2 = tk.Button(self, image=self.photo_image2, command=self.on_click_2)
            button2.place(height=40, width=350, x=100, y=180)

            image3 = Image.open('Pictures//scale_3.jpg')
            resized_image3 = image3.resize((350, 40), Image.LANCZOS)
            self.photo_image3 = ImageTk.PhotoImage(resized_image3)
            button3 = tk.Button(self, image=self.photo_image3, command=self.on_click_3)
            button3.place(height=40, width=350, x=100, y=220)

            image4 = Image.open('Pictures//scale_4.jpg')
            resized_image4 = image4.resize((350, 40), Image.LANCZOS)
            self.photo_image4 = ImageTk.PhotoImage(resized_image4)
            button4 = tk.Button(self, image=self.photo_image4, command=self.on_click_4)
            button4.place(height=40, width=350, x=100, y=260)

            image5 = Image.open('Pictures//scale_5.jpg')
            resized_image5 = image5.resize((350, 40), Image.LANCZOS)
            self.photo_image5 = ImageTk.PhotoImage(resized_image5)
            button5 = tk.Button(self, image=self.photo_image5, command=self.on_click_5)
            button5.place(height=40, width=350, x=100, y=300)

            image6 = Image.open('Pictures//scale_6.jpg')
            resized_image6 = image6.resize((350, 40), Image.LANCZOS)
            self.photo_image6 = ImageTk.PhotoImage(resized_image6)
            button6 = tk.Button(self, image=self.photo_image6, command=self.on_click_6)
            button6.place(height=40, width=350, x=100, y=340)

            image7 = Image.open('Pictures//scale_7.jpg')
            resized_image7 = image7.resize((350, 40), Image.LANCZOS)
            self.photo_image7 = ImageTk.PhotoImage(resized_image7)
            button7 = tk.Button(self, image=self.photo_image7, command=self.on_click_7)
            button7.place(height=40, width=350, x=100, y=380)

            image8 = Image.open('Pictures//scale_8.jpg')
            resized_image8 = image8.resize((350, 40), Image.LANCZOS)
            self.photo_image8 = ImageTk.PhotoImage(resized_image8)
            button8 = tk.Button(self, image=self.photo_image8, command=self.on_click_8)
            button8.place(height=40, width=350, x=100, y=420)

            image9 = Image.open('Pictures//scale_9.jpg')
            resized_image9 = image9.resize((350, 40), Image.LANCZOS)
            self.photo_image9 = ImageTk.PhotoImage(resized_image9)
            button9 = tk.Button(self, image=self.photo_image9, command=self.on_click_9)
            button9.place(height=40, width=350, x=100, y=460)

            image10 = Image.open('Pictures//scale_10.jpg')
            resized_image10 = image10.resize((350, 40), Image.LANCZOS)
            self.photo_image10 = ImageTk.PhotoImage(resized_image10)
            button10 = tk.Button(self, image=self.photo_image10, command=self.on_click_10)
            button10.place(height=40, width=350, x=100, y=500)


    def on_click_0(self):
        s.list_effort_each_exercise.update({self.exercises[0]: 0})
        exercises= self.exercises[1:]
        s.screen.switch_frame(EffortScale, exercises=exercises)

    def on_click_1(self):
        s.list_effort_each_exercise.update({self.exercises[0]: 1})
        exercises = self.exercises[1:]
        s.screen.switch_frame(EffortScale, exercises=exercises)

    def on_click_2(self):
        s.list_effort_each_exercise.update({self.exercises[0]: 2})
        exercises = self.exercises[1:]
        s.screen.switch_frame(EffortScale, exercises=exercises)

    def on_click_3(self):
        s.list_effort_each_exercise.update({self.exercises[0]: 3})
        exercises = self.exercises[1:]
        s.screen.switch_frame(EffortScale, exercises=exercises)

    def on_click_4(self):
        s.list_effort_each_exercise.update({self.exercises[0]: 4})
        exercises = self.exercises[1:]
        s.screen.switch_frame(EffortScale, exercises=exercises)

    def on_click_5(self):
        s.list_effort_each_exercise.update({self.exercises[0]: 5})
        exercises = self.exercises[1:]
        s.screen.switch_frame(EffortScale, exercises=exercises)

    def on_click_6(self):
        s.list_effort_each_exercise.update({self.exercises[0]: 6})
        exercises = self.exercises[1:]
        s.screen.switch_frame(EffortScale, exercises=exercises)

    def on_click_7(self):
        s.list_effort_each_exercise.update({self.exercises[0]: 7})
        exercises = self.exercises[1:]
        s.screen.switch_frame(EffortScale, exercises=exercises)

    def on_click_8(self):
        s.list_effort_each_exercise.update({self.exercises[0]: 8})
        exercises = self.exercises[1:]
        s.screen.switch_frame(EffortScale, exercises=exercises)

    def on_click_9(self):
        s.list_effort_each_exercise.update({self.exercises[0]: 9})
        exercises = self.exercises[1:]
        s.screen.switch_frame(EffortScale, exercises=exercises)

    def on_click_10(self):
        s.list_effort_each_exercise.update({self.exercises[0]: 10})
        exercises = self.exercises[1:]
        s.screen.switch_frame(EffortScale, exercises=exercises)


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
    s.finished_effort= False
    s.ex_in_training=["bend_elbows_ball", "arms_up_and_down_stick"]
    s.list_effort_each_exercise= {}
    s.chosen_patient_ID= '314808981'
    s.screen.switch_frame(ChooseStickExercisesPage)
    #s.screen.switch_frame(EffortScale,exercises= s.ex_in_training)
    app = FullScreenApp(s.screen)
    s.screen.mainloop()