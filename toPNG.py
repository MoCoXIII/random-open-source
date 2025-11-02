import os
from tkinter import filedialog
from PIL import Image

# converts all found images of the below filetypes in your folder to png
# Note: deletes original image, even if conversion somehow fails

directory = filedialog.askdirectory(title="Select Folder")

for filename in os.listdir(directory):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff')):
        image_path = os.path.join(directory, filename)
        image = Image.open(image_path)
        image.save(os.path.join(directory, os.path.splitext(filename)[0] + '.png'), 'PNG')
        os.remove(image_path)
