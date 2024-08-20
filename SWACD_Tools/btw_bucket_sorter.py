#   SW-ACD Decal Sorting Script
#
#   1. Importing Libraries
#       The script starts by importing several libraries:
#           os for interacting with the operating system (e.g., file paths).
#           cv2 from OpenCV for image processing.
#           numpy for numerical operations.
#           PIL.Image from the Python Imaging Library (PIL) for handling image operations.
#           collections.Counter for counting elements in lists.
#           tkinter for creating the graphical user interface (GUI).
#   2. Brightness Calculation Function
#           calculate_brightness(pixel):
#               This function calculates the brightness of a pixel using a weighted average formula based on the RGB values, reflecting the human eye’s sensitivity to different colors.
#   3. Brightness Analysis
#           analyze_brightness(image):
#               The function converts the image to a list of brightness levels for all pixels.
#               It then counts how often each brightness level occurs and identifies the two most common brightness levels in the image.
#   4. Transparency Analysis
#           analyze_transparency(image):
#               This function extracts the alpha (transparency) channel from the image and analyzes the transparency levels.
#               It counts the occurrences of each transparency level and identifies the two most common levels, converting them into percentages.
#   5. Shape Classification
#       Helper Functions:
#           is_rectangle(contour) checks if a contour has four sides, indicating it is a rectangle.
#           is_diagonal(contour) checks if a contour forms a diagonal shape based on its angle.
#           is_curve(contour) checks if a contour is curved by analyzing its convex hull.
#           classify_shape(image):
#               This function classifies the main shape in the image by examining the contours (outlines) detected in the image.
#               Depending on the detected shape, it categorizes the image into one of three categories: "sw_r" (rectangle), "sw_d" (diagonal), or "sw_c" (curve).
#   6. Grayscale Check
#           is_grayscale(image):
#               This function checks whether an image is grayscale by comparing the RGB channels. If all channels are equal, the image is grayscale.
#   7. Folder Processing Decision
#           should_process_folder(folder_name):
#               This function determines whether a folder should be processed. It skips folders starting with digits or specific prefixes like "sw_d", "sw_r", or "sw_c".
#   8. Main Image Processing
#           process_images(directory, mode, include_subfolders, ignore_color):
#               This is the core function that processes the images in a selected directory:
#               It walks through the directory and processes each image based on the selected mode (brightness, transparency, or shapes).
#           Brightness Mode: Images are sorted into folders based on the two most common brightness levels.
#           Transparency Mode: Images are sorted based on the two most common transparency levels.
#           Shapes Mode: Images are categorized into shape-based folders (sw_r, sw_d, sw_c).
#
#           If ignore_color is selected, non-grayscale images are skipped during processing.
#           If include_subfolders is disabled, only the main folder is processed.
#   9. GUI Setup
#           select_folder_and_mode():
#               This function opens a file dialog for the user to select a directory and initiates the image processing based on the selected mode and options.
#           The GUI (tkinter) includes:
#               Radio buttons for selecting the sorting mode (brightness, transparency, or shapes).
#               Checkboxes to include subfolders and ignore non-grayscale images.
#               A button to select the folder and start processing.
#   10. Main Execution
#           The script concludes with the root.mainloop() which keeps the GUI running, allowing users to interact with the interface and trigger image processing based on their selections.
#           Overall, this script allows the user to sort a collection of images into folders based on brightness, transparency, or basic shape categories using a simple graphical interface.

import os
import cv2
import numpy as np
from PIL import Image
from collections import Counter
from tkinter import Tk, Button, Label, filedialog, Radiobutton, StringVar, Checkbutton, BooleanVar


# Brightness calculation function
def analyze_brightness(image):
    # Convert image to grayscale
    grayscale_image = image.convert("L")
    grayscale_pixels = np.array(grayscale_image, dtype=float)

    if image.mode == "RGBA":
        # Get the alpha channel
        alpha_channel = np.array(image.split()[-1], dtype=float) / 255.0
        # Weight the grayscale values by their alpha (transparency) levels
        weighted_pixels = grayscale_pixels * alpha_channel
    else:
        weighted_pixels = grayscale_pixels

    if weighted_pixels.size == 0:
        return [0, 0]  # If no visible pixels, treat as fully dark

    # Convert weighted pixel values to integers to avoid floating-point precision issues
    weighted_pixels = np.round(weighted_pixels).astype(int)

    # Flatten the weighted pixel array and calculate the most common brightness levels
    brightness_counter = Counter(weighted_pixels.flatten())
    most_common = brightness_counter.most_common(2)
    
    return [level[0] for level in most_common]




# Analyze transparency levels in the image
def analyze_transparency(image):
    alpha_channel = image.split()[-1]
    transparency_levels = list(alpha_channel.getdata())
    transparency_counter = Counter(transparency_levels)
    most_common = transparency_counter.most_common(2)
    return [int(level[0] / 255 * 100) for level in most_common]

# Check if the contour is a rectangle
def is_rectangle(contour):
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    return len(approx) == 4

# Check if the contour is a diagonal
def is_diagonal(contour):
    (x, y), (MA, ma), angle = cv2.fitEllipse(contour)
    return 30 <= abs(angle) <= 60 or 120 <= abs(angle) <= 150

