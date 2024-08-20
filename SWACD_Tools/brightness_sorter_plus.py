import os
import numpy as np
from PIL import Image
from collections import Counter
from tkinter import Tk, Button, Label, filedialog, Checkbutton, BooleanVar

# Define the brightness/alpha buckets, including the 90 bucket
buckets = [5, 10, 20, 25, 50, 70, 80, 90, 100]

# Function to classify shapes into specified brightness/alpha buckets
def bucket_classify_shape(image):
    # Convert image to grayscale and separate alpha channel
    grayscale_image = image.convert("L")
    pixels = np.array(grayscale_image, dtype=float)

    if image.mode == "RGBA":
        alpha_channel = np.array(image.split()[-1], dtype=float) / 255.0
        # Apply alpha channel to the pixel brightness values
        weighted_pixels = pixels * alpha_channel
    else:
        weighted_pixels = pixels

    # Get non-transparent pixels, excluding fully transparent ones
    non_transparent_pixels = weighted_pixels[alpha_channel > 0]
    if len(non_transparent_pixels) == 0:
        return None  # Handle cases where the image is fully transparent

    # Calculate the most common brightness level among non-transparent pixels
    brightness_counter = Counter(non_transparent_pixels)
    most_common_brightness = brightness_counter.most_common(1)[0][0]

    print(f"Most common brightness for current image: {most_common_brightness}")

    # Assign the image to the nearest bucket
    nearest_bucket = min(buckets, key=lambda x: abs(x - most_common_brightness))
    return f"Shape_Brightness_{nearest_bucket}"

# Main function to process images and sort them into brightness/alpha buckets
def process_images_by_buckets(directory, include_subfolders):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                file_path = os.path.join(root, filename)
                
                image = Image.open(file_path).convert("RGBA")
                target_folder_name = bucket_classify_shape(image)
                
                if target_folder_name:
                    target_directory = os.path.join(root, target_folder_name)
                    os.makedirs(target_directory, exist_ok=True)
                    target_path = os.path.join(target_directory, filename)
                    os.rename(file_path, target_path)
                    print(f"Moved {filename} to {target_folder_name}")
        
        if not include_subfolders:
            dirs.clear()

# Function to select the folder and start processing
def select_folder_and_sort_by_buckets():
    directory = filedialog.askdirectory()
    if directory:
        include_subfolders = include_subfolders_var.get()
        process_images_by_buckets(directory, include_subfolders)
        Label(root, text=f"Processing complete!", fg="green").pack()

if __name__ == "__main__":
    root = Tk()
    root.title("Shape Bucket Sorter")

    Label(root, text="Sort Shapes by Brightness/Alpha Buckets:").pack(pady=10)

    include_subfolders_var = BooleanVar(value=True)
    Checkbutton(root, text="Include Subfolders", variable=include_subfolders_var).pack(pady=10)

    Button(root, text="Select Folder and Sort", command=select_folder_and_sort_by_buckets).pack(pady=20)

    root.mainloop()
