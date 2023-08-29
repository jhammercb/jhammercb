#!/usr/bin/env python3

import os
import subprocess

# Check if script is run with sudo
if os.geteuid() != 0:
    print("Error: You need to run this script as root using sudo.")
    exit(1)

# Install required Dependencies
def install_dependencies():
    os.system("sudo apt-get update")
    os.system("sudo apt-get install -y tc")

# Clear Impairments
def clear_impairments(interface):
    try:
        output = subprocess.check_output(f"tc qdisc show dev {interface}", shell=True).decode('utf-8')
        if "qdisc netem" in output:
            os.system(f"sudo tc qdisc del dev {interface} root")
    except subprocess.CalledProcessError:
        print(f"No existing qdisc found on interface {interface}. Skipping deletion.")

#Set Desired Impairment    
def set_impairments(interface, latency, loss):
    os.system(f"sudo tc qdisc add dev {interface} root netem delay {latency}ms loss {loss}%")

#Get the Interfaces to be picked
def get_interfaces():
    try:
        output = subprocess.check_output("ip link show", shell=True).decode('utf-8')
        interfaces = []
        for line in output.split("\n"):
            if "mtu" in line:
                interface = line.split(":")[1].strip().split(" ")[0]
                interfaces.append(interface)
        return interfaces
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def main():
    install_dependencies()
    
    interfaces = get_interfaces()
    if not interfaces:
        print("No interfaces found. Exiting.")
        return

    print("Available network interfaces:")
    for i, interface in enumerate(interfaces):
        print(f"{i}. {interface}")
    
    interface_selection = int(input("Enter the number corresponding to the interface you want to configure: "))
    if interface_selection not in range(len(interfaces)):
        print("Invalid selection, exiting.")
        return

    selected_interface = interfaces[interface_selection]
    
    while True:
        print("Pick a level of latency:")
        latency_choices = ["0ms", "5ms", "10ms"]
        for i, choice in enumerate(latency_choices):
            print(f"{i}. {choice}")

        latency_selection = int(input("Enter the number corresponding to your choice: "))
        if latency_selection not in range(len(latency_choices)):
            print("Invalid selection, try again.")
            continue
        latency = latency_choices[latency_selection].replace("ms", "")
        
        print("Then, pick a loss level:")
        loss_choices = ["0%", "0.05%", "1%", "1.5%", "2%", "5%", "10%"]
        for i, choice in enumerate(loss_choices):
            print(f"{i}. {choice}")

        loss_selection = int(input("Enter the number corresponding to your choice: "))
        if loss_selection not in range(len(loss_choices)):
            print("Invalid selection, try again.")
            continue
        loss = loss_choices[loss_selection].replace("%", "")
        
        clear_impairments(selected_interface)
        set_impairments(selected_interface, latency, loss)
        
        print(f"Network impairments set. Interface: {selected_interface}, Latency: {latency}ms, Loss: {loss}%")
        
        should_continue = input("Would you like to set another impairment? (y/n): ")
        if should_continue.lower() != 'y':
            break

if __name__ == "__main__":
    main()
