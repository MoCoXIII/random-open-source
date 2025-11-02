from PIL import Image
import os

# utility for converting RGBA images that do not make use of their alpha channel to RGB
# not for direct execution, use "from cleantransparency import cleanFolder, isRGBA" and then call the functions when needed

def cleanFolder(folder):
    images = [os.path.join(folder, f) for f in os.listdir(folder)]
    for image in images:
        if os.path.isfile(image):
            img = Image.open(image)
            img = img.convert("RGBA")
            if all(x[3] == 255 for x in img.getdata()):
                img = img.convert("RGB")
                print(f"Converted {image} to RGB")
                img.save(image)
            else:
                print(f"{image} is transparent")

def isRGBA(image):
    img = Image.open(image)
    isRGBA = img.mode == "RGBA"
    img.close()
    return isRGBA