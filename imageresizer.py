import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image

# resizes all images inside a folder to be a square with power of two sidelengths
# useful for minecraft textures
# WILL NOT ASK YOU FOR CONFIRMATION, IMAGE MODIFICATION IS NOT REVERSIBLE

def is_square(image_path):
    with Image.open(image_path) as img:
        return img.width == img.height


def next_smallest_power_of_2(n):
    power = 1
    while power < n and power <= 1024:
        power *= 2
    return power if power == n else power // 2


def resize_image(image_path, new_size):
    with Image.open(image_path) as img:
        img = img.resize((new_size, new_size), resample=Image.Resampling.NEAREST)
        img.save(image_path)
        print(f"Resized {os.path.basename(image_path)} to {new_size}x{new_size}")


def process_images_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            if is_square(image_path):
                with Image.open(image_path) as img:
                    next_power_2 = next_smallest_power_of_2(img.width)
                    if img.width != next_power_2:
                        resize_image(image_path, next_power_2)


def main():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Folder")
    if folder_path:
        process_images_in_folder(folder_path)

main()
