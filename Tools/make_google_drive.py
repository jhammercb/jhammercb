#!/usr/bin/env python3

import os
import shutil


def create_folder_and_copy_file(src_folder, dest_drive, filename):
    # Get folder name from user
    folder_name = input("Please enter the new folder name: ")
    folder_path = os.path.join(dest_drive, folder_name)
    
    # Check if the folder already exists
    if os.path.exists(folder_path):
        print(f"Folder {folder_name} already exists!")
        return
    
    # Create new folder
    os.mkdir(folder_path)
    
    # Copy file from source to destination folder
    shutil.copy(os.path.join(src_folder, filename), folder_path)
    
    # Rename the copied file
    os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, folder_name + " Cloudbrink Overview" + ".pptx"))

def main():
    # The path to the source folder containing the file you want to copy
    source_folder = "/Users/johnweidenhammer/Library/CloudStorage/GoogleDrive-john@cloudbrink.com/Shared drives/Cloudbrink Sales/Customers/_Template"
    
    # The path to the Google Drive mounted on MacOS (adjust accordingly)
    google_drive_path = "/Users/johnweidenhammer/Library/CloudStorage/GoogleDrive-john@cloudbrink.com/Shared drives/Cloudbrink Sales/Customers"
    
    # The name of the file you want to copy
    file_name = "Cloudbrink_Template_Sept.pptx"
    
    create_folder_and_copy_file(source_folder, google_drive_path, file_name)

if __name__ == "__main__":
    main()
