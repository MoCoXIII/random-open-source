import os
import random
import tempfile
import time
import threading
import tkinter as tk
from tkinter import filedialog
from PIL import Image
from customtkinter import *

# takes in two images and simulates creating a new image using the colors form the first image spreading to approximate the second image as best as possible
# configure maximum simulations dimension at the very bottom

def get_neighbors_in_radius(img, x, y, radius):
    neighbors = [(x, y)]
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            new_x, new_y = x + i, y + j
            if (i, j) != (0, 0) and 0 <= new_x < img.width and 0 <= new_y < img.height:
                neighbors.append((new_x, new_y))
    return neighbors


def best_color_in_radius(img1, img2, x, y, radius, seperate=False):
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

    for neighbor_x, neighbor_y in get_neighbors_in_radius(img1, x, y, radius):
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
def get_positions_in_radius(x, y, radius, width, height):
    positions = []
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            nx, ny = x + i, y + j
            if 0 <= nx < width and 0 <= ny < height:
                positions.append((nx, ny))
    return positions


# New incremental approximate function: process only pixels in pixels_to_check
def approximate_image_incremental(img1, img2, pixels_to_check, radius=1):
    """
    Process only pixels in pixels_to_check based on the snapshot img1 and target img2.
    Returns (new_img, changed_set) where changed_set is a set of coords that changed.
    """
    new_img = img1.copy()
    changed = set()
    for x, y in pixels_to_check:
        # If already identical to target, keep same pixel (and it won't change)
        if img1.getpixel((x, y)) == img2.getpixel((x, y)):
            # ensure new_img has the same pixel (copy preserves it, but keep consistent)
            continue
        best_color = best_color_in_radius(img1, img2, x, y, radius)
        if best_color:
            if best_color != img1.getpixel((x, y)):
                new_img.putpixel((x, y), best_color)
                changed.add((x, y))
        else:
            # no better neighbor found, keep original
            continue
    return new_img, changed


def approximate_image(img1, img2):
    new_img = Image.new("RGBA", (img1.width, img1.height))
    for y in range(img1.height):
        for x in range(img1.width):
            if img1.getpixel((x, y)) == img2.getpixel((x, y)):
                new_img.putpixel((x, y), img1.getpixel((x, y)))
                # print("Saving time by not checking perfect pixel", (x, y), end="\r")
                continue
            best_color = best_color_in_radius(img1, img2, x, y, 1)
            if best_color:
                new_img.putpixel((x, y), best_color)
            else:
                new_img.putpixel((x, y), img1.getpixel((x, y)))
    return new_img


def main():
    set_appearance_mode("Dark")
    root = CTk()
    root.geometry(f"800x600+{root.winfo_screenwidth()//2-400}+{root.winfo_screenheight()//2-300}")
    frame = CTkScrollableFrame(root)
    frame.pack(expand=True, fill="both")
    # randomchoicefolder = filedialog.askdirectory(title="Select Folder")
    # if not randomchoicefolder:
    #     root.destroy()
    #     return
    # possiblechoices = []
    # for r, dirs, files in os.walk(randomchoicefolder):
    #     for f in files:
    #         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', ".gif")):
    #             possiblechoices.append(os.path.join(r, f))
    # img1_path = random.choice(possiblechoices)
    # print(img1_path)
    # img2_path = random.choice(possiblechoices)
    # print(img2_path)
    filetypes = [("All image files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.gif;*.tiff")]
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
    img1 = Image.open(img1_path).convert("RGBA")
    img2 = Image.open(img2_path).convert("RGBA")
    # img1 = Image.new("RGBA", (128, 128))
    # img2 = Image.new("RGBA", (128, 128))
    # for x in range(128):
    #     for y in range(128):
    #         if x < 64:
    #             img1.putpixel((x, y), (0, 0, 0, 255))
    #             img2.putpixel((x, y), (255, 255, 255, 255))
    #         else:
    #             img1.putpixel((x, y), (255, 255, 255, 255))
    #             img2.putpixel((x, y), (0, 0, 0, 255))
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
    img_label.image = img_tk

    # pending_set contains pixels to evaluate on next step (initially all pixels)
    pending_set = set((x, y) for x in range(img1.width) for y in range(img1.height))
    search_radius = 1

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
        new_img_snapshot, changed = approximate_image_incremental(
            img1, img2, pending_set, search_radius
        )

        # If nothing changed at all, stop
        if not changed and new_img_snapshot.tobytes() == img1.tobytes():
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
        img_label.image = img_tk
        img_label.pack()

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
        for cx, cy in changed:
            for pos in get_positions_in_radius(
                cx, cy, search_radius, img1.width, img1.height
            ):
                next_pending.add(pos)
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
    step_toggle_button.pack()

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

    def shouldSaveFrame(stepsDone, img_dim, totalSteps=None):
        result = True
        maxDim = max(img_dim)
        if totalSteps is None:
            # unknown amount of steps to take, use half-life
            # first frame should always be saved
            if doneSteps == 0:
                result = True
            else:
                result = random.random() < 0.5 ** (doneSteps / (maxDim / 10))
        else:
            # known amount of steps to take
            # first frame should always be saved
            if doneSteps == 0:
                result = True
            else:
                result = random.random() < 0.5 ** (doneSteps / (totalSteps / 10))
        return result

    finish_and_record_button = CTkButton(
        frame, text="Finish and record", command=finish_and_record_threaded
    )
    finish_and_record_button.pack()

    step_button = CTkButton(frame, text="Step", command=step)
    step_button.pack()

    stepDisplayLabel = CTkLabel(frame, text="Steps:")
    stepDisplayLabel.pack()
    stepDisplay = CTkEntry(frame)
    stepDisplay.pack()

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
            img_label.pack()
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
    step_to_button.pack()

    def step_to_export():
        threading.Thread(target=step_to, args=(True,)).start()

    step_to_gif_export_button = CTkButton(
        frame, text="Step to & export gif", command=step_to_export
    )
    step_to_gif_export_button.pack()

    def export():
        nonlocal new_img
        export_path = filedialog.asksaveasfilename(
            title="Export final image", defaultextension=".png"
        )
        if export_path:
            new_img.save(export_path)

    export_button = CTkButton(frame, text="Export", command=export)
    export_button.pack()

    def select_img1():
        nonlocal img1, img2, filetypes, pending_set
        filepath = filedialog.askopenfilename(title="Select img1", filetypes=filetypes)
        if filepath:
            img1 = Image.open(filepath).convert("RGBA")
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
            img_label.image = img1_tk

    select_img1_button = CTkButton(frame, text="Select img1", command=select_img1)
    select_img1_button.pack()

    def select_img2():
        nonlocal img2, img1, filetypes, pending_set
        filepath = filedialog.askopenfilename(title="Select img2", filetypes=filetypes)
        if filepath:
            img2 = Image.open(filepath).convert("RGBA")
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
    select_img2_button.pack()

    img_label.pack()

    root.mainloop()


if __name__ == "__main__":
    max_width = 262144
    max_height = 262144
    main()
