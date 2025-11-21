import subprocess
import os
from tkinter import messagebox, filedialog

# file "deleting" utility for your download folder.
# set maxSizeMB to the maximum file size you want to allow in your folder (Megabytes),
# then run this script.
# for each item larger than the max, you will be asked if its data should be erased.
# this is used to delete large files without actually losing that you downloaded them,
# so you can look through your download folder and see what you downloaded without it occupying space
# and maybe re-download it later.

# be careful to not delete important files

maxSizeMB = 2
maxSizeKB = maxSizeMB * 1024
maxSizeBytes = maxSizeKB * 1024

folder = filedialog.askdirectory()

for filename in os.listdir(folder):
    filepath = os.path.normpath(os.path.join(folder, filename))
    filesize = os.path.getsize(filepath)
    if filesize > maxSizeBytes and not filename.endswith((".pdf", ".zip", ".jpg", ".jpeg", ".png")):
        print(f"{filename} is larger than {maxSizeMB} MB")
        # subprocess.run(["explorer.exe", "/select,", filepath])
        if messagebox.askyesno("File too large", f"File {filename} ({filesize / 1024 / 1024:.2f} MB) is larger than {maxSizeMB} MB. Clear content?"):
            subprocess.run(["powershell.exe", f"Clear-Content -Path \"{filepath}\""], check=True)
print("Done checking everything.")
