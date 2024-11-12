import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os
import re
import math
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import Excel
import Settings as s
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import fitz  # PyMuPDF
from io import BytesIO

def get_percentage_of_successes_in_last_10_training():
    df = pd.read_excel("Patients.xlsx", sheet_name="patients_history_of_trainings")
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)
    filtered_rows = df[df.iloc[:, 0] == s.chosen_patient_ID]

    x_values = []
    y_values = []

    row = filtered_rows.iloc[0]  # Get the first (and only) row
    row_values_without_id= row.iloc[1:]

    # Extracting first and second values in every group of three
    row_values = []
    for i in range(0, len(row_values_without_id), 3):
        row_values.append(row_values_without_id.iloc[i])  # First value
        if i + 1 < len(row_values_without_id):
            row_values.append(row_values_without_id.iloc[i + 1])  # Second value

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
    x_values, y_values = get_percentage_of_successes_in_last_10_training()

    # Create a new plot
    if len(x_values) == 1:
        plt.scatter(x_values, y_values)  # Use scatter plot for a single data point
    else:
        plt.plot(x_values, y_values, marker='o')  # Add markers to ensure single points are visible

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


def email_sending_level_up():
    # Generate the graph file path
    graph_file_path = draw_a_success_graph_and_save()

    # Generate the graph and get its buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='jpg')
    buffer.seek(0)

    # Email configuration
    sender_email = 'yaelszn@gmail.com'
    receiver_email = s.email_of_patient
    password = 'diyf cxzc tifj sotp'

    # Read the PNG file and add text
    png_path_with_text = add_text_to_image(s.current_level_of_patient)

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




def email_sending_not_level_up():
    # Generate the graph file path
    graph_file_path = draw_a_success_graph_and_save()

    # Generate the graph and get its buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='jpg')
    buffer.seek(0)

    # Email configuration
    sender_email = 'yaelszn@gmail.com'
    receiver_email = s.email_of_patient
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
        <p>{name}, כל הכבוד על האימון היום! </p>
        <p> הרמה הנוכחית שלך היא רמה  {s.current_level_of_patient} </p>
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





def get_ordered_images(image_list):
    """
    Reorder the image list according to the pattern requested:
    - 2 images: 1, 2
    - 4 images: 1, 3, 2, 4
    - 6 images: 1, 4, 2, 5, 3, 6
    """
    n = len(image_list)
    if n == 2:
        return [image_list[0], image_list[1]]
    elif n == 4:
        return [image_list[0], image_list[2], image_list[1], image_list[3]]
    elif n == 6:
        return [image_list[0], image_list[3], image_list[1], image_list[4], image_list[2], image_list[5]]
    else:
        return image_list  # If the number of images is not 2, 4, or 6, return as-is


def collect_images_from_folders(patient_id, exercise_name, timestamp):
    """
    Collect all the image file paths from the 'Graphs' and 'Tables' folders for a given exercise.
    The images are ordered by their number suffix as described.
    """
    # Define the base paths for the graphs and tables folders
    base_path_graphs = f"Patients/{patient_id}/Graphs/{exercise_name}/{timestamp}"
    base_path_tables = f"Patients/{patient_id}/Tables/{exercise_name}/{timestamp}"

    # Collect all .jpeg images from the Graphs folder and .png images from the Tables folder
    graph_images = sorted([os.path.join(base_path_graphs, img) for img in os.listdir(base_path_graphs) if img.endswith('.jpeg')], key=lambda x: int(re.search(r'(\d+)\.jpeg$', x).group(1)))
    table_images = sorted([os.path.join(base_path_tables, img) for img in os.listdir(base_path_tables) if img.endswith('.png')], key=lambda x: int(re.search(r'(\d+)\.png$', x).group(1)))

    # Combine and reorder the images
    graph_images_ordered = get_ordered_images(graph_images)
    table_images_ordered = get_ordered_images(table_images)

    return table_images_ordered, graph_images_ordered  # Tables first, then Graphs


