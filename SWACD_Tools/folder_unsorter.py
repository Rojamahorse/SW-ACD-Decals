import os
import shutil
from tkinter import Tk, filedialog, Button, Label

# Function to move all files from subfolders to the main folder
def unsort_files(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            if root != directory:  # Only move files from subfolders
                try:
                    shutil.move(file_path, directory)
                    print(f"Moved {filename} to {directory}")
                except shutil.Error as e:
                    print(f"Error moving {filename}: {e}")
        # Optionally, you can remove empty subfolders
        if root != directory and not os.listdir(root):
            os.rmdir(root)
            print(f"Removed empty folder {root}")

# Function to select the main folder and start the unsorting process
def select_folder_and_unsort():
    directory = filedialog.askdirectory()
    if directory:
        unsort_files(directory)
        Label(root, text=f"Unsorting complete!", fg="green").pack()

if __name__ == "__main__":
    root = Tk()
    root.title("Folder Unsorter")

    Label(root, text="Select the main folder to unsort:").pack(pady=10)

    Button(root, text="Select Folder and Unsort", command=select_folder_and_unsort).pack(pady=20)

    root.mainloop()
