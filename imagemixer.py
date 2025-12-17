import os
import random
import tempfile
import time
import threading
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image
from customtkinter import *  # type: ignore
from CTkXYFrame import *  # get it from https://github.com/Akascape/CTkXYFrame

# takes in two images and simulates creating a new image using the colors form the first image spreading to approximate the second image as best as possible
# configure maximum simulations dimension at the very bottom

row, col = 0, 0
def rc(newline:bool=False):
    global row, col
    if not newline:
        col += 1
    else:
        row += 1
        col = 0

def get_neighbors_in_radius(img, x, y):
    neighbors = [(x, y)]
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            new_x, new_y = x + i, y + j
            if (i, j) != (0, 0) and 0 <= new_x < img.width and 0 <= new_y < img.height:
                neighbors.append((new_x, new_y))
    return neighbors


def best_color_in_radius(img1, img2, x, y, seperate=False):
    best_r_diff = float("inf")
    best_g_diff = float("inf")
    best_b_diff = float("inf")
    best_a_diff = float("inf")
    best_r_neighbor = None
    best_g_neighbor = None
    best_b_neighbor = None
    best_a_neighbor = None
    best_neighbor = None
    best_diff = float("inf")
    target_color = img2.getpixel((x, y))

    for neighbor_x, neighbor_y in get_neighbors_in_radius(img1, x, y):
        source_color = img1.getpixel((neighbor_x, neighbor_y))
        r_diff = abs(source_color[0] - target_color[0])
        g_diff = abs(source_color[1] - target_color[1])
        b_diff = abs(source_color[2] - target_color[2])
        a_diff = abs(source_color[3] - target_color[3])
        if seperate:
            if r_diff < best_r_diff:
                best_r_diff = r_diff
                best_r_neighbor = (neighbor_x, neighbor_y)
            if g_diff < best_g_diff:
                best_g_diff = g_diff
                best_g_neighbor = (neighbor_x, neighbor_y)
            if b_diff < best_b_diff:
                best_b_diff = b_diff
                best_b_neighbor = (neighbor_x, neighbor_y)
            if a_diff < best_a_diff:
                best_a_diff = a_diff
                best_a_neighbor = (neighbor_x, neighbor_y)
        else:
            total_diff = r_diff + g_diff + b_diff + a_diff
            if total_diff < best_diff:
                best_diff = total_diff
                best_neighbor = (neighbor_x, neighbor_y)
    if seperate:
        if best_r_neighbor and best_g_neighbor and best_b_neighbor and best_a_neighbor:
            return (
                img1.getpixel(best_r_neighbor)[0],
                img1.getpixel(best_g_neighbor)[1],
                img1.getpixel(best_b_neighbor)[2],
                img1.getpixel(best_a_neighbor)[3],
            )
        else:
            return None
    else:
        if best_neighbor:
            return img1.getpixel(best_neighbor)
        else:
            return None


# New helper: compute positions within radius of a given pixel (bounded)
def get_positions_in_radius(x, y, width, height):
    positions = []
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            nx, ny = x + i, y + j
            if 0 <= nx < width and 0 <= ny < height:
                positions.append((nx, ny))
    return positions