def create_pdf():
    """
    Create a PDF with a global header, section headers, and fixed-size images, with the images
    ordered for specific layouts depending on the number of images in each section.
    """

    pdf_path, image_groups, section_headers, global_header_line1, global_header_line2, global_header_line3 = data_creation_to_create_pdf()

    # Register the Hebrew-compatible font
    pdfmetrics.registerFont(TTFont('Hebrew', "arial.ttf-master/arial.ttf"))

    # Create a canvas to generate the PDF
    pdf_canvas = canvas.Canvas(pdf_path, pagesize=letter)

    # Set the PDF page dimensions (letter size)
    width, height = letter

    # Calculate the total height needed for the global header (3 lines of text with intervals)
    line_height = 0.5 * inch  # Height of each line plus some interval
    total_header_height = 3 * line_height

    # Calculate the starting Y position to vertically center the global header
    start_y_position = (height + total_header_height) / 2 + 100  # This centers the 3 lines of text

    # Set the font for the global header
    pdf_canvas.setFont("Hebrew", 24)

    # Line 1
    text_width_line1 = pdf_canvas.stringWidth(global_header_line1, "Hebrew", 24)
    x_position_line1 = (width - text_width_line1) / 2  # Center the first line horizontally
    pdf_canvas.drawString(x_position_line1, start_y_position, global_header_line1)

    # Line 2 (with interval)
    text_width_line2 = pdf_canvas.stringWidth(global_header_line2, "Hebrew", 24)
    x_position_line2 = (width - text_width_line2) / 2  # Center the second line horizontally
    pdf_canvas.drawString(x_position_line2, start_y_position - 1.5 * line_height, global_header_line2)

    # Line 3 (with interval)
    text_width_line3 = pdf_canvas.stringWidth(global_header_line3, "Hebrew", 24)
    x_position_line3 = (width - text_width_line3) / 2  # Center the third line horizontally
    pdf_canvas.drawString(x_position_line3, start_y_position - 3 * line_height, global_header_line3)

    # Start placing content after the header
    current_y_position = start_y_position - 3 * line_height - inch  # Adjust Y position after the header

    # Set a consistent padding/margin between images and sections
    image_padding = 0.1 * inch  # Reduced padding between images
    section_padding = 0.25 * inch  # Padding between sections

    # Calculate the image size based on a 3-images-per-row layout
    images_per_row = 3
    margin_x = 0.4 * inch  # Reduced margin to make images bigger
    image_width = (width - 2 * margin_x - (images_per_row - 1) * image_padding) / images_per_row
    image_height = image_width * 2 / 3  # Maintain aspect ratio (3:2) for the images

    # Iterate over each section, placing the section header and corresponding images
    for section_index, image_paths in enumerate(image_groups):
        # Draw the section header only once
        section_header_printed = False

        # Determine the number of images in the current section
        total_images = len(image_paths)

        if total_images == 12:
            # Split the image list into two halves
            first_half = image_paths[:6]
            second_half = image_paths[6:]

            # Reorder the images to match the requested layout for 12 images
            reordered_images = [
                first_half[0], first_half[1], first_half[2],  # First row
                second_half[0], second_half[1], second_half[2],  # Second row
                first_half[3], first_half[4], first_half[5],  # Third row
                second_half[3], second_half[4], second_half[5]  # Fourth row
            ]
            images_per_row = 3
        elif total_images == 8:
            # Split the image list into two halves
            first_half = image_paths[:4]
            second_half = image_paths[4:]

            # Reorder the images to match the requested layout for 8 images
            reordered_images = [
                first_half[0], first_half[1],  # First row
                second_half[0], second_half[1],  # Second row
                first_half[2], first_half[3],  # Third row
                second_half[2], second_half[3]  # Fourth row
            ]
            images_per_row = 2  # For layout, but image size remains based on 3 per row
        elif total_images == 4:
            # Reorder the images to match the requested layout for 4 images
            reordered_images = [
                image_paths[0], image_paths[1],  # First row
                image_paths[2], image_paths[3]  # Second row
            ]
            images_per_row = 2  # For layout, but image size remains based on 3 per row
        else:
            # If the image count doesn't match the specific cases, keep the original order
            reordered_images = image_paths
            images_per_row = 3 if total_images >= 3 else total_images

        # Calculate the height needed for this section (including images and section header)
        rows_in_section = math.ceil(len(reordered_images) / images_per_row)
        total_section_height = rows_in_section * (image_height + image_padding) + section_padding + 20  # 20 for header

        # Check if there's enough space to fit the entire section on the current page
        if current_y_position - total_section_height < inch:
            # Not enough space, move to the next page
            pdf_canvas.showPage()  # Create a new page
            current_y_position = height - 1 * inch  # Reset Y position for the new page (starting from the top)
            section_header_printed = False  # Ensure the header is printed once when the new page is started

        # Print section header and images
        for i, image_path in enumerate(reordered_images):
            # Print the section header once before the first image
            if not section_header_printed:
                # Draw the section header
                section_header = section_headers[section_index]
                pdf_canvas.setFont("Hebrew", 14)  # Use Hebrew font for section headers
                pdf_canvas.drawString(1 * inch, current_y_position, section_header)
                section_header_printed = True  # Mark that the section header has been printed
                current_y_position -= section_padding  # Adjust Y position after section header

            # Calculate the total width of images in the current row to center them
            row_start_index = i // images_per_row * images_per_row  # Starting index of the current row
            images_in_row = min(images_per_row, len(reordered_images) - row_start_index)
            total_row_width = images_in_row * image_width + (images_in_row - 1) * image_padding
            x_start_position = (width - total_row_width) / 2  # Center the row of images

            # Calculate x and y positions for the image
            x_position = x_start_position + (i % images_per_row) * (image_width + image_padding)  # Adjust x to center images
            y_position_offset = (i // images_per_row) * (image_height + image_padding)  # Adjust y based on row index

            # Insert the image at the calculated position
            pdf_canvas.drawImage(image_path, x_position, current_y_position - y_position_offset - image_height,
                                 width=image_width, height=image_height)

            # Draw a border around the image
            pdf_canvas.rect(x_position, current_y_position - y_position_offset - image_height,
                            image_width, image_height, stroke=1, fill=0)

        # Adjust Y position for the next section
        current_y_position -= rows_in_section * (image_height + image_padding) + 50

    # Finalize the PDF
    pdf_canvas.save()
    return pdf_path


def data_creation_to_create_pdf():
    # Example usage
    exercises = s.exercises_by_order
    image_groups = []
    section_headers = []


    patient_workbook_path = "Patients.xlsx"
    first_name = Excel.find_value_by_colName_and_userID(patient_workbook_path, "patients_details", s.chosen_patient_ID,
                                                        "first name")
    last_name = Excel.find_value_by_colName_and_userID(patient_workbook_path, "patients_details", s.chosen_patient_ID,
                                                       "last name")

    start_time = s.starts_and_ends_of_stops[-1]

    date_part, time_part = start_time.split(' ')
    formatted_date = date_part.replace('-', '/')
    formatted_time = time_part.replace('-', ':')
    formatted_dt = f'{formatted_date} {formatted_time}'

    # Global header with 3 lines
    global_header_line1 = f' סיכום אימון של המטופל: {first_name} {last_name}'[::-1]
    global_header_line2 = f'מספר מטופל: {s.chosen_patient_ID[::-1]}'[::-1]
    global_header_line3 = f'זמן האימון: {formatted_dt[::-1]}'[::-1]

    for exercise_name in exercises:
        # Collect the images for each exercise
        table_images, graph_images = collect_images_from_folders(s.chosen_patient_ID, exercise_name,
                                                                 s.starts_and_ends_of_stops[-1])

        # Add images and section headers to the lists (Tables first, then Graphs)
        image_groups.append(table_images + graph_images)  # Add all images for the exercise
        section_headers.append(f"Exercise name: {exercise_name.capitalize()}")  # Section header for the exercise

    # Define the directory path where you want to save the PDF
    output_directory = f'Patients/{s.chosen_patient_ID}/'

    # Check if the directory exists, if not, create it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Define the full path including the filename
    output_path = os.path.join(output_directory, f'{start_time}.pdf')

    # Create the PDF with images, headers, and a global title
    return output_path, image_groups, section_headers, global_header_line1, global_header_line2, global_header_line3


def create_pdf_preview(pdf_path):
    # Open the PDF
    pdf_document = fitz.open(pdf_path)

    # Check if there is a second page (page 1 in zero-indexed format)
    if pdf_document.page_count < 2:
        print("The PDF does not have a second page. No preview created.")
        pdf_document.close()
        return None  # Return None if there's no second page

    # Load the second page (page index 1)
    page = pdf_document.load_page(1)

    # Render page to a pixmap (an image representation)
    pix = page.get_pixmap()

    # Convert the pixmap to a PIL image
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Save the image to a BytesIO object
    image_io = BytesIO()
    image.save(image_io, format='JPEG')
    image_io.seek(0)

    # Close the PDF
    pdf_document.close()

    return image_io

def email_to_physical_therapist():
    # Define the PDF file path
    pdf_file_path = create_pdf()

    # Generate the PDF preview
    preview_image_io = create_pdf_preview(pdf_file_path)

    # Email configuration
    sender_email = 'yaelszn@gmail.com'
    # Assuming receiver_emails is a string of comma-separated emails
    receiver_emails_str = Excel.find_value_by_colName_and_userID("Patients.xlsx", "patients_details",
                                                                 s.chosen_patient_ID, "email of therapist")

    # Convert the comma-separated string into a list
    receiver_emails = receiver_emails_str.split(',')  # Add all recipient emails here
    password = 'diyf cxzc tifj sotp'

    # Create message container
    message = MIMEMultipart("related")
    message['From'] = sender_email
    message['To'] = ", ".join(receiver_emails)  # Display recipients as comma-separated
    message['Subject'] = f'{s.full_name} סיכום אימון '

    # Set up initial variables for email content
    number_of_pauses = 0
    did_paused = "לא"
    did_stopped = "הושלם"

    # Determine if the training was paused or stopped
    if s.stop_requested and len(s.starts_and_ends_of_stops) == 2:
        did_stopped = "הופסק באמצע"

    if len(s.starts_and_ends_of_stops) > 2:
        did_paused = "כן"
        number_of_pauses = len(s.starts_and_ends_of_stops) // 2 - 1

    # Create HTML content with the inline image
    html_content = f'''
    <html>
      <body style="direction: rtl;">
        <p> סיכום אימון של <b>{s.full_name}</b>, </p>
        <p> האם בוצעה הפסקה באימון?  <b>{did_paused}</b> </p>
    '''

    if number_of_pauses != 0:
        html_content += f'<p> בוצעו  <b>{number_of_pauses}</b> הפסקות באימון </p>'

    html_content += f'''
        <p> האם האימון הושלם או הופסק באמצע? <b>{did_stopped}</b> </p>
        <div style="height: 20px;"></div> <!-- Empty row with height 20px -->
        <p style="font-family: Arial, sans-serif; font-weight: bold;">סיכום האימון מופיע בקובץ המצורף</p>
        <p>תצוגה מקדימה של סיכום האימון:</p>
        <img src="cid:preview_image" alt="PDF Preview">
        <div style="height: 20px;"></div> <!-- Empty row with height 20px -->
        <p style="font-family: Arial, sans-serif; font-size: 20px; font-weight: bold;">יישר כוח!</p>
      </body>
    </html>
    '''

    # Attach HTML content
    message.attach(MIMEText(html_content, 'html'))

    # Attach the PDF preview image as an inline image if it exists
    if preview_image_io:
        preview_image = MIMEImage(preview_image_io.read(), _subtype="jpeg")
        preview_image.add_header('Content-ID', '<preview_image>')
        message.attach(preview_image)

    # Attach the PDF file
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_data = pdf_file.read()
        pdf_attachment = MIMEApplication(pdf_data, _subtype="pdf")
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename='summary.pdf')
        message.attach(pdf_attachment)

    # Connect to SMTP server and send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_emails, message.as_string())
        print('Email sent successfully!')


if __name__ == '__main__':
    s.email_of_patient = "yaelszn@gmail.com"
    s.full_name = "יעל שניידמן"
    s.stop_requested = True
    s.starts_and_ends_of_stops=[1,2,3,4,5]

    email_to_physical_therapist()