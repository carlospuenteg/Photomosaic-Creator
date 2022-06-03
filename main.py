import numpy as np
from PIL import Image
import os
import cv2
import shutil
import time
import filecmp
from colorthief import ColorThief

"""
Images taken from: 
- Animals: https://unsplash.com/es/s/fotos/animals?order_by=latest&orientation=squarish
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
# Removes duplicate images from a folder

def remove_duplicates(folder):
    print(f"{Ansi.GREEN}Removing duplicates...{Ansi.RESET}")
    dir = "images/" + folder
    num_removed = 0
    toRemove = []

    for img1 in os.listdir(dir):
        for img2 in os.listdir(dir):
            if img1 != img2 and img2 not in toRemove and img1 not in toRemove and filecmp.cmp(dir + "/" + img1, dir + "/" + img2):
                toRemove.append(img2)
                num_removed += 1

    for file in toRemove:
        os.remove(dir + "/" + file)
    print(f"{num_removed} duplicates removed")

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

    return np.array(res)

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

def resize_images(size, folder, new_folder, same_name):
    i = 0
    for file in os.listdir(folder):
        if not file.startswith('.'):
            print(f"{i}. {Ansi.GREEN}Resizing{Ansi.RESET} {file}")
            img = Image.open(folder + "/" + file)
            resized_img = img.resize((size, size))
            if same_name:
                if file[:2] != "r_": 
                    fileName = f"r_{file}"
                    os.remove(f"{folder}/{file}")
                else: fileName = file
            else:
                fileName = f'{str(i)}.jpg'
            resized_img.save(f"{new_folder}/{fileName}")
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
            print(f"{i}. {Ansi.GREEN}Renaming{Ansi.RESET} {file}")
            img = Image.open(folder + "/" + file).convert('RGB')
            img.save(new_folder + "/" + str(i) + ".jpg")
            i += 1

#------------------------------------------------------------------------------
# Creates a new folder with the best images to be used as a palette for a main image

def get_best_colors(image_path, num_colors=20):
    color_thief = ColorThief(image_path)
    count = (num_colors+1) if num_colors >= 7 else num_colors if num_colors > 3 else 2
    palette = color_thief.get_palette(color_count=count)
    print(len(palette))
    return np.array(palette)

def get_best_for_main(folder, main_image, num_images=20):
    path = f"images/{folder}"
    temp_path = "images/temp"
    new_path = f"images/best_{folder}_{main_image.split('.')[0]}"
    main_image_path = f"{MAIN_IMAGES_FOLDER}/{main_image}"

    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    if os.path.exists(new_path):
        shutil.rmtree(new_path)
    os.makedirs(temp_path)
    os.makedirs(new_path)

    rename_images(path,temp_path)

    images_avg_color = get_colors(temp_path)
    new_index = 0
    
    print(f"{Ansi.MAGENTA}Obtaining the best images...{Ansi.RESET}")
    for rgb in get_best_colors(main_image_path, num_images):
        closest_index = closest(images_avg_color, rgb)
        images_avg_color[closest_index] = [-255,-255,-255]
        img = Image.open(temp_path + "/" + str(closest_index) + ".jpg")
        img.save(new_path + "/" + str(new_index) + ".jpg")
        new_index += 1

    shutil.rmtree(temp_path)

#------------------------------------------------------------------------------
# Creates a new folder with the images from the given folder, removing the images with similar colors

def get_best(folder, min_color_diff=20):
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
    
    print(f"{Ansi.MAGENTA}Obtaining the best images...{Ansi.RESET}")
    for i,rgb in enumerate(images_avg_color):
        valid = True
        for color in best_images:
            diffs = [ abs(rgb[j] - color[j]) for j in range(3) ]
            if sum(diffs) <= min_color_diff:
                valid = False
                break
        if valid:
            best_images.append(rgb)
            print(f"{Ansi.YELLOW}Saved{Ansi.RESET} image {new_index}")
            img = Image.open(temp_path + "/" + str(i) + ".jpg")
            img.save(new_path + "/" + str(new_index) + ".jpg")
            new_index += 1

    shutil.rmtree(temp_path)
    
    print("Previous images: " + str(len(images_avg_color)))
    print("Best images: " + str(len(best_images)))

#------------------------------------------------------------------------------
# This is executed when the script is run

def create_img(main_image, images_size=50, **args):
    images_folder = args.get("images_folder", "animals")
    resize = args.get("resize", False)
    new_name = args.get('new_name', "photomosaic.jpg")

    create_folders()

    num_images = len(os.listdir(IMAGES_FOLDER + "/" + images_folder))
    num_resized = len(os.listdir(RESIZED_FOLDER))
    if resize or num_images != num_resized or np.array(Image.open(f"{RESIZED_FOLDER}/0.jpg")).shape[0] != images_size:
        shutil.rmtree(RESIZED_FOLDER)
        os.makedirs(RESIZED_FOLDER)
        resize_images(images_size, f"{IMAGES_FOLDER}/{images_folder}", RESIZED_FOLDER, False)


    images_avg_color = get_colors()
    images = [ np.array(Image.open(RESIZED_FOLDER + "/" + str(i) + ".jpg"))[:,:,::-1] for i in range(len(images_avg_color)) ] # [:,:,::-1] to convert from BGR to RGB
    main_img = np.array(Image.open(MAIN_IMAGES_FOLDER + "/" + main_image))
    new_img_arr = np.zeros((len(main_img)*images_size, len(main_img[0])*images_size, 3), dtype=np.uint8)

    for i,line in enumerate(main_img):
        print(f"{Ansi.MAGENTA}Creating...{Ansi.RESET} {round(i/len(main_img)*100,2)}%")
        for j,pixel in enumerate(line):
            s = images_size
            index = closest(images_avg_color, pixel)
            new_img_arr[i*s : i*s+s , j*s : j*s+s] = images[index]

    print(f"{Ansi.YELLOW}Saving...{Ansi.RESET}")
    cv2.imwrite(OUTPUT_FOLDER + "/" + new_name, new_img_arr)

#########################################################################################
# This is executed when the script is run

startTime = time.time()
#------------------------------------------------------------------------------
"""
remove_duplicates("animals")

get_best(
    folder=             "animals",
    min_color_diff=     20,
)

get_best_for_main(
    folder=         "animals",
    main_image=     "img2_high-res.jpeg",
    num_images=     29
)

resize_images(
    size=           1000,
    folder=         IMAGES_FOLDER + "/animals",
    new_folder=     IMAGES_FOLDER + "/animals",
    same_name=      True
)

create_img( 
    main_image=     "img1.jpeg", 
    images_size=    50, 
    images_folder=  "animals",
    new_name=       "photomosaic.jpg",
    resize=         False
)
"""
#------------------------------------------------------------------------------

get_best_for_main(
    folder=         "animals",
    main_image=     "img2_high-res.jpeg",
    num_images=     2
)

#------------------------------------------------------------------------------
print(f'{Ansi.CYAN}Done in: {round(time.time() - startTime,4)}s{Ansi.RESET}')