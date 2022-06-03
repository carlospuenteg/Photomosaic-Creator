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

def get_colors(folder="resized"):
    res = []
    folders = [str(i) + ".jpg" for i in range(len(os.listdir(folder)))]
    for file in folders:
        print(file)
        if not file.startswith('.'):
            avg = [0,0,0]
            img = np.array(Image.open(folder + "/" + file))
            for line in img:
                for pixel in line:
                    avg[0] += pixel[0]
                    avg[1] += pixel[1]
                    avg[2] += pixel[2]
            avg = [ int( c / (len(img) * len(img[0])) ) for c in avg]
            res.append(avg)

    return res

#------------------------------------------------------------------------------

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

def main(file="img_test.jpeg", size=10, format=True, folder="animals"):
    if format: 
        for f in os.listdir("resized"):
            os.remove("resized/" + f)
        os.system("python3 resize.py " + str(size) + " " + str(size) + " " + folder)

    images_avg = get_colors()
    images = [ np.array(Image.open("resized/" + str(i) + ".jpg"))[:,:,::-1] for i in range(len(images_avg)) ]
    main_img = np.array(Image.open("main-image/" + file))
    new_img = np.zeros((len(main_img)*size, len(main_img[0])*size, 3), dtype=np.uint8)

    for i,line in enumerate(main_img):
        for j,pixel in enumerate(line):
            # print(main_img[i,j], images_avg[closest(images_avg, main_img[i,j])], closest(images_avg, main_img[i,j]))
            new_img[i*size:i*size+size,j*size:j*size+size] = images[closest(images_avg, pixel)]

    cv2.imwrite("result/" + file, new_img)

#------------------------------------------------------------------------------

main("img3-higher.jpeg", 50 , True, "animals")