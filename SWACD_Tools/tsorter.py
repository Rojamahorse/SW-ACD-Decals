import os
from PIL import Image
from collections import Counter

def analyze_transparency(image):
    """
    Analyze the transparency of all pixels in the image and return the two most common levels.
    """
    alpha_channel = image.split()[-1]
    transparency_levels = list(alpha_channel.getdata())

    # Count the frequency of each transparency level
    transparency_counter = Counter(transparency_levels)

    # Get the two most common transparency levels
    most_common = transparency_counter.most_common(2)
    
    # Convert transparency levels to percentage
    most_common_levels = [int(level[0] / 255 * 100) for level in most_common]
    
    return most_common_levels

def process_images(directory):
    for filename in os.listdir(directory):
        if filename.endswith((".png", ".jpg")):  # Adjust file types as needed
            file_path = os.path.join(directory, filename)
            image = Image.open(file_path).convert("RGBA")

            # Analyze transparency to get the top two most common levels
            most_common_levels = analyze_transparency(image)
            
            # Create a folder name based on the most common transparency levels
            if len(most_common_levels) == 2:
                folder_name = f"{most_common_levels[0]}_{most_common_levels[1]}"
            else:
                # In case there is only one common level (e.g., fully opaque images)
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