# New incremental approximate function: process only pixels in pixels_to_check
def approximate_image_incremental(img1, img2, pixels_to_check):
    """
    Process only pixels in pixels_to_check based on the snapshot img1 and target img2.
    Returns (new_img, changed_set) where changed_set is a set of coords that changed.
    """
    new_img = img1.copy()
    changed = set()
    pixels_to_ignore = set()
    best_pixels = set()
    if not swap:
        for x, y in pixels_to_check:
            # If already identical to target, keep same pixel (and it won't change)
            if img1.getpixel((x, y)) == img2.getpixel((x, y)):
                # ensure new_img has the same pixel (copy preserves it, but keep consistent by not modifying it)
                continue
            best_color = best_color_in_radius(img1, img2, x, y)
            if best_color:
                if best_color != img1.getpixel((x, y)):
                    new_img.putpixel((x, y), best_color)
                    changed.add((x, y))
            else:
                # no better neighbor found, keep original
                continue
    else:
        for x, y in pixels_to_check:
            # If already identical to target, keep same pixel (and it won't change)
            if img1.getpixel((x, y)) == img2.getpixel((x, y)) or (x, y) in pixels_to_ignore:
                # ensure new_img has the same pixel (copy preserves it, but keep consistent by not modifying it)
                continue
            best_pixel = None
            best_diff = float("inf")
            for nx, ny in get_positions_in_radius(x, y, img1.width, img1.height):
                if (nx, ny) in pixels_to_ignore:
                    continue
                diff_not_switched = abs(img1.getpixel((nx, ny))[0] - img2.getpixel((x, y))[0]) + abs(
                    img1.getpixel((nx, ny))[1] - img2.getpixel((x, y))[1]
                ) + abs(img1.getpixel((nx, ny))[2] - img2.getpixel((x, y))[2]) + abs(
                    img1.getpixel((nx, ny))[3] - img2.getpixel((x, y))[3]
                )
                diff_switched = abs(img1.getpixel((nx, ny))[0] - img2.getpixel((nx, ny))[0]) + abs(
                    img1.getpixel((nx, ny))[1] - img2.getpixel((nx, ny))[1]
                ) + abs(img1.getpixel((nx, ny))[2] - img2.getpixel((nx, ny))[2]) + abs(
                    img1.getpixel((nx, ny))[3] - img2.getpixel((nx, ny))[3]
                )
                if diff_not_switched > diff_switched and diff_switched < best_diff:
                    best_diff = diff_switched
                    best_pixel = (nx, ny)
            if best_pixel:
                new_img.putpixel((x, y), img1.getpixel(best_pixel))
                changed.add((x, y))
                new_img.putpixel(best_pixel, img1.getpixel((x, y)))
                changed.add(best_pixel)
                pixels_to_ignore.add(best_pixel)
                best_pixels.add(best_pixel)
    return new_img, changed, best_pixels


def approximate_image(img1, img2):
    new_img = Image.new("RGBA", (img1.width, img1.height))
    for y in range(img1.height):
        for x in range(img1.width):
            if img1.getpixel((x, y)) == img2.getpixel((x, y)):
                new_img.putpixel((x, y), img1.getpixel((x, y)))
                # print("Saving time by not checking perfect pixel", (x, y), end="\r")
                continue
            best_color = best_color_in_radius(img1, img2, x, y)
            if best_color:
                new_img.putpixel((x, y), best_color)
            else:
                new_img.putpixel((x, y), img1.getpixel((x, y)))
    return new_img


