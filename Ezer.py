# import tkinter as tk
# import random
# from PIL import Image, ImageTk, ImageSequence
#
# # Paths
# background_image_path = "Pictures/butterflies/background.jpg"  # Change this to your background image
# gif_path = "transparent_butterfly.gif"
#
# class AnimatedButterfly:
#     def __init__(self, canvas, gif_path, x, y):
#         self.canvas = canvas
#         self.frames = []
#         self.current_frame = 0
#         self.running = False  # Starts as a still image
#         self.flying = False  # Controls flying behavior
#         self.x, self.y = x, y  # Butterfly position
#         self.dx, self.dy = 0, 0  # Direction of movement
#
#         # Open GIF and extract frames
#         gif = Image.open(gif_path)
#         for frame in ImageSequence.Iterator(gif):
#             frame = frame.convert("RGBA")
#             self.frames.append(ImageTk.PhotoImage(frame))
#
#         # Add butterfly to Canvas (initial still state)
#         self.gif_id = self.canvas.create_image(x, y, image=self.frames[0], anchor=tk.CENTER)
#
#         # Bind click event to start animation
#         self.canvas.tag_bind(self.gif_id, "<Button-1>", self.toggle_fly)
#
#     def toggle_fly(self, event):
#         """Starts the animation & movement when clicked"""
#         if not self.running:  # If still, start animation
#             self.running = True
#             self.animate()
#         elif not self.flying:  # If already animating, start flying
#             self.flying = True
#             self.choose_direction()
#             self.fly(50)  # Move in 10 steps (1 second total)
#
#     def animate(self):
#         """Controls GIF animation"""
#         if self.running:
#             self.current_frame = (self.current_frame + 1) % len(self.frames)
#             self.canvas.itemconfig(self.gif_id, image=self.frames[self.current_frame])
#             self.canvas.after(100, self.animate)  # Adjust speed
#
#     def choose_direction(self):
#         """Chooses a random direction and keeps it for the entire flight"""
#         self.dx = random.choice([-15, -10, 0, 10, 15])  # Left, Right, or stay same
#         self.dy = random.choice([-15, -10, 0])  # Up, Down, or stay same
#
#         # Ensure it moves in some direction (avoid dx=0 and dy=0)
#         while self.dx == 0 and self.dy == 0:
#             self.dx = random.choice([-15, -10, 0, 10, 15])
#             self.dy = random.choice([-15, -10, 0, 10, 15])
#
#     def fly(self, steps_remaining):
#         """Moves the butterfly smoothly in a fixed direction"""
#         if self.flying and steps_remaining > 0:
#             self.x += self.dx
#             self.y += self.dy
#             self.canvas.move(self.gif_id, self.dx, self.dy)
#
#             # Schedule the next step after 100ms (1 second total with 10 steps)
#             self.canvas.after(100, self.fly, steps_remaining - 1)
#         else:
#             # Once movement is complete, remove butterfly from screen
#             self.canvas.delete(self.gif_id)
#             self.flying = False  # Stop flying
#
# # Initialize Tkinter Window
# root = tk.Tk()
# root.title("Flying Butterfly")
# root.geometry("800x600")  # Set window size
#
# # Create a Canvas
# canvas = tk.Canvas(root, width=800, height=600)
# canvas.pack(fill="both", expand=True)
#
# # Load and set background image
# bg_image = Image.open(background_image_path).resize((800, 600))  # Resize to fit window
# bg_photo = ImageTk.PhotoImage(bg_image)
# canvas.create_image(0, 0, image=bg_photo, anchor=tk.NW)
#
# # Load and display butterfly (starts as still)
# butterfly = AnimatedButterfly(canvas, gif_path, x=400, y=500)  # Adjust start position
#
# # Run the application
# root.mainloop()
