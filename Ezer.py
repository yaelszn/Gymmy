from PIL import Image

# Load the image
image_path = 'Pictures/background.jpg'
image = Image.open(image_path)

# Get the pixel color at the top-left corner (or other background location)
background_color = image.getpixel((0, 0))  # (x, y) coordinates of the pixel

print("Background color (RGB):", background_color)