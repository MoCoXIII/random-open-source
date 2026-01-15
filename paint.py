import math
import pyautogui
import time
import keyboard
import tkinter.filedialog
from PIL import Image

running = True
canvas = (0, 0, 0, 0)
targetPath = tkinter.filedialog.askopenfilename(
    filetypes=[("Images", [".png", ".jpg", ".jpeg", ".webp"])]
)
target = Image.open(targetPath)

def takeScreenshot():
    global img
    img = pyautogui.screenshot(allScreens=True)

print("Take screenshot with 0")
keyboard.add_hotkey('0', takeScreenshot)

print("hover color selection boxes and press 1, 2 when finished")
# wait for user to click and record where the click happened
colors = []


def addColor(e):
    global colors
    x, y = pyautogui.position()
    colors.append((x, y, img.getpixel((x, y))))


keyboard.hook_key("1", addColor)


def sizeCanvas(e):
    keyboard.unhook_all()
    print("select bottom left corner of canvas (3)")
    # wait for numpad 3 to be pressed
    while True:
        if keyboard.is_pressed("3"):
            break
    bl = pyautogui.position()
    print("select top right corner of canvas (4)")
    # wait for numpad 4 to be pressed
    while True:
        if keyboard.is_pressed("4"):
            break
    tr = pyautogui.position()
    global canvas
    canvas = (bl[0], tr[1], tr[0], bl[1])  # left, top, right, bottom
    draw()


keyboard.hook_key("2", sizeCanvas)


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


def draw():
    global colors, target, canvas

    left, top, right, bottom = canvas
    width = right - left
    height = bottom - top

    # Resize target to canvas size
    img = target.convert("RGBA").resize((width, height), Image.Resampling.NEAREST)
    pixels = img.load()

    print("Drawing starts in 3 seconds...")
    time.sleep(3)

    last_color = None
    stepX = 15
    stepY = 15

    for y in range(0, height, stepY):
        # for x in range(0, width, step):
        x = 0
        pyautogui.moveTo(left + x, top + y, duration=0)
        while x < width:
            run_start = x
            px = pixels[x, y]
            if px[3] == 0:  # completely transparent
                x += stepX
                continue
            cx, cy, palette_color = closest_palette_color(px, colors)
            nx, ny, nextColor = closest_palette_color(pixels[x, y], colors)
            sameColor = nextColor == palette_color
            while x < width and sameColor:
                x += stepX
                try:
                    nx, ny, nextColor = closest_palette_color(pixels[x, y], colors)
                except IndexError:
                    break
                sameColor = nextColor == palette_color

            # Select color only if it changed
            if last_color != palette_color:
                pyautogui.click(cx, cy, duration=0)
                pyautogui.click(left + run_start, top + y)
                # pyautogui.click(left + x, top + y)
                last_color = palette_color

            pyautogui.mouseDown()
            pyautogui.moveTo(left + x - stepX, top + y, duration=0)
            pyautogui.mouseUp()
            # pyautogui.click(left + x, top + y)

            # emergency stop
            if keyboard.is_pressed("esc"):
                print("Stopped")
                global running
                running = False
                return
    
    running = False

while running:
    time.sleep(1)
