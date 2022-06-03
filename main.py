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

def remove_duplicates(folder="animals"):
    print(f"{Ansi.GREEN}Removing duplicates...{Ansi.RESET}")
    dir = f"images/{folder}"
    num_removed = 0
    toRemove = []

    for img1 in os.listdir(dir):
        for img2 in os.listdir(dir):
            if img1 != img2 and img2 not in toRemove and img1 not in toRemove and filecmp.cmp(f"{dir}/{img1}", f"{dir}/{img2}"):
                toRemove.append(img2)
                num_removed += 1

    for file in toRemove:
        os.remove(f"{dir}/{file}")
    print(f"{num_removed} duplicates removed")

#------------------------------------------------------------------------------
# Gets the average value of each primary color of each image in the resized images folder by reducing the size of each image to 1 pixel

def get_colors(folder, files=None):
    res = []

    print(f"{Ansi.CYAN}Analyzing images...{Ansi.RESET}")
    for file in files:
        img = Image.open(f"{folder}/{file}").resize((1, 1))
        res.append(img.getpixel((0,0)))

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

def resize_images(folder="images/animals", size=1000):
    i = 0
    for file in os.listdir(folder):
        if not file.startswith('.'):
            print(f"{i}. {Ansi.GREEN}Resizing{Ansi.RESET} {file}")
            img = Image.open(f"{folder}/{file}").resize((size, size))
            if file[:2] == "r_": 
                fileName = file
            else:
                fileName = f"r_{file}"
                os.remove(f"{folder}/{file}")
            img.save(f"{folder}/{fileName}")
            i += 1

#------------------------------------------------------------------------------
# Creates the needed folders

def create_folders():
    if not os.path.exists("images"):
        os.makedirs("images")
    if not os.path.exists("output"):
        os.makedirs("output")
    if not os.path.exists("main-images"):
        os.makedirs("main-images")

#------------------------------------------------------------------------------
# Creates a new folder with the best images to be used as a palette for a main image

def get_best_colors(image_path, num_colors=20):
    color_thief = ColorThief(image_path)
    count = (num_colors+1) if num_colors >= 7 else num_colors if num_colors > 3 else 2
    palette = color_thief.get_palette(color_count=count)
    return np.array(palette)

def get_best_for_main(main_image, folder="animals", num_images=20):
    path = f"images/{folder}"
    new_path = f"images/best_{folder}_{main_image.split('.')[0]}"
    main_image_path = f"main-images/{main_image}"

    if os.path.exists(new_path):
        shutil.rmtree(new_path)
    os.makedirs(new_path)

    files = np.array([f for f in sorted(os.listdir(path)) if f.endswith(".jpg")])
    images_avg_color = get_colors(path, files)
    new_index = 0
    
    print(f"{Ansi.MAGENTA}Obtaining the best images...{Ansi.RESET}")
    for rgb in get_best_colors(main_image_path, num_images):
        closest_index = closest(images_avg_color, rgb)
        images_avg_color[closest_index] = [-255,-255,-255]
        img = Image.open(path + "/" + files[closest_index])
        img.save(new_path + "/" + str(new_index) + ".jpg")
        new_index += 1

#------------------------------------------------------------------------------
# Creates a new folder with the images from the given folder, removing the images with similar colors

def get_best(folder="animals", min_color_diff=20):
    path = f"images/{folder}"
    new_path = f"images/best_{folder}"

    if os.path.exists(new_path):
        shutil.rmtree(new_path)
    os.makedirs(new_path)

    files = np.array([f for f in sorted(os.listdir(path)) if f.endswith(".jpg")])
    images_avg_color = get_colors(path, files)
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
            img = Image.open(f"{path}/{files[i]}")
            img.save(f"{new_path}/{new_index}.jpg")
            print(f"{Ansi.YELLOW}Saved{Ansi.RESET} image {new_index}")
            new_index += 1
    
    print("Previous images: " + str(len(images_avg_color)))
    print("Best images: " + str(len(best_images)))

#------------------------------------------------------------------------------
# This is executed when the script is run

def create_img(main_image, images_size=50, **args):
    images_folder_name = args.get('images_folder', 'animals')
    images_folder = f"images/{images_folder_name}"
    new_name = args.get('new_name', "photomosaic.jpg")
    num_images = args.get('num_images', -1)

    if num_images != -1:
        get_best_for_main(main_image, images_folder_name,num_images)
        images_folder = f"images/best_{images_folder_name}_{main_image.split('.')[0]}"

    create_folders()

    files = np.array([f for f in sorted(os.listdir(images_folder)) if f.endswith(".jpg")])
    images_avg_color = get_colors(images_folder, files)

    images = [ np.array(Image.open(f"{images_folder}/{file}").resize((images_size, images_size)))[:,:,::-1] for file in files ] # [:,:,::-1] to convert from BGR to RGB
    main_img = np.array(Image.open(f"main-images/{main_image}"))
    new_img_arr = np.zeros((len(main_img)*images_size, len(main_img[0])*images_size, 3), dtype=np.uint8)

    for i,line in enumerate(main_img):
        print(f"{Ansi.MAGENTA}Creating...{Ansi.RESET} {round(i/len(main_img)*100,2)}%")
        for j,pixel in enumerate(line):
            s = images_size
            index = closest(images_avg_color, pixel)
            new_img_arr[i*s : i*s+s , j*s : j*s+s] = images[index]

    print(f"{Ansi.YELLOW}Saving...{Ansi.RESET}")
    cv2.imwrite(f"output/{new_name}", new_img_arr)

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
    main_image=     "img2_high-res.jpeg",
    folder=         "animals",
    num_images=     20
)

resize_images(
    folder=         "images/animals",
    size=           1000,
)

create_img( 
    main_image=     "img1_high-res.jpeg", 
    images_size=    50, 
    images_folder=  "animals",
    new_name=       "photomosaic.jpg",
    num_images=     5
)
"""
#------------------------------------------------------------------------------
create_img( 
    main_image=     "img1_high-res.jpeg", 
    images_size=    50, 
    images_folder=  "animals",
    new_name=       "photomosaic.jpg",
    num_images=     10
)
#------------------------------------------------------------------------------
print(f'{Ansi.CYAN}Done in: {round(time.time() - startTime,4)}s{Ansi.RESET}')