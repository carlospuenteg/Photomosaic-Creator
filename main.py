import numpy as np
from PIL import Image; Image.MAX_IMAGE_PIXELS = 933120000
import os
import cv2
import shutil
import time
import filecmp
from colorthief import ColorThief
import imageio

"""
Images taken from: 
- Animals: https://unsplash.com/es/s/fotos/animals?order_by=latest&orientation=squarish
- Landscapes: https://unsplash.com/es/s/fotos/landscapes?orientation=squarish
"""

#------------------------------------------------------------------------------

BEST_FOLDER = "$b_"
ALL_FOLDER = "$all"

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
# Progress bar

def progress_bar(percent, text="", bar_len=30):
    done = round(percent*bar_len)
    left = bar_len - done # ━

    print(f"   {Ansi.GREEN}{'▩'*done}{Ansi.RESET}{'▩'*left} {f'[{round(percent*100,2)}%]'.ljust(8)} {Ansi.MAGENTA}{text}{Ansi.RESET}", end='\r')

    if percent == 1: print("✅")

#------------------------------------------------------------------------------
# Removes duplicate images from a folder

def remove_duplicates(folder="images/animals"):
    files = os.listdir(folder)
    num_removed = 0
    toRemove = []

    for i,img1 in enumerate(files):
        progress_bar(i/(len(files)-1), text="Removing duplicates")
        for img2 in os.listdir(folder):
            if img1 != img2 and img2 not in toRemove and img1 not in toRemove and filecmp.cmp(f"{folder}/{img1}", f"{folder}/{img2}"):
                toRemove.append(img2)
                num_removed += 1

    for file in toRemove:
        os.remove(f"{folder}/{file}")
    print(f"{num_removed} duplicates removed")

#------------------------------------------------------------------------------
# Resizes each image from the given folder to the given size

def resize_images(folder="images/animals", size=1000):
    files = os.listdir(folder)

    for i,file in enumerate(files):
        if not file.startswith('.'):
            progress_bar(i/(len(files)-1), text="Resizing")
            Image.open(f"{folder}/{file}").resize((size, size)).save(f"{folder}/{file}")

#------------------------------------------------------------------------------
# Resizes each image from the given folder to the given size      

def treat_images(folder="images/animals", size=1000):
    resize_images(folder, size)
    remove_duplicates(folder)

#------------------------------------------------------------------------------
# Resizes each image from the given folder to the given size      

def clean_folders():
    folders = os.listdir("images")
    for i,folder in enumerate(folders):
        if folder.startswith(BEST_FOLDER):
            shutil.rmtree(f"images/{folder}")
            progress_bar(i/(len(folders)-1), text="Cleaning folders")

#------------------------------------------------------------------------------
# Creates a folder with all the images from the other folders

def create_all_folder(size=200):
    path = f"images/{ALL_FOLDER}"
    if os.path.exists(path): 
        shutil.rmtree(path)
    os.makedirs(path)
    for folder in os.listdir("images"):
        if not folder.startswith(BEST_FOLDER) and not folder.startswith(".DS_Store"):
            files = os.listdir(f"images/{folder}")
            for i,file in enumerate(files):
                progress_bar(i/(len(files)-1), text=f"Adding [{folder}] to [{ALL_FOLDER}] ")
                if not file.startswith('.'):
                    img = Image.open(f"images/{folder}/{file}").resize((size, size))
                    img.save(f"{path}/{file}")

#------------------------------------------------------------------------------
# Gets the index of the image with the most similar colors to the given pixel
def closest(arr, color):
    distances = np.sqrt(np.sum((arr-color)**2,axis=1))
    index_of_smallest = np.where(distances==np.amin(distances))
    return index_of_smallest[0][0]

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
# Removes every element from the given folder

def clean_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

#------------------------------------------------------------------------------
# Gets the average value of each primary color of each image in the resized images folder by reducing the size of each image to 1 pixel

def get_avg_color(path):
    return Image.open(path).resize((1, 1)).getpixel((0,0))

def get_avg_colors(folder, files):
    res = []
    for i,file in enumerate(files):
        progress_bar(i/(len(files)-1), text="Analyzing the average colors")
        res.append(get_avg_color(f"{folder}/{file}"))
    return np.array(res)

#------------------------------------------------------------------------------
# Checks if the average deviation from the average color of an image is less than the given threshold

def check_color_deviation(image_path, max, avg_color=None, size_to_test=10):
    if max >= 765: return True
    if avg_color is None: avg_color = get_avg_color(image_path)

    img = Image.open(image_path).resize((size_to_test,size_to_test))

    img_data = np.array(img.getdata())
    sum_diff_avg = 0
    for pixel in img_data:
        sum_diff_avg += sum(np.absolute(np.subtract(pixel,avg_color)))

    return sum_diff_avg/len(img_data) <= max

#------------------------------------------------------------------------------
# Gets the average contrast in each image

