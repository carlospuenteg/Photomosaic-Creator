from PIL import Image
import os
import sys

def resize(file, size, new_file="res_image.png", folder="images/animals"):
    img = Image.open(folder + "/" + file)
    init_width = img.size[0]
    init_height = img.size[1]

    if (len(size) != 2):
        print("Error: size must be a list of length 2"); return
    else:
        new_width = size[0]
        new_height = size[1]
        if not new_width or not new_height:
            if not new_width and new_height:
                new_width = int(init_width / (init_height / new_height))
            elif not new_height and new_width:
                new_height = int(init_height / (init_width / new_width))
            else:
                print("Error: Width or height must be specified"); return
        if new_width > init_width or new_height > init_height:
            print("Error: new size is larger than original image"); return
        resized_img = img.resize((new_width, new_height))
        resized_img.save("resized/" + new_file)

def resize_all(size, folder="images/animals"):
    i = 0
    for file in os.listdir(folder):
        print("Resizing " + file)
        if not file.startswith('.'):
            resize(file, size, str(i) + ".jpg", folder)
            i += 1

resize_all((int(sys.argv[1]), int(sys.argv[2])), "images/" + sys.argv[3])