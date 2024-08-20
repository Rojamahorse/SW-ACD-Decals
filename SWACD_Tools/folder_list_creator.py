import os
import tkinter as tk
from tkinter import filedialog, messagebox

def get_all_subdirectories(base_dir):
    folder_list = []
    for root, dirs, files in os.walk(base_dir):
        for directory in dirs:
            relative_path = os.path.relpath(os.path.join(root, directory), base_dir)
            folder_list.append(os.path.join(os.path.basename(base_dir), relative_path).replace("\\", "/"))
    return folder_list

def generate_folder_list():
    base_dir = filedialog.askdirectory(title="Select Base Directory")
    if not base_dir:
        messagebox.showerror("Error", "No directory selected")
        return

    # Add the base directory itself to the list
    subdirectories = get_all_subdirectories(base_dir)
    subdirectories.append(os.path.basename(base_dir))

    # Sort the subdirectories in reverse alphabetical order
    subdirectories.sort(reverse=True)

    # Surround each folder name with double quotes
    subdirectories = [f'"{folder}"' for folder in subdirectories]

    # Convert list to a string with double quotes around each element
    result = "Folders = [" + ", ".join(subdirectories) + "]"

    # Display result in the text widget
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, result)

def save_to_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(result_text.get(1.0, tk.END))
        messagebox.showinfo("Saved", f"Folder list saved to {file_path}")

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(result_text.get(1.0, tk.END))
    messagebox.showinfo("Copied", "Folder list copied to clipboard")

# Set up the main window
root = tk.Tk()
root.title("Folder List Generator")

# Set up the main frame
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Button to generate folder list
generate_button = tk.Button(frame, text="Generate Folder List", command=generate_folder_list)
generate_button.pack(pady=5)

# Text widget to display the result
result_text = tk.Text(frame, wrap=tk.WORD, width=80, height=20)
result_text.pack(pady=5)

# Button to save result to a file
save_button = tk.Button(frame, text="Save to File", command=save_to_file)
save_button.pack(pady=5)

# Button to copy result to clipboard
copy_button = tk.Button(frame, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack(pady=5)

# Start the GUI event loop
root.mainloop()
