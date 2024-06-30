data = {
    'date': date_values,
    'effort': effort_values
}

df = pd.DataFrame(data)
new_headers = {'effort': "דירוג המאמץ", 'date': "תאריך ושעת אימון"}
df.rename(columns=new_headers, inplace=True)

# Load the background image
image = Image.open('Pictures//scale_table.jpg')
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

# Disable actions on Treeview clicks and selections
self.treeview.bind("<ButtonRelease-1>", self.no_op)
self.treeview.bind("<KeyPress>", self.no_op)

# Pack the Treeview widget
self.treeview.place(x=270, y=180)

# Set up a vertical scrollbar
scrollbar = tk.Scrollbar(self, orient="vertical", command=self.treeview.yview)
self.treeview.configure(yscrollcommand=scrollbar.set)
scrollbar.place(x=725, y=180, height=310)

# Back button
back_button_img = Image.open("Pictures//back_to_menu.jpg")  # Change path to your image file
back_button_photo = ImageTk.PhotoImage(back_button_img)
back_button = tk.Button(self, image=back_button_photo, command=self.on_click_to_physio_menu,
                        width=back_button_img.width, height=back_button_img.height, bd=0,
                        highlightthickness=0)  # Set border width to 0 to remove button border
back_button.image = back_button_photo  # Store reference to image to prevent garbage collection
back_button.place(x=30, y=30)


def no_op(self, event):
    # No operation function
    pass


def on_click_to_physio_menu(self):
    # Placeholder for the function to handle back button click
    pass