# Check if the contour is a curve
def is_curve(contour):
    hull = cv2.convexHull(contour)
    return len(hull) > 6

# Classify the shape based on contours
def classify_shape(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    found_diagonal = False
    found_curve = False
    found_rectangle = False

    for contour in contours:
        if is_diagonal(contour):
            found_diagonal = True
        elif is_curve(contour):
            found_curve = True
        elif is_rectangle(contour):
            found_rectangle = True

    if found_diagonal:
        return "sw_d"
    elif found_curve:
        return "sw_c"
    elif found_rectangle:
        return "sw_r"

    return None

# Check if the image is grayscale
def is_grayscale(image):
    # Check if the image is a PIL image and convert to NumPy array if needed
    if isinstance(image, Image.Image):
        image = np.array(image)

    # Handle grayscale images (2D)
    if len(image.shape) == 2:
        return True
    # Handle images with 3 channels (RGB/BGR)
    elif len(image.shape) == 3 and image.shape[2] == 3:
        b, g, r = cv2.split(image)
    # Handle images with 4 channels (RGBA/BGRA)
    elif len(image.shape) == 3 and image.shape[2] == 4:
        b, g, r, _ = cv2.split(image)  # Ignore the alpha channel
    else:
        return False

    # Check if all the channels are equal, indicating a grayscale image
    return np.all(b == g) and np.all(g == r)





# Determine if the folder should be processed
def should_process_folder(folder_name):
    return not folder_name[0].isdigit() and not folder_name.startswith(("sw_d", "sw_r", "sw_c"))

# Main function to process images based on the selected mode
# Adjust the folder naming logic to reflect grouping
def process_images(directory, mode, include_subfolders, ignore_color):
    def consolidate_level(level):
        if level in (0, 100):
            return "100"  # Group shapes
        else:
            # Round to nearest 10 or 20 increment for grouping
            return str((level // 20) * 20)

    for root, dirs, files in os.walk(directory):
        folder_name = os.path.basename(root)

        if should_process_folder(folder_name):
            for filename in files:
                if filename.endswith((".png", ".jpg")):
                    file_path = os.path.join(root, filename)
                    
                    if mode == "shapes":
                        image = cv2.imread(file_path)
                        if ignore_color and not is_grayscale(image):
                            print(f"Skipping non-grayscale image: {filename}")
                            continue
                        shape_category = classify_shape(image)
                        if shape_category:
                            target_directory = os.path.join(root, shape_category)
                            os.makedirs(target_directory, exist_ok=True)
                            target_path = os.path.join(target_directory, filename)
                            os.rename(file_path, target_path)
                            print(f"Moved {filename} to {shape_category}")
                    
                    else:  # Brightness or transparency mode
                        image = Image.open(file_path).convert("RGBA" if mode == "transparency" else "RGB")
                        if ignore_color and not is_grayscale(np.array(image)):
                            print(f"Skipping non-grayscale image: {filename}")
                            continue
                        if mode == "brightness":
                            most_common_levels = analyze_brightness(image)
                        elif mode == "transparency":
                            most_common_levels = analyze_transparency(image)

                        consolidated_levels = [consolidate_level(level) for level in most_common_levels]
                        if len(consolidated_levels) == 2:
                            target_folder_name = f"{consolidated_levels[0]}_{consolidated_levels[1]}"
                        else:
                            target_folder_name = f"{consolidated_levels[0]}_0"

                        # Additional categorization by brightness impact could be added here
                        # e.g., target_folder_name += "_Bright" or "_Dark" based on some criteria

                        target_directory = os.path.join(root, target_folder_name)
                        os.makedirs(target_directory, exist_ok=True)
                        target_path = os.path.join(target_directory, filename)
                        os.rename(file_path, target_path)
                        print(f"Moved {filename} to {target_folder_name}")
        
        if not include_subfolders:
            dirs.clear()


# Function to select the folder and start processing
def select_folder_and_mode():
    directory = filedialog.askdirectory()
    if directory:
        mode = selected_mode.get()
        include_subfolders = include_subfolders_var.get()
        ignore_color = ignore_color_var.get()
        process_images(directory, mode, include_subfolders, ignore_color)
        Label(root, text=f"Processing by {mode} complete!", fg="green").pack()

if __name__ == "__main__":
    root = Tk()
    root.title("Image Bucket Sorter")

    Label(root, text="Select sorting mode:").pack(pady=10)
    
    selected_mode = StringVar(value="brightness")
    
    Radiobutton(root, text="Sort by Brightness", variable=selected_mode, value="brightness").pack()
    Radiobutton(root, text="Sort by Transparency", variable=selected_mode, value="transparency").pack()
    Radiobutton(root, text="Sort by Basic Shapes", variable=selected_mode, value="shapes").pack()

    include_subfolders_var = BooleanVar(value=True)
    Checkbutton(root, text="Include Subfolders", variable=include_subfolders_var).pack(pady=10)

    ignore_color_var = BooleanVar(value=False)
    Checkbutton(root, text="Ignore Non-Grayscale Images", variable=ignore_color_var).pack(pady=10)

    Button(root, text="Select Folder and Sort", command=select_folder_and_mode).pack(pady=20)

    root.mainloop()
