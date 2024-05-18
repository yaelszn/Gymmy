import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Open the existing image
image_path = "C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Pictures/levelUp.jpg"
with open(image_path, "rb") as f:
    image_data = f.read()

# Load the image
image = Image.open(BytesIO(image_data))

# Create a drawing object
draw = ImageDraw.Draw(image)

# Define the text to be added
text = "100"
font_size = 50

# Load a font
font = ImageFont.truetype("arial.ttf", font_size)

# Calculate text size and position
text_width, text_height = draw.textsize(text, font)
image_width, image_height = image.size
text_x = (image_width - text_width) // 2
text_y = (image_height - text_height) // 2 + 40

# Add text to the image
draw.text((text_x, text_y), text, fill="white", font=font)

# Encode the modified image data
buffered = BytesIO()
image.save(buffered, format="JPEG")
modified_image_data = buffered.getvalue()

# Encode the modified image data
image_msg = MIMEImage(modified_image_data)
image_msg.add_header("Content-ID", "<image>")
image_msg.add_header("Content-Disposition", "inline", filename="levelUp.jpg")

# Email configuration
sender_email = 'yaelszn@gmail.com'
receiver_email = 'yaelszn@gmail.com'
password = 'diyf cxzc tifj sotp'

# Create message container
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = receiver_email
message['Subject'] = 'Image Email'

# Email content
body = '<html><body>This is a test email with an image attached:<br><img src="cid:image"></body></html>'
message.attach(MIMEText(body, 'html'))

# Attach the image
message.attach(image_msg)

# Connect to SMTP server
with smtplib.SMTP('smtp.gmail.com', 587) as server:
    server.starttls()  # Secure the connection
    server.login(sender_email, password)
    text = message.as_string()
    server.sendmail(sender_email, receiver_email, text)
    print('Email sent successfully!')


###########################
######################33
###########################3
#####################3



def two_angles_graph(df, exercise):
    worksheet = s.excel_workbook.add_worksheet(("graphs_"+exercise)[:31])

    first_graph_name = df.iloc[0, 0] + ", " + df.iloc[4, 0] + ", " + df.iloc[8, 0]
    y_values_1 = df.iloc[48, :]
    y_values_1_float = y_values_1.astype(float)
    create_and_save_graph(df.columns, y_values_1_float, first_graph_name, worksheet, 48)

    second_graph_name = df.iloc[12, 0] + ", " + df.iloc[16, 0] + ", " + df.iloc[20, 0]
    y_values_2 = df.iloc[49, :]
    y_values_2_float = y_values_2.astype(float)
    create_and_save_graph(df.columns, y_values_2_float, second_graph_name, worksheet, 49)

    third_graph_name = df.iloc[24, 0] + ", " + df.iloc[28, 0] + ", " + df.iloc[32, 0]
    y_values_3 = df.iloc[50, :]
    y_values_3_float = y_values_3.astype(float)
    create_and_save_graph(df.columns, y_values_3_float, third_graph_name, worksheet, 50)

    fourth_graph_name = df.iloc[36, 0] + ", " + df.iloc[40, 0] + ", " + df.iloc[44, 0]
    y_values_4 = df.iloc[51, :]
    y_values_4_float = y_values_4.astype(float)
    create_and_save_graph(df.columns, y_values_4_float, fourth_graph_name, worksheet, 51)





def three_angles_graph(df, exercise):
    worksheet = s.excel_workbook.add_worksheet(("graphs_"+exercise)[:31])

    first_graph_name = df.iloc[0, 0] + ", " + df.iloc[4, 0] + ", " + df.iloc[8, 0]
    y_values_1 = df.iloc[72, :]
    y_values_1_float = y_values_1.astype(float)
    create_and_save_graph(df.columns, y_values_1_float, first_graph_name, worksheet, 72)

    second_graph_name = df.iloc[12, 0] + ", " + df.iloc[16, 0] + ", " + df.iloc[20, 0]
    y_values_2 = df.iloc[73, :]
    y_values_2_float = y_values_2.astype(float)
    create_and_save_graph(df.columns, y_values_2_float, second_graph_name, worksheet, 73)

    third_graph_name = df.iloc[24, 0] + ", " + df.iloc[28, 0] + ", " + df.iloc[32, 0]
    y_values_3 = df.iloc[74, :]
    y_values_3_float = y_values_3.astype(float)
    create_and_save_graph(df.columns, y_values_3_float, third_graph_name, worksheet, 74)

    fourth_graph_name = df.iloc[36, 0] + ", " + df.iloc[40, 0] + ", " + df.iloc[44, 0]
    y_values_4 = df.iloc[75, :]
    y_values_4_float = y_values_4.astype(float)
    create_and_save_graph(df.columns, y_values_4_float, fourth_graph_name, worksheet, 75)

    fifth_graph_name = df.iloc[48, 0] + ", " + df.iloc[52, 0] + ", " + df.iloc[56, 0]
    y_values_5 = df.iloc[76, :]
    y_values_5_float = y_values_5.astype(float)
    create_and_save_graph(df.columns, y_values_5_float, fifth_graph_name, worksheet, 76)

    sixth_graph_name = df.iloc[60, 0] + ", " + df.iloc[64, 0] + ", " + df.iloc[68, 0]
    y_values_6 = df.iloc[77, :]
    y_values_6_float = y_values_6.astype(float)
    create_and_save_graph(df.columns, y_values_6_float, sixth_graph_name, worksheet, 77)