def check_contrasts(image_path, max):
    if max >= 765: return True
    img = Image.open(image_path)
    img_resized = [np.array(img.resize((2, 2))), np.array(img.resize((3, 3)))]

    for arr in img_resized:
        color_left = np.average(arr[:,0], axis=0)
        color_right = np.average(arr[:,-1], axis=0)
        if sum(np.absolute(np.subtract(color_right,color_left))) > max:
            return False

        color_top = np.average(arr[0,:], axis=0)
        color_bottom = np.average(arr[-1,:], axis=0)
        if sum(np.absolute(np.subtract(color_bottom,color_top))) > max:
            return False

    return True

#------------------------------------------------------------------------------
# Copies a file, resizes it, and moves it to other location

def copy_resized(path, new_path, fileName, size):
    img = Image.open(path).resize((size, size))
    img.save(new_path)

#------------------------------------------------------------------------------
# Copies a file to other location

def copy(path, new_path, fileName):
    shutil.copy(path, new_path)

#------------------------------------------------------------------------------
# Creates a new folder with the images from the given folder, removing the images with similar colors

def get_best(folder="animals", max_avg_color_deviation=765, max_contrast=765, size=1000):
    path = f"images/{folder}"
    new_path = f"images/{BEST_FOLDER}{folder}"

    if not os.path.exists(path): 
        print(f"{Ansi.RED}Folder ./{path} not found{Ansi.RESET}")
        return

    clean_folder(new_path)

    files = np.array([f for f in sorted(os.listdir(path)) if f.endswith(".jpg")])
    images_size = np.array(Image.open(f"{path}/{files[0]}")).shape[0]

    avg_colors = get_avg_colors(path, files)

    if images_size > size:
        for i,file in enumerate(files):
            if check_contrasts(f"{path}/{file}", max_contrast) and check_color_deviation(f"{path}/{file}", max_avg_color_deviation, avg_colors[i]):
                copy_resized(f"{path}/{file}", f"{new_path}/{file}", file, size)
            progress_bar(i/(len(files)-1), text="Obtaining the best images")
    else:
        for i,file in enumerate(files):
            if check_contrasts(f"{path}/{file}", max_contrast) and check_color_deviation(f"{path}/{file}", max_avg_color_deviation, avg_colors[i]):
                copy(f"{path}/{file}", f"{new_path}/{file}", file)
            progress_bar(i/(len(files)-1), text="Obtaining the best images")

    print(f"Previous images: {len(files)}")
    print(f"Best images: {len(os.listdir(new_path))}")

#------------------------------------------------------------------------------
# Creates a new folder with the best images to be used as a palette for a main image

def get_best_colors(image_path, num_colors=255):
    color_thief = ColorThief(image_path)
    count = (num_colors+1) if num_colors >= 7 else num_colors if num_colors > 3 else 2
    palette = color_thief.get_palette(color_count=count)
    return np.array(palette)

def get_best_colors_main(main_image, folder="animals", num_images=20):
    path = f"images/{folder}"
    new_path = f"images/{folder}_{main_image.split('.')[0]}"
    main_image_path = f"main-images/{main_image}"

    clean_folder(new_path)

    files = np.array([f for f in sorted(os.listdir(path)) if f.endswith(".jpg")])
    images_avg_color = get_avg_colors(path, files)
    best_colors = get_best_colors(main_image_path, num_images)
    
    for i,rgb in enumerate(best_colors):
        progress_bar(i/(num_images-1), text="Obtaining the best images")
        closest_index = closest(images_avg_color, rgb)
        images_avg_color[closest_index] = [-255,-255,-255]
        shutil.copy(f"{path}/{files[closest_index]}", f"{new_path}/{files[closest_index]}")

#------------------------------------------------------------------------------
# Save an image

def save_img(img, path, quality=95):
    if not cv2.imwrite(path, img, [cv2.IMWRITE_JPEG_QUALITY, quality]):
        print(f"{Ansi.RED}Unable to save the image. Image is probably too big.{Ansi.RESET}")
    else:
        print(f"{Ansi.GREEN}Image saved{Ansi.RESET} ({os.path.getsize(path)/2**20:.2f} MB)")

#------------------------------------------------------------------------------
# Save a GIF

def save_gif(images, path, quality=95, frame_duration=250):
    images[0].save(path, format="GIF", append_images=images, save_all=True, duration=frame_duration, loop=0, quality=quality)
    # imageio.mimsave(f"{new_folder}/{new_name}_zoom.gif", gif_images, fps=0.1)
    print(f"{Ansi.GREEN}GIF saved{Ansi.RESET} ({os.path.getsize(path)/2**20:.2f} MB)")

#------------------------------------------------------------------------------
# Save the photomosaic

def save_full_img(img_arr, new_path, quality=95):
    save_img(img_arr, new_path, quality)

#------------------------------------------------------------------------------
# Save a low res version of the photomosaic

def save_lowres_img(img_arr, new_path, shape, quality=95):
    img = cv2.resize(img_arr, (shape[1], shape[0]), interpolation=cv2.INTER_AREA)
    save_img(img, new_path, quality)

#------------------------------------------------------------------------------
# Create a zoomed version of an image

