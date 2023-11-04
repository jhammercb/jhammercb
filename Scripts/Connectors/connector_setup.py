#!/usr/bin/env python3

# Logging function to capture subprocess output
def run_subprocess(command, log_file_path="/var/log/connector_setup.log", check=False):
    with open(log_file_path, 'a') as log_file:
        result = subprocess.run(command, stdout=log_file, stderr=subprocess.STDOUT, text=True, check=check)
    return result

import os

if os.geteuid() != 0:
    exit('Error: This script must be run with sudo.')
import subprocess
import sys

def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Package {package} is not installed. Installing it now.")
        run_subprocess([sys.executable, "-m", "pip", "install", package], check=True)

# Checking and installing 'cryptography' if necessary
install_and_import('cryptography')

import os
from cryptography.fernet import Fernet
import base64

def download_tar_file(username, password):
    print("Downloading the tar file...")
    cmd = [
        "sudo", "curl", "--user", f"{username}:{password}", 
        "-o", "/root/config_connector-12.2.6_1.tar.gz", 
        "https://d.cloudbrink.com/common/config_connector-12.2.6_1.tar.gz"
    ]
    run_subprocess(cmd, check=True)

def verify_md5sum():
    print("Verifying the MD5 checksum...")
    cmd = ["sudo", "md5sum", "/root/config_connector-12.2.6_1.tar.gz"]
    result = run_subprocess(cmd, capture_output=True, text=True)
    checksum = result.stdout.split()[0]
    return checksum == "b1189aa7369734e47413a3f4cea972ec"

def extract_files():
    print("Extracting the files...")
    cmd = [
        "sudo", "tar", "-xvf", "/root/config_connector-12.2.6_1.tar.gz"
    ]
    run_subprocess(cmd, check=True)

def execute_script():
    print("Executing the configure_node.sh script...")
    os.chdir("config_connector-12.2.6")
    cmd = ["sudo", "bash", "configure_node.sh"]
    run_subprocess(cmd, check=True)

def setup_cron_on_reboot(uuid):
    print("Setting up the post-reboot cron job...")
    cron_command = f"bash -c 'cd /config_connector-12.2.6/config_connector-12.2.6 && bash configure_connector.sh -o {uuid} && (crontab -l | grep -v configure_connector.sh | crontab -)'"
    run_subprocess(f'(crontab -l; echo "@reboot {cron_command}") | crontab -', shell=True, check=True)

def decrypt_credentials(encryption_key, encrypted_username, encrypted_password):
    # Convert the base64-encoded strings to bytes
    key = base64.urlsafe_b64decode(encryption_key)
    encrypted_username_bytes = base64.urlsafe_b64decode(encrypted_username)
    encrypted_password_bytes = base64.urlsafe_b64decode(encrypted_password)
    
    # Create the Fernet cipher suite
    cipher_suite = Fernet(key)
    
    # Decrypt the credentials
    decrypted_username = cipher_suite.decrypt(encrypted_username_bytes).decode('utf-8')
    decrypted_password = cipher_suite.decrypt(encrypted_password_bytes).decode('utf-8')
    
    return decrypted_username, decrypted_password

def main():
    # Set the environment variables for this script's execution context
    os.environ['ENCRYPTION_KEY'] = 'UufdHpchcGBCeW8lWmlIE4pdYblWWpkpEqSP5ZH46DM='
    os.environ['ENCRYPTED_USERNAME'] = 'gAAAAABlRnOAxNnx5EL7il68VJ1QIe50Q7Q-iynZ9Xj7lt-DwnPw-MgUOCqDoKHYslLS2-mGBVpQX77KlC3Jx4uL0sBuXvosOg=='
    os.environ['ENCRYPTED_PASSWORD'] = 'gAAAAABlRnOBn87tRPf_xEC_1Q2GAZXXDDI5bGb6jS0Gy7pn_VeuqMsShUB92dob2R_gd5OC3JyQ8Da2kLX2Pwa99kXzfTvCIw=='

    # Load the key from an environment variable
    key = os.environ.get('ENCRYPTION_KEY')
    
    # Load the encrypted credentials from an environment variable or secure config
    encrypted_username = os.environ.get('ENCRYPTED_USERNAME')
    encrypted_password = os.environ.get('ENCRYPTED_PASSWORD')
    
    # Decrypt the credentials
    username, password = decrypt_credentials(key, encrypted_username, encrypted_password)
    
    # Now use the decrypted credentials
    download_tar_file(username, password)
    if not verify_md5sum():
        print("MD5 checksum verification failed. Exiting...")
        return
    extract_files()
    
    uuid = input("Please enter the UUID for the configure_connector.sh command: ")
    setup_cron_on_reboot(uuid)
    
    print("The configure_node.sh script will now reboot the VM.")
    execute_script()

if __name__ == "__main__":
    main()