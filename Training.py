class EffortScale(tk.Frame):
    def __init__(self, master, exercises, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        image = Image.open('Pictures//background.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        self.background_label = tk.Label(self, image=self.photo_image)
        self.background_label.pack()
        self.chosen_effort= -1


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