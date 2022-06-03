# Photomosaic Creator

## Index
- [Introduction](#introduction)
- [Results](#results)
- [Run the script](#run-the-script)
- [How it works](#how-it-works)
  - [Main function (create_img)](#main-function-create_img)
    - [Arguments](#arguments-create_img)
    - [Examples](#examples-create_img)
  - [get_best()](#function-get_best)
    - [Description](#description)
    - [Arguments](#arguments-get_best)
    - [Examples](#examples-get_best)
  - [get_best_for_main()](#function-get_best_for_main)
    - [Description](#description-get_best_for_main)
    - [Arguments](#arguments-get_best_for_main)
    - [Examples](#examples-get_best_for_main)
  - [remove_duplicates()](#function-remove_duplicates)
    - [Description](#description)
    - [Arguments](#arguments-remove_duplicates)
    - [Examples](#examples-remove_duplicates)
  - [resize_images()](#function-resize_images)
    - [Description](#description)
    - [Arguments](#arguments-resize_images)
    - [Examples](#examples-resize_images)
- [Possible errors](#possible-errors)

## Introduction
This program allows you to create a photomosaic from a set of images.

The image and the set of images can be any size you want, but the more size, the more time it will take and the larger the resulting image will be.

You can use the preset sets/folders of images or you can upload your own folders to the `images` folder.

The more images the set has, the better the result, but the more time it will take to create the photomosaic.

## Results

<img src="./Examples/result_1/full.png" alt="example_img_full" width="500">
<img src="./Examples/result_1/zoom_1.png" alt="example_img_zoom_1" width="500">
<img src="./Examples/result_1/zoom_2.png" alt="example_img_zoom_2" width="500">
<img src="./Examples/result_1/zoom_3.png" alt="example_img_zoom_4" width="500">

## Run the script

Open the terminal, go to this folder and type:
```bash
$ python3 main.py
```

## How it works

1. Creates the needed folders
2. If `resize=True` or if `the number of images in the folder is different than the number of images in the resized folder`or if `the size of the first image in the resized folder is different than the desired image size`: The `resized` folder will be replaced with the new resized images from the given set of images
3. Obtains the average value of each primary color of each image in the `resized` folder by reducing the size of each image to 1 pixel
4. Creates an array with all the numpy arrays of the images in the `resized` folder, converted from BGR to RGB
5. Creates a numpy array from the selected main image in the `main-images` folder
6. Creates the photomosaic by choosing the images with the closest average color for each pixel in the main image
7. Saves the photomosaic in the `output` folder

### Main function (create_img())

#### Arguments (create_img)
| argument | description | example | default value | Required |
| -------- | ----------- | ------- | ------------- | -------- |
| 1 | Name of the main image | "my_img.jpeg" | | Yes |
| 2 | Size in px of the images that make up the main image | 100 | 50 | Yes |
| resize | Whether or not you want to resize the images. It should always be set to false. Only give it the value `True` if you have stopped the script in the middle of the resizing or if there's been an error related to it | resize=False | False | No |
| images_folder | Folder where the images are | images_folder="animals" | "animals" | No |
| new_name | Name of the new image | new_name="photomosaic.jpg" | "photomosaic.jpg" | No |
| rem_duplicates | Whether or not you want to remove the duplicate images from the folder | rem_duplicates=True | False | No |

#### Examples (create_img)
```python
create_img( 
    main_image=     "img1.jpeg", 
    images_size=    50, 
    images_folder=  "landscapes",
    new_name=       "photomosaic.jpg"
    resize=         False,
)
create_img( 
    main_image=     "img2_high-res.jpeg", 
    images_size=    50, 
    images_folder=  "animals",
    new_name=       "my_photomosaic.jpg"
    resize=         False,
)
```


### Function: get_best()

#### Description

Function that picks the best images from the given set of images.

#### Arguments (get_best)

| argument | description | example | default value | Required |
| -------- | ----------- | ------- | ------------- | -------- |
| folder | Folder of the set of images | "landscapes" | | Yes |
| min_color_diff | The minumum color difference between the images (the more difference, the less images) | 10 | 20 | No |

#### Examples (get_best)
```python
get_best(
    folder=             "animals",
    min_color_diff=     20,
)
get_best(
    folder=     "landscapes",
    min_color_diff= 10
)
```


### Function: get_best_for_main()

#### Description (get_best_for_main)

Creates a new folder with the best images to be used as a palette for a main image

#### Arguments (get_best_for_main)

| argument | description | example | default value | Required |
| -------- | ----------- | ------- | ------------- | -------- |
| folder | Folder of the set of images | "landscapes" | | Yes |
| main_image |Path of the main image from where the color palette will be created | img2_high-res.jpeg | | Yes |
| num_images | Number of images to be used in the palette | 10 | 20 | No |

#### Examples
```python
get_best_for_main(
    folder=         "animals",
    main_image=     "img2_high-res.jpeg",
    num_images=     29
)
```


### Function: remove_duplicates()

#### Description (remove_duplicates)

Function that removes the duplicate images from the given folder.

#### Arguments (remove_duplicates)

| argument | description | example | default value | Required |
| -------- | ----------- | ------- | ------------- | -------- |
| folder | Folder of the set of images | "landscapes" | | Yes |

#### Examples (remove_duplicates)
```python
remove_duplicates("animals")
remove_duplicates("landscapes")
```


### Function: resize_images()

#### Description (resize_images)

Function that resizes the images in the given folder to the given size.

#### Arguments (resize_images)

| argument | description | example | default value | Required |
| -------- | ----------- | ------- | ------------- | -------- |
| size | Size of the images (just a number, since the set of images have to be squared) | 1000 | | Yes |
| folder | Folder with the images to resize | "images/animals" | | Yes |
| new_folder | Folder where the resized images will be saved | "images/animals" | | Yes |
| same_name | Whether or not the images will have the same name (and be overwritten if the `new_folder` is the same as the `folder`) or if they will have a numerical name (0 to ...) | True | | Yes |

#### Examples (resize_images)
```python
resize_images(1000, IMAGES_FOLDER + "/animals", IMAGES_FOLDER + "/animals", True)
```

## Possible errors

If you get the error: `zsh: killed python3 main.py`, it means that the program is taking too long to run (it's taking too much memory).

To solve it, you can try to reduce the size of the resized images or of the main image.