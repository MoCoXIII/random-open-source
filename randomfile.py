import os
import random
import shutil
import subprocess
import threading
import tkinter.messagebox
import tkinter.filedialog
import tkinter.simpledialog

mode = "custom"
folder = tkinter.filedialog.askdirectory(title="Select folder to play files from")
if not folder:
    exit()

match mode:
    case "open":
        files = [f"{r}/{f}" for r, d, f in os.walk(folder) for f in f]
        safeFileTypes = [".png", ".webm", ".jpg", ".jpeg", ".webp", ".gif", ".mp4"]
        while True:
            file = random.choice(files)
            if file.endswith(tuple(safeFileTypes)):
                os.startfile(os.path.join(folder, file))
            elif input(f"Open {file}? "):
                os.startfile(os.path.join(folder, file))
            files.remove(file)
            input("Enter to open another")
    case "custom":
        imageExtensions = [".png", ".jpg", ".jpeg", ".webp"]
        videoExtensions = [".webm", ".mp4", ".gif", ".mov"]
        allExtensions = imageExtensions + videoExtensions
        wantedExtensions = None
        if wantedExtensions:
            files = [f"{r}/{f}" for r, d, f in os.walk(folder) for f in f if f.endswith(tuple(wantedExtensions))]
        else:
            files = [f"{r}/{f}" for r, d, f in os.walk(folder) for f in f]
        import pygame
        import pyvidplayer2

        pygame.init()
        screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Random File Player")
        clock = pygame.time.Clock()

        current_file = None
        current_image = None
        current_video = None
        file = ""

        showPath = False
        doUpdate = True  # whether to update moved file locations instead of removing them from the playlist
        alphabetical = False
        autoAdvance = False
        advanceTimer = 0  # frame counter
        advanceImage = 5 * 60  # frames to keep an image open
        advanceVideo = 0  # frames to keep the last frame of a video open
        advanceNow = False

        played = []
        index = -1

        def load():
            # if len(file) > 150:
            #     print(f"Loading {file[:120]}...{file[-30:]} ...", end=" ")
            # else:
            #     print(f"Loading {file} ...", end=" ")
            global current_image, current_video, current_file, img_rect, file
            if file.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                img = pygame.image.load(os.path.join(folder, file))
                img_w, img_h = img.get_size()
                scale_factor = min(screen_w / img_w, screen_h / img_h)
                scaled_img = pygame.transform.scale(img, (int(img_w * scale_factor), int(img_h * scale_factor)))
                img_rect = scaled_img.get_rect()
                img_rect.center = (screen_w // 2, screen_h // 2)
                current_image = scaled_img
                screen.blit(scaled_img, img_rect)
            elif file.endswith(('.webm', '.mp4', ".gif", ".mov")):
                current_video = pyvidplayer2.Video(os.path.join(folder, file))
                img_w, img_h = current_video.current_size
                scale_factor = min(screen_w / img_w, screen_h / img_h)
                scaled_w, scaled_h = int(img_w * scale_factor), int(img_h * scale_factor)
                current_video.resize((scaled_w, scaled_h))
                current_video.play()
            current_file = file
            # print(f"Done.{" "*((150+21)-len(file))}", end="\r")
        def advance(_load=True):
            global current_video, index, current_file, current_image, autoAdvance, file
            index += 1
            update(_load)
        def back(_load=True):
            global current_video, index, current_file, current_image, current_video, file
            if current_video: current_video.close()
            index -= 1
            index = max(index, 0)
            file = played[index]
            current_file = None
            current_image = None
            current_video = None
            if _load:
                load()
        def update(_load=True):
            global index, file, current_file, current_image, current_video, autoAdvance
            if current_video:
                current_video.close()
            if index >= len(played):
                try:
                    if alphabetical:
                        file = sorted(files)[0]
                    else:
                        file = random.choice(files)
                    played.append(file)
                    files.remove(file)
                except IndexError:
                    index -= 1
                    autoAdvance = False
                    return
            else:
                file = played[index]
            current_file = None
            current_image = None
            current_video = None
            if _load:
                load()

        while True:
            screen.fill((0, 0, 0))
            if advanceNow:
                advanceNow = False
                advanceTimer = 0
                advance()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_d:
                        advance()
                    if event.key == pygame.K_a:
                        back()
                    elif event.key == pygame.K_r:
                        if current_video: current_video.restart()
                    elif event.key == pygame.K_l:
                        if current_video: current_video.seek(5)
                    elif event.key == pygame.K_j:
                        if current_video: current_video.seek(-5)
                    elif event.key == pygame.K_k:
                        if current_video: current_video.toggle_pause()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    elif event.key == pygame.K_o:
                        if current_file:
                            os.startfile(os.path.join(folder, current_file))
                    elif event.key == pygame.K_e:
                        if current_file:
                            subprocess.run(["explorer.exe", "/select,", os.path.normpath(current_file)])
                    elif event.key == pygame.K_f:
                        autoAdvance = not autoAdvance
                    elif event.key == pygame.K_p:
                        alphabetical = not alphabetical
                    elif event.key == pygame.K_h:
                        showPath = not showPath
                    elif event.key == pygame.K_u:
                        doUpdate = not doUpdate
                    elif event.key == pygame.K_i:
                        # advance, but skip to next image (ignore videos)
                        advance(False)
                        while not file.endswith(tuple(imageExtensions)) and len(files) > 0:
                            advance(False)
                        update()
                    elif event.key == pygame.K_v:
                        # advance, but skip to next video (ignore images)
                        advance(False)
                        while not file.endswith(tuple(videoExtensions)) and len(files) > 0:
                            advance(False)
                        update()
                    elif event.key == pygame.K_RSHIFT:
                        tkinter.filedialog.askdirectory(initialdir=folder, title="Reset default opening location")
                    elif event.key == pygame.K_BACKSPACE:
                        newFolder = tkinter.filedialog.askdirectory()  # ask this first in case the user wants to reset their default opening location
                        if not newFolder:
                            continue
                        if not current_file:
                            tkinter.messagebox.showwarning("No file selected", "No file selected to move")
                            continue
                        try:
                            if current_video:
                                current_video.close()
                            newPath = shutil.move(current_file, newFolder)
                            if doUpdate:
                                played[played.index(current_file)] = newPath
                            else:
                                played.remove(current_file)
                                update()
                            # tkinter.messagebox.showinfo("Moved", f"Moved {current_file} to {newFolder}")
                        except OSError as e:
                            tkinter.messagebox.showerror("Move failed", f"Failed to move {current_file}: {e}")
                    elif event.key == pygame.K_KP_PLUS:
                        index_entry = tkinter.simpledialog.askinteger("Go to index", "Enter index", minvalue=1, maxvalue=len(played) - 1 + len(files) - 0)
                        if index_entry is None:
                            continue
                        while index != index_entry - 1:
                            if index < index_entry - 1:
                                advance(False)
                            else:
                                back(False)
                        load()
            screen_w, screen_h = screen.get_size()
            if current_image:
                screen.blit(current_image, img_rect)
                if autoAdvance:
                    screen.blit(pygame.font.Font(None, 24).render(f"Proceeding in {((advanceImage - advanceTimer)/60):.2f} seconds", True, (255, 255, 255), (0, 0, 0)), (10, 100))
                    advanceTimer += 1
                    if advanceTimer >= advanceImage:
                        advanceNow = True
            if current_video:
                img_w, img_h = current_video.current_size # type: ignore
                x = (screen_w - img_w) // 2
                y = (screen_h - img_h) // 2
                current_video.draw(screen, (x, y))
                if autoAdvance and current_video.frame >= current_video.frame_count - 1:
                    screen.blit(pygame.font.Font(None, 24).render(f"Proceeding in {((advanceVideo - advanceTimer)/60):.2f} seconds", True, (255, 255, 255), (0, 0, 0)), (10, 100))
                    advanceTimer += 1
                    if advanceTimer >= advanceVideo:
                        advanceNow = True
            screen.blit(pygame.font.Font(None, 24).render(f"{len(files)}", True, (255, 255, 255), (0, 0, 0)), (10, 10))
            screen.blit(pygame.font.Font(None, 24).render(f"{index + 1}/{len(played)}", True, (255, 255, 255), (0, 0, 0)), (10, 40))
            # text up to y40 is permanent
            y = 40
            if autoAdvance:
                y += 30
                screen.blit(pygame.font.Font(None, 24).render(f"Auto Advance: ON", True, (255, 255, 255), (0, 0, 0)), (10, y))
            if alphabetical:
                y += 30
                screen.blit(pygame.font.Font(None, 24).render("Alphabetical: ON", True, (255, 255, 255), (0, 0, 0)), (10, y))
            if not doUpdate:
                y += 30
                screen.blit(pygame.font.Font(None, 24).render("Update: OFF", True, (255, 255, 255), (0, 0, 0)), (10, y))
            if showPath:
                screen.blit(pygame.font.Font(None, 24).render(f"{current_file}", True, (255, 255, 255), (0, 0, 0)), (10, screen_h - 24))
            pygame.display.flip()
            clock.tick(60)
    case "explore":
        maxL = 0
        files = []
        def addFiles(folder):
            global maxL, files
            for r, d, f in os.walk(folder):
                for f in f:
                    l = f"{r}/{f}"
                    maxL = max(maxL, len(l))
                    print(l.ljust(maxL), end="\r")
                    files.append(l)
            print(str("Added all files").ljust(maxL))

        t = threading.Thread(target=addFiles, args=(folder,))
        t.start()

        while True:
            if len(files) == 0:
                tkinter.messagebox.showinfo("No files", "No files found. Press ok to try again.")
            file = random.choice(files)
            subprocess.run(["explorer.exe", "/select,", os.path.normpath(file)])
            files.remove(file)
            if not tkinter.messagebox.askokcancel("Another?", "Open another file?"):
                break
