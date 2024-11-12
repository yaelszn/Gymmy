# -*- coding: utf-8 -*-
import queue
import time
import tkinter as tk
from datetime import datetime
from statistics import mean, stdev
from tkinter import ttk
import random
from datetime import datetime

import numpy as np
import openpyxl
import matplotlib
from matplotlib import pyplot as plt

matplotlib.use('TkAgg')  # Use the TkAgg backend
import cv2
import pandas as pd
import pygame
from PIL import Image, ImageTk
from email_validator import validate_email, EmailNotValidError
import Settings as s
from Audio import say, get_wav_duration
from gtts import gTTS
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import Excel
import re



class Screen(tk.Tk):
    def __init__(self):
        print("screen start")
        tk.Tk.__init__(self, className='Gymmy')
        self._frame = None
        self["bg"]="#F3FCFB"
        #self.after(1000, lambda: self.pause_execution())

    def pause_execution(self):
        # Create a dummy function that does nothing
        pass

    def switch_frame(self, frame_class, **kwargs):
        """Destroys all existing frames and creates a new one safely from any thread."""

        def switch():
            # Destroy all existing frames
            for widget in self.winfo_children():
                widget.destroy()

            # Create a new frame
            new_frame = frame_class(self, **kwargs)
            self._frame = new_frame
            self._frame.pack()

        # Use after() to ensure it runs in the main thread
        self.after(0, switch)

    def quit(self):
        self.destroy()



class EntrancePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        image = Image.open('Pictures//background.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()


        # Set initial value
        s.chosen_patient_ID = None

        # Load images for buttons
        therapist_image = Image.open("Pictures//therapist_entrance_button.jpg")
        therapist_photo = ImageTk.PhotoImage(therapist_image)
        patient_image = Image.open("Pictures//patient_entrance_button.jpg")
        patient_photo = ImageTk.PhotoImage(patient_image)

        # Store references to prevent garbage collection
        self.therapist_photo = therapist_photo
        self.patient_photo = patient_photo

        # Create buttons with images
        enter_as_therapist_button = tk.Button(self, image=therapist_photo,
                                              command=self.on_click_therapist_chosen,
                                              width=therapist_image.width, height=therapist_image.height,
                                              bg='#50a6ad', bd=0, highlightthickness=0)
        enter_as_therapist_button.place(x=160, y=130)

        enter_as_patient_button = tk.Button(self, image=patient_photo,
                                            command=self.on_click_patient_chosen,
                                            width=patient_image.width, height=patient_image.height,
                                            bg='#50a6ad', bd=0, highlightthickness=0)
        enter_as_patient_button.place(x=540, y=130)

        shut_down_button_img = Image.open("Pictures//shut_down.jpg")  # Change path to your image file
        shut_down_button_photo = ImageTk.PhotoImage(shut_down_button_img)

        shut_down_button = tk.Button(self, image=shut_down_button_photo, command=lambda: self.on_click_shut_down(),
                                              width=shut_down_button_img.width, height=shut_down_button_img.height, bd=0, highlightthickness=0)  # Set border width to 0 to remove button border
        shut_down_button.image = shut_down_button_photo  # Store reference to image to prevent garbage collection
        shut_down_button.place(x=30, y=30)

        s.ex_in_training = []

    def on_click_shut_down(self):
        s.finish_program = True  # Signal all threads to stop
        s.req_exercise=""
        s.camera.join()
        s.training.join()
        s.robot.join()
        print("All threads have stopped.")
        self.quit()
    def on_click_therapist_chosen(self):
        s.screen.switch_frame(ID_therapist_fill_page)

    def on_click_patient_chosen(self):
        s.screen.switch_frame(ID_patient_fill_page)

#enterence page of patient
class ID_patient_fill_page(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//IDFillPage.jpg')
        self.photo_image = ImageTk.PhotoImage(image)  # self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image=self.photo_image).pack()
        self.user_id_entry_patient = tk.Entry(self, font=('Thaoma', 14), width=20)
        self.user_id_entry_patient.place(x=400, y=260)
        self.labels = []

        to_previous_button_img = Image.open("Pictures//previous.jpg")
        to_previous_button_photo = ImageTk.PhotoImage(to_previous_button_img)
        to_previous_button = tk.Button(self, image=to_previous_button_photo, command=lambda: self.to_previous_button_click(),
                                   width=to_previous_button_img.width, height=to_previous_button_img.height, bd=0,
                                   highlightthickness=0)  # Set border width to 0 to remove button border
        to_previous_button.image = to_previous_button_photo  # Store reference to image to prevent garbage collection
        to_previous_button.place(x=30, y=30)

        # Load image for the submit button
        submit_image = Image.open("Pictures//enter.jpg")
        submit_photo = ImageTk.PhotoImage(submit_image)

        # Create button with image
        submit_button = tk.Button(self, image=submit_photo,
                                  command=lambda: self.on_submit_patient(),
                                  width=submit_image.width, height=submit_image.height,
                                  bg='#50a6ad', bd=0, highlightthickness=0)  # Set highlightthickness to 0
        submit_button.image = submit_photo  # Store reference to image to prevent garbage collection
        submit_button.place(x=460, y=300)  # Adjust x and y coordinates as needed


    def to_previous_button_click(self):
        s.screen.switch_frame(EntrancePage)

    def on_submit_patient(self):
        self.delete_all_labels()
        user_id = self.user_id_entry_patient.get()
        print(f"User ID entered: {user_id}")
        # Add your logic here to handle the user ID, e.g., store it in a variable or perform an action.

        if user_id != "":
            excel_file_path = "Patients.xlsx"
            df = pd.read_excel(excel_file_path, sheet_name="patients_details")

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
                self.label.place(x=320, y=360)
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
                    patient_workbook_path= "Patients.xlsx"
                    s.chosen_patient_ID=user_id
                    s.email_of_patient= Excel.find_value_by_colName_and_userID(patient_workbook_path, "patients_details", user_id, "email")
                    s.current_level_of_patient= Excel.find_value_by_colName_and_userID(patient_workbook_path, "patients_details", user_id, "level")
                    s.points_in_current_level_before_training= Excel.find_value_by_colName_and_userID(patient_workbook_path, "patients_details", user_id, "points in current level")
                    s.rep= int(Excel.find_value_by_colName_and_userID(patient_workbook_path, "patients_details", user_id, "number of repetitions in each exercise"))
                    gender = Excel.find_value_by_colName_and_userID(patient_workbook_path, "patients_details", user_id, "gender")
                    s.full_name = Excel.find_value_by_colName_and_userID(patient_workbook_path, "patients_details", user_id, "first name") + " " + Excel.find_value_by_colName_and_userID(patient_workbook_path, "patients_details", user_id, "last name")
                    s.audio_path = 'audio files/Hebrew/' + gender + '/'

                    df1 = pd.read_excel(excel_file_path, sheet_name="patients_exercises")

                    # Convert the first column to string for comparison
                    df1.iloc[:, 0] = df1.iloc[:, 0].astype(str)


                    # Filter rows based on the condition
                    row_of_patient = df1[df1.iloc[:, 0] == user_id_cleaned]


                    s.ex_in_training=[]
                    num_columns1= df1.shape[1]


                    for i in range (0,num_columns1): #including 0
                        if row_of_patient.iloc[0,i]==True:
                            s.ex_in_training.append(df1.columns[i])

                    print(s.ex_in_training)
                    s.screen.switch_frame(StartOfTraining)


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

#enterence page of therapist
class ID_therapist_fill_page(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//IDFillPage.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        self.user_id_entry_physio= tk.Entry(self, font=('Thaoma', 14), width=20)
        self.user_id_entry_physio.place(x=400, y=260)
        self.labels=[]


        to_previous_button_img = Image.open("Pictures//previous.jpg")
        to_previous_button_photo = ImageTk.PhotoImage(to_previous_button_img)
        to_previous_button = tk.Button(self, image=to_previous_button_photo, command=lambda: self.to_previous_button_click(),
                                   width=to_previous_button_img.width, height=to_previous_button_img.height, bd=0,
                                   highlightthickness=0)  # Set border width to 0 to remove button border
        to_previous_button.image = to_previous_button_photo  # Store reference to image to prevent garbage collection
        to_previous_button.place(x=30, y=30)

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

    def to_previous_button_click(self):
        s.screen.switch_frame(EntrancePage)

    def on_submit_physio(self):
        self.delete_all_labels()
        user_id = self.user_id_entry_physio.get()
        print(f"User ID entered: {user_id}")
        # Add your logic here to handle the user ID, e.g., store it in a variable or perform an action.

        if user_id != "":
            excel_file_path = "Physiotherapists.xlsx"
            df = pd.read_excel(excel_file_path, sheet_name="details")

            # Convert the first column to string for comparison
            df['ID_str'] = df.iloc[:, 0].astype(str).str.strip()

            # Convert the user_id to string and remove leading/trailing spaces for comparison
            user_id_cleaned = str(user_id).strip()

            # Filter rows based on the condition
            row_of_patient = df[df['ID_str'] == user_id_cleaned]

            if row_of_patient.empty:
                back = Image.open('Pictures//id_not_in_system.jpg')
                background_img = ImageTk.PhotoImage(back)

                self.label = tk.Label(self, image=background_img, compound=tk.CENTER, highlightthickness=0)
                self.label.place(x=250, y=360)
                self.label.image = background_img
                self.labels.append(self.label)



            else:
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
        df = pd.read_excel(excel_file_path, sheet_name="details")
        ID_entered=self.id_entry.get()
        is_in_ID = ID_entered in df['ID'].astype(str).values #chaeck if the ID that the user inserted is already in system



        if ID_entered=="":
            back = Image.open('Pictures//no_id.jpg')
            no_id_label = ImageTk.PhotoImage(back)
            self.label = tk.Label(self, image=no_id_label, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=185, y=425)
            self.label.image = no_id_label
            self.labels.append(self.label)

        elif is_in_ID is True:
            back = Image.open('Pictures//id_already_in_system.jpg')
            id_already_in_system = ImageTk.PhotoImage(back)
            self.label = tk.Label(self, image=id_already_in_system, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=80, y=425)
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

        self.email_entry = tk.Entry(self, font=('Thaoma', 14), width=20, justify='right')
        self.email_entry.place(x=370, y=425)

        add_patient_button_img = Image.open("Pictures//add.jpg")  # Change path to your image file
        add_patient_button_photo = ImageTk.PhotoImage(add_patient_button_img)

        add_patient_button = tk.Button(self, image=add_patient_button_photo,
                                      command=lambda: self.on_click_patient_registration(),
                                      width=add_patient_button_img.width, height=add_patient_button_img.height, bd=0,
                                      highlightthickness=0)  # Set border width to 0 to remove button border
        add_patient_button.image = add_patient_button_photo  # Store reference to image to prevent garbage collection
        add_patient_button.place(x=425, y=480)
        self.labels = []  # collect the labels that apear so that on a click on the button i can delete them

    def on_select_gender(self, option):
        if option=='אישה':
            self.gender='Female'

        else:
            self.gender='Male'

    def is_email_valid (self, email):
        try:
            # Validate the email address
            validate_email(email)
            # If no exception is raised, the email is valid
            return True
        except EmailNotValidError:
            # If an exception is raised, the email is not valid
            #print(str(e))
            return False

    def on_click_patient_registration(self):
        self.delete_all_labels()

        excel_file_path = "Patients.xlsx"
        workbook=openpyxl.load_workbook(excel_file_path)
        df = pd.read_excel(excel_file_path, sheet_name="patients_details")
        ID_entered=self.id_entry.get()
        is_in_ID = ID_entered in df['ID'].astype(str).values #chaeck if the ID that the user inserted is already in system



        if ID_entered=="":
            back = Image.open('Pictures//no_id.jpg')
            background_img = ImageTk.PhotoImage(back)

            self.label = tk.Label(self, image=background_img, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=185, y=490)
            self.label.image = background_img
            self.labels.append(self.label)


        elif is_in_ID is True:
            error = Image.open('Pictures//id_already_in_system.jpg')
            id_already_in_system = ImageTk.PhotoImage(error)
            self.label = tk.Label(self, image=id_already_in_system, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=80, y=490)
            self.label.image = id_already_in_system
            self.labels.append(self.label)


        elif self.is_email_valid(self.email_entry.get()) is False: #if email is not valid
            error = Image.open('Pictures//not_valid_email.jpg')
            id_already_in_system = ImageTk.PhotoImage(error)
            self.label = tk.Label(self, image=id_already_in_system, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=230, y=490)
            self.label.image = id_already_in_system
            self.labels.append(self.label)


        else:
            s.chosen_patient_ID=ID_entered
            #modifying the columns that has other value than false
            new_row_data_details={
                'ID': str(ID_entered),
                'first name': str(self.first_name_entry.get()),
                'last name': str(self.last_name_entry.get()),
                'gender': self.gender,
                'number of exercises': 0,
                'email': str(self.email_entry.get()),
                'points in current level': 0,
                'level': 1
            }

            sheet1=workbook["patients_details"]
            columns = list(new_row_data_details.keys())
            sheet1.append([new_row_data_details[column] for column in columns])
            #workbook.save("Patients.xlsx")

            #insert a row to the excel of history of training
            new_row_hystory_of_training = {'ID': ID_entered}
            sheet2 = workbook["patients_history_of_trainings"]
            columns = list(new_row_hystory_of_training.keys())
            sheet2.append([new_row_hystory_of_training[column] for column in columns])
            #workbook.save("Patients.xlsx")

            #insert a row to the excel of exercises
            df2 = pd.read_excel(excel_file_path, sheet_name="patients_exercises")
            sheet3 = workbook["patients_exercises"]
            new_row_data_exercises = {column: False for column in df2.columns}
            new_row_data_exercises.update({'ID': ID_entered})

            columns = list(new_row_data_exercises.keys())
            sheet3.append([new_row_data_exercises[column] for column in columns])
            workbook.save("Patients.xlsx")

            self.create_folders_when_insert_patient()

            back = Image.open('Pictures//successfully_added_patient.jpg')
            successfully_added_patient = ImageTk.PhotoImage(back)
            self.label = tk.Label(self, image=successfully_added_patient, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=170, y=490)
            self.label.image = successfully_added_patient
            self.first_name_entry.delete(0, tk.END)
            self.last_name_entry.delete(0, tk.END)
            self.id_entry.delete(0, tk.END)
            self.selected_option.set(self.options[0])
            self.email_entry.delete(0, tk.END)
            self.gender='Male'
            self.labels.append(self.label)


    def create_folders_when_insert_patient(self):
        Excel.create_and_open_folder(f"Patients/{s.chosen_patient_ID}")  # open folder for patient
        Excel.create_and_open_folder(f"Patients/{s.chosen_patient_ID}/Graphs")  # open graphs folder
        Excel.create_and_open_folder(f"Patients/{s.chosen_patient_ID}/Tables")  # open graphs folder

        df = pd.read_excel("Patients.xlsx", sheet_name="patients_exercises", header=None)

        # Assuming the headers are in the first row of the DataFrame
        headers = df.iloc[0]  # Extract headers from the first row

        # Exclude a specific header
        header_to_exclude = 'ID'
        selected_headers = [header for header in headers if header != header_to_exclude]

        # Iterate over each selected header
        for header in selected_headers:
            #create a file for each execise
            Excel.create_and_open_folder(f"Patients/{s.chosen_patient_ID}/Graphs/{header}")  # open graphs folder

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
        df = pd.read_excel(excel_file_path, sheet_name="patients_details" ,usecols=['ID', 'first name', 'last name'])
        new_headers = {'ID': 'תעודת זהות', 'first name': 'שם פרטי', 'last name': 'שם משפחה'}
        df.rename(columns=new_headers, inplace=True)
        s.chosen_patient_ID=None
        s.excel_file_path_Patient=None

        for col in df.columns[1:3]:
            df[col] = df[col].apply(lambda x: x)

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
            #s.screen.switch_frame(ChooseBallExercisesPage)
            s.screen.switch_frame(ChooseTrainingOrExerciseInformation)


def play_video(cap, label, exercise, previous, scale_factor=0.35, slow_factor=1.2):

    if previous is not None:
        def on_click(event):
            # Call the Graph function with the exercise name
            s.screen.switch_frame(TablesPage, exercise=exercise, previous=previous)
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

def get_row_of_exercises_patient():
    excel_file_path = "Patients.xlsx"
    df = pd.read_excel(excel_file_path, sheet_name="patients_exercises")

    print("Current dtype:", df.iloc[:, 0].dtype)
    # Convert the first column to string for comparison
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)

    # Convert the user_id to string and remove leading/trailing spaces for comparison
    user_id_cleaned = str(s.chosen_patient_ID).strip()

    # Filter rows based on the condition
    row_of_patient = df[df.iloc[:, 0] == user_id_cleaned]

    return row_of_patient

def which_image_to_put (row_of_patient, ex):

    if ex_in_training_or_not(row_of_patient, ex)==True:
        return "vi"
    else:
        return "empty"

    # A function that check which image to put as a checkbox on each checkbox click


def which_checkbox(button1, ex):
    row_of_patient = get_row_of_exercises_patient()

    # Retrieve the current checkbox value
    current_value = ex_in_training_or_not(row_of_patient, ex)

    # Toggle the value in the underlying data
    new_value_ex_patient = {ex: (not current_value)}
    Excel.find_and_change_values_exercises(new_value_ex_patient)

    # Retrieve the new current value after the update to ensure it has been toggled
    updated_value = not current_value

    # Choose the new image based on the updated value
    if updated_value:
        image1 = Image.open('Pictures//vi.png')  # True = checked (vi)
    else:
        image1 = Image.open('Pictures//empty.png')  # False = empty

    # Convert to PhotoImage
    button1_photo = ImageTk.PhotoImage(image1)

    # Update the button's image
    button1.config(image=button1_photo)

    # Store a reference to prevent garbage collection
    button1.image = button1_photo  # Keep a reference to the image


class ChooseBallExercisesPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        # Load background image
        background_image = Image.open('Pictures//background.jpg')
        self.background_photo = ImageTk.PhotoImage(background_image)
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.pack()

        name_label(self)
        how_many_repetitions_of_exercises(self)

        forward_arrow_button_img = Image.open("Pictures//forward_arrow.jpg")
        forward_arrow_button_photo = ImageTk.PhotoImage(forward_arrow_button_img)
        forward_arrow_button = tk.Button(self, image=forward_arrow_button_photo, command=lambda: self.on_arrow_click(),
                                width=forward_arrow_button_img.width, height=forward_arrow_button_img.height, bd=0,
                                highlightthickness=0)
        forward_arrow_button.image = forward_arrow_button_photo
        forward_arrow_button.place(x=50, y=480)


        to_patients_list_button_img = Image.open("Pictures//previous.jpg")
        to_patients_list_button_photo = ImageTk.PhotoImage(to_patients_list_button_img)
        to_patients_list_button = tk.Button(self, image=to_patients_list_button_photo, command=lambda: self.to_previous_button_click(),
                                   width=to_patients_list_button_img.width, height=to_patients_list_button_img.height, bd=0,
                                   highlightthickness=0)  # Set border width to 0 to remove button border
        to_patients_list_button.image = to_patients_list_button_photo  # Store reference to image to prevent garbage collection
        to_patients_list_button.place(x=30, y=30)

        row_of_patient = get_row_of_exercises_patient()

        count=1
        self.background_color = "#deeaf7"  # Set the background color to light blue

        ex_1_name="ball_bend_elbows"
        ex_2_name= "ball_raise_arms_above_head"
        ex_3_name= "ball_switch"
        ex_4_name= "ball_open_arms_and_forward"
        ex_5_name= "ball_open_arms_above_head"
        formatted_ex_1_name = ex_1_name.replace('_', ' ')
        formatted_ex_2_name = ex_2_name.replace('_', ' ')
        formatted_ex_3_name = ex_3_name.replace('_', ' ')
        formatted_ex_4_name = ex_4_name.replace('_', ' ')
        formatted_ex_5_name = ex_5_name.replace('_', ' ')


        # Create labels for videos
        self.label1 = tk.Label(self)
        self.label1.place(x=30, y=125)  # Adjust x and y coordinates for the first video

        button1_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_1_name)}.png')
        button1_photo = ImageTk.PhotoImage(button1_image)
        button1 = tk.Button(self, image=button1_photo, command=lambda: which_checkbox(button1, ex_1_name),
                            width=button1_photo.width(), height=button1_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button1.image = button1_photo  # Store reference to image to prevent garbage collection
        button1.place(x=95, y=440)
        self.label_text1 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_1_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text1.place(x=25, y=85)
        count += 1


        self.label2 = tk.Label(self)
        self.label2.place(x=230, y=125)  # Adjust x and y coordinates for the second video

        button2_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_2_name)}.png')
        button2_photo = ImageTk.PhotoImage(button2_image)
        button2 = tk.Button(self, image=button2_photo, command=lambda: which_checkbox(button2, ex_2_name),
                            width=button2_photo.width(), height=button2_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button2.image = button2_photo  # Store reference to image to prevent garbage collection
        button2.place(x=295, y=440)
        self.label_text2 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_2_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text2.place(x=225, y=85)
        count += 1


        self.label3 = tk.Label(self)
        self.label3.place(x=430, y=125)  # Adjust x and y coordinates for the third video
        button3_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_3_name)}.png')
        button3_photo = ImageTk.PhotoImage(button3_image)
        button3 = tk.Button(self, image=button3_photo, command=lambda: which_checkbox(button3, ex_3_name),
                            width=button3_photo.width(), height=button3_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button3.image = button3_photo  # Store reference to image to prevent garbage collection
        button3.place(x=495, y=440)
        self.label_text3 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_3_name}', font=("Thaoma", 9, 'bold'),
                                    bg=self.background_color,
                                    justify='center', width=25, wraplength=170, anchor='center')
        self.label_text3.place(x=425, y=85)
        count += 1


        self.label4 = tk.Label(self)
        self.label4.place(x=630, y=125)  # Adjust x and y coordinates for the fourth video
        button4_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_4_name)}.png')
        button4_photo = ImageTk.PhotoImage(button4_image)
        button4 = tk.Button(self, image=button4_photo,  command=lambda: which_checkbox(button4, ex_4_name),
                            width=button4_photo.width(), height=button4_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button4.image = button4_photo  # Store reference to image to prevent garbage collection
        button4.place(x=695, y=440)
        self.label_text4 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_4_name}', font=("Thaoma", 9, 'bold'),
                                    bg=self.background_color,
                                    justify='center', width=25, wraplength=170, anchor='center')
        self.label_text4.place(x=625, y=85)
        count += 1


        self.label5 = tk.Label(self)
        self.label5.place(x=830, y=125)  # Adjust x and y coordinates for the fifth video
        button5_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_5_name)}.png')
        button5_photo = ImageTk.PhotoImage(button5_image)
        button5 = tk.Button(self, image=button5_photo,  command=lambda: which_checkbox(button5, ex_5_name),
                            width=button5_photo.width(), height=button5_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button5.image = button5_photo  # Store reference to image to prevent garbage collection
        button5.place(x=895, y=440)
        self.label_text5 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_5_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text5.place(x=825, y=85)
        count += 1


        # Video paths
        video_file1 = f'Videos//{ex_1_name}_vid.mp4'
        video_path1 = os.path.join(os.getcwd(), video_file1)
        self.cap1 = cv2.VideoCapture(video_path1)

        video_file2 = f'Videos//{ex_2_name}_vid.mp4'
        video_path2 = os.path.join(os.getcwd(), video_file2)
        self.cap2 = cv2.VideoCapture(video_path2)

        video_file3 = f'Videos//{ex_3_name}_vid.mp4'
        video_path3 = os.path.join(os.getcwd(), video_file3)
        self.cap3 = cv2.VideoCapture(video_path3)

        video_file4 = f'Videos//{ex_4_name}_vid.mp4'
        video_path4 = os.path.join(os.getcwd(), video_file4)
        self.cap4 = cv2.VideoCapture(video_path4)

        video_file5 = f'Videos//{ex_5_name}_vid.mp4'
        video_path5 = os.path.join(os.getcwd(), video_file5)
        self.cap5 = cv2.VideoCapture(video_path5)


        # Check if videos are opened successfully
        if not (self.cap1.isOpened() and self.cap2.isOpened() and self.cap3.isOpened() and self.cap4.isOpened() and self.cap5.isOpened()):
            print("Error opening video streams or files")

        else:
            # Play videos
            play_video(self.cap1, self.label1,ex_1_name, "ball")
            play_video(self.cap2, self.label2, ex_2_name, "ball")  # Change "Page2" to the name of the page you want to switch to
            play_video(self.cap3, self.label3, ex_3_name, "ball")  # Change "Page3" to the name of the page you want to switch to
            play_video(self.cap4, self.label4, ex_4_name, "ball")  # Change "Page4" to the name of the page you want to switch to
            play_video(self.cap5, self.label5, ex_5_name, "ball")  # Change "Page5" to the name of the page you want to switch to




    def on_arrow_click(self):
        Excel.find_and_change_values_patients({"number of repetitions in each exercise": self.selected_option_rep.get(), "rate": self.selected_option_rate.get()})

        s.screen.switch_frame(ChooseRubberBandExercisesPage)

    def to_previous_button_click(self):
        num_of_exercises_in_training=Excel.count_number_of_exercises_in_training_by_ID()
        if num_of_exercises_in_training<5:
            back = Image.open('Pictures//not_enough_exercises_chosen.jpg')
            background_img = ImageTk.PhotoImage(back)

            self.label = tk.Label(self, image=background_img, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=170, y=20)
            self.label.image = background_img

        else:
            Excel.find_and_change_values_patients({"number of exercises": num_of_exercises_in_training, "number of repetitions in each exercise": self.selected_option.get(), "rate": self.selected_option_rate.get()})
            s.screen.switch_frame(ChooseTrainingOrExerciseInformation)




class ChooseRubberBandExercisesPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # Load background image
        background_image = Image.open('Pictures//background.jpg')
        self.background_photo = ImageTk.PhotoImage(background_image)
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.pack()

        add_to_exercise_page(self)


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

        to_patients_list_button_img = Image.open("Pictures//previous.jpg")
        to_patients_list_button_photo = ImageTk.PhotoImage(to_patients_list_button_img)
        to_patients_list_button = tk.Button(self, image=to_patients_list_button_photo,
                                   command=lambda: self.to_previous_button_click(),
                                   width=to_patients_list_button_img.width, height=to_patients_list_button_img.height,
                                   bd=0,
                                   highlightthickness=0)  # Set border width to 0 to remove button border
        to_patients_list_button.image = to_patients_list_button_photo  # Store reference to image to prevent garbage collection
        to_patients_list_button.place(x=30, y=30)

        row_of_patient = get_row_of_exercises_patient()

        count= 1+s.ball_exercises_number
        self.background_color = "#deeaf7"  # Set the background color to light blue

        ex_1_name = "band_open_arms"
        ex_2_name = "band_open_arms_and_up"
        ex_3_name = "band_up_and_lean"
        formatted_ex_1_name = ex_1_name.replace('_', ' ')
        formatted_ex_2_name = ex_2_name.replace('_', ' ')
        formatted_ex_3_name = ex_3_name.replace('_', ' ')


        #create labels for videos

        self.label1 = tk.Label(self)
        self.label1.place(x=230, y=125)  # Adjust x and y coordinates for the first video
        button1_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_1_name)}.png')
        button1_photo = ImageTk.PhotoImage(button1_image)
        button1 = tk.Button(self, image=button1_photo, command=lambda: which_checkbox(button1, ex_1_name),
                            width=button1_photo.width(), height=button1_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button1.image = button1_photo  # Store reference to image to prevent garbage collection
        button1.place(x=295, y=440)
        self.label_text1 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_1_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text1.place(x=225, y=85)
        count += 1


        self.label2 = tk.Label(self)
        self.label2.place(x=430, y=125)  # Adjust x and y coordinates for the second video

        button2_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_2_name)}.png')
        button2_photo = ImageTk.PhotoImage(button2_image)
        button2 = tk.Button(self, image=button2_photo,
                            command=lambda: which_checkbox(button2, ex_2_name),
                            width=button2_photo.width(), height=button2_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button2.image = button2_photo  # Store reference to image to prevent garbage collection
        button2.place(x=495, y=440)
        self.label_text2 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_2_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text2.place(x=425, y=85)
        count += 1


        self.label3 = tk.Label(self)
        self.label3.place(x=630, y=125)  # Adjust x and y coordinates for the third video
        button3_image = Image.open(
            f'Pictures//{which_image_to_put(row_of_patient, ex_3_name)}.png')
        button3_photo = ImageTk.PhotoImage(button3_image)
        button3 = tk.Button(self, image=button3_photo,
                            command=lambda: which_checkbox(button3, ex_3_name),
                            width=button3_photo.width(), height=button3_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button3.image = button3_photo  # Store reference to image to prevent garbage collection
        button3.place(x=695, y=440)
        self.label_text3 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_3_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text3.place(x=625, y=85)
        count += 1



        # Video paths
        video_file1 = f'Videos//{ex_1_name}_vid.mp4'
        video_path1 = os.path.join(os.getcwd(), video_file1)
        self.cap1 = cv2.VideoCapture(video_path1)

        video_file2 = f'Videos//{ex_2_name}_vid.mp4'
        video_path2 = os.path.join(os.getcwd(), video_file2)
        self.cap2 = cv2.VideoCapture(video_path2)

        video_file3 = f'Videos//{ex_3_name}_vid.mp4'
        video_path3 = os.path.join(os.getcwd(), video_file3)
        self.cap3 = cv2.VideoCapture(video_path3)



        # Check if videos are opened successfully
        if not (
                self.cap1.isOpened() and self.cap2.isOpened() and self.cap3.isOpened()):
            print("Error opening video streams or files")

        else:
            # Play videos
            play_video(self.cap1, self.label1, ex_1_name, "band")
            play_video(self.cap2, self.label2,ex_2_name, "band")  # Change "Page2" to the name of the page you want to switch to
            play_video(self.cap3, self.label3,ex_3_name, "band")  # Change "Page3" to the name of the page you want to switch to


    def on_arrow_click_forward(self):
        Excel.find_and_change_values_patients({"number of repetitions in each exercise": self.selected_option.get(),
                                               "rate": self.selected_option_rate.get()})
        s.screen.switch_frame(ChooseStickExercisesPage)

    def on_arrow_click_back(self):
        Excel.find_and_change_values_patients({"number of repetitions in each exercise": self.selected_option.get(),
                                               "rate": self.selected_option_rate.get()})
        s.screen.switch_frame(ChooseBallExercisesPage)

    def to_previous_button_click(self):
        num_of_exercises_in_training = Excel.count_number_of_exercises_in_training_by_ID()
        if num_of_exercises_in_training < 5:
            back = Image.open('Pictures//not_enough_exercises_chosen.jpg')
            background_img = ImageTk.PhotoImage(back)

            self.label = tk.Label(self, image=background_img, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=170, y=20)
            self.label.image = background_img

        else:
            Excel.find_and_change_values_patients({"number of exercises": num_of_exercises_in_training, "number of repetitions in each exercise": self.selected_option.get(), "rate": self.selected_option_rate.get()})
            s.screen.switch_frame(ChooseTrainingOrExerciseInformation)






class ChooseStickExercisesPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # Load background image
        background_image = Image.open('Pictures//background.jpg')
        self.background_photo = ImageTk.PhotoImage(background_image)
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.pack()

        add_to_exercise_page(self)


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

        to_patients_list_button_img = Image.open("Pictures//previous.jpg")
        to_patients_list_button_photo = ImageTk.PhotoImage(to_patients_list_button_img)
        to_patients_list_button = tk.Button(self, image=to_patients_list_button_photo,
                                            command=lambda: self.to_previous_button_click(),
                                            width=to_patients_list_button_img.width,
                                            height=to_patients_list_button_img.height,
                                            bd=0,
                                            highlightthickness=0)  # Set border width to 0 to remove button border
        to_patients_list_button.image = to_patients_list_button_photo  # Store reference to image to prevent garbage collection
        to_patients_list_button.place(x=30, y=30)

        row_of_patient=get_row_of_exercises_patient()

        count= 1 + s.ball_exercises_number + s.band_exercises_number
        self.background_color = "#deeaf7"  # Set the background color to light blue

        ex_1_name = "stick_bend_elbows"
        ex_2_name = "stick_bend_elbows_and_up"
        ex_3_name = "stick_raise_arms_above_head"
        ex_4_name =  "stick_switch"
        formatted_ex_1_name = ex_1_name.replace('_', ' ')
        formatted_ex_2_name = ex_2_name.replace('_', ' ')
        formatted_ex_3_name = ex_3_name.replace('_', ' ')
        formatted_ex_4_name = ex_4_name.replace('_', ' ')


        # Create labels for videos
        self.label1 = tk.Label(self)
        self.label1.place(x=125, y=125)  # Adjust x and y coordinates for the first video
        button1_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_1_name)}.png')
        button1_photo = ImageTk.PhotoImage(button1_image)
        button1 = tk.Button(self, image=button1_photo, command=lambda: which_checkbox(button1, ex_1_name),
                            width=button1_photo.width(), height=button1_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button1.image = button1_photo  # Store reference to image to prevent garbage collection
        button1.place(x=190, y=440)
        self.label_text1 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_1_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text1.place(x=120, y=85)
        count += 1


        self.label2 = tk.Label(self)
        self.label2.place(x=325, y=125)  # Adjust x and y coordinates for the second video
        button2_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_2_name)}.png')
        button2_photo = ImageTk.PhotoImage(button2_image)
        button2 = tk.Button(self, image=button2_photo,
                            command=lambda: which_checkbox(button2, ex_2_name),
                            width=button2_photo.width(), height=button2_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button2.image = button2_photo  # Store reference to image to prevent garbage collection
        button2.place(x=390, y=440)
        self.label_text2 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_2_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text2.place(x=320, y=85)
        count += 1


        self.label3 = tk.Label(self)
        self.label3.place(x=525, y=125)  # Adjust x and y coordinates for the third video
        button3_image = Image.open(
            f'Pictures//{which_image_to_put(row_of_patient, ex_3_name)}.png')
        button3_photo = ImageTk.PhotoImage(button3_image)
        button3 = tk.Button(self, image=button3_photo,
                            command=lambda: which_checkbox(button3, ex_3_name),
                            width=button3_photo.width(), height=button3_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button3.image = button3_photo  # Store reference to image to prevent garbage collection
        button3.place(x=590, y=440)
        self.label_text3 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_3_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text3.place(x=520, y=85)
        count += 1


        self.label4 = tk.Label(self)
        self.label4.place(x=725, y=125)  # Adjust x and y coordinates for the third video
        button4_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_4_name)}.png')
        button4_photo = ImageTk.PhotoImage(button4_image)
        button4 = tk.Button(self, image=button4_photo,
                            command=lambda: which_checkbox(button4, ex_4_name),
                            width=button4_photo.width(), height=button4_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button4.image = button4_photo  # Store reference to image to prevent garbage collection
        button4.place(x=790, y=440)
        self.label_text4 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_4_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text4.place(x=720, y=85)
        count += 1




        # Video paths
        video_file1 = f'Videos//{ex_1_name}_vid.mp4'
        video_path1 = os.path.join(os.getcwd(), video_file1)
        self.cap1 = cv2.VideoCapture(video_path1)

        video_file2 = f'Videos//{ex_2_name}_vid.mp4'
        video_path2 = os.path.join(os.getcwd(), video_file2)
        self.cap2 = cv2.VideoCapture(video_path2)

        video_file3 = f'Videos//{ex_3_name}_vid.mp4'
        video_path3 = os.path.join(os.getcwd(), video_file3)
        self.cap3 = cv2.VideoCapture(video_path3)

        video_file4 = f'Videos//{ex_4_name}_vid.mp4'
        video_path4 = os.path.join(os.getcwd(), video_file4)
        self.cap4 = cv2.VideoCapture(video_path4)



        # Check if videos are opened successfully
        if not (
                self.cap1.isOpened() and self.cap2.isOpened() and self.cap3.isOpened() and self.cap4.isOpened()):
            print("Error opening video streams or files")

        else:
            # Play videos
            play_video(self.cap1, self.label1, ex_1_name, "stick")
            play_video(self.cap2, self.label2,ex_2_name, "stick")
            play_video(self.cap3, self.label3,ex_3_name, "stick")
            play_video(self.cap4, self.label4,ex_4_name, "stick")


    def on_arrow_click_forward(self):
        Excel.find_and_change_values_patients({"number of repetitions in each exercise": self.selected_option.get(),
                                               "rate": self.selected_option_rate.get()})
        s.screen.switch_frame(ChooseNoToolExercisesPage)

    def on_arrow_click_back(self):
        Excel.find_and_change_values_patients({"number of repetitions in each exercise": self.selected_option.get(),
                                               "rate": self.selected_option_rate.get()})
        s.screen.switch_frame(ChooseRubberBandExercisesPage)

    def to_previous_button_click(self):
        num_of_exercises_in_training = Excel.count_number_of_exercises_in_training_by_ID()
        if num_of_exercises_in_training < 5:
            back = Image.open('Pictures//not_enough_exercises_chosen.jpg')
            background_img = ImageTk.PhotoImage(back)

            self.label = tk.Label(self, image=background_img, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=170, y= 20)
            self.label.image = background_img

        else:
            Excel.find_and_change_values_patients({"number of exercises": num_of_exercises_in_training, "number of repetitions in each exercise": self.selected_option.get(), "rate": self.selected_option_rate.get()})
            s.screen.switch_frame(ChooseTrainingOrExerciseInformation)



class ChooseNoToolExercisesPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # Load background image
        background_image = Image.open('Pictures//background.jpg')
        self.background_photo = ImageTk.PhotoImage(background_image)
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.pack()

        add_to_exercise_page(self)

        end_button_img = Image.open("Pictures//end_button.jpg")
        end_button_photo = ImageTk.PhotoImage(end_button_img)
        end_button = tk.Button(self, image=end_button_photo,
                                         command=lambda: self.on_end_click(),
                                         width=end_button_img.width, height=end_button_img.height,
                                         bd=0,
                                         highlightthickness=0)
        end_button.image = end_button_photo
        end_button.place(x=50, y=490)

        backward_arrow_button_img = Image.open("Pictures//previous_arrow.jpg")
        backward_arrow_button_photo = ImageTk.PhotoImage(backward_arrow_button_img)
        backward_arrow_button = tk.Button(self, image=backward_arrow_button_photo,
                                          command=lambda: self.on_arrow_click_back(),
                                          width=backward_arrow_button_img.width,
                                          height=backward_arrow_button_img.height, bd=0,
                                          highlightthickness=0)
        backward_arrow_button.image = backward_arrow_button_photo
        backward_arrow_button.place(x=913, y=480)

        row_of_patient=get_row_of_exercises_patient()

        count= 1 + s.ball_exercises_number + s.band_exercises_number + s.stick_exercises_number
        self.background_color = "#deeaf7"  # Set the background color to light blue

        ex_1_name = "notool_hands_behind_and_lean"
        ex_2_name = "notool_right_hand_up_and_bend"
        ex_3_name = "notool_left_hand_up_and_bend"
        ex_4_name =  "notool_raising_hands_diagonally"
        formatted_ex_1_name = ex_1_name.replace('_', ' ')
        formatted_ex_2_name = ex_2_name.replace('_', ' ')
        formatted_ex_3_name = ex_3_name.replace('_', ' ')
        formatted_ex_4_name = ex_4_name.replace('_', ' ')


        # Create labels for videos
        self.label1 = tk.Label(self)
        self.label1.place(x=125, y=125)  # Adjust x and y coordinates for the first video
        button1_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_1_name)}.png')
        button1_photo = ImageTk.PhotoImage(button1_image)
        button1 = tk.Button(self, image=button1_photo, command=lambda: which_checkbox(button1, ex_1_name),
                            width=button1_photo.width(), height=button1_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button1.image = button1_photo  # Store reference to image to prevent garbage collection
        button1.place(x=190, y=440)
        self.label_text1 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_1_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text1.place(x=120, y=85)
        count += 1

        self.label2 = tk.Label(self)
        self.label2.place(x=325, y=125)  # Adjust x and y coordinates for the second video
        button2_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_2_name)}.png')
        button2_photo = ImageTk.PhotoImage(button2_image)
        button2 = tk.Button(self, image=button2_photo,
                            command=lambda: which_checkbox(button2, ex_2_name),
                            width=button2_photo.width(), height=button2_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button2.image = button2_photo  # Store reference to image to prevent garbage collection
        button2.place(x=390, y=440)
        self.label_text2 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_2_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text2.place(x=320, y=85)
        count += 1


        self.label3 = tk.Label(self)
        self.label3.place(x=525, y=125)  # Adjust x and y coordinates for the third video
        button3_image = Image.open(
            f'Pictures//{which_image_to_put(row_of_patient, ex_3_name)}.png')
        button3_photo = ImageTk.PhotoImage(button3_image)
        button3 = tk.Button(self, image=button3_photo,
                            command=lambda: which_checkbox(button3, ex_3_name),
                            width=button3_photo.width(), height=button3_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button3.image = button3_photo  # Store reference to image to prevent garbage collection
        button3.place(x=590, y=440)
        self.label_text3 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_3_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text3.place(x=520, y=85)
        count += 1

        self.label4 = tk.Label(self)
        self.label4.place(x=725, y=125)  # Adjust x and y coordinates for the third video
        button4_image = Image.open(f'Pictures//{which_image_to_put(row_of_patient, ex_4_name)}.png')
        button4_photo = ImageTk.PhotoImage(button4_image)
        button4 = tk.Button(self, image=button4_photo,
                            command=lambda: which_checkbox(button4, ex_4_name),
                            width=button4_photo.width(), height=button4_photo.height(), bd=0,
                            highlightthickness=0)  # Set border width to 0 to remove button border
        button4.image = button4_photo  # Store reference to image to prevent garbage collection
        button4.place(x=790, y=440)
        self.label_text4 = tk.Label(self, text=f'Exercise {count}\n{formatted_ex_4_name}', font=("Thaoma", 9, 'bold'), bg=self.background_color,
            justify='center', width=25, wraplength=170, anchor='center')
        self.label_text4.place(x=720, y=85)
        count += 1




        # Video paths
        video_file1 = f'Videos//{ex_1_name}_vid.mp4'
        video_path1 = os.path.join(os.getcwd(), video_file1)
        self.cap1 = cv2.VideoCapture(video_path1)

        video_file2 = f'Videos//{ex_2_name}_vid.mp4'
        video_path2 = os.path.join(os.getcwd(), video_file2)
        self.cap2 = cv2.VideoCapture(video_path2)

        video_file3 = f'Videos//{ex_3_name}_vid.mp4'
        video_path3 = os.path.join(os.getcwd(), video_file3)
        self.cap3 = cv2.VideoCapture(video_path3)

        video_file4 = f'Videos//{ex_4_name}_vid.mp4'
        video_path4 = os.path.join(os.getcwd(), video_file4)
        self.cap4 = cv2.VideoCapture(video_path4)



        # Check if videos are opened successfully
        if not (
                self.cap1.isOpened() and self.cap2.isOpened() and self.cap3.isOpened() and self.cap4.isOpened()):
            print("Error opening video streams or files")
        else:
            # Play videos
            play_video(self.cap1, self.label1, ex_1_name, "no_tool")
            play_video(self.cap2, self.label2,ex_2_name, "no_tool")
            play_video(self.cap3, self.label3,ex_3_name, "no_tool")
            play_video(self.cap4, self.label4,ex_4_name, "no_tool")


    def on_end_click(self):
        num_of_exercises_in_training = Excel.count_number_of_exercises_in_training_by_ID()
        if num_of_exercises_in_training < 5:
            back = Image.open('Pictures//not_enough_exercises_chosen.jpg')
            background_img = ImageTk.PhotoImage(back)

            self.label = tk.Label(self, image=background_img, compound=tk.CENTER, highlightthickness=0)
            self.label.place(x=190, y=480)
            self.label.image = background_img

        else:
            Excel.find_and_change_values_patients({"number of exercises": num_of_exercises_in_training, "number of repetitions in each exercise": self.selected_option.get(), "rate": self.selected_option_rate.get()})
            s.screen.switch_frame(ChooseTrainingOrExerciseInformation)

    def on_arrow_click_back(self):
        Excel.find_and_change_values_patients({"number of repetitions in each exercise": self.selected_option.get(),
                                               "rate": self.selected_option_rate.get()})
        s.screen.switch_frame(ChooseStickExercisesPage)





def get_sorted_folders(directory):
    # Get the list of folder names in the specified directory
    folder_names = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]

    # Convert folder names to datetime objects
    folder_datetimes = []
    for folder in folder_names:
        try:
            folder_datetime = datetime.strptime(folder, "%d-%m-%Y %H-%M-%S")
            folder_datetimes.append((folder, folder_datetime))
        except ValueError:
            # Skip folder names that don't match the expected format
            continue

    # Sort the list of tuples by datetime in descending order
    sorted_folders = sorted(folder_datetimes, key=lambda x: x[1], reverse=True)

    # Extract just the folder names from the sorted list
    sorted_folder_names = [folder for folder, _ in sorted_folders]

    return sorted_folder_names


def convert_white_to_transparent(image_path, tolerance=100):
    img = Image.open(image_path)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        # Check if the pixel is near-white by allowing a tolerance range
        if item[0] >= 255 - tolerance and item[1] >= 255 - tolerance and item[2] >= 255 - tolerance:
            # Replace near-white with transparent
            newData.append((255, 255, 255, 0))  # Make it fully transparent
        else:
            newData.append(item)

    img.putdata(newData)
    return img

#Page that appears when there is an exercise
class ExercisePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # The subjects from which the algorithm can choose
        subjects = ["butterflies", "galaxy", "garden"]
        random.shuffle(subjects)
        self.chosen_subject = subjects[0]  # Instance variable for later use

        # Create a canvas for layering background and transparent image
        self.canvas = tk.Canvas(self, width=1024, height=576)
        self.canvas.pack(fill="both", expand=True)

        # Load background image
        background_image = Image.open(f'Pictures/{self.chosen_subject}/background.jpg')
        self.background_photo = ImageTk.PhotoImage(background_image)

        self.stop_training_button_img = Image.open("Pictures/stop_training_button.jpg")
        self.stop_training_button_photo = ImageTk.PhotoImage(self.stop_training_button_img)
        self.stop_training_button = tk.Button(self, image=self.stop_training_button_photo,
                                         command=self.stop_training_button_click,
                                         bd=0, highlightthickness=0)  # Set border width to 0 to remove button border
        self.stop_training_button.image = self.stop_training_button_photo  # Prevent garbage collection
        self.stop_training_button.place(x=15, y=10)
        self.stop = False

        self.pause_training_button_img = Image.open("Pictures/pause_training_button.jpg")
        self.pause_training_button_photo = ImageTk.PhotoImage(self.pause_training_button_img)
        self.pause_training_button = tk.Button(self, image=self.pause_training_button_photo,
                                         command=self.pause_training_button_click,
                                         bd=0, highlightthickness=0)  # Set border width to 0 to remove button border
        self.pause_training_button.image = self.pause_training_button_photo  # Prevent garbage collection
        self.pause_training_button.place(x=95, y=10)

        # Place background image on canvas
        self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        # List to hold references to the images (to avoid garbage collection)
        self.image_references = []

        # Predetermined positions (you can adjust these to your liking)
        self.positions = [
            (180, 10), (350, 10), (520, 10), (690, 10), (860, 10),
            (10, 190), (180, 190), (350, 190), (520, 190), (690, 190), (860, 190),
            (10, 370), (180, 370), (350, 370), (520, 370), (690, 370), (860, 370)
        ]


        # Shuffle the positions to make their selection random
        random.shuffle(self.positions)

        # Track count for patient repetitions
        self.count = 1

        # Start the loop using after()
        self.update_exercise()

    def update_exercise(self):
        # Non-blocking exercise loop using after()

        if (not s.gymmy_done) or (not s.camera_done):  # While the exercise is still running
            if self.count == s.patient_repetitions_counting_in_exercise:
                # Get the next random position from the shuffled list
                x_image, y_image = self.positions[s.patient_repetitions_counting_in_exercise]

                # Path to a random image in the chosen category
                image_num = random.randint(1, 27)
                image_path = f'Pictures/{self.chosen_subject}/{image_num}.png'

                # Convert near-white background to transparent (adjust tolerance as needed)
                transparent_image = convert_white_to_transparent(image_path, tolerance=30)

                # Load the image with transparent background into Tkinter
                exercise_photo = ImageTk.PhotoImage(transparent_image)

                # Place the transparent image on top of the background
                self.canvas.create_image(x_image, y_image, image=exercise_photo, anchor="nw")

                # Append each image reference to the list to prevent garbage collection
                self.image_references.append(exercise_photo)

                # Increment the count to wait for the next successful repetition
                self.count += 1

            # Schedule next iteration to keep updating the screen
            self.after_id= self.after(1, self.update_exercise)  # Call the function every 1ms
        else:
            print("Exercise complete")

    def stop_training_button_click(self):
        s.req_exercise = ""
        s.stop_requested=True
        s.finish_workout= True
        self.after_cancel(self.after_id)  # Cancel any pending after() calls

        print("Stop training button clicked")

    def pause_training_button_click(self):
        s.starts_and_ends_of_stops.append(datetime.now())

        if s.did_training_paused:
            # Define what happens when the button is clicked
            print("Pause training button clicked")
            s.did_training_paused= False

            if hasattr(self, 'pause_training_button'):
                self.pause_training_button.destroy()

                # Create a new button
            self.pause_training_button_img = Image.open("Pictures//pause_training_button.jpg")
            self.pause_training_button_photo = ImageTk.PhotoImage(self.pause_training_button_img)
            self.pause_training_button = tk.Button(self, image=self.pause_training_button_photo,
                                                   command=self.pause_training_button_click,
                                                   bd=0, highlightthickness=0)
            self.pause_training_button.image = self.pause_training_button_photo  # Prevent garbage collection
            self.pause_training_button.place(x=95, y=10)

        else:
            if hasattr(self, 'pause_training_button'):
                self.pause_training_button.destroy()

                # Create a new button
            self.pause_training_button_img = Image.open("Pictures//continue_training_button.jpg")
            self.pause_training_button_photo = ImageTk.PhotoImage(self.pause_training_button_img)
            self.pause_training_button = tk.Button(self, image=self.pause_training_button_photo,
                                                   command=self.pause_training_button_click,
                                                   bd=0, highlightthickness=0)
            self.pause_training_button.image = self.pause_training_button_photo  # Prevent garbage collection
            self.pause_training_button.place(x=95, y=10)

            s.did_training_paused = True


class ChooseTrainingOrExerciseInformation(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        image = Image.open('Pictures//background.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        name_label(self)

        to_previous_button_img = Image.open("Pictures//previous.jpg")
        to_previous_button_photo = ImageTk.PhotoImage(to_previous_button_img)
        to_previous_button = tk.Button(self, image=to_previous_button_photo, command=lambda: self.to_previous_button_click(),
                                   width=to_previous_button_img.width, height=to_previous_button_img.height, bd=0,
                                   highlightthickness=0)  # Set border width to 0 to remove button border
        to_previous_button.image = to_previous_button_photo  # Store reference to image to prevent garbage collection
        to_previous_button.place(x=30, y=30)

        # Load images for buttons
        training_image = Image.open("Pictures//information_training_button.jpg")
        training_photo = ImageTk.PhotoImage(training_image)
        exercise_image = Image.open("Pictures//to_information_exercises_button.jpg")
        exercise_photo = ImageTk.PhotoImage(exercise_image)

        # Store references to prevent garbage collection
        self.training_photo = training_photo
        self.patient_photo = exercise_photo

        # Create buttons with images
        enter_trainings = tk.Button(self, image=training_photo,
                                              command=self.on_click_training_chosen,
                                              width=training_image.width, height=training_image.height,
                                              bg='#50a6ad', bd=0, highlightthickness=0)
        enter_trainings.place(x=160, y=130)

        enter_exercises = tk.Button(self, image=exercise_photo,
                                            command=self.on_click_exercise_chosen,
                                            width=exercise_image.width, height=exercise_image.height,
                                            bg='#50a6ad', bd=0, highlightthickness=0)
        enter_exercises.place(x=540, y=130)

    def to_previous_button_click(self):
        s.screen.switch_frame(PatientDisplaying)

    def on_click_training_chosen(self):
        s.screen.switch_frame(InformationAboutTrainingPage)

    def on_click_exercise_chosen(self):
        s.screen.switch_frame(ChooseBallExercisesPage)

# class GraphPage(tk.Frame):
#     def __init__(self, master, exercise, previous, **kwargs):
#         tk.Frame.__init__(self, master, **kwargs)
#         self.queue = queue.Queue()
#         self.exercise = exercise
#         self.forward_arrow_button = None
#         self.backward_arrow_button = None
#         self.label1=None
#         self.label2= None
#         image = Image.open('Pictures//background.jpg')
#         self.photo_image = ImageTk.PhotoImage(image)
#         tk.Label(self, image=self.photo_image).pack()
#
        # if previous=="ball":
        #     previous_page=ChooseBallExercisesPage
        # elif previous=="band":
        #     previous_page=ChooseRubberBandExercisesPage
        # elif previous=="stick":
        #     previous_page=ChooseStickExercisesPage
        # elif previous=="no_tool":
        #     previous_page=ChooseNoToolExercisesPage
        #
        # previous_page_button_img = Image.open("Pictures//previous.jpg")
        # previous_page_button_photo = ImageTk.PhotoImage(previous_page_button_img)
        # previous_page_category = tk.Button(self, image=previous_page_button_photo,
        #                                   command=lambda: s.screen.switch_frame(previous_page),
        #                                   width=previous_page_button_img.width,
        #                                   height=previous_page_button_img.height, bd=0,
        #                                   highlightthickness=0)
        # previous_page_category.image = previous_page_button_photo
        # previous_page_category.place(x=30, y=30)
#
#
#         sorted_folders= get_sorted_folders(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}')
#         if len(sorted_folders)==0:
#             did_before = Image.open('Pictures//patient_didnt_do.jpg')
#             self.did_before = ImageTk.PhotoImage(did_before)
#             self.did_before_label = tk.Label(self, image=self.did_before, bd=0)
#             self.did_before_label.place(x=270, y=75)
#
#         else:
#             num_of_angles= self.get_number_of_angles_in_exercise(exercise)
#             self.show_graphs(sorted_folders, 0, num_of_angles, exercise)
#
#     def show_graphs(self, sorted_folder, place, num_of_angles, exercise):
#         if place>0:
#             self.backward_arrow_button_img = Image.open("Pictures//previous_arrow.jpg")
#             self.backward_arrow_button_photo = ImageTk.PhotoImage(self.backward_arrow_button_img)
#             self.backward_arrow_button = tk.Button(self, image=self.backward_arrow_button_photo,
#                                               command=lambda: self.help_function(sorted_folder, place-1, num_of_angles, exercise),
#                                               width=self.backward_arrow_button_img.width,
#                                               height=self.backward_arrow_button_img.height, bd=0,
#                                               highlightthickness=0)
#             self.backward_arrow_button.image = self.backward_arrow_button_photo
#             self.backward_arrow_button.place(x=945, y=480)
#
#         if place<len(sorted_folder)-1:
#             self.forward_arrow_button_img = Image.open("Pictures//forward_arrow.jpg")
#             self.forward_arrow_button_photo = ImageTk.PhotoImage(self.forward_arrow_button_img)
#             self.forward_arrow_button = tk.Button(self, image=self.forward_arrow_button_photo,
#                                              command=lambda: self.help_function(sorted_folder, place+1, num_of_angles, exercise),
#                                              width=self.forward_arrow_button_img.width,
#                                              height=self.forward_arrow_button_img.height, bd=0,
#                                              highlightthickness=0)
#             self.forward_arrow_button.image = self.forward_arrow_button_photo
#             self.forward_arrow_button.place(x=20, y=480)
#
#
#         back = Image.open('Pictures//empty.JPG')
#         background_img = ImageTk.PhotoImage(back)
#
#
#         directory= f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/{sorted_folder[place]}.xlsx'
#         print(directory)
#
#         success_number = Excel.get_success_number(directory, exercise)
#         #effort_number = Excel.get_effort_number(directory, exercise)
#
#
#         self.label1 = tk.Label(self, text=f'{sorted_folder[place]}',
#                               image=background_img, compound=tk.CENTER, font=("Thaoma", 20, 'bold'), width=350,
#                               height=30)
#         self.label1.place(x=160, y=15)
#         self.label1.image = background_img
#
#         if success_number is not None:
#             self.label2 = tk.Label(self, text= "מספר חזרות מוצלחות: "+ str(success_number),
#                                   image=background_img, compound=tk.CENTER, font=("Thaoma", 11, 'bold'), width=350,
#                                   height=30)
#             self.label2.place(x=155, y=50)
#             self.label2.image = background_img
#
#         # if effort_number is not None:
#         #     self.label = tk.Label(self,
#         #                           text=str(effort_number) + "דירוג קושי התרגיל על ידי המתאמן: ",
#         #                           image=background_img, compound=tk.CENTER, font=("Thaoma", 11, 'bold'), width=350,
#         #                           height=30)
#         #     self.label.place(x=155, y=40)
#         #     self.label.image = background_img
#
#
#         if num_of_angles == 1:
#             self.one_angle_graph(exercise, sorted_folder[place])
#         if num_of_angles == 2:
#             self.two_angles_graph(exercise, sorted_folder[place])
#         if num_of_angles == 3:
#             self.three_angles_graph(exercise, sorted_folder[place])
#
#     def help_function(self, sorted_folder, place_to_put, num_of_angles, exercise):
#         if self.label1:
#             self.label1.place_forget()
#         if self.label2:
#             self.label2.place_forget()
#         if self.forward_arrow_button:
#             self.forward_arrow_button.destroy()
#             self.forward_arrow_button = None
#         if self.backward_arrow_button:
#             self.backward_arrow_button.destroy()
#             self.backward_arrow_button = None
#         self.show_graphs(sorted_folder, place_to_put, num_of_angles, exercise)
#
#     def find_image(self, directory, number):
#         # Create a regex pattern to match the files with ' ' followed by the specific number and '.jpeg'
#         pattern = re.compile(r' (\d+)\.jpeg$')
#
#         # Iterate through the files in the directory
#         for filename in os.listdir(directory):
#             match = pattern.search(filename)
#             if match and match.group(1) == str(number):
#                 return os.path.join(directory, filename)
#         return None
#
#
#
#     def get_number_of_angles_in_exercise(self, exercise):
#         try:
#             # Load the workbook
#             workbook = openpyxl.load_workbook("exercises_table.xlsx")
#
#             # Select the desired sheet
#             sheet = workbook[workbook.sheetnames[0]]
#
#             # Iterate through rows starting from the specified row
#             for row_number in range(1,sheet.max_row + 1):
#                 first_cell_value = sheet.cell(row=row_number, column=1).value
#
#                 if first_cell_value == exercise:
#                     return sheet.cell(row=row_number, column=2).value
#
#
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             return False
#
#     def three_angles_graph(self, exercise, folder):
#         # Determine the resize factor
#         resize_factor = 0.42
#
#         # Load the image
#         dir1= self.find_image(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{folder}', 1)
#         graph1 = Image.open(dir1)
#         new_width1 = int(graph1.width * resize_factor)
#         new_height1 = int(graph1.height * resize_factor)
#         graph1_resized = graph1.resize((new_width1, new_height1), Image.Resampling.LANCZOS)
#         self.graph1 = ImageTk.PhotoImage(graph1_resized)
#         self.graph1_label = tk.Label(self, image=self.graph1, bd=0)
#         self.graph1_label.place(x=100, y=90)
#
#         dir2 = self.find_image(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{folder}', 2)
#         graph2 = Image.open(dir2)
#         new_width2 = int(graph2.width * resize_factor)
#         new_height2 = int(graph2.height * resize_factor)
#         graph2_resized = graph2.resize((new_width2, new_height2), Image.Resampling.LANCZOS)
#         self.graph2 = ImageTk.PhotoImage(graph2_resized)
#         self.graph2_label = tk.Label(self, image=self.graph2, bd=0)
#         self.graph2_label.place(x=100, y=325)
#
#         dir3 = self.find_image(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{folder}', 3)
#         graph3 = Image.open(dir3)
#         new_width3 = int(graph3.width * resize_factor)
#         new_height3 = int(graph3.height * resize_factor)
#         graph3_resized = graph3.resize((new_width3, new_height3), Image.Resampling.LANCZOS)
#         self.graph3 = ImageTk.PhotoImage(graph3_resized)
#         self.graph3_label = tk.Label(self, image=self.graph3, bd=0)
#         self.graph3_label.place(x=380, y=90)
#
#         dir4 = self.find_image(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{folder}', 4)
#         graph4 = Image.open(dir4)
#         new_width4 = int(graph4.width * resize_factor)
#         new_height4 = int(graph4.height * resize_factor)
#         graph4_resized = graph4.resize((new_width4, new_height4), Image.Resampling.LANCZOS)
#         self.graph4 = ImageTk.PhotoImage(graph4_resized)
#         self.graph4_label = tk.Label(self, image=self.graph4, bd=0)
#         self.graph4_label.place(x=380, y=325)
#
#         dir5 = self.find_image(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{folder}', 5)
#         graph5 = Image.open(dir5)
#         new_width5 = int(graph5.width * resize_factor)
#         new_height5 = int(graph5.height * resize_factor)
#         graph5_resized = graph5.resize((new_width5, new_height5), Image.Resampling.LANCZOS)
#         self.graph5 = ImageTk.PhotoImage(graph5_resized)
#         self.graph5_label = tk.Label(self, image=self.graph5, bd=0)
#         self.graph5_label.place(x=660, y=90)
#
#         dir6 = self.find_image(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{folder}', 6)
#         graph6 = Image.open(dir6)
#         new_width6 = int(graph6.width * resize_factor)
#         new_height6 = int(graph6.height * resize_factor)
#         graph6_resized = graph6.resize((new_width6, new_height6), Image.Resampling.LANCZOS)
#         self.graph6 = ImageTk.PhotoImage(graph6_resized)
#         self.graph6_label = tk.Label(self, image=self.graph6, bd=0)
#         self.graph6_label.place(x=660, y=325)
#
#
#     def two_angles_graph(self, exercise, folder):
#         # Determine the resize factor
#         resize_factor = 0.45
#
#         dir1 = self.find_image(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{folder}', 1)
#         graph1 = Image.open(dir1)
#         new_width1 = int(graph1.width * resize_factor)
#         new_height1 = int(graph1.height * resize_factor)
#         graph1_resized = graph1.resize((new_width1, new_height1), Image.Resampling.LANCZOS)
#         self.graph1 = ImageTk.PhotoImage(graph1_resized)
#         self.graph1_label = tk.Label(self, image=self.graph1, bd=0)
#         self.graph1_label.place(x=190, y=90)
#
#         dir2 = self.find_image(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{folder}', 2)
#         graph2 = Image.open(dir2)
#         new_width2 = int(graph2.width * resize_factor)
#         new_height2 = int(graph2.height * resize_factor)
#         graph2_resized = graph2.resize((new_width2, new_height2), Image.Resampling.LANCZOS)
#         self.graph2 = ImageTk.PhotoImage(graph2_resized)
#         self.graph2_label = tk.Label(self, image=self.graph2, bd=0)
#         self.graph2_label.place(x=190, y=325)
#
#         dir3 = self.find_image(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{folder}', 3)
#         graph3 = Image.open(dir3)
#         new_width3 = int(graph3.width * resize_factor)
#         new_height3 = int(graph3.height * resize_factor)
#         graph3_resized = graph3.resize((new_width3, new_height3), Image.Resampling.LANCZOS)
#         self.graph3 = ImageTk.PhotoImage(graph3_resized)
#         self.graph3_label = tk.Label(self, image=self.graph3, bd=0)
#         self.graph3_label.place(x=540, y=90)
#
#         dir4 = self.find_image(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{folder}', 4)
#         graph4 = Image.open(dir4)
#         new_width4 = int(graph4.width * resize_factor)
#         new_height4 = int(graph4.height * resize_factor)
#         graph4_resized = graph4.resize((new_width4, new_height4), Image.Resampling.LANCZOS)
#         self.graph4 = ImageTk.PhotoImage(graph4_resized)
#         self.graph4_label = tk.Label(self, image=self.graph4, bd=0)
#         self.graph4_label.place(x=540, y=325)
#
#
#
#     def one_angle_graph(self, exercise, folder):
#         # Determine the resize factor
#         resize_factor = 0.45
#
#         dir1 = self.find_image(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{folder}', 1)
#         graph1 = Image.open(dir1)
#         new_width1 = int(graph1.width * resize_factor)
#         new_height1 = int(graph1.height * resize_factor)
#         graph1_resized = graph1.resize((new_width1, new_height1), Image.Resampling.LANCZOS)
#         self.graph1 = ImageTk.PhotoImage(graph1_resized)
#         self.graph1_label = tk.Label(self, image=self.graph1, bd=0)
#         self.graph1_label.place(x=350, y=90)
#
#         dir2 = self.find_image(f'C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{folder}', 2)
#         graph2 = Image.open(dir2)
#         new_width2 = int(graph2.width * resize_factor)
#         new_height2 = int(graph2.height * resize_factor)
#         graph2_resized = graph2.resize((new_width2, new_height2), Image.Resampling.LANCZOS)
#         self.graph2 = ImageTk.PhotoImage(graph2_resized)
#         self.graph2_label = tk.Label(self, image=self.graph2, bd=0)
#         self.graph2_label.place(x=350, y=325)




class TablesPage(tk.Frame):
    def __init__(self, master, exercise, previous, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.queue = queue.Queue()
        self.exercise = exercise
        self.forward_arrow_button = None
        self.backward_arrow_button = None
        self.label1 = None
        self.label2 = None
        self.background_color = "#deeaf7"  # Set the background color to light blue

        # Set the background color for the Frame
        self.configure(bg=self.background_color)

        # Load background image
        image = Image.open('Pictures//background.jpg')
        self.photo_image = ImageTk.PhotoImage(image)

        # Add a label with the background image and set the background to match the window
        tk.Label(self, image=self.photo_image, bg=self.background_color).pack(fill='both', expand=True)

        # Define previous page navigation based on tool used
        if previous == "ball":
            previous_page = ChooseBallExercisesPage
        elif previous == "band":
            previous_page = ChooseRubberBandExercisesPage
        elif previous == "stick":
            previous_page = ChooseStickExercisesPage
        elif previous == "no_tool":
            previous_page = ChooseNoToolExercisesPage

        # Load the previous page button image and set background
        previous_page_button_img = Image.open("Pictures//previous.jpg")
        previous_page_button_photo = ImageTk.PhotoImage(previous_page_button_img)
        previous_page_category = tk.Button(self, image=previous_page_button_photo,
                                           command=lambda: s.screen.switch_frame(previous_page),
                                           width=previous_page_button_img.width,
                                           height=previous_page_button_img.height, bd=0,
                                           highlightthickness=0, bg=self.background_color)
        previous_page_category.image = previous_page_button_photo
        previous_page_category.place(x=30, y=30)

        try:
            # Attempt to fetch sorted folders for the exercise
            sorted_folders = get_sorted_folders(f'Patients/{s.chosen_patient_ID}/Tables/{exercise}')

            if len(sorted_folders) == 0:
                # Display 'patient_didnt_do.jpg' if no folders are found
                didnt_do_before = Image.open('Pictures//patient_didnt_do.jpg')
                self.didnt_do_before = ImageTk.PhotoImage(didnt_do_before)
                self.didnt_do_before_label = tk.Label(self, image=self.didnt_do_before, bd=0, bg=self.background_color)
                self.didnt_do_before_label.place(x=270, y=75)
            else:
                # Show tables if folders are found
                num_of_angles = self.get_number_of_angles_in_exercise(exercise)
                self.show_tables(sorted_folders, 0, num_of_angles, exercise)

        except FileNotFoundError:
            # Handle case where the path does not exist
            didnt_do_before = Image.open('Pictures//patient_didnt_do.jpg')
            self.didnt_do_before = ImageTk.PhotoImage(didnt_do_before)
            self.didnt_do_before_label = tk.Label(self, image=self.didnt_do_before, bd=0, bg=self.background_color)
            self.didnt_do_before_label.place(x=270, y=75)
            print(f"Error: The path 'Patients/{s.chosen_patient_ID}/Tables/{exercise}' does not exist.")


    def show_tables(self, sorted_folder, place, num_of_angles, exercise):
        if place > 0:
            self.backward_arrow_button_img = Image.open("Pictures//previous_arrow.jpg")
            self.backward_arrow_button_photo = ImageTk.PhotoImage(self.backward_arrow_button_img)
            self.backward_arrow_button = tk.Button(self, image=self.backward_arrow_button_photo,
                                                   command=lambda: self.help_function(sorted_folder, place-1, num_of_angles, exercise),
                                                   width=self.backward_arrow_button_img.width,
                                                   height=self.backward_arrow_button_img.height, bd=0,
                                                   highlightthickness=0, bg=self.background_color)
            self.backward_arrow_button.image = self.backward_arrow_button_photo
            self.backward_arrow_button.place(x=945, y=480)

        if place < len(sorted_folder) - 1:
            self.forward_arrow_button_img = Image.open("Pictures//forward_arrow.jpg")
            self.forward_arrow_button_photo = ImageTk.PhotoImage(self.forward_arrow_button_img)
            self.forward_arrow_button = tk.Button(self, image=self.forward_arrow_button_photo,
                                                  command=lambda: self.help_function(sorted_folder, place+1, num_of_angles, exercise),
                                                  width=self.forward_arrow_button_img.width,
                                                  height=self.forward_arrow_button_img.height, bd=0,
                                                  highlightthickness=0, bg=self.background_color)
            self.forward_arrow_button.image = self.forward_arrow_button_photo
            self.forward_arrow_button.place(x=20, y=480)

        back = Image.open('Pictures//empty.JPG')
        background_img = ImageTk.PhotoImage(back)

        # Directory path
        directory = f'Patients/{s.chosen_patient_ID}/{sorted_folder[place]}.xlsx'
        print(directory)

        # Fetch success numbers

        first_name_of_patient = Excel.find_value_by_colName_and_userID("Patients.xlsx", "patients_details", s.chosen_patient_ID, "first name")
        last_name_of_patient = Excel.find_value_by_colName_and_userID("Patients.xlsx", "patients_details", s.chosen_patient_ID, "last name")

        self.label1 = tk.Label(self, text=f'{last_name_of_patient} {first_name_of_patient}', image=background_img, compound=tk.CENTER,
                               font=("Thaoma", 16, 'bold'), width=350, height=15, bg=self.background_color)
        self.label1.place(x=160, y=5)
        self.label1.image = background_img


        # Format the date and time from the folder name
        date_part, time_part = sorted_folder[place].split(' ')
        formatted_date = date_part.replace('-', '/')
        formatted_time = time_part.replace('-', ':')
        formatted_text = f'{formatted_date} {formatted_time}'

        # Display date and time with custom background color
        self.label2 = tk.Label(self, text=f'{formatted_text}', image=background_img, compound=tk.CENTER,
                               font=("Thaoma", 16, 'bold'), width=350, height=15, bg=self.background_color)
        self.label2.place(x=160, y=30)
        self.label2.image = background_img

        success_number = Excel.get_success_number(directory, exercise)

        if success_number is not None:
            self.label3 = tk.Label(self, text="מספר חזרות מוצלחות: " + str(success_number), image=background_img,
                                   compound=tk.CENTER, font=("Thaoma", 16, 'bold'), width=350,
                                   height=15, bg=self.background_color)
            self.label3.place(x=155, y=55)
            self.label3.image = background_img

        # Handle different number of angles
        if num_of_angles == 1:
            self.one_angle_graph(exercise, sorted_folder[place])
        if num_of_angles == 2:
            self.two_angles_graph(exercise, sorted_folder[place])
        if num_of_angles == 3:
            self.three_angles_graph(exercise, sorted_folder[place])

    def help_function(self, sorted_folder, place_to_put, num_of_angles, exercise):
        # Clean up previous labels and buttons
        if self.label1:
            self.label1.place_forget()
        if self.label2:
            self.label2.place_forget()
        if self.forward_arrow_button:
            self.forward_arrow_button.destroy()
            self.forward_arrow_button = None
        if self.backward_arrow_button:
            self.backward_arrow_button.destroy()
            self.backward_arrow_button = None
        self.show_tables(sorted_folder, place_to_put, num_of_angles, exercise)

    def find_image(self, directory, number):
        # Create a regex pattern to match files with ' ' followed by the specific number and either '.jpeg', '.jpg', or '.png'
        pattern = re.compile(r' (\d+)\.(?:jpeg|jpg|png)$')

        # Iterate through the files in the directory
        for filename in os.listdir(directory):
            match = pattern.search(filename)
            if match and match.group(1) == str(number):
                return os.path.join(directory, filename)
        return None



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

    def three_angles_graph(self, exercise, folder):
        # Determine the resize factor
        resize_factor_width = 0.55
        resize_factor_height = 0.4

        # Load the image for table 1
        dir1 = self.find_image(
            f'Patients/{s.chosen_patient_ID}/Tables/{exercise}/{folder}', 1)
        table1 = Image.open(dir1)
        new_width1 = int(table1.width * resize_factor_width)
        new_height1 = int(table1.height * resize_factor_height)
        table1_resized = table1.resize((new_width1, new_height1), Image.Resampling.LANCZOS)
        self.table1 = ImageTk.PhotoImage(table1_resized)
        self.table1_label = tk.Label(self, image=self.table1, bd=0, bg='#deeaf7')  # Set background color here
        self.table1_label.place(x=100, y=90)

        # Load the image for table 2
        dir2 = self.find_image(
            f'Patients/{s.chosen_patient_ID}/Tables/{exercise}/{folder}', 2)
        table2 = Image.open(dir2)
        new_width2 = int(table2.width * resize_factor_width)
        new_height2 = int(table2.height * resize_factor_height)
        table2_resized = table2.resize((new_width2, new_height2), Image.Resampling.LANCZOS)
        self.table2 = ImageTk.PhotoImage(table2_resized)
        self.table2_label = tk.Label(self, image=self.table2, bd=0, bg='#deeaf7')  # Set background color here
        self.table2_label.place(x=100, y=325)

        # Load the image for table 3
        dir3 = self.find_image(
            f'Patients/{s.chosen_patient_ID}/Tables/{exercise}/{folder}', 3)
        table3 = Image.open(dir3)
        new_width3 = int(table3.width * resize_factor_width)
        new_height3 = int(table3.height * resize_factor_height)
        table3_resized = table3.resize((new_width3, new_height3), Image.Resampling.LANCZOS)
        self.table3 = ImageTk.PhotoImage(table3_resized)
        self.table3_label = tk.Label(self, image=self.table3, bd=0, bg='#deeaf7')  # Set background color here
        self.table3_label.place(x=380, y=90)

        # Load the image for table 4
        dir4 = self.find_image(
            f'Patients/{s.chosen_patient_ID}/Tables/{exercise}/{folder}', 4)
        table4 = Image.open(dir4)
        new_width4 = int(table4.width * resize_factor_width)
        new_height4 = int(table4.height * resize_factor_height)
        table4_resized = table4.resize((new_width4, new_height4), Image.Resampling.LANCZOS)
        self.table4 = ImageTk.PhotoImage(table4_resized)
        self.table4_label = tk.Label(self, image=self.table4, bd=0, bg='#deeaf7')  # Set background color here
        self.table4_label.place(x=380, y=325)

        # Load the image for table 5
        dir5 = self.find_image(
            f'Patients/{s.chosen_patient_ID}/Tables/{exercise}/{folder}', 5)
        table5 = Image.open(dir5)
        new_width5 = int(table5.width * resize_factor_width)
        new_height5 = int(table5.height * resize_factor_height)
        table5_resized = table5.resize((new_width5, new_height5), Image.Resampling.LANCZOS)
        self.table5 = ImageTk.PhotoImage(table5_resized)
        self.table5_label = tk.Label(self, image=self.table5, bd=0, bg='#deeaf7')  # Set background color here
        self.table5_label.place(x=660, y=90)

        # Load the image for table 6
        dir6 = self.find_image(
            f'Patients/{s.chosen_patient_ID}/Tables/{exercise}/{folder}', 6)
        table6 = Image.open(dir6)
        new_width6 = int(table6.width * resize_factor_width)
        new_height6 = int(table6.height * resize_factor_height)
        table6_resized = table6.resize((new_width6, new_height6), Image.Resampling.LANCZOS)
        self.table6 = ImageTk.PhotoImage(table6_resized)
        self.table6_label = tk.Label(self, image=self.table6, bd=0, bg='#deeaf7')  # Set background color here
        self.table6_label.place(x=660, y=325)

    def two_angles_graph(self, exercise, folder):
        # Determine the resize factor
        resize_factor_width = 0.55
        resize_factor_height = 0.4

        # Load the image for table 1
        dir1 = self.find_image(
            f'Patients/{s.chosen_patient_ID}/Tables/{exercise}/{folder}', 1)
        table1 = Image.open(dir1)
        new_width1 = int(table1.width * resize_factor_width)
        new_height1 = int(table1.height * resize_factor_height)
        table1_resized = table1.resize((new_width1, new_height1), Image.Resampling.LANCZOS)
        self.table1 = ImageTk.PhotoImage(table1_resized)
        self.table1_label = tk.Label(self, image=self.table1, bd=0, bg='#deeaf7')  # Set background color here
        self.table1_label.place(x=230, y=90)

        # Load the image for table 2
        dir2 = self.find_image(
            f'Patients/{s.chosen_patient_ID}/Tables/{exercise}/{folder}', 2)
        table2 = Image.open(dir2)
        new_width2 = int(table2.width * resize_factor_width)
        new_height2 = int(table2.height * resize_factor_height)
        table2_resized = table2.resize((new_width2, new_height2), Image.Resampling.LANCZOS)
        self.table2 = ImageTk.PhotoImage(table2_resized)
        self.table2_label = tk.Label(self, image=self.table2, bd=0, bg='#deeaf7')  # Set background color here
        self.table2_label.place(x=230, y=325)

        # Load the image for table 3
        dir3 = self.find_image(
            f'Patients/{s.chosen_patient_ID}/Tables/{exercise}/{folder}', 3)
        table3 = Image.open(dir3)
        new_width3 = int(table3.width * resize_factor_width)
        new_height3 = int(table3.height * resize_factor_height)
        table3_resized = table3.resize((new_width3, new_height3), Image.Resampling.LANCZOS)
        self.table3 = ImageTk.PhotoImage(table3_resized)
        self.table3_label = tk.Label(self, image=self.table3, bd=0, bg='#deeaf7')  # Set background color here
        self.table3_label.place(x=510, y=90)

        # Load the image for table 4
        dir4 = self.find_image(
            f'Patients/{s.chosen_patient_ID}/Tables/{exercise}/{folder}', 4)
        table4 = Image.open(dir4)
        new_width4 = int(table4.width * resize_factor_width)
        new_height4 = int(table4.height * resize_factor_height)
        table4_resized = table4.resize((new_width4, new_height4), Image.Resampling.LANCZOS)
        self.table4 = ImageTk.PhotoImage(table4_resized)
        self.table4_label = tk.Label(self, image=self.table4, bd=0, bg='#deeaf7')  # Set background color here
        self.table4_label.place(x=510, y=325)



    def one_angle_graph(self, exercise, folder):
        # Determine the resize factor
        resize_factor_width = 0.15
        resize_factor_height = 0.4

        # Load the image for table 1
        dir1 = self.find_image(f'Patients/{s.chosen_patient_ID}/Tables/{exercise}/{folder}', 1)
        table1 = Image.open(dir1)
        new_width1 = int(table1.width * resize_factor_width)
        new_height1 = int(table1.height * resize_factor_height)
        table1_resized = table1.resize((new_width1, new_height1), Image.Resampling.LANCZOS)
        self.table1 = ImageTk.PhotoImage(table1_resized)
        self.table1_label = tk.Label(self, image=self.table1, bd=0, bg='#deeaf7')  # Set background color here
        self.table1_label.place(x=370, y=90)

        # Load the image for table 2
        dir2 = self.find_image(f'Patients/{s.chosen_patient_ID}/Tables/{exercise}/{folder}', 2)
        table2 = Image.open(dir2)
        new_width2 = int(table2.width * resize_factor_width)
        new_height2 = int(table2.height * resize_factor_height)
        table2_resized = table2.resize((new_width2, new_height2), Image.Resampling.LANCZOS)
        self.table2 = ImageTk.PhotoImage(table2_resized)
        self.table2_label = tk.Label(self, image=self.table2, bd=0, bg='#deeaf7')  # Set background color here
        self.table2_label.place(x=370, y=325)



def add_to_exercise_page(self):
    name_label(self)
    how_many_repetitions_of_exercises(self)
    rate_of_exercises(self)


def name_label(self):
    back = Image.open('Pictures//empty.JPG')
    background_img = ImageTk.PhotoImage(back)
    first_name_of_patient = Excel.find_value_by_colName_and_userID("Patients.xlsx", "patients_details",
                                                                   s.chosen_patient_ID, "first name")
    last_name_of_patient = Excel.find_value_by_colName_and_userID("Patients.xlsx", "patients_details",
                                                                  s.chosen_patient_ID, "last name")
    self.background_color = "#deeaf7"  # Set the background color to light blue

    self.label1 = tk.Label(self, text=f'{first_name_of_patient} {last_name_of_patient}', image=background_img,
                           compound=tk.CENTER,
                           font=("Thaoma", 26, 'bold'), width=350, height=50, bg=self.background_color)
    self.label1.place(x=270, y=27)
    self.label1.image = background_img


def how_many_repetitions_of_exercises(self):
    # List of options for the dropdown
    self.options = ["5", "6", "7", "8", "9", "10"]

    # Create a StringVar to hold the selected value
    self.selected_option_rep = tk.StringVar()

    # Get the current number of repetitions from Excel
    current_number_of_repetitions = Excel.find_value_by_colName_and_userID(
        "Patients.xlsx", "patients_details", s.chosen_patient_ID, "number of repetitions in each exercise"
    )

    # Set the default selected option based on the value from Excel
    self.selected_option_rep.set(self.options[int(current_number_of_repetitions) - 5])  # Subtract 5 to match the index

    # Create a custom style for the OptionMenu
    style = ttk.Style()
    style.theme_use('clam')  # Set theme to 'clam'

    # Configure the appearance of the OptionMenu and the dropdown items
    style.configure('Custom.TMenubutton', font=('Arial', 16, 'bold'), background='lightgray', foreground='black',
                    padding=[10, 10], anchor='center')  # Add padding and set anchor to 'center'

    # To configure the dropdown font (for the items inside the menu), modify the 'TMenu' style
    style.configure('Custom.TMenu', font=('Arial', 16))  # Increase font for dropdown items

    # Create the OptionMenu with the custom style
    self.option_menu = ttk.OptionMenu(self, self.selected_option_rep, self.selected_option_rep.get(), *self.options)
    self.option_menu['style'] = 'Custom.TMenubutton'  # Apply the custom style
    self.option_menu.config(width=4)  # Adjust the width of the dropdown
    self.option_menu.place(x=520, y=480)


    # Adjust dropdown items font
    self.option_menu['menu'].config(font=('Arial', 16))

    # Background and label setup
    self.background_color = "#deeaf7"
    background_img = ImageTk.PhotoImage(Image.open('Pictures//empty.JPG'))
    self.label1 = tk.Label(self, text=":מספר חזרות ", image=background_img, compound=tk.CENTER,
                           font=("Thaoma", 16, 'bold'), width=110, height=50, bg=self.background_color)
    self.label1.place(x=620, y=480)
    self.label1.image = background_img


def rate_of_exercises(self):

    # List of options for the dropdown
    self.options_rate = ["slow", "moderate", "fast"]

    # Create a StringVar to hold the selected value
    self.selected_option_rate = tk.StringVar()

    # Get the current number of repetitions from Excel
    current_rate = Excel.find_value_by_colName_and_userID(
        "Patients.xlsx", "patients_details", s.chosen_patient_ID, "rate"
    )

    # Set the default selected option based on the value from Excel
    self.selected_option_rate.set(self.options_rate[self.options_rate.index(str(current_rate))])

    # Create a custom style for the OptionMenu
    style = ttk.Style()
    style.theme_use('clam')  # Set theme to 'clam'

    # Configure the appearance of the OptionMenu and the dropdown items
    style.configure('Custom.TMenubutton', font=('Arial', 16, 'bold'), background='lightgray', foreground='black',
                    padding=[10, 10], anchor='center')  # Add padding and set anchor to 'center'

    # To configure the dropdown font (for the items inside the menu), modify the 'TMenu' style
    style.configure('Custom.TMenu', font=('Arial', 16))  # Increase font for dropdown items

    # Configure the appearance of the OptionMenu and the dropdown items
    style.configure('Custom.TMenubutton', font=('Arial', 16, 'bold'), background='lightgray', foreground='black',
                    padding=[10, 10], anchor='center')  # Add padding and set anchor to 'center'

    # To configure the dropdown font (for the items inside the menu), modify the 'TMenu' style
    style.configure('Custom.TMenu', font=('Arial', 16))  # Increase font for dropdown items

    # Create the OptionMenu with the custom style
    self.option_menu_rate = ttk.OptionMenu(self, self.selected_option_rate, self.selected_option_rate.get(), *self.options_rate)
    self.option_menu_rate['style'] = 'Custom.TMenubutton'  # Apply the custom style
    self.option_menu_rate.config(width=11)  # Adjust the width of the dropdown
    self.option_menu_rate.place(x=270, y=480)


    # Adjust dropdown items font
    self.option_menu_rate['menu'].config(font=('Arial', 16))
    # Background and label setup
    self.background_color = "#deeaf7"
    background_img = ImageTk.PhotoImage(Image.open('Pictures//empty.JPG'))


    self.label2 = tk.Label(self, text=":קצב ", image=background_img, compound=tk.CENTER,
                           font=("Thaoma", 16, 'bold'), width=50, height=50, bg=self.background_color)
    self.label2.place(x=450, y=480)
    self.label2.image = background_img


class InformationAboutTrainingPage (tk.Frame):
    def __init__(self, master):

        tk.Frame.__init__(self, master)
        dates, percent_success, exertion_rate, time_in_training = self.create_data()
        df = pd.DataFrame({
            'זמן באימון (שניות)': time_in_training,
            'דירוג מאמץ על ידי המטופל': exertion_rate,
            'אחוז הצלחה באימון': percent_success,
            'תאריך ושעה': dates
        })

        # Load the background image
        image = Image.open('Pictures//training_list.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        # Create a label to display the background image
        self.background_label = tk.Label(self, image=self.photo_image)
        self.background_label.pack(fill="both", expand=True)

        name_label(self)

        # Display the DataFrame in a Treeview widget
        self.treeview = ttk.Treeview(self, style="Treeview", show="headings")
        self.treeview["columns"] = tuple(df.columns)

        # Set up a custom style for the Treeview
        style = ttk.Style(self)
        style.configure("Treeview", font=("Thaoma", 14, 'bold'), rowheight=30)

        # Add columns to the Treeview
        for col in df.columns:
            self.treeview.column(col, anchor="e", width=150)
            self.treeview.heading(col, text=col, anchor="e")

        self.treeview.column("תאריך ושעה", anchor="e", width=200)

        # Insert data into the Treeview
        for index, row in df.iterrows():
            values = tuple(row)
            self.treeview.insert("", index, values=values)

        # Remove event handling for row selection
        self.treeview.unbind("<ButtonRelease-1>")  # Disables row selection on click
        self.treeview.config(height=10)

        # Pack the Treeview widget
        self.treeview.place(x=150, y=180)

        # Set up a vertical scrollbar
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(x=800, y=180, height=310)

        back_button_img = Image.open("Pictures//previous.jpg")
        back_button_photo = ImageTk.PhotoImage(back_button_img)
        back_button = tk.Button(self, image=back_button_photo, command=lambda: self.on_click_to_previous(),
                                width=back_button_img.width, height=back_button_img.height, bd=0,
                                highlightthickness=0)
        back_button.image = back_button_photo
        back_button.place(x=30, y=30)

    def on_click_to_previous(self):
        s.screen.switch_frame(ChooseTrainingOrExerciseInformation)

    def create_data(self):
        df = pd.read_excel("Patients.xlsx", sheet_name="patients_history_of_trainings")
        df.iloc[:, 0] = df.iloc[:, 0].astype(str)
        filtered_rows = df[df.iloc[:, 0] == s.chosen_patient_ID]

        row = filtered_rows.iloc[0]  # Get the first (and only) row
        row_values_without_id = row.iloc[1:]

        dates = []
        percent_success = []
        exertion_rate = []
        time_in_training = []

        for i in range(0, len(row_values_without_id), 4):
            date_value = row_values_without_id.iloc[i]
            if pd.notna(date_value):  # Check if not NaN
                try:
                    # Convert the string to datetime
                    dates.append(date_value)  # Append formatted date
                except ValueError:
                    # Handle cases where the date format is unexpected
                    dates.append(date_value)

            if i + 1 < len(row_values_without_id):
                success_value = row_values_without_id.iloc[i + 1]
                if pd.notna(success_value):  # Check if not NaN
                    percent_success.append(int(success_value))  # Append as int

            if i + 2 < len(row_values_without_id):
                exertion_value = row_values_without_id.iloc[i + 2]
                if pd.notna(exertion_value):  # Check if not NaN
                    exertion_rate.append(int(exertion_value))  # Append as int

            if i + 3 < len(row_values_without_id):
                training_time_value = row_values_without_id.iloc[i + 3]
                if pd.notna(training_time_value):  # Check if not NaN
                    time_in_training.append(int(training_time_value))  # Append as int

        return dates, percent_success, exertion_rate, time_in_training



class ExplanationPage(tk.Frame):
    def __init__(self, master, exercise, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        image = Image.open('Pictures//background.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()

        self.label = tk.Label(self)
        self.label.place(x=400, y=120)
        video_file = f'Videos//{exercise}_vid.mp4'
        video_path = os.path.join(os.getcwd(), video_file)
        self.cap = cv2.VideoCapture(video_path)

        skip_explanation_button_img = Image.open("Pictures//skip_explanation_button.jpg")
        skip_explanation_button_photo = ImageTk.PhotoImage(skip_explanation_button_img)
        skip_explanation_button = tk.Button(self, image=skip_explanation_button_photo, command=lambda: self.on_click_skip(),
                                width=skip_explanation_button_img.width, height=skip_explanation_button_img.height, bd=0,
                                highlightthickness=0)
        skip_explanation_button.image = skip_explanation_button_photo
        skip_explanation_button.place(x=30, y=30)


        if not (self.cap.isOpened()):
            print("Error opening video streams or files")

        else:
            # Play videos
            play_video(self.cap, self.label, exercise, None, 0.5, 0.8)
            say(exercise)
            self.after(get_wav_duration(exercise)*1000+500, lambda: self.end_of_explanation())

    def end_of_explanation(self):
        say(str(f'{s.rep} times'))
        s.explanation_over = True

    def on_click_skip(self):
        s.explanation_over = True


class Number_of_good_repetitions_page(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        # Create a canvas for layering background and text with no border or highlight
        self.canvas = tk.Canvas(self, width=1024, height=576, bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Load and display the background image
        image = Image.open('Pictures//good_repetitions.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.photo_image, anchor="nw")

        # Overlay text directly on the canvas instead of using Labels
        self.canvas.create_text(480, 190, text=str(s.patient_repetitions_counting_in_exercise),
                                font=("Arial", 100, "bold"), fill="black")

        self.canvas.create_text(480, 450, text=str(s.rep),
                                font=("Arial", 100, "bold"), fill="black")


        say("you managed to perform")
        first_delay = get_wav_duration("you managed to perform") * 1000 + 500

        # First after delay
        self.after(first_delay, lambda: self.say_repetitions())

    def say_repetitions(self):
        say(str(s.patient_repetitions_counting_in_exercise))
        second_delay = get_wav_duration(str(s.patient_repetitions_counting_in_exercise)) * 1000 + 500

        # Second after delay
        self.after(second_delay, lambda: self.say_good_repetitions())

    def say_good_repetitions(self):
        say("good repetitions out of")
        third_delay = get_wav_duration("good repetitions out of") * 1000 + 500

        # Third after delay
        self.after(third_delay, lambda: self.say_rep_count())

    def say_rep_count(self):
        say(str(s.rep))


    # class ExercisePage(tk.Frame):
#     def __init__(self, master):
#         tk.Frame.__init__(self, master)
#         image = Image.open('Pictures//exercise.jpg')
#         self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
#         tk.Label(self, image = self.photo_image).pack()
#         say("start_ex")



########################################### Encouragemennts Pages ######################################################

class Very_good(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//verygood.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()
        say('Very_good')


class Excellent(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//excellent.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()
        say('Excellent')

class Well_done(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//welldone.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()
        say('Well_done')


class AlmostExcellent(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//almostexcellent.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()
        say('almostexcellent')


class FailPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//fail.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()
        say('fail')


################################################# Categories Screens ##############################################
class StartOfTraining(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//hello.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        say("welcome")

def wait_until_waving():
    s.req_exercise="hello_waving"

class Ball(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//ball.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        say("Ball")
        self.after(6000,lambda: wait_until_waving())


class Stick(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//stick.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        say("Stick")
        self.after(6000,lambda: wait_until_waving())


class Rubber_Band(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//rubber_band.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        say("Band")
        self.after(6000,lambda: wait_until_waving())


class NoTool(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//background.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()
        say("NoTool")
        self.after(6000,lambda: wait_until_waving())


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
        say('goodbye')


class ClappingPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open('Pictures//clapping_page.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()
        random_number = random.randint(1, 8)
        say(f'clap {random_number}')
        self.after(get_wav_duration(f'clap {random_number}')*1000+500, lambda: s.screen.switch_frame(GoodbyePage))




######################################################## Effort scale Page #################################################
class EffortScale(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        image = Image.open('Pictures//scale.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        self.background_label = tk.Label(self, image=self.photo_image)
        self.background_label.pack()
        say('please_rate_effort')



        ## buttons to press for scale
        image0 = Image.open('Pictures//scale_0.jpg')
        resized_image0 = image0.resize((350, 40), Image.LANCZOS)
        self.photo_image0 = ImageTk.PhotoImage(resized_image0)
        button0= tk.Button(self,image=self.photo_image0, command=self.on_click_0)
        button0.place(height=40, width=350, x=180, y=100)

        image1 = Image.open('Pictures//scale_1.jpg')
        resized_image1 = image1.resize((350, 40), Image.LANCZOS)
        self.photo_image1 = ImageTk.PhotoImage(resized_image1)
        button1= tk.Button(self,image=self.photo_image1, command=self.on_click_1)
        button1.place(height=40, width=350, x=180, y=140)

        image2 = Image.open('Pictures//scale_2.jpg')
        resized_image2= image2.resize((350, 40), Image.LANCZOS)
        self.photo_image2 = ImageTk.PhotoImage(resized_image2)
        button2 = tk.Button(self, image=self.photo_image2, command=self.on_click_2)
        button2.place(height=40, width=350, x=180, y=180)

        image3 = Image.open('Pictures//scale_3.jpg')
        resized_image3 = image3.resize((350, 40), Image.LANCZOS)
        self.photo_image3 = ImageTk.PhotoImage(resized_image3)
        button3 = tk.Button(self, image=self.photo_image3, command=self.on_click_3)
        button3.place(height=40, width=350, x=180, y=220)

        image4 = Image.open('Pictures//scale_4.jpg')
        resized_image4 = image4.resize((350, 40), Image.LANCZOS)
        self.photo_image4 = ImageTk.PhotoImage(resized_image4)
        button4 = tk.Button(self, image=self.photo_image4, command=self.on_click_4)
        button4.place(height=40, width=350, x=180, y=260)

        image5 = Image.open('Pictures//scale_5.jpg')
        resized_image5 = image5.resize((350, 40), Image.LANCZOS)
        self.photo_image5 = ImageTk.PhotoImage(resized_image5)
        button5 = tk.Button(self, image=self.photo_image5, command=self.on_click_5)
        button5.place(height=40, width=350, x=180, y=300)

        image6 = Image.open('Pictures//scale_6.jpg')
        resized_image6 = image6.resize((350, 40), Image.LANCZOS)
        self.photo_image6 = ImageTk.PhotoImage(resized_image6)
        button6 = tk.Button(self, image=self.photo_image6, command=self.on_click_6)
        button6.place(height=40, width=350, x=180, y=340)

        image7 = Image.open('Pictures//scale_7.jpg')
        resized_image7 = image7.resize((350, 40), Image.LANCZOS)
        self.photo_image7 = ImageTk.PhotoImage(resized_image7)
        button7 = tk.Button(self, image=self.photo_image7, command=self.on_click_7)
        button7.place(height=40, width=350, x=180, y=380)

        image8 = Image.open('Pictures//scale_8.jpg')
        resized_image8 = image8.resize((350, 40), Image.LANCZOS)
        self.photo_image8 = ImageTk.PhotoImage(resized_image8)
        button8 = tk.Button(self, image=self.photo_image8, command=self.on_click_8)
        button8.place(height=40, width=350, x=180, y=420)

        image9 = Image.open('Pictures//scale_9.jpg')
        resized_image9 = image9.resize((350, 40), Image.LANCZOS)
        self.photo_image9 = ImageTk.PhotoImage(resized_image9)
        button9 = tk.Button(self, image=self.photo_image9, command=self.on_click_9)
        button9.place(height=40, width=350, x=180, y=460)

        image10 = Image.open('Pictures//scale_10.jpg')
        resized_image10 = image10.resize((350, 40), Image.LANCZOS)
        self.photo_image10 = ImageTk.PhotoImage(resized_image10)
        button10 = tk.Button(self, image=self.photo_image10, command=self.on_click_10)
        button10.place(height=40, width=350, x=180, y=500)


    def on_click_0(self):
        s.effort= 0
        s.finished_effort=True

    def on_click_1(self):
        s.effort = 1
        s.finished_effort = True

    def on_click_2(self):
        s.effort = 2
        s.finished_effort = True

    def on_click_3(self):
        s.effort = 3
        s.finished_effort = True

    def on_click_4(self):
        s.effort = 4
        s.finished_effort = True

    def on_click_5(self):
        s.effort = 5
        s.finished_effort = True

    def on_click_6(self):
        s.effort = 6
        s.finished_effort = True

    def on_click_7(self):
        s.effort = 7
        s.finished_effort = True

    def on_click_8(self):
        s.effort = 8
        s.finished_effort = True

    def on_click_9(self):
        s.effort = 9
        s.finished_effort = True
    def on_click_10(self):
        s.effort = 10
        s.finished_effort = True


class Repeat_training_or_not(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        image = Image.open('Pictures//background.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()




        # Load images for buttons
        finish_training_image = Image.open("Pictures//finish_training_button.jpg")
        finish_training_photo = ImageTk.PhotoImage(finish_training_image)
        repeat_training_image = Image.open("Pictures//repeat_training_button.jpg")
        repeat_training_photo = ImageTk.PhotoImage(repeat_training_image)

        # Store references to prevent garbage collection
        self.finish_training_photo = finish_training_photo
        self.repeat_training_photo = repeat_training_photo

        # Create buttons with images
        finish_training_button = tk.Button(self, image=finish_training_photo,
                                              command=self.on_click_not_repeat,
                                              width=finish_training_image.width, height=finish_training_image.height,
                                              bg='#50a6ad', bd=0, highlightthickness=0)
        finish_training_button.place(x=160, y=130)

        repeat_training_button = tk.Button(self, image=repeat_training_photo,
                                            command=self.on_click_repeat,
                                            width=repeat_training_image.width, height=repeat_training_image.height,
                                            bg='#50a6ad', bd=0, highlightthickness=0)
        repeat_training_button.place(x=540, y=130)


    def on_click_repeat(self):
        s.another_training_requested= True
        s.choose_continue_or_not= True
        s.screen.switch_frame(Not_first_round_entrance_page)

    def on_click_not_repeat(self):
        s.choose_continue_or_not= True
        s.screen.switch_frame(ClappingPage)


class Not_first_round_entrance_page(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        image = Image.open('Pictures//not_first_round_entrance.jpg')
        self.photo_image = ImageTk.PhotoImage(image) #self. - for keeping the photo in memory so it will be shown
        tk.Label(self, image = self.photo_image).pack()



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
    # s.audio_path = 'audio files/Hebrew/Male/'
    s.screen = Screen()
    # s.finished_effort= False
    # s.ex_in_training=["bend_elbows_ball", "arms_up_and_down_stick"]
    # s.list_effort_each_exercise= {}
    s.chosen_patient_ID='314808981'
    s.ball_exercises_number = 5
    s.band_exercises_number = 3
    s.stick_exercises_number = 4
    s.weights_exercises_number = 4
    s.no_tool_exercises_number = 4
    #s.screen.switch_frame(ExplanationPage, exercise="bend_elbows_ball")
    s.gymmy_done=False
    s.camera_done= False
    s.rep=5
    s.audio_path = 'audio files/Hebrew/Male/'
    s.patient_repetitions_counting_in_exercise = 1
    s.screen.switch_frame(ChooseBallExercisesPage)
    app = FullScreenApp(s.screen)
    s.screen.mainloop()