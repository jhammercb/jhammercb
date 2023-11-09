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

def setup_cron_on_reboot(uuid):
    print("Setting up the post-reboot cron job...")
    cron_command = f"bash -c 'cd /home/cb/config_connector-12.2.6 && sudo bash configure_connector.sh -o {uuid} && (crontab -l | grep -v configure_connector.sh | crontab -)'"
    subprocess.run(f'(crontab -l; echo "@reboot {cron_command}") | crontab -', shell=True, check=True)

def add_path_to_script(script_path):
    path_addition = "export PATH=$PATH:/usr/local/sbin:/usr/sbin:/sbin\n"

    with open(script_path, 'r') as file:
        contents = file.readlines()

    if not any(line.startswith('export PATH=') for line in contents):
        contents.insert(1, path_addition)

    with open(script_path, 'w') as file:
        file.writelines(contents)

def main():
    username = input("Please enter the username for downloading the tar file: ")
    password = getpass.getpass("Please enter the password for downloading the tar file: ")

    download_tar_file(username, password)
    if not verify_md5sum():
        print("MD5 checksum verification failed. Exiting...")
        return
    extract_files()
    
    script_path = "/home/cb/config_connector-12.2.6/configure_connector.sh"
    add_path_to_script(script_path)

    uuid = input("Please enter the UUID for the configure_connector.sh command: ")
    setup_cron_on_reboot(uuid)
    
    print("The configure_node.sh script will now reboot the VM.")
    execute_script()

if __name__ == "__main__":
    main()