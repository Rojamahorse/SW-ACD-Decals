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
#           analyze_brightness(image):
#               This function converts the image to grayscale and calculates the brightness of the pixels.
#               It then counts how often each brightness level occurs and identifies the two most common brightness levels.
#               If the image has transparency, the brightness levels are weighted by the transparency levels.
#   3. Transparency Analysis
#           analyze_transparency(image):
#               This function extracts the alpha (transparency) channel from the image.
#               It counts the occurrences of each transparency level and identifies the two most common levels, converting them into percentages.
#               The transparency levels are then rounded to the nearest increment (e.g., 5 or 10) to group similar levels together.
#   4. Image Classification
#           classify_image_strict(image):
#               This function classifies the image as either a "Shape" or a "Gradient" based on the number of unique brightness levels and transparency levels.
#               Shapes are defined as having only one brightness level and one transparency level (excluding full transparency).
#   5. Grayscale Check
#           is_grayscale(image):
#               This function checks whether an image is grayscale by comparing the RGB channels. If all channels are equal, the image is grayscale.
#   6. Folder Processing Decision
#           should_process_folder(folder_name):
#               This function determines whether a folder should be processed. It skips folders starting with digits or specific prefixes like "sw_d", "sw_r", or "sw_c".
#   7. Main Image Processing
#           process_images(directory, include_subfolders, ignore_color):
#               This is the core function that processes the images in a selected directory:
#               It walks through the directory and processes each image based on the classification logic (Shapes or Gradients).
#               Shapes are moved into a "Shapes" folder, and Gradients are sorted based on their transparency levels.
#               If ignore_color is selected, non-grayscale images are skipped during processing.
#               If include_subfolders is disabled, only the main folder is processed.
#   8. GUI Setup
#           select_folder_and_mode():
#               This function opens a file dialog for the user to select a directory and initiates the image processing based on the selected mode and options.
#           The GUI (tkinter) includes:
#               Checkboxes to include subfolders and ignore non-grayscale images.
#               A button to select the folder and start processing.
#   9. Main Execution
#           The script concludes with the root.mainloop() which keeps the GUI running, allowing users to interact with the interface and trigger image processing based on their selections.
#           Overall, this script allows the user to sort a collection of images into folders based on brightness, transparency, or basic shape categories using a simple graphical interface.

import os
import cv2
import numpy as np
from PIL import Image
from collections import Counter
from tkinter import Tk, Button, Label, filedialog, Checkbutton, BooleanVar

# Analyze transparency levels in the image
def analyze_transparency(image):
    alpha_channel = image.split()[-1]
    transparency_levels = list(alpha_channel.getdata())
    transparency_counter = Counter(transparency_levels)
    most_common = transparency_counter.most_common(2)
    # Convert levels to percentages and round to nearest 10%
    return [round(int(level[0] / 255 * 100), -1) for level in most_common]

# Image classification based on strict criteria
def classify_image_strict(image):
    grayscale_image = image.convert("L")
    pixels = np.array(grayscale_image, dtype=float)

    if image.mode == "RGBA":
        alpha_channel = np.array(image.split()[-1], dtype=float) / 255.0
        weighted_pixels = pixels * alpha_channel
    else:
        weighted_pixels = pixels

    # Get unique brightness levels excluding fully transparent pixels
    unique_brightness = np.unique(np.round(weighted_pixels).astype(int))

    if image.mode == "RGBA":
        transparency_levels = np.unique(np.array(image.split()[-1], dtype=int))
        # Remove fully transparent pixels from consideration
        transparency_levels = transparency_levels[transparency_levels != 0]
    else:
        transparency_levels = np.array([255])

    # A shape must have only one brightness level and one transparency level
    if len(unique_brightness) == 1 and len(transparency_levels) == 1:
        return "Shape"
    else:
        return "Gradient"

# Consolidate transparency levels for bucket sorting
def consolidate_level(level):
    if level in (0, 100):
        return "100"  # Group shapes
    else:
        # Round to nearest 10 increment for grouping
        return str((level // 10) * 10)

# Main function to process images based on the classification logic
def process_images(directory, include_subfolders, ignore_color):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith((".png", ".jpg")):
                file_path = os.path.join(root, filename)
                
                image = Image.open(file_path).convert("RGBA")
                if ignore_color and not is_grayscale(np.array(image)):
                    print(f"Skipping non-grayscale image: {filename}")
                    continue

                classification = classify_image_strict(image)
                if classification == "Shape":
                    target_folder_name = "Shapes"
                else:
                    most_common_levels = analyze_transparency(image)
                    # Ensure the levels are sorted to avoid redundant folders
                    consolidated_levels = sorted([consolidate_level(level) for level in most_common_levels])
                    
                    # Handle case where there is only one transparency level
                    if len(consolidated_levels) == 1:
                        consolidated_levels.append("0")
                    
                    target_folder_name = f"{consolidated_levels[0]}_{consolidated_levels[1]}"

                target_directory = os.path.join(root, target_folder_name)
                os.makedirs(target_directory, exist_ok=True)
                target_path = os.path.join(target_directory, filename)
                os.rename(file_path, target_path)
                print(f"Moved {filename} to {target_folder_name}")
        
        if not include_subfolders:
            dirs.clear()

# Check if the image is grayscale
def is_grayscale(image):
    if isinstance(image, Image.Image):
        image = np.array(image)

    if len(image.shape) == 2:
        return True
    elif len(image.shape) == 3 and image.shape[2] == 3:
        b, g, r = cv2.split(image)
    elif len(image.shape) == 3 and image.shape[2] == 4:
        b, g, r, _ = cv2.split(image)
    else:
        return False

    return np.all(b == g) and np.all(g == r)

# Function to select the folder and start processing
def select_folder_and_mode():
    directory = filedialog.askdirectory()
    if directory:
        include_subfolders = include_subfolders_var.get()
        ignore_color = ignore_color_var.get()
        process_images(directory, include_subfolders, ignore_color)
        Label(root, text=f"Processing complete!", fg="green").pack()

if __name__ == "__main__":
    root = Tk()
    root.title("Image Bucket Sorter")

    Label(root, text="Sorting Options:").pack(pady=10)

    include_subfolders_var = BooleanVar(value=True)
    Checkbutton(root, text="Include Subfolders", variable=include_subfolders_var).pack(pady=10)

    ignore_color_var = BooleanVar(value=False)
    Checkbutton(root, text="Ignore Non-Grayscale Images", variable=ignore_color_var).pack(pady=10)

    Button(root, text="Select Folder and Sort", command=select_folder_and_mode).pack(pady=20)

    root.mainloop()
