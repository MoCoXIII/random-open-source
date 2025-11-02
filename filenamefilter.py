import os
from tkinter import filedialog
import re

# this script isolates the text between square brackets in a folder and ask the user if they want to rename the file each time

# Example:
# useless title [video url].mp4 -> video url.mp4

pattern = r".*\[(.*)\](.*)"

folder = filedialog.askdirectory()

for oldName in os.listdir(folder):
    match = re.match(pattern, oldName)
    if match:
        newName = match.group(1) + match.group(2)
        if newName:
            if input(f"{oldName} -> {newName}"):
                os.rename(os.path.join(folder, oldName), os.path.join(folder, newName))
                print(f"Renamed {oldName} to {newName}")
