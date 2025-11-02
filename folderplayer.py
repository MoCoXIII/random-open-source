import os, random, pyvidplayer2
import tkinter as tk
from tkinter import filedialog
import threading
from PIL import Image, ImageTk

# folder player that literally displays every file in a folder and its subfolders
# you will be prompted to choose if you want to shuffle the order of the files for a more random experience
# to not shuffle, just leave the input blank and press enter - then a tkinter window should open (look for it in the task bar)

root = tk.Tk()
root.withdraw()

folder_path = filedialog.askdirectory(title="Select Folder")
file_list = [os.path.join(root, f) for root, dirs, files in os.walk(folder_path) for f in files]

if input("Shuffle (blank for no): "):
    random.shuffle(file_list)

file_index = 0
def show_file():
    global file_index
    file_path = file_list[file_index]
    file_index_entry.delete(0, tk.END)
    file_index_entry.insert(0, str(file_index))

    file_label['text'] = file_path
    if file_path.lower().endswith(('.txt', '.log')):
        with open(file_path, 'r') as f:
            text = f.read()
        text_box.delete('1.0', tk.END)
        text_box.insert('1.0', text)
        img_label.grid_forget()
        text_box.grid(row=0, column=1)
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', ".webp")):#, '.gif'
        img = Image.open(file_path)
        width, height = img.size
        old_width, old_height = width, height
        scale = 0.5
        if width > height * 1.2:
            screen_width = root.winfo_screenwidth()
            width = int(scale * screen_width)
            height = int(width * height / old_width)
        else:
            screen_height = root.winfo_screenheight()
            height = int(scale * screen_height)
            width = int(height * width / old_height)
        img = img.resize((width, height), Image.Resampling.NEAREST)
        img_tk = ImageTk.PhotoImage(img)
        img_label.config(image=img_tk)
        img_label.image = img_tk
        text_box.grid_forget()
        img_label.grid(row=0, column=1, rowspan=4)
    elif file_path.lower().endswith(('.mp4', '.mov', '.avi', '.webm', ".mkv", ".gif")):
        # os.startfile(file_path)
        def playvid():
            pyvidplayer2.Video(file_path).preview()
        threading.Thread(target=playvid).run()
        text_box.grid_forget()
        img_label.grid_forget()
    else:
        print(f"Cannot display {file_path}")

def previous_file():
    global file_index
    file_index -= 1
    if file_index < 0:
        file_index = len(file_list) - 1
    show_file()

def go_to_file():
    global file_index
    try:
        file_index = int(file_index_entry.get())
        file_index %= len(file_list)
        show_file()
    except ValueError:
        pass

def next_file():
    global file_index
    file_index += 1
    if file_index >= len(file_list):
        file_index = 0
    show_file()

file_label = tk.Label(root, text="")
file_label.grid(row=0, column=0)
text_box = tk.Text(root)
img_label = tk.Label(root, image=None)

file_index_entry = tk.Entry(root)
file_index_entry.insert(0, '0')
file_index_entry.grid(row=1, column=0)
file_index_button = tk.Button(root, text="Go to file", command=go_to_file)
file_index_button.grid(row=2, column=0)

next_button = tk.Button(root, text="Next", command=next_file)
next_button.grid(row=3, column=0)
previous_button = tk.Button(root, text="Previous", command=previous_file)
previous_button.grid(row=4, column=0)

root.deiconify()
root.geometry("+0+0")
root.mainloop()
