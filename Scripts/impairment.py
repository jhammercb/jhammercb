#!/usr/bin/env python3

import os
import subprocess
import re

# Verify outputs
def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
        return output
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e.output}")
        return 

def verify_impairments(interface, latency, loss):
    # Run command to get current qdisc settings
    cmd_output = run_command(f"tc qdisc show dev {interface}")
    
    if cmd_output is None:
        print("Failed to verify qdisc settings.")
        return False

    # Use regex to find the latency and loss settings in the output
    latency_search = re.search(f"delay {latency}ms", cmd_output)
    loss_search = re.search(f"loss {loss}%", cmd_output)

    if latency_search and loss_search:
        print(f"Verification succeeded. Latency: {latency}ms, Loss: {loss}% are set correctly.")
        return True
    else:
        print("Verification failed. Settings may not be applied correctly.")
        print("Current settings are:")
        print(cmd_output)
        return False

# Check if script is run with sudo
if os.geteuid() != 0:
    print("Error: You need to run this script as root using sudo.")
    exit(1)

#Check if TC is already installed
def is_tc_installed():
    try:
        subprocess.check_call(["tc", "-V"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

# Install required Dependencies
def install_dependencies():
    if not is_tc_installed():
        print("Installing tc...")
        os.system("sudo apt-get update")
        os.system("sudo apt-get install -y tc")
    else:
        print("tc is already installed.")

# Clear Impairments
def clear_impairments(interface):
    try:
        output = subprocess.check_output(f"tc qdisc show dev {interface}", shell=True).decode('utf-8')
        if "qdisc netem" in output:
            os.system(f"sudo tc qdisc del dev {interface} root")
    except subprocess.CalledProcessError:
        print(f"No existing qdisc found on interface {interface}. Skipping deletion.")

# Exempt specific ports from impairments so you dont lose access
def exempt_ports(interface):
    run_command(f"sudo iptables -A OUTPUT -t mangle -p tcp --sport 22 -j MARK --set-mark 1")
    run_command(f"sudo iptables -A OUTPUT -t mangle -p tcp --sport 3389 -j MARK --set-mark 1")
    run_command(f"sudo tc filter add dev {interface} parent 1:0 protocol ip prio 1 handle 1 fw flowid 1:1")

#Set Desired Impairment    
def set_impairments(interface, latency, loss):
    os.system(f"sudo tc qdisc add dev {interface} parent 1:2 handle 30: netem delay {latency}ms loss {loss}%")

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
        action = input("What would you like to do? (set/clear/exit): ").lower()

        if action == "exit":
            print("Exiting.")
            break

        if action == "clear":
            clear_impairments(selected_interface)
            print(f"Network impairments cleared for interface: {selected_interface}")
            continue

        if action == "set":
            print("Pick a level of latency:")
            latency_choices = ["0ms", "5ms", "10ms", "Custom"]
            for i, choice in enumerate(latency_choices):
                print(f"{i}. {choice}")

            latency_selection = int(input("Enter the number corresponding to your choice: "))
            if latency_selection not in range(len(latency_choices)):
                print("Invalid selection, try again.")
                continue

            if latency_choices[latency_selection] == "Custom":
                latency = input("Enter custom latency in ms: ")
            else:
                latency = latency_choices[latency_selection].replace("ms", "")
        
            print("Then, pick a loss level:")
            loss_choices = ["0%", "1%", "2%", "5%", "10%", "Custom"]
            for i, choice in enumerate(loss_choices):
                print(f"{i}. {choice}")

            loss_selection = int(input("Enter the number corresponding to your choice: "))
            if loss_selection not in range(len(loss_choices)):
                print("Invalid selection, try again.")
                continue

            if loss_choices[loss_selection] == "Custom":
                loss = input("Enter custom loss in percentage: ")
            else:
                loss = loss_choices[loss_selection].replace("%", "")
        
            clear_impairments(selected_interface)
            exempt_ports(selected_interface)
            set_base_qdisc(selected_interface)
            set_impairments(selected_interface, latency, loss)

            if verify_impairments(selected_interface, latency, loss):
                print(f"Network impairments set successfully. Interface: {selected_interface}, Latency: {latency}ms, Loss: {loss}%")
            else:
                print("Failed to set network impairments. Please check your settings.")

        elif action == "clear":
            # Clear existing impairments and port exemptions
            clear_impairments(selected_interface)
            clear_exemptions(selected_interface)
                
        should_continue = input("Would you like to set another impairment? (y/n): ")
        if should_continue.lower() != 'y':
            break

if __name__ == "__main__":
    main()
