Create a folder named slideshow in the same location where the code is stored, then add all of the photographs in that folder with the numbers 001 to 022.
OR, add the following code to the project code.
import os

def rename_images(folder_path):
    # Get all image files
    image_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    # Sort the files 
    image_files.sort()
    
    # Rename files
    for i, filename in enumerate(image_files):
        old_file = os.path.join(folder_path, filename)
        new_file = os.path.join(folder_path, f"{i+1:03d}{os.path.splitext(filename)[1]}")
        os.rename(old_file, new_file)
        print(f"Renamed {filename} to {os.path.basename(new_file)}")

# Usage
rename_images("path_to_your_image_folder")
