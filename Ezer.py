import tkinter as tk
from PIL import Image, ImageTk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multi-Page Application Example")
        self.geometry("800x600")

        # Add a shared label (e.g., title bar)
        self.shared_label = tk.Label(self, text="Shared Header", bg="#333", fg="white", font=("Arial", 16))
        self.shared_label.pack(side="top", fill="x")

        # Container for frames (pages)
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Shared navigation
        self.pages = {}
        for Page in (EntrancePage, ID_therapist_fill_page, ID_patient_fill_page):
            page = Page(container, self)
            self.pages[Page] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.switch_frame(EntrancePage)

    def switch_frame(self, page_class):
        """Bring the desired page to the front."""
        page = self.pages[page_class]
        page.tkraise()

class EntrancePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Background image
        image = Image.open('Pictures/background.jpg')
        self.photo_image = ImageTk.PhotoImage(image)
        tk.Label(self, image=self.photo_image).pack()

        # Load button images
        therapist_image = Image.open("Pictures/therapist_entrance_button.jpg")
        therapist_photo = ImageTk.PhotoImage(therapist_image)
        patient_image = Image.open("Pictures/patient_entrance_button.jpg")
        patient_photo = ImageTk.PhotoImage(patient_image)

        # Therapist button
        therapist_button = tk.Button(self, image=therapist_photo, command=lambda: controller.switch_frame(ID_therapist_fill_page))
        therapist_button.photo = therapist_photo  # Prevent garbage collection
        therapist_button.place(x=160, y=130)

        # Patient button
        patient_button = tk.Button(self, image=patient_photo, command=lambda: controller.switch_frame(ID_patient_fill_page))
        patient_button.photo = patient_photo  # Prevent garbage collection
        patient_button.place(x=540, y=130)

        # Shut down button
        shutdown_image = Image.open("Pictures/shut_down.jpg")
        shutdown_photo = ImageTk.PhotoImage(shutdown_image)
        shutdown_button = tk.Button(self, image=shutdown_photo, command=self.on_click_shut_down)
        shutdown_button.photo = shutdown_photo  # Prevent garbage collection
        shutdown_button.place(x=30, y=30)

    def on_click_shut_down(self):
        print("Shutdown triggered.")
        self.quit()

class ID_therapist_fill_page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Therapist Fill Page")
        label.pack(pady=20)
        back_button = tk.Button(self, text="Back", command=lambda: controller.switch_frame(EntrancePage))
        back_button.pack()

class ID_patient_fill_page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Patient Fill Page")
        label.pack(pady=20)
        back_button = tk.Button(self, text="Back", command=lambda: controller.switch_frame(EntrancePage))
        back_button.pack()

if __name__ == "__main__":
    app = App()
    app.mainloop()