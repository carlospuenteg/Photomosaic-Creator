import numpy as np
from PIL import Image
import os
import cv2

"""
Images taken from: 
- Animals: https://unsplash.com/es/s/fotos/animals?orientation=squarish
- Landscapes: https://unsplash.com/es/s/fotos/landscapes?orientation=squarish
"""

#------------------------------------------------------------------------------
# Constants

RESIZED_FOLDER = "resized"
IMAGES_FOLDER = "images"
OUTPUT_FOLDER = "output"
MAIN_IMAGES_FOLDER = "main-images"

#------------------------------------------------------------------------------
# ANSI COLORS for the terminal

class Ansi:
    BLACK = '\u001b[30m'
    RED = '\u001b[31m'
    GREEN = '\u001b[32m'
    YELLOW = '\u001b[33m'
    BLUE = '\u001b[34m'
    MAGENTA = '\u001b[35m'
    CYAN = '\u001b[36m'
    WHITE = '\u001b[37m'
    RESET = '\u001b[0m'

#------------------------------------------------------------------------------
# Gets the average value of each primary color of each image in the resized images folder

def get_colors():
    res = []
    folders = [str(i) + ".jpg" for i in range(len(os.listdir(RESIZED_FOLDER)))]

    for file in folders:
        print(f"{Ansi.CYAN}Analyzing{Ansi.RESET} {file}")
        avg = [0,0,0]
        img = np.array(Image.open(RESIZED_FOLDER + "/" + file))
        for line in img:
            for pixel in line:
                avg[0] += pixel[0]
                avg[1] += pixel[1]
                avg[2] += pixel[2]
        avg = [ int( color/(len(img) * len(img[0])) ) for color in avg]
        res.append(avg)

    return res

#------------------------------------------------------------------------------
# Gets the index of the image with the most similar colors to the given pixel

def closest(arr, color):
    index = 0
    min_diff = 765
    for i,rgb in enumerate(arr):
        diffs = [ abs(rgb[j] - color[j]) for j in range(3) ]
        if (sum(diffs) < min_diff):
            min_diff = sum(diffs)
            index = i
    return index

#------------------------------------------------------------------------------
# Resizes each image from the given folder to the given size

def resize_images(size, folder=IMAGES_FOLDER + "/animals"):
    i = 0
    for file in os.listdir(folder):
        if not file.startswith('.'):
            print(f"{Ansi.GREEN}Resizing{Ansi.RESET} {file}")
            img = Image.open(folder + "/" + file)
            resized_img = img.resize((size, size))
            resized_img.save(RESIZED_FOLDER + "/" + str(i) + ".jpg")
            i += 1

#------------------------------------------------------------------------------
# Creates the needed folders

def create_folders():
    if not os.path.exists(RESIZED_FOLDER):
        os.mkdir(RESIZED_FOLDER)
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(MAIN_IMAGES_FOLDER):
        os.makedirs(MAIN_IMAGES_FOLDER)

#------------------------------------------------------------------------------
# This is executed when the script is run

def create_img(main_image, images_size, **args): # resize=True, images_folder="animals"
    resize = args.get("resize", False)
    images_folder = args.get("images_folder", "animals")
    new_name = args.get('new_name', "photomosaic.jpg")

    create_folders()

    if resize: 
        for f in os.listdir(RESIZED_FOLDER):
            os.remove(RESIZED_FOLDER + "/" + f)
        resize_images(images_size, IMAGES_FOLDER + "/" + images_folder)

    images_avg = get_colors()
    images = [ np.array(Image.open(RESIZED_FOLDER + "/" + str(i) + ".jpg"))[:,:,::-1] for i in range(len(images_avg)) ] # [:,:,::-1] to convert from BGR to RGB
    main_img = np.array(Image.open(MAIN_IMAGES_FOLDER + "/" + main_image))
    new_img = np.zeros((len(main_img)*images_size, len(main_img[0])*images_size, 3), dtype=np.uint8)

    for i,line in enumerate(main_img):
        print(f"{Ansi.MAGENTA}Creating...{Ansi.RESET} {round(i/len(main_img)*100,2)}%")
        for j,pixel in enumerate(line):
            s = images_size
            new_img[i*s : i*s+s , j*s : j*s+s] = images[closest(images_avg, pixel)]

    print(f"{Ansi.YELLOW}Saving...{Ansi.RESET}")
    cv2.imwrite(OUTPUT_FOLDER + "/" + new_name, new_img)

#------------------------------------------------------------------------------

create_img( "img1.jpeg" , 50 , resize=True)