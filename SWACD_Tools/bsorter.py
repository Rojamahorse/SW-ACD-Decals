import os
from PIL import Image
from collections import Counter

def calculate_brightness(pixel):
    """
    Calculate the brightness of a pixel using the luminance formula.
    """
    r, g, b = pixel[:3]  # Ignore alpha if present
    # Luminance formula: 0.299*R + 0.587*G + 0.114*B
    return int(0.299 * r + 0.587 * g + 0.114 * b)

def analyze_brightness(image):
    """
    Analyze the brightness of all pixels in the image and return the two most common levels.
    """
    pixels = list(image.getdata())
    brightness_levels = [calculate_brightness(pixel) for pixel in pixels]

    # Count the frequency of each brightness level
    brightness_counter = Counter(brightness_levels)

    # Get the two most common brightness levels
    most_common = brightness_counter.most_common(2)
    
    return [level[0] for level in most_common]

def process_images(directory):
    for filename in os.listdir(directory):
        if filename.endswith((".png", ".jpg")):  # Adjust file types as needed
            file_path = os.path.join(directory, filename)
            image = Image.open(file_path).convert("RGB")

            # Analyze brightness to get the top two most common levels
            most_common_levels = analyze_brightness(image)
            
            # Create a folder name based on the most common brightness levels
            if len(most_common_levels) == 2:
                folder_name = f"{most_common_levels[0]}_{most_common_levels[1]}"
            else:
                # In case there is only one common level
                folder_name = f"{most_common_levels[0]}_0"

            # Create directory if it doesn't exist
            target_directory = os.path.join(directory, folder_name)
            os.makedirs(target_directory, exist_ok=True)

            # Move the image to the appropriate directory
            target_path = os.path.join(target_directory, filename)
            os.rename(file_path, target_path)

            print(f"Moved {filename} to {folder_name}")

if __name__ == "__main__":
    # Get the directory where this script is located
    script_directory = os.path.dirname(os.path.realpath(__file__))
    process_images(script_directory)