def create_zoom_img(img_arr, full_shape, main_img_shape, zoom):
    center_x = full_shape[0]//2
    center_y = full_shape[1]//2
    left = center_y - int(full_shape[1]/(zoom*2))
    right = center_y + int(full_shape[1]/(zoom*2))
    top = center_x - int(full_shape[0]/(zoom*2))
    bottom = center_x + int(full_shape[0]/(zoom*2))
    img = img_arr[top:bottom, left:right]
    img_res = cv2.resize(img, (main_img_shape[1], main_img_shape[0]), interpolation=cv2.INTER_AREA)
    return img_res

#------------------------------------------------------------------------------
# Saved zoom images of the photomosaic

def save_zoom_images(img_arr, new_folder, new_name, main_img_shape, images_size, quality=95, min_images=5, zoom_incr=2):
    full_shape = img_arr.shape
    zoom_path = f"{new_folder}/zoom"
    
    os.mkdir(zoom_path)
    zoom = zoom_incr
    while min(full_shape[0], full_shape[1])/zoom > images_size*min_images:
        save_img(
            create_zoom_img(img_arr, full_shape, main_img_shape, zoom), 
            f"{zoom_path}/{new_name}_zoom_{zoom}.jpg", 
            quality)
        zoom *= zoom_incr

#------------------------------------------------------------------------------
# Save a GIF of the zoomed images of the photomosaic

def save_zoom_gif(img_arr, new_folder, new_name, main_img_shape, images_size, quality=95, min_images=5, zoom_incr=1.3):
    full_shape = img_arr.shape
    gif_images = []
    zoom = 1
    while min(full_shape[0], full_shape[1])/zoom > images_size*min_images:
        zoom_img = cv2.cvtColor(create_zoom_img(img_arr, full_shape, main_img_shape, zoom), cv2.COLOR_BGR2RGB)
        gif_images.append(Image.fromarray(zoom_img))
        zoom *= zoom_incr

    save_gif(gif_images, f"{new_folder}/{new_name}_zoom.gif", quality)


#------------------------------------------------------------------------------
# This is executed when the script is run

def create_img(main_image, images_size=50, images_folder="animals", new_name="photomosaic", num_images=-1, quality=85, save_lowres=True, save_full=True, save_zoom=True, save_gif=True):
    images_folder_name = images_folder
    images_folder = f"images/{images_folder_name}"
    main_img = np.array(Image.open(f"main-images/{main_image}"))

    max_images = min(255, len(os.listdir(images_folder)))
    min_images = 3
    if num_images != -1:
        num_images = min_images if num_images < min_images else max_images if num_images > max_images else num_images
        get_best_colors_main(main_image, images_folder_name, num_images)
        images_folder = f"images/{images_folder_name}_{main_image.split('.')[0]}"

    create_folders()

    files = np.array([f for f in sorted(os.listdir(images_folder)) if f.endswith(".jpg")])
    images_avg_color = get_avg_colors(images_folder, files)

    images = [ np.array(Image.open(f"{images_folder}/{file}").resize((images_size, images_size)))[:,:,::-1] for file in files ] # [:,:,::-1] to convert from BGR to RGB
    new_img_arr = np.zeros((len(main_img)*images_size, len(main_img[0])*images_size, 3), dtype=np.uint8)

    for i,line in enumerate(main_img):
        progress_bar(i/(len(main_img)-1), text=f"Creating the photomosaic")
        for j,pixel in enumerate(line):
            s = images_size
            index = closest(images_avg_color, pixel)
            new_img_arr[i*s : i*s+s , j*s : j*s+s] = images[index]

    new_folder = f"output/{new_name}"
    if os.path.exists(new_folder):
        shutil.rmtree(new_folder)
    os.mkdir(new_folder)

    print(f"{Ansi.YELLOW}Saving...{Ansi.RESET}")
    if save_full:
        save_full_img(new_img_arr, f"{new_folder}/{new_name}.jpg", quality)
    if save_lowres:
        save_lowres_img(new_img_arr, f"{new_folder}/{new_name}_lowres.jpg", main_img.shape, quality)
    if save_zoom:
        save_zoom_images(new_img_arr, new_folder, new_name, main_img.shape, images_size, quality)
    if save_gif:
        save_zoom_gif(new_img_arr, new_folder, new_name, main_img.shape, images_size, quality)
    

#########################################################################################
# This is executed when the script is run
#------------------------------------------------------------------------------
startTime = time.time()
#------------------------------------------------------------------------------
create_img( 
    main_image=     "cannon-h.jpeg", 
    images_size=     50, 
    images_folder=  "$b_$all",
    new_name=       "cannon",
)
#------------------------------------------------------------------------------
print(f'{Ansi.CYAN}Done in: {round(time.time() - startTime,4)}s{Ansi.RESET}')
#########################################################################################
"""
remove_duplicates("animals")
resize_images(
    folder=         "images/animals",
    size=           1000,
)
treat_images()
create_all_folder()
clean_folders()

get_best(
    folder=                     "$all",
    max_avg_color_deviation=    120,
    max_contrast=               150
)
create_img( 
    main_image=     "cannon-h.jpeg", 
    images_size=     50, 
    images_folder=  "$b_$all",
    new_name=       "photomosaic.jpg",
)
"""