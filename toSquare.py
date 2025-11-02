import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

root = tk.Tk()
root.withdraw()

# utility for making all pngs in a folder square, letting you choose which side to crop from to achieve a square
# provides skip button in case you need to crop manually, moving the skipped item into a new subfolder

folder_path = filedialog.askdirectory(title="Select Folder")
skipped_folder = os.path.join(folder_path, "skipped")
if not os.path.exists(skipped_folder):
    os.makedirs(skipped_folder)

cancel = False
filenames = os.listdir(folder_path)
index = 0


def process_next_file():
    global cancel, index, img
    if cancel or index >= len(filenames):
        return
    filename = filenames[index]
    index += 1
    if filename.lower().endswith(".png"):
        image_path = os.path.join(folder_path, filename)
        img = Image.open(image_path)
        if img.width != img.height:
            window = tk.Toplevel(root)
            window.title(filename)
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            scale_factor = 0.5 * min(
                screen_width / img.width, screen_height / img.height
            )
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            img_resized = img.resize((new_width, new_height), Image.Resampling.NEAREST)
            img_tk = ImageTk.PhotoImage(img_resized)
            img_label = tk.Label(window, image=img_tk)
            img_label.grid(row=0, column=0)
            if img.width > img.height:
                question = "This image is landscape, do you want to crop left or right?"
                options = ["Left", "Right", "Skip"]
            else:
                question = "This image is portrait, do you want to crop top or bottom?"
                options = ["Top", "Bottom", "Skip"]
            answer = tk.StringVar()
            answer.set(options[0])
            option_menu = tk.OptionMenu(window, answer, *options)
            option_menu.grid(row=1, column=0)

            scale_factor = 0.5 * min(
                screen_width / img.width, screen_height / img.height
            )
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            img_resized = img.resize((new_width, new_height), Image.Resampling.NEAREST)
            img_preview = ImageTk.PhotoImage(img_resized.copy())
            img_preview_label = tk.Label(window, image=img_preview)
            img_preview_label.grid(row=0, column=1, columnspan=2)

            def update_preview(*args):
                crop = get_crop(new_width, new_height)
                img_preview = ImageTk.PhotoImage(img_resized.copy().crop(crop))
                img_preview_label.config(image=img_preview)
                img_preview_label.image = img_preview  # type: ignore

            def get_crop(width, height):
                crop = (0, 0, width, height)
                if answer.get() == "Left":
                    crop = (width - height, 0, width, height)
                elif answer.get() == "Right":
                    crop = (0, 0, height, height)
                elif answer.get() == "Top":
                    crop = (0, height - width, width, height)
                elif answer.get() == "Bottom":
                    crop = (0, 0, width, width)
                return crop

            update_preview()

            answer.trace_add("write", update_preview)

            def ok():
                global img
                if answer.get() == "Skip":
                    os.rename(image_path, os.path.join(skipped_folder, filename))
                else:
                    crop = get_crop(img.width, img.height)
                    img = img.crop(crop)
                    img.save(image_path)
                    print(f"{filename} has been cropped to be square")
                window.destroy()
                process_next_file()

            ok_button = tk.Button(window, text="OK", command=ok)
            ok_button.grid(row=1, column=1)

            def _break():
                global cancel
                cancel = True
                window.destroy()

            cancel_button = tk.Button(window, text="Cancel", command=_break)
            cancel_button.grid(row=1, column=2)
            window.wait_window(window)
        else:
            print(f"{filename} is already square")
            process_next_file()
    else:
        process_next_file()


process_next_file()
