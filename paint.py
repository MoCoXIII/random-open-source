import math
from tkinter import simpledialog
import pyautogui
import time
import keyboard
import tkinter.filedialog
from PIL import Image

stepX = 1
stepY = 1
avgStep = (stepX + stepY) // 2


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
    print("Draw started. Let go of the keyboard and mouse.")
    global colors, target, width, height, canvas, pixels, left, top
    left, top, right, bottom = canvas
    width = right - left
    height = bottom - top
    last_color = None
    lines = getLines()

    lines.sort(
        key=lambda l: ((l[1][2] - l[1][0]) ** 2 + (l[1][3] - l[1][1]) ** 2, l[0][2]),
        reverse=True,
    )
    last_color = None
    pause = True
    for color, (x1, y1, x2, y2) in lines:
        if color != last_color:
            last_color = color
            pyautogui.click(color[0], color[1], duration=0, _pause=pause)
        pyautogui.click(x1, y1, duration=0, _pause=pause)
        pyautogui.mouseDown(_pause=pause)
        pyautogui.moveTo(x2, y2, duration=0, _pause=pause)
        pyautogui.mouseUp(_pause=pause)
    print("Done drawing. Press 6 to draw again, hold escape to leave")


def getLines():
    return contourLines()
    return horizontalLines()


def contourLines(min_length=5, max_deviation=avgStep):
    """
    Returns a list of contour line segments:
    [(color, (x1, y1, x2, y2)), ...]
    """
    NEIGHBORS = [
        (-1, -1),
        (0, -1),
        (1, -1),
        (-1, 0),
        (1, 0),
        (-1, 1),
        (0, 1),
        (1, 1),
    ]

    w, h = targetimg.size
    pixels = targetimg.load()

    # Map every pixel to its closest palette color
    palette_map = [
        [closest_palette_color(pixels[x, y], colors) for x in range(0, w, stepX)]
        for y in range(0, h, stepY)
    ]

    # Track visited boundary *edges*
    visited_edge = set()

    lines = []

    def distance_point_to_line(px, py, x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            return math.hypot(px - x1, py - y1)
        num = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
        den = math.hypot(y2 - y1, x2 - x1)
        return num / den

    for y in range(0, h, stepY):
        for x in range(0, w, stepX):
            base_color = palette_map[y // stepY][x // stepX]

            # Look for boundary directions
            for dx, dy in NEIGHBORS:
                nx, ny = x + dx * stepX, y + dy * stepY
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if palette_map[ny // stepY][nx // stepX] == base_color:
                    continue

                edge_key = (x, y, dx * stepX, dy * stepY)
                if edge_key in visited_edge:
                    continue

                # Trace one boundary loop
                contour = []
                stack = [(x, y, dx * stepX, dy * stepY)]

                while stack:
                    cx, cy, cdx, cdy = stack.pop()
                    key = (cx, cy, cdx, cdy)
                    if key in visited_edge:
                        continue

                    nx, ny = cx + cdx, cy + cdy
                    if not (0 <= nx < w and 0 <= ny < h):
                        continue
                    if palette_map[ny // stepY][nx // stepX] == base_color:
                        continue

                    visited_edge.add(key)
                    contour.append((cx, cy))

                    # Walk along the boundary
                    for ndx, ndy in NEIGHBORS:
                        tx, ty = cx + ndx * stepX, cy + ndy * stepY
                        if not (0 <= tx < w and 0 <= ty < h):
                            continue
                        if palette_map[ty // stepY][tx // stepX] != base_color:
                            continue

                        ox, oy = tx + cdx, ty + cdy
                        if not (0 <= ox < w and 0 <= oy < h):
                            continue
                        if palette_map[oy // stepY][ox // stepX] != base_color:
                            stack.append((tx, ty, cdx, cdy))

                # Fit maximal straight segments along this contour
                if len(contour) < min_length:
                    continue

                contour.sort()  # stabilizes traversal

                i = 0
                while i < len(contour) - min_length:
                    x1, y1 = contour[i]
                    x2, y2 = contour[i + 1]

                    j = i + 2
                    while j < len(contour):
                        px, py = contour[j]
                        d = distance_point_to_line(px, py, x1, y1, x2, y2)
                        if d > max_deviation:
                            break
                        x2, y2 = px, py
                        j += 1

                    length = math.hypot(x2 - x1, y2 - y1)
                    if length >= min_length:
                        lines.append(
                            (base_color, (x1 + left, y1 + top, x2 + left, y2 + top))
                        )

                    i = j

    return lines


def getAvgColor(img, x, y, w, h):
    return img.getpixel((x + w // 2, y + h // 2))


def horizontalLines():
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

    return lines


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


def set_step_size(e):
    global stepX, stepY, avgStep
    stepX, stepY = map(
        int,
        str(simpledialog.askstring("Step size", "Enter step size (x,y):")).split(","),
    )
    avgStep = (stepX + stepY) // 2


print("draw with 6")
keyboard.on_release_key("6", draw)

print("set step size with 7")
keyboard.on_release_key("7", set_step_size)
while not keyboard.is_pressed("esc"):
    time.sleep(1)
