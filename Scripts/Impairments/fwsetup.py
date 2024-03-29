#!/usr/bin/env python3

import os
import subprocess
import logging
import time

# Check if script is run with sudo
if os.geteuid() != 0:
    print("Error: You need to run this script as root using sudo.")
    exit(1)

# Setting up logging
logging.basicConfig(filename='fwsetup.log', level=logging.INFO)

def execute_command(cmd):
    """Execute the given command on the shell and return its output."""
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.PIPE).strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing '{cmd}': {e.stderr}")
        print(f"Error: {e.stderr}")
        exit(1)

def show_progress(step):
    print(f"{step}...", end="", flush=True)
    time.sleep(1)
    print("done!")

def backup_file(filename):
    """Create a backup of the given file."""
    if os.path.exists(filename):
        execute_command(f"cp {filename} {filename}.backup")
    else:
        print(f"Warning: {filename} does not exist. Skipping backup.")

def files_to_backup(ip_address):
    # Backup configurations
    backup_file('/etc/netplan/50-cloud-init.yaml')
    backup_file('/etc/dnsmasq.conf')
    backup_file('/etc/resolv.conf')

def write_to_file(filename, content):
    """Write content to a given file."""
    with open(filename, 'w') as f:
        f.write(content)

def validate_ip(ip_address):
    """Basic IP validation."""
    parts = ip_address.split(".")
    if len(parts) != 4:
        return False
    for item in parts:
        try:
            if not 0 <= int(item) <= 255:
                return False
        except ValueError:
            return False
    return True

def setup_dns_fw(ip_address):
    print("Starting DNS FW setup...")

    print("Backing up current netplan configuration...")
    backup_file('/etc/netplan/50-cloud-init.yaml')

    print("Writing new netplan configuration...")
    netplan_content = f'''
network:
    ethernets:
        eth0:
            dhcp4: true
            optional: true
        eth1:
            dhcp4: false
            addresses: [{ip_address}/24]
    version: 2
    '''
    write_to_file('/etc/netplan/50-cloud-init.yaml', netplan_content)

 execute_command("sudo netplan apply")
    if not check_netplan_config(ip_address):
        raise Exception("Netplan configuration for eth1 is not as expected.")

    # Set up IP tables
    print("Configuring IP tables...")
    iptables_commands = [
        "iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE",
        "echo 1 > /proc/sys/net/ipv4/ip_forward",
        "iptables -I OUTPUT -o eth0 -d 8.8.8.8 -j ACCEPT",
        "iptables -I OUTPUT -o eth0 -p udp --dport 9993 -j ACCEPT",
        "iptables -I OUTPUT -o eth0 -p tcp --sport 22 -j ACCEPT",
        "iptables -I OUTPUT -o eth0 -p udp --dport 443 -j ACCEPT",
        "iptables -A OUTPUT -o eth0 -d 1.1.1.1 -j DROP"
    ]
    for cmd in iptables_commands:
        execute_command(cmd)

    # Install required packages
    print("Installing required packages...")
    packages = ["iptables", "dnsmasq"]
    for pkg in packages:
        execute_command(f"sudo apt install -y {pkg}")

    # Add entries to dnsmasq.conf
    print("Updating dnsmasq configuration...")
    backup_file('/etc/dnsmasq.conf')
    dnsmasq_entries = [
        "server=/.cloudbrink.com/8.8.8.8",
        "server=/.okta.com/8.8.8.8",
        "server=/.oktacdn.com/8.8.8.8"
    ]
    with open('/etc/dnsmasq.conf', 'a') as f:
        for entry in dnsmasq_entries:
            f.write(entry + "\n")

    # Set nameserver in resolv.conf
    print("Setting nameserver in resolv.conf...")
    backup_file('/etc/resolv.conf')
    write_to_file('/etc/resolv.conf', "nameserver 1.1.1.1")

    # Disable and stop systemd-resolved service
    print("Disabling and stopping systemd-resolved service...")
    execute_command("sudo systemctl disable systemd-resolved")
    execute_command("sudo systemctl stop systemd-resolved")

    print("DNS FW setup completed successfully!")

def unconfigure_dns_fw():
    print("Starting DNS FW unconfiguration...")

    # Restore backed up files
    print("Restoring netplan configuration...")
    execute_command("mv /etc/netplan/50-cloud-init.yaml.backup /etc/netplan/50-cloud-init.yaml")

    #Apply the original netplan settings
    execute_command("sudo netplan apply")
    if check_netplan_config("{ip_address}")
        raise Exception("Failed to restore the original netplan configuration")

    print("Restoring dnsmasq configuration...")
    execute_command("mv /etc/dnsmasq.conf.backup /etc/dnsmasq.conf")

    print("Restoring resolv.conf...")
    execute_command("mv /etc/resolv.conf.backup /etc/resolv.conf")

    # Enable and restart systemd-resolved
    print("Restoring systemd-resolved service")
    execute_command("sudo systemctl enable systemd-resolved")
    execute_command("sudo systemctl restart systemd-resolved")

    print("DNS FW unconfiguration completed successfully!")

def main():
    while True:
        print("\nChoose an option:")
        print("1: Setup DNS FW")
        print("2: Unconfigure DNS FW")
        print("3: Setup Impairment Options")
        print("4: Exit")
        
        choice = input("Enter your choice (1/2/3/4): ")

        if choice == "1":
            ip_address = input("Please enter the IP address for eth1 (e.g. 192.168.3.1): ")
            if validate_ip(ip_address):
                confirmation = input(f"You're about to set eth1's IP to {ip_address}. Are you sure? (yes/no) ")
                if confirmation.lower() == "yes":
                    setup_dns_fw(ip_address)
                    logging.info(f"DNS FW set up with IP address: {ip_address}")
                else:
                    print("Setup DNS FW was cancelled.")
            else:
                print("Invalid IP address entered.")
        elif choice == "2":
            confirmation = input("You're about to unconfigure the DNS FW. This will revert the settings. Are you sure? (yes/no) ")
            if confirmation.lower() == "yes":
                unconfigure_dns_fw()
                logging.info("DNS FW was unconfigured.")
            else:
                print("Unconfigure DNS FW was cancelled.")
        elif choice == "3":
            print("Work in progress, not yet ready")
            break
        elif choice == "4":
            print("......")
            break
        else:
            print("That's not on the menu!")

if __name__ == "__main__":
    main()