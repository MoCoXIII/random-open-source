import os
from PIL import Image
import numpy as np

# for every image in folder1, find the image with the closest average color in folder2.
# only works for pngs

def closest_color(folder1, folder2):
    avg_colors_1 = {}
    avg_colors_2 = {}
    
    for filename in os.listdir(folder1):
        if filename.lower().endswith(".png"):
            img1 = Image.open(os.path.join(folder1, filename))
            avg_color_1 = np.array(img1.resize((1, 1)).convert("RGB").getdata()).mean(axis=(0, 1))
            avg_colors_1[filename] = avg_color_1
    
    for f in os.listdir(folder2):
        if f.lower().endswith(".png"):
            img2 = Image.open(os.path.join(folder2, f))
            avg_color_2 = np.array(img2.resize((1, 1)).convert("RGB").getdata()).mean(axis=(0, 1))
            avg_colors_2[f] = avg_color_2
    
    for filename, avg_color_1 in avg_colors_1.items():
        closest_dist = float("inf")
        closest = ""
        for f, avg_color_2 in avg_colors_2.items():
            dist = np.linalg.norm(avg_color_1 - avg_color_2)
            if dist < closest_dist:
                closest_dist = dist
                closest = f
        print(f"{os.path.join(folder1, filename)} closest to {os.path.join(folder2, closest)}")
