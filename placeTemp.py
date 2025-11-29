import os
import random
import shutil
import pyvidplayer2
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import tkinter as tk

# utility for placing files into a folder structure from a temp folder
# previews images and videos within tkinter or pyvidplayer preview
# detects duplicate filenames and deletes from temp if they are the same (if not the same file, don't delete so you may rename it)

# it is recommended to look for duplicate files using a program like czkawka first
# https://github.com/qarmin/czkawka

TEMP = filedialog.askdirectory(title="Select Temp Folder")
DEST = filedialog.askdirectory(title="Select Default Destination Folder")
lastDest = DEST

randomOrder = input("Randomorder (empty for ordered):")

root = tk.Tk()
root.geometry(f"+0+0")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
img_label = tk.Label()

dirlist = os.listdir(TEMP)
if randomOrder:
    random.shuffle(dirlist)
for filename in dirlist:
    if any(filename.endswith(ext) for ext in [".txt", ".py"]):
        continue
    file_path = os.path.join(TEMP, filename)
    video = any(filename.endswith(ext) for ext in [".mp4", ".gif", ".mov"]) or False
    if not video:
        try:
            img = Image.open(file_path)
            scale_factor = 0.5 * min(
                screen_width / img.width, screen_height / img.height
            )
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            img = img.resize((new_width, new_height), Image.Resampling.NEAREST)
            img_tk = ImageTk.PhotoImage(img)
            img_label.config(image=img_tk)
            img_label.image = img_tk  # type: ignore
            img_label.pack()
        except Exception as e:
            print(e)
            video = True
    if video:
        try:
            video = pyvidplayer2.Video(file_path)
            original_width, original_height = video.current_size
            scale_factor = 0.5 * min(
                screen_width / original_width, screen_height / original_height
            )
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            video.resize((new_width, new_height))
            video.preview()
        except Exception as e:
            print(f"Failed to open {filename} as video: {e}")
            if input("Open (blank for don't):"):
                os.startfile(file_path)
            continue

    root.update_idletasks()

    try:
        dest = filedialog.askdirectory(title=f"Select folder for {filename} in {DEST}", initialdir=lastDest)
        lastDest = dest
        if not dest:
            exit()
        if os.path.exists(os.path.join(dest, filename)):
            print(f"{filename} already exists in {dest}.")
            os.startfile(os.path.join(dest, filename), "open")
            if messagebox.askyesno("File exists", f"{filename} already exists in {dest}. Is it the same?"):
                pass  # User confirmed it's the same, do nothing
            else:
                # different file with same name. DO NOT DELETE FROM TEMP, so the user can rename it.
                print(f"File {filename} in {dest} is different. Not deleting from TEMP.")
                continue
        else:
            shutil.copy2(file_path, dest)
            print(f"Successfully copied {filename}")

        if os.path.exists(os.path.join(dest, filename)):
            try:
                os.remove(file_path)
                print(f"Successfully removed original {filename}")
            except Exception as e:
                print(f"Failed to delete {filename} from temp: {e}")
        else:
            print(f"Copied files not found, not deleting temp.")
    except Exception as e:
        print(f"Failed to copy {filename}: {e}")

reset = filedialog.askdirectory(initialdir=DEST, title="Select folder to open filedialog at next time")
