import numpy as np
from PIL import Image
import os
import cv2
import shutil
import time

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
# Gets the average value of each primary color of each image in the resized images folder by reducing the size of each image to 1 pixel

def get_colors(folder=RESIZED_FOLDER):
    res = []
    folders = [str(i) + ".jpg" for i in range(len(os.listdir(folder)))]

    print(f"{Ansi.CYAN}Analyzing images...{Ansi.RESET}")
    for file in folders:
        img = Image.open(folder + "/" + file)
        resized_img = img.resize((1, 1))
        res.append(resized_img.getpixel((0,0)))

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

def resize_images(size, folder=IMAGES_FOLDER + "/animals", new_folder=RESIZED_FOLDER):
    i = 0
    for file in os.listdir(folder):
        if not file.startswith('.'):
            print(f"{i}. {Ansi.GREEN}Resizing{Ansi.RESET} {file}")
            img = Image.open(folder + "/" + file)
            resized_img = img.resize((size, size))
            resized_img.save(new_folder + "/" + str(i) + ".jpg")
            i += 1

#------------------------------------------------------------------------------
# Creates the needed folders

def create_folders():
    if not os.path.exists(RESIZED_FOLDER):
        os.makedirs(RESIZED_FOLDER)
    if not os.path.exists(IMAGES_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(MAIN_IMAGES_FOLDER)

#------------------------------------------------------------------------------
# Renames images from a folder and saves them in other folder

def rename_images(folder, new_folder):
    print(f"{Ansi.GREEN}Renaming files...{Ansi.RESET}")
    i = 0
    for file in os.listdir(folder):
        if not file.startswith('.'):
            img = Image.open(folder + "/" + file)
            img.save(new_folder + "/" + str(i) + ".jpg")
            i += 1


#------------------------------------------------------------------------------
# Creates a new folder with the images from the given folder, removing the images with similar colors

def get_best(folder="animals", color_diff=50):
    path = "images/" + folder
    temp_path = "images/temp"
    new_path = "images/best_" + folder

    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    if os.path.exists(new_path):
        shutil.rmtree(new_path)
    os.makedirs(temp_path)
    os.makedirs(new_path)

    rename_images(path,temp_path)

    images_avg_color = get_colors(temp_path)
    best_images = []
    new_index = 0
    
    for i,rgb in enumerate(images_avg_color):
        invalid = False
        for color in best_images:
            diffs = [ abs(rgb[j] - color[j]) for j in range(3) ]
            if sum(diffs) < color_diff:
                invalid = True
                break
        if not invalid:
            best_images.append(rgb)
            img = Image.open(temp_path + "/" + str(i) + ".jpg")
            img.save(new_path + "/" + str(new_index) + ".jpg")
            new_index += 1

    shutil.rmtree(temp_path)
    
    print("Previous images: " + str(len(images_avg_color)))
    print("Best images: " + str(len(best_images)))

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

    images_avg_color = get_colors()
    images = [ np.array(Image.open(RESIZED_FOLDER + "/" + str(i) + ".jpg"))[:,:,::-1] for i in range(len(images_avg_color)) ] # [:,:,::-1] to convert from BGR to RGB
    main_img = np.array(Image.open(MAIN_IMAGES_FOLDER + "/" + main_image))
    new_img = np.zeros((len(main_img)*images_size, len(main_img[0])*images_size, 3), dtype=np.uint8)

    for i,line in enumerate(main_img):
        print(f"{Ansi.MAGENTA}Creating...{Ansi.RESET} {round(i/len(main_img)*100,2)}%")
        for j,pixel in enumerate(line):
            s = images_size
            new_img[i*s : i*s+s , j*s : j*s+s] = images[closest(images_avg_color, pixel)]

    print(f"{Ansi.YELLOW}Saving...{Ansi.RESET}")
    cv2.imwrite(OUTPUT_FOLDER + "/" + new_name, new_img)

#------------------------------------------------------------------------------
# This is executed when the script is run

startTime = time.time()

# get_best("animals", 20)
create_img( "img1.jpeg" , 50 , resize=True , images_folder="best_animals" )

print(f'{Ansi.CYAN}Done in: {round(time.time() - startTime,4)}s{Ansi.RESET}')