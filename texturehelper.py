import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image

root = tk.Tk()
root.withdraw()

new_images_folder = filedialog.askdirectory(title="Select folder with new images")
texture_folder = filedialog.askdirectory(title="Select folder with textures")

# utility for replacing pngs in one folder with pngs from another folder
# same aspect ratio recommended to avoid stretched images, but not needed
# for each file in the new images folder, it will find the best matching texture from the texture folder,
# and replace it with the new image (scaling it to the size of the new image) while maintaining transparency for each pixel (multiplicative)

new_images = [
    os.path.join(new_images_folder, f)
    for f in os.listdir(new_images_folder)
    if os.path.isfile(os.path.join(new_images_folder, f)) and f.lower().endswith(".png") and Image.open(os.path.join(new_images_folder, f)).width == Image.open(os.path.join(new_images_folder, f)).height
]
textures = [
    os.path.join(texture_folder, f)
    for f in os.listdir(texture_folder)
    if os.path.isfile(os.path.join(texture_folder, f)) and f.lower().endswith(".png") and Image.open(os.path.join(texture_folder, f)).width == 16 and Image.open(os.path.join(texture_folder, f)).height == 16
]

textures = list(dict.fromkeys(textures))

for image in new_images:
    if Image.open(image).width == Image.open(image).height:
        img = Image.open(image).convert("RGBA")
        avg_color = [sum(x)/len(x) for x in list(img.resize((1, 1)).convert("RGBA").getdata())[:3]]
        best_match = min(textures, key=lambda x: sum(abs(a-b) for a, b in zip(avg_color, [sum(x)/len(x) for x in list(Image.open(x).convert("RGBA").resize((1, 1)).getdata())[:3]])))
        
        with Image.open(best_match).convert("RGBA") as tex:
            tex = tex.resize(img.size, Image.Resampling.NEAREST)
            tex_data = tex.getdata()
            img_data = img.getdata()

            new_data = [
                (img_pixel[0], img_pixel[1], img_pixel[2], int(tex_pixel[3] * img_pixel[3] / 255))
                for tex_pixel, img_pixel in zip(tex_data, img_data)
            ]
            
            img.putdata(new_data)
            if all(x[3] == 255 for x in new_data):
                img = img.convert("RGB")
            img.save(best_match)
            textures.remove(best_match)
            os.remove(image)
            print(f"Successfully replaced {best_match} with {image}")
            if len(textures) == 0:
                print("No more textures to replace")
                exit(1)
print("Source images processed")
