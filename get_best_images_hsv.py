"""
def hsv2rgb(r,g,b):
    hsv = colorsys.hsv_to_rgb(r,g,b)
    return int(hsv[0] * 255), int(hsv[1] * 255), int(hsv[2] * 255)

def get_best_colors(num_colors):
    desired_colors = []
    for i in range(num_colors):
        color = hsv2rgb( 1/(num_colors) * i ,1,1 )
        desired_colors.append(color)

    return np.array(desired_colors)

def get_best_images(folder, num_images=20):
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
    new_index = 0
    
    print(f"{Ansi.MAGENTA}Obtaining the best images...{Ansi.RESET}")
    for i,rgb in enumerate(get_best_colors(num_images)):
        closest_index = closest(images_avg_color, rgb)
        img = Image.open(temp_path + "/" + str(closest_index) + ".jpg")
        img.save(new_path + "/" + str(new_index) + ".jpg")
        new_index += 1

    shutil.rmtree(temp_path)
"""