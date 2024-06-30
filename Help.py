from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

import pandas as pd
import matplotlib.pyplot as plt
import smtplib
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import re


def get_percentage_of_successes_in_arrays():
    df = pd.read_excel("Patients.xlsx", sheet_name="patients_history_of_trainings")
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)
    filtered_rows = df[df.iloc[:, 0] == "314808981"]

    x_values = []
    y_values = []

    row = filtered_rows.iloc[0]  # Get the first (and only) row
    row_values = row.iloc[1:]  # Exclude the first value of the row

    if len(row_values) > 20:
        last_20_values = row_values[-20:]  # Get the last 20 values
    else:
        last_20_values = row_values  # Take all values if there are less than 20

    count = 1
    for index, cell_value in enumerate(last_20_values):
        if index % 2 != 0:  # Check if index is odd
            y_values.append(cell_value)
        else:
            x_values.append(count)
            count += 1

    return x_values, y_values


def draw_a_success_graph_and_save():
    x_values, y_values = get_percentage_of_successes_in_arrays()

    # Create a new plot
    plt.plot(x_values, y_values)
    plt.xlabel('תאריך'[::-1])
    plt.ylabel('אחוזי הצלחה'[::-1])
    #plt.title("גרף אחוזי הצלחה באימון"[::-1])

    # Save the plot to a file
    graph_file_path = "graph.jpg"
    plt.savefig(graph_file_path)

    # Clear the plot
    plt.clf()

    return graph_file_path


def add_text_to_image(level):
    # Open the image
    image = Image.open("C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Pictures/level_for_email.png")

    # Initialize ImageDraw object
    draw = ImageDraw.Draw(image)

    # Choose a font (default font)
    font = ImageFont.truetype("arial.ttf", 50)

    # Define text color
    text_color = (0, 0, 0)  # white

    # Define text position
    text_width, text_height = draw.textsize(str(level), font)
    image_width, image_height = image.size
    text_x = (image_width - text_width) // 2
    text_y = (image_height - text_height) // 2 -10

    # Add text to the image
    draw.text((text_x, text_y), str(level), fill=text_color, font=font)

    # Save the image with text
    image_with_text_path = "C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Pictures/temp_level_for_email.png"
    image.save(image_with_text_path)

    return image_with_text_path


def email_sending_level_up(level):
    # Generate the graph file path
    graph_file_path = draw_a_success_graph_and_save()

    # Generate the graph and get its buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='jpg')
    buffer.seek(0)

    # Email configuration
    sender_email = 'yaelszn@gmail.com'
    receiver_email = 'yaelszn@gmail.com'
    password = 'diyf cxzc tifj sotp'

    # Read the PNG file and add text
    png_path_with_text = add_text_to_image(level)

    with open(png_path_with_text, "rb") as file:
        png_data = file.read()

    with open(graph_file_path, 'rb') as graph_file:
        graph_data = graph_file.read()

    # Create message container
    message = MIMEMultipart("related")
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'לגימי יש משהו לומר לך!'
    name = 'יעל'
    # Create HTML content with embedded image and graph
    html_content = f'''
    <html>
      <body style="direction: rtl;">
        <p>{name}, כל הכבוד על ההשגים שלך! </p>
        <p>באימון האחרון עלית לרמה </p>
        <img src="cid:image" alt="Image" style="display: block; margin: 0 auto;">
        <div style="height: 20px;"></div> <!-- Empty row with height 20px -->
        <div style="height: 20px;"></div> <!-- Empty row with height 20px -->
        <div style="height: 20px;"></div> <!-- Empty row with height 20px -->
        <p>גרף ההתקדמות באחוזי ההצלחה שלך בכל אימון: </p>
        <img src="cid:graph" alt="Image">
        <div style="height: 20px;"></div> <!-- Empty row with height 20px -->
        <p style="font-family: Arial, sans-serif; font-size: 20px; font-weight: bold;">יישר כוח!</p>
      </body>
    </html>
    '''

    # Attach HTML content
    message.attach(MIMEText(html_content, 'html'))

    # Attach the PNG image as inline content
    png_image = MIMEImage(png_data, 'png')
    png_image.add_header('Content-ID', '<image>')
    message.attach(png_image)

    # Attach the graph as inline content
    graph_image = MIMEImage(graph_data, 'jpeg')
    graph_image.add_header('Content-ID', '<graph>')
    message.attach(graph_image)

    # Attach the graph file
    with open(graph_file_path, 'rb') as graph_file:
        graph_data = graph_file.read()
        graph_attachment = MIMEImage(graph_data, 'jpeg')
        graph_attachment.add_header('Content-Disposition', 'attachment', filename='graph.jpg')
        message.attach(graph_attachment)

    # Connect to SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print('Email sent successfully!')




def email_sending_not_level_up(level):
    # Generate the graph file path
    graph_file_path = draw_a_success_graph_and_save()

    # Generate the graph and get its buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='jpg')
    buffer.seek(0)

    # Email configuration
    sender_email = 'yaelszn@gmail.com'
    receiver_email = 'yaelszn@gmail.com'
    password = 'diyf cxzc tifj sotp'

    with open(graph_file_path, 'rb') as graph_file:
        graph_data = graph_file.read()

    # Create message container
    message = MIMEMultipart("related")
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'לגימי יש משהו לומר לך!'
    name = 'יעל'
    # Create HTML content with embedded image and graph
    html_content = f'''
    <html>
      <body style="direction: rtl;">
        <p>{name}, כל הכבוד שהתאמנת היום! </p>
        <p> הרמה הנוכחית שלך היא רמה  {level} </p>
        <div style="height: 20px;"></div> <!-- Empty row with height 20px -->
        <p style="font-family: Arial, sans-serif; font-weight: bold;">גרף ההתקדמות באחוזי ההצלחה שלך בכל אימון: </p>
        <img src="cid:graph" alt="Image">
        <div style="height: 20px;"></div> <!-- Empty row with height 20px -->
        <p style="font-family: Arial, sans-serif; font-size: 20px; font-weight: bold;">יישר כוח!</p>
      </body>
    </html>
    '''

    # Attach HTML content
    message.attach(MIMEText(html_content, 'html'))

    # Attach the graph as inline content
    graph_image = MIMEImage(graph_data, 'jpeg')
    graph_image.add_header('Content-ID', '<graph>')
    message.attach(graph_image)

    # Attach the graph file
    with open(graph_file_path, 'rb') as graph_file:
        graph_data = graph_file.read()
        graph_attachment = MIMEImage(graph_data, 'jpeg')
        graph_attachment.add_header('Content-Disposition', 'attachment', filename='graph.jpg')
        message.attach(graph_attachment)

    # Connect to SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print('Email sent successfully!')


#email_sending_level_up("5")
#email_sending_not_level_up("5")

import os
from datetime import datetime


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


# Example usage
# directory_path = "C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/4382/Graphs/right_hand_up_and_bend_notool"  # Replace with your directory path
# sorted_folders = get_sorted_folders(directory_path)
#
# print("Folders from latest to earliest:")
# for folder in sorted_folders:
#     print(folder)


def find_image(directory, number):
    # Create a regex pattern to match the files with ' ' followed by the specific number and '.jpeg'
    pattern = re.compile(r' (\d+)\.jpeg$')

    # Iterate through the files in the directory
    for filename in os.listdir(directory):
        match = pattern.search(filename)
        if match and match.group(1) == str(number):
            return os.path.join(directory, filename)
    return None

print(find_image("C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients/4382/Graphs/bend_elbows_ball/01-06-2024 18-42-16", 1))