def main():
    set_appearance_mode("Dark")
    root = CTk()
    root.geometry(
        f"800x600+{root.winfo_screenwidth()//2-400}+{root.winfo_screenheight()//2-300}"
    )

    frame = CTkXYFrame(root)
    frame.pack(expand=True, fill="both")
    filetypes = [("All image files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.gif;*.tiff")]
    rngFileTypes = (".png", ".jpg", ".jpeg", ".webp", ".gif")
    possiblechoices = ""
    possibleFirstChoices = ""
    possibleSecondChoices = ""
    match selection:
        case "r":
            randomchoicefolder = filedialog.askdirectory(title="Select Folder")
            if not randomchoicefolder:
                root.destroy()
                return
            possiblechoices = []
            for r, dirs, files in os.walk(randomchoicefolder):
                for f in files:
                    if f.lower().endswith(rngFileTypes):
                        possiblechoices.append(os.path.join(r, f))
            img1_path = random.choice(possiblechoices)
            img2_path = random.choice(possiblechoices)
            print("Img1:", img1_path)
            img1 = Image.open(img1_path).convert("RGBA")
            print("Img2:", img2_path)
            img2 = Image.open(img2_path).convert("RGBA")
        case "r2":
            randomFirstFolder = filedialog.askdirectory(title="First Folder")
            randomSecondFolder = filedialog.askdirectory(title="Second Folder")
            if not randomFirstFolder or not randomSecondFolder:
                root.destroy()
                return
            possibleFirstChoices = []
            possibleSecondChoices = []
            for r, dirs, files in os.walk(randomFirstFolder):
                for f in files:
                    if f.lower().endswith(rngFileTypes):
                        possibleFirstChoices.append(os.path.join(r, f))
            for r, dirs, files in os.walk(randomSecondFolder):
                for f in files:
                    if f.lower().endswith(rngFileTypes):
                        possibleSecondChoices.append(os.path.join(r, f))
            img1_path = random.choice(possibleFirstChoices)
            img2_path = random.choice(possibleSecondChoices)
            print("Img1:", img1_path)
            img1 = Image.open(img1_path).convert("RGBA")
            print("Img2:", img2_path)
            img2 = Image.open(img2_path).convert("RGBA")
        case "s":
            img1_path = filedialog.askopenfilename(
                title="Select first image", filetypes=filetypes
            )
            if not img1_path:
                root.destroy()
                return
            img2_path = filedialog.askopenfilename(
                title="Select second image", filetypes=filetypes
            )
            if not img2_path:
                root.destroy()
                return
            print("Img1:", img1_path)
            img1 = Image.open(img1_path).convert("RGBA")
            print("Img2:", img2_path)
            img2 = Image.open(img2_path).convert("RGBA")
        case _:
            img1 = Image.new("RGBA", (128, 128))
            img2 = Image.new("RGBA", (128, 128))
            for x in range(128):
                for y in range(128):
                    if x < 64:
                        img1.putpixel((x, y), (0, 0, 0, 255))
                        img2.putpixel((x, y), (255, 255, 255, 255))
                    else:
                        img1.putpixel((x, y), (255, 255, 255, 255))
                        img2.putpixel((x, y), (0, 0, 0, 255))
    min_width = min(img1.width, img2.width)
    min_height = min(img1.height, img2.height)
    min_width = min(min_width, max_width)
    min_height = min(min_height, max_height)
    img1 = img1.resize((min_width, min_height), Image.Resampling.NEAREST)
    img2 = img2.resize((min_width, min_height), Image.Resampling.NEAREST)

    original_1 = img1.copy()

    doneSteps = 0

    new_img = Image.new("RGBA", (1, 1))

    img_tk = CTkImage(light_image=img1, dark_image=img1, size=img1.size)
    img_label = CTkLabel(frame, text="", image=img_tk)
    img_label.image = img_tk  # type: ignore

    # pending_set contains pixels to evaluate on next step (initially all pixels)
    pending_set = set((x, y) for x in range(img1.width) for y in range(img1.height))

    def stepthread():
        nonlocal run_step
        while run_step.get():
            step()

    def step():
        nonlocal img1, img2, new_img, step_toggle_button, doneSteps, run_step, pending_set, start_time
        # If there is nothing pending, no change possible
        if not pending_set:
            run_step.set(False)
            print("No pending pixels to process; stopping at step", doneSteps)
            step_toggle_button.configure(text="Start")
            duration = time.time() - start_time
            print(f"Processing took {duration:.2f} seconds")
            return

        # Process only pending pixels using img1 snapshot
        new_img_snapshot, changed, best = approximate_image_incremental(
            img1, img2, pending_set
        )

        # If nothing changed at all, stop
        if not changed and new_img_snapshot.tobytes() == img1.tobytes() and (not serial or doneSteps > img1.width * img1.height):
            run_step.set(False)
            print("Image not changing anymore at step", doneSteps)
            step_toggle_button.configure(text="Start")
            duration = time.time() - start_time
            print(f"Processing took {duration:.2f} seconds")
            return

        # Update img1 to the new image produced this step
        img1 = new_img_snapshot

        # Update GUI
        img_tk = CTkImage(light_image=img1, dark_image=img1, size=img1.size)
        img_label.configure(image=img_tk)
        img_label.image = img_tk  # type: ignore
        img_label.grid(row=imgRow, column=imgCol, columnspan=2)

        # increment step counter
        doneSteps += 1
        stepDisplay.delete(0, tk.END)
        stepDisplay.insert(0, str(doneSteps))

        # Check for perfect match
        if img1.tobytes() == img2.tobytes():
            run_step.set(False)
            print("Image perfect at step", doneSteps)
            step_toggle_button.configure(text="Start")
            # No need to compute next pending set
            pending_set = set()
            return

        # Compute next pending set: any pixel that could have their best neighbor change,
        # i.e., any pixel within radius of a changed pixel (including changed pixels themselves)
        next_pending = set()
        if not serial:
            for cx, cy in changed:
                for pos in get_positions_in_radius(
                    cx, cy, img1.width, img1.height
                ):
                    next_pending.add(pos)
        else:
            first_pending = next(iter(pending_set), None)
            if first_pending is None:
                next_pending = set()
            elif best:
                next_pending = set((x, y) for x, y in best)
            else:
                x, y = first_pending
                x = (x + stepX) % img1.width
                y = (y + (x == 0) * stepY) % img1.height
                next_pending = set([(x, y)])
        pending_set = next_pending

    run_step = BooleanVar(value=False)
    start_time = time.time()

    def toggle_step():
        nonlocal run_step, step_toggle_button, start_time
        if run_step.get():
            run_step.set(False)
            step_toggle_button.configure(text="Start")
            duration = time.time() - start_time
            print(f"Processing took {duration:.2f} seconds")
        else:
            run_step.set(True)
            step_toggle_button.configure(text="Stop")
            start_time = time.time()
            threading.Thread(target=stepthread).start()

    step_toggle_button = CTkButton(frame, text="Start", command=toggle_step)
    step_toggle_button.grid(row=row, column=col)

    def finish_and_record_threaded():
        threading.Thread(target=finish_and_record).start()

    def finish_and_record():
        nonlocal original_1, img1, img2, new_img, step_toggle_button, doneSteps, step_to_button, step_to_gif_export_button, pending_set, start_time, run_step
        step_to_gif_export_button.configure(state="disabled")
        step_to_button.configure(state="disabled")
        step_toggle_button.configure(state="disabled")

        start_time = time.time()
        run_step.set(True)

        images = []
        while run_step.get():
            saveFrame = shouldSaveFrame(doneSteps, img1.size)
            if saveFrame:
                img1.save(os.path.join(tempfile.gettempdir(), f"step_{doneSteps}.png"))
                images.append(
                    Image.open(
                        os.path.join(tempfile.gettempdir(), f"step_{doneSteps}.png")
                    )
                )
            step()

        duration = time.time() - start_time
        print(f"Processing took {duration:.2f} seconds")

        img1.save(os.path.join(tempfile.gettempdir(), f"step_{doneSteps}.png"))
        images.append(
            Image.open(os.path.join(tempfile.gettempdir(), f"step_{doneSteps}.png"))
        )

        export_path = filedialog.asksaveasfilename(
            title="Export gif",
            filetypes=[("GIF files", "*.gif")],
            defaultextension=".gif",
        )
        if export_path:
            images[0].save(
                export_path,
                save_all=True,
                append_images=images[1:],
                duration=100,
                loop=0,
            )

        step_toggle_button.configure(text="Start")
        step_toggle_button.configure(state="normal")
        step_to_button.configure(state="normal")
        step_to_gif_export_button.configure(state="normal")

    def shouldSaveFrame(doneSteps, img_dim, totalSteps=None):
        maxDim = max(img_dim)
        if totalSteps is None:
            totalSteps = maxDim  # fallback

        # Always save the first frame
        if doneSteps == 0:
            return True

        # Define a target "half-life" scale — adjust factor to tune acceleration rate
        halfLife = totalSteps / 10

        # Compute a deterministic skip factor that increases over time
        # This formula increases exponentially, making saving rarer as steps go up
        skip = int(1 + (doneSteps / halfLife) ** 2)

        # Only save when doneSteps is a multiple of skip
        return doneSteps % skip == 0

    finish_and_record_button = CTkButton(
        frame, text="Finish and record", command=finish_and_record_threaded
    )
    rc()
    finish_and_record_button.grid(row=row, column=col)

    stepDisplayLabel = CTkLabel(frame, text="Steps:")
    rc(True)
    stepDisplayLabel.grid(row=row, column=col)
    stepDisplay = CTkEntry(frame)
    rc()
    stepDisplay.grid(row=row, column=col)
    
    step_button = CTkButton(frame, text="Step", command=step)
    rc(True)
    step_button.grid(row=row, column=col)

    def step_to(record=False):
        nonlocal original_1, img1, img2, new_img, step_toggle_button, doneSteps, step_to_button, step_to_gif_export_button, pending_set, start_time
        step_to_gif_export_button.configure(state="disabled")
        step_to_button.configure(state="disabled")
        step_toggle_button.configure(state="disabled")

        start_time = time.time()

        num_steps = int(stepDisplay.get())
        step_diff = num_steps - doneSteps
        if step_diff < 0 or record:
            img1 = original_1.copy()
            img_tk = CTkImage(light_image=img1, dark_image=img1, size=img1.size)
            img_label.configure(image=img_tk)
            img_label.image = img_tk  # type: ignore
            img_label.grid(row=imgRow, column=imgCol, columnspan=2)
            doneSteps = 0
            # reset pending set to full image
            pending_set = set(
                (x, y) for x in range(img1.width) for y in range(img1.height)
            )
            steps_to_make = num_steps
        else:
            steps_to_make = step_diff
        images = []
        for i in range(steps_to_make):
            saveFrame = shouldSaveFrame(i, img1.size, steps_to_make)
            if record and saveFrame:
                # save current image before stepping
                temp_path = os.path.join(tempfile.gettempdir(), f"step_{i}.png")
                img1.save(temp_path)
                images.append(
                    Image.open(os.path.join(tempfile.gettempdir(), f"step_{i}.png"))
                )
            step()

        duration = time.time() - start_time
        print(f"Processing took {duration:.2f} seconds")

        if record:
            # save final and export frames
            img1.save(os.path.join(tempfile.gettempdir(), f"step_{num_steps}.png"))
            images.append(
                Image.open(os.path.join(tempfile.gettempdir(), f"step_{num_steps}.png"))
            )

            export_path = filedialog.asksaveasfilename(
                title="Export gif",
                filetypes=[("GIF files", "*.gif")],
                defaultextension=".gif",
            )
            if export_path:
                images[0].save(
                    export_path,
                    save_all=True,
                    append_images=images[1:],
                    duration=100,
                    loop=1,
                )

        step_to_gif_export_button.configure(state="normal")
        step_to_button.configure(state="normal")
        step_toggle_button.configure(state="normal")

    def step_to_thread():
        threading.Thread(target=step_to).start()

    step_to_button = CTkButton(frame, text="Step to", command=step_to_thread)
    rc()
    step_to_button.grid(row=row, column=col)

    def step_to_export():
        threading.Thread(target=step_to, args=(True,)).start()

    step_to_gif_export_button = CTkButton(
        frame, text="Step to & export gif", command=step_to_export
    )
    rc(True)
    step_to_gif_export_button.grid(row=row, column=col)

    def export():
        nonlocal new_img
        export_path = filedialog.asksaveasfilename(
            title="Export final image", defaultextension=".png"
        )
        if export_path:
            new_img.save(export_path)

    export_button = CTkButton(frame, text="Export", command=export)
    rc()
    export_button.grid(row=row, column=col)

    def select_img1():
        nonlocal img1, img2, filetypes, pending_set, img1_path
        img1_path = filedialog.askopenfilename(title="Select img1", filetypes=filetypes)
        if img1_path:
            print("Img1:", img1_path)
            img1 = Image.open(img1_path).convert("RGBA")
            min_width = min(img1.width, img2.width)
            min_height = min(img1.height, img2.height)
            min_width = min(min_width, max_width)
            min_height = min(min_height, max_height)
            img1 = img1.resize((min_width, min_height), Image.Resampling.NEAREST)
            img2 = img2.resize((min_width, min_height), Image.Resampling.NEAREST)
            # reset pending set to full image after new selection
            pending_set = set(
                (x, y) for x in range(img1.width) for y in range(img1.height)
            )
            img1_tk = CTkImage(light_image=img1, dark_image=img1, size=img1.size)
            img_label.configure(image=img1_tk)
            img_label.image = img1_tk  # type: ignore

    select_img1_button = CTkButton(frame, text="Select img1", command=select_img1)
    rc(True)
    select_img1_button.grid(row=row, column=col)

    def select_img2():
        nonlocal img2, img1, filetypes, pending_set, img2_path
        img2_path = filedialog.askopenfilename(title="Select img2", filetypes=filetypes)
        if img2_path:
            print("Img2:", img2_path)
            img2 = Image.open(img2_path).convert("RGBA")
            min_width = min(img1.width, img2.width)
            min_height = min(img1.height, img2.height)
            min_width = min(min_width, max_width)
            min_height = min(min_height, max_height)
            img1 = img1.resize((min_width, min_height), Image.Resampling.NEAREST)
            img2 = img2.resize((min_width, min_height), Image.Resampling.NEAREST)
            # changing the target may require full re-evaluation
            pending_set = set(
                (x, y) for x in range(img1.width) for y in range(img1.height)
            )

    select_img2_button = CTkButton(frame, text="Select img2", command=select_img2)
    rc()
    select_img2_button.grid(row=row, column=col)

    if selection in ["r", "r2"]:
        def pick_random_img1():
            nonlocal img1, filetypes, pending_set, possiblechoices, possibleFirstChoices, img1, img2, img1_path
            if selection == "r":
                img1_path = random.choice(possiblechoices)
            elif selection == "r2":
                img1_path = random.choice(possibleFirstChoices)
            print("Img1:", img1_path)
            img1 = Image.open(img1_path).convert("RGBA")
            min_width = min(img1.width, img2.width)
            min_height = min(img1.height, img2.height)
            min_width = min(min_width, max_width)
            min_height = min(min_height, max_height)
            img1 = img1.resize((min_width, min_height), Image.Resampling.NEAREST)
            img2 = img2.resize((min_width, min_height), Image.Resampling.NEAREST)
            # reset pending set to full image after new selection
            pending_set = set(
                (x, y) for x in range(img1.width) for y in range(img1.height)
            )
            img1_tk = CTkImage(light_image=img1, dark_image=img1, size=img1.size)
            img_label.configure(image=img1_tk)
            img_label.image = img1_tk  # type: ignore

        pick_random_img1_button = CTkButton(
            frame, text="Pick random img1", command=pick_random_img1
        )
        rc(True)
        pick_random_img1_button.grid(row=row, column=col)

        def pick_random_img2():
            nonlocal img2, filetypes, pending_set, possiblechoices, possibleSecondChoices, img1, img2, img2_path
            if selection == "r":
                img2_path = random.choice(possiblechoices)
            elif selection == "r2":
                img2_path = random.choice(possibleSecondChoices)
            print("Img2:", img2_path)
            img2 = Image.open(img2_path).convert("RGBA")
            min_width = min(img1.width, img2.width)
            min_height = min(img1.height, img2.height)
            min_width = min(min_width, max_width)
            min_height = min(min_height, max_height)
            img1 = img1.resize((min_width, min_height), Image.Resampling.NEAREST)
            img2 = img2.resize((min_width, min_height), Image.Resampling.NEAREST)
            # changing the target may require full re-evaluation
            pending_set = set(
                (x, y) for x in range(img1.width) for y in range(img1.height)
            )

        pick_random_img2_button = CTkButton(
            frame, text="Pick random img2", command=pick_random_img2
        )
        rc()
        pick_random_img2_button.grid(row=row, column=col)
    
    def open_img1():
        nonlocal img1
        if img1:
            os.startfile(str(img1_path))

    def open_img2():
        nonlocal img2
        if img2:
            os.startfile(str(img2_path))

    rc(True)
    open_img1_button = CTkButton(frame, text="Open img1", command=open_img1)
    open_img1_button.grid(row=row, column=col)

    open_img2_button = CTkButton(frame, text="Open img2", command=open_img2)
    rc()
    open_img2_button.grid(row=row, column=col)
    
    def sprout(x=random.randint(0, img1.width - 1), y=random.randint(0, img1.height - 1)):
        """empty pending set and put in only one random pixel"""
        nonlocal pending_set
        pending_set.clear()
        pending_set.add((x, y))
        toggle_step()
    sprout_button = CTkButton(frame, text="Sprout", command=sprout)
    rc(True)
    sprout_button.grid(row=row, column=col)
    
    def customSprout():
        y = simpledialog.askinteger("Custom Sprout", "Height", minvalue=0, maxvalue=img1.height - 1, initialvalue=img1.height // 2)
        x = simpledialog.askinteger("Custom Sprout", "Width", minvalue=0, maxvalue=img1.width - 1, initialvalue=img1.width // 2)
        if x and y:
            sprout(x, y)
    custom_button = CTkButton(frame, text="Custom Sprout", command=customSprout)
    rc()
    custom_button.grid(row=row, column=col)
    
    def pendAll():
        nonlocal pending_set
        pending_set = set(
            (x, y) for x in range(img1.width) for y in range(img1.height)
        )
    pendAll_button = CTkButton(frame, text="Pend All", command=pendAll)
    rc(True)
    pendAll_button.grid(row=row, column=col)
    
    def toggleSerial():
        global serial
        serial = not serial
        toggleSerial_button.configure(text="Disable Serial" if serial else "Enable Serial")
        if serial:
            sprout(0, 0)
    toggleSerial_button = CTkButton(frame, text="Toggle Serial", command=toggleSerial)
    rc()
    toggleSerial_button.grid(row=row, column=col)

    rc(True)
    imgRow, imgCol = row, col

    img_label.grid(row=imgRow, column=imgCol, columnspan=2)

    root.mainloop()


if __name__ == "__main__":
    selection = "r"  # "r" for random, "r2" for choosing individial random choice folders for img1 and img2, "s" for selection, anything else for test image
    radius = 1  # manhattan distance to neighbors to consider
    stepX = 1  # only for ...
    stepY = 1  # ... serial mode
    swap = False
    serial = False
    max_height = 500
    max_width = max_height
    main()
