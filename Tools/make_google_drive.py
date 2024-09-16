#!/usr/bin/env python3

import os
import shutil

def create_folder_and_copy_files(src_folder, dest_drive, filenames):
    # Get folder name from user
    folder_name = input("Please enter the new folder name: ")
    folder_path = os.path.join(dest_drive, folder_name)
    
    # Check if the folder already exists
    if os.path.exists(folder_path):
        print(f"Folder {folder_name} already exists!")
        return
    
    # Create new folder
    try:
        os.mkdir(folder_path)
        print(f"Created folder: {folder_path}")
    except Exception as e:
        print(f"Error creating folder: {e}")
        return

    # Copy each file from the source to the destination folder and rename if necessary
    for filename in filenames:
        try:
            src_file_path = os.path.join(src_folder, filename)
            dest_file_path = shutil.copy(src_file_path, folder_path)
            print(f"Copied {src_file_path} to {dest_file_path}")

            # Rename 'CB-Note-Template' to 'folder_name + Notes'
            if filename == "CB-Note-Template.gdoc":
                new_name = folder_name + "-Notes.gdoc"
                os.rename(dest_file_path, os.path.join(folder_path, new_name))
                print(f"Renamed to: {new_name}")

            # Rename 'Cloudbrink Overview - Latest.pptx' to 'folder_name + Presentation'
            elif filename == "Cloudbrink Overview - Latest.pptx":
                new_name = folder_name + " Overview.pptx"
                os.rename(dest_file_path, os.path.join(folder_path, new_name))
                print(f"Renamed to: {new_name}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

def main():
    # The path to the source folder containing the files you want to copy
    source_folder = "/Users/johnweidenhammer/Library/CloudStorage/GoogleDrive-john@cloudbrink.com/Shared drives/Cloudbrink Sales/Customers/_Template"
    
    # The path to the Google Drive mounted on MacOS (adjust accordingly)
    google_drive_path = "/Users/johnweidenhammer/Library/CloudStorage/GoogleDrive-john@cloudbrink.com/Shared drives/Cloudbrink Sales/Customers"
    
    # The names of the files you want to copy
    file_names = ["Cloudbrink Overview - Latest.pptx", "CB-Note-Template.gdoc"]

    create_folder_and_copy_files(source_folder, google_drive_path, file_names)

if __name__ == "__main__":
    main()
