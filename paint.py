import math
from tkinter import simpledialog
import pyautogui
import time
import keyboard
import tkinter.filedialog
from PIL import Image

running = True


def takeScreenshot(e):
    global screenimg
    screenimg = pyautogui.screenshot(allScreens=True)


print("Take screenshot with 0")
keyboard.on_release_key("0", takeScreenshot)


def addColor(e):
    global colors
    x, y = pyautogui.position()
    colors.append((x, y, screenimg.getpixel((x, y))))


colors = []
print("add colors with 1")
keyboard.on_release_key("1", addColor)


def setBl(e):
    bl = pyautogui.position()
    global canvas
    canvas[0] = bl[0]
    canvas[3] = bl[1]
    updateDimensions()


def setTr(e):
    tr = pyautogui.position()
    global canvas
    canvas[1] = tr[1]
    canvas[2] = tr[0]
    updateDimensions()


def updateDimensions():
    global width, height, canvas
    left, top, right, bottom = canvas
    width = right - left
    height = bottom - top


canvas = [0, 0, 0, 0]
print("set canvas bottom left with 2")
keyboard.on_release_key("2", setBl)
print("set canvas top right with 3")
keyboard.on_release_key("3", setTr)


def setTargetPath(e):
    global targetPath, target, targetimg, pixels
    targetPath = tkinter.filedialog.askopenfilename(
        filetypes=[("Images", [".png", ".jpg", ".jpeg", ".webp"])]
    )
    target = Image.open(targetPath)
    targetimg = target.convert("RGBA").resize((width, height), Image.Resampling.NEAREST)
    pixels = targetimg.load()


print("Choose image with 4")
keyboard.on_release_key("4", setTargetPath)


def color_distance(c1, c2):
    return math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2)


def closest_palette_color(pixel, colors):
    best = None
    best_dist = float("inf")
    for cx, cy, col in colors:
        d = color_distance(pixel, col)
        if d < best_dist:
            best_dist = d
            best = (cx, cy, col)
    return best


def draw(e):
    global colors, target, width, height, canvas, pixels
    left, top, right, bottom = canvas
    width = right - left
    height = bottom - top
    last_color = None
    lines = []
    for y in range(0, height, stepY):
        x = 0
        while x < width:
            px = pixels[x, y]
            if px[3] == 0:  # completely transparent
                x += stepX
                continue
            cx, cy, palette_color = closest_palette_color(px, colors)
            nx, ny, nextColor = closest_palette_color(pixels[x, y], colors)
            sameColor = nextColor == palette_color
            run_start = x
            while x < width and sameColor:
                x += stepX
                try:
                    nx, ny, nextColor = closest_palette_color(pixels[x, y], colors)
                except IndexError:
                    break
                sameColor = nextColor == palette_color
            lines.append(
                (
                    (cx, cy, palette_color),
                    (left + run_start, top + y, left + x - stepX, top + y),
                )
            )

    lines.sort(key=lambda l: (l[1][2] - l[1][0], l[0][2]), reverse=True)
    last_color = None
    for color, (x1, y1, x2, y2) in lines:
        if color != last_color:
            last_color = color
            pyautogui.click(color[0], color[1], duration=0, _pause=True)
        pyautogui.click(x1, y1, duration=0, _pause=True)
        pyautogui.mouseDown(_pause=True)
        pyautogui.moveTo(x2, y2, duration=0, _pause=True)
        pyautogui.mouseUp(_pause=True)

        # emergency stop
        if keyboard.is_pressed("esc"):
            print("Stopped")
            global running
            running = False
            return

    running = False


def preview(e):
    global height, width, stepX, stepY, pixels
    img_preview = Image.new("RGBA", (width // stepX, height // stepY), "white")
    for y in range(0, height, stepY):
        for x in range(0, width, stepX):
            px = pixels[x, y]
            if px[3] == 0:  # completely transparent
                continue
            cx, cy, palette_color = closest_palette_color(px, colors)
            try:
                img_preview.putpixel((x // stepX, y // stepY), palette_color)
            except IndexError:
                pass
    img_preview.show()


print("preview with 5")
keyboard.on_release_key("5", preview)

stepX = 5
stepY = 5


def set_step_size(e):
    global stepX, stepY
    stepX, stepY = map(
        int,
        str(simpledialog.askstring("Step size", "Enter step size (x,y):")).split(","),
    )


print("draw with 6")
keyboard.on_release_key("6", draw)

print("set step size with 7")
keyboard.on_release_key("7", set_step_size)
while running:
    time.sleep(1)
