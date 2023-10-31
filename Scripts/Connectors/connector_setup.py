#!/usr/bin/env python3

import os
import subprocess
import hashlib
import getpass

def download_tar_file(username, password):
    print("Downloading the tar file...")
    cmd = [
        "sudo", "curl", "--user", f"{username}:{password}", 
        "-o", "/root/config_connector-12.2.6_1.tar.gz", 
        "https://d.cloudbrink.com/common/config_connector-12.2.6_1.tar.gz"
    ]
    subprocess.run(cmd, check=True)

def verify_md5sum():
    print("Verifying the MD5 checksum...")
    cmd = ["sudo", "md5sum", "/root/config_connector-12.2.6_1.tar.gz"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    checksum = result.stdout.split()[0]
    return checksum == "b1189aa7369734e47413a3f4cea972ec"

def extract_files():
    print("Extracting the files...")
    cmd = [
        "sudo", "tar", "-xvf", "/root/config_connector-12.2.6_1.tar.gz"
    ]
    subprocess.run(cmd, check=True)

def execute_script():
    print("Executing the configure_node.sh script...")
    os.chdir("config_connector-12.2.6")
    cmd = ["sudo", "bash", "configure_node.sh"]
    subprocess.run(cmd, check=True)

def main():
    username = input("Please enter the username for downloading the tar file: ")
    password = getpass.getpass("Please enter the password for downloading the tar file: ")

    download_tar_file(username, password)
    if not verify_md5sum():
        print("MD5 checksum verification failed. Exiting...")
        return
    extract_files()
    execute_script()
    print("The configure_node.sh script will now reboot the VM. Please be aware!")

if __name__ == "__main__":
    main()
