from PIL import Image
import os
from tkinter import filedialog

# resize selected image to selected width and keep aspect ratio

# path = str(input("Image path: "))
path = filedialog.askopenfilename()

if os.path.isfile(path):
    with Image.open(path) as img:
        img = img.convert("RGBA")
        w = int(input("Width: "))
        h = img.height * w // img.width
        img = img.resize((w, h), Image.Resampling.NEAREST)
        savepath = os.path.join(os.path.dirname(path), os.path.basename(path))
        savepath = str(input(f"Save path [{savepath}]: ") or savepath)
        img.save(savepath)
