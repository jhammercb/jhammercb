#!/usr/bin/env python3

import subprocess
import sys
import os

# Check if script is run with sudo
if os.geteuid() != 0:
    print("Error: You need to run this script as root using sudo.")
    exit(1)

def run_command(command_list, suppress_errors=False):
    try:
        subprocess.run(command_list, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        # Suppress error message for specific commands or error codes
        if suppress_errors and (e.returncode == 2 or 'Cannot delete qdisc with handle of zero' in e.stderr):
            return
        print(f"Running command: {' '.join(command_list)}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        print(f"Command {command_list} failed with error code {e.returncode}")

def list_interfaces():
    output = subprocess.run(["ls", "/sys/class/net"], capture_output=True, text=True)
    return output.stdout.strip().split("\n")

def apply_qdisc(interface, latency, loss):
    # Interface names must be strings
    ifb0 = "ifb0"    

    # Check if a qdisc is already present; if so, delete it
    qdisc_output = subprocess.run(["sudo", "tc", "qdisc", "show", "dev", interface], capture_output=True, text=True).stdout
    if "qdisc" in qdisc_output:
        run_command(["sudo", "tc", "qdisc", "del", "dev", interface, "root"], suppress_errors=True)
        run_command(["sudo", "tc", "qdisc", "del", "dev", ifb0, "root"], suppress_errors=True)
    
    # Convert the latency and loss into integers and then into two halves for applying on interface and ifb0
    latency_half = str(int(round(float(latency) / 2))) + "ms"
    loss_half = str(int(round(float(loss) / 2))) + "%"

    # Add prio qdiscs
    run_command(["sudo", "tc", "qdisc", "add", "dev", interface, "root", "handle", "1:", "prio", "bands", "2", "priomap", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"])
    run_command(["sudo", "tc", "qdisc", "add", "dev", ifb0, "root", "handle", "1:", "prio", "bands", "2", "priomap", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"])
    
    # Add the netem rules to parent 1:1
    run_command(["sudo", "tc", "qdisc", "add", "dev", interface, "parent", "1:1", "handle", "10:", "netem", "delay", latency_half])
    run_command(["sudo", "tc", "qdisc", "replace", "dev", interface, "parent", "1:1", "handle", "20:", "netem", "delay", latency_half])
    run_command(["sudo", "tc", "qdisc", "add", "dev", ifb0, "parent", "1:1", "handle", "10:", "netem", "delay", latency_half])
    run_command(["sudo", "tc", "qdisc", "replace", "dev", ifb0, "parent", "1:1", "handle", "20:", "netem", "delay", latency_half])
    
    # Add the netem rules to parent 1:2
    run_command(["sudo", "tc", "qdisc", "add", "dev", interface, "parent", "1:2", "handle", "30:", "netem", "delay", latency_half, "loss", loss_half])
    run_command(["sudo", "tc", "qdisc", "add", "dev", ifb0, "parent", "1:2", "handle", "30:", "netem", "delay", latency_half, "loss", loss_half])

    # Add filters
    run_command(["sudo", "tc", "filter", "add", "dev", interface, "parent", "1:", "protocol", "ip", "prio", "1", "handle", "0x10", "u32", "match", "ip", "dport", "3389", "0xffff", "flowid", "1:1"])
    run_command(["sudo", "tc", "filter", "add", "dev", interface, "parent", "1:", "protocol", "ip", "prio", "1", "handle", "0x20", "u32", "match", "ip", "sport", "22", "0xffff", "flowid", "1:1"])
    run_command(["sudo", "tc", "filter", "add", "dev", ifb0, "parent", "1:", "protocol", "ip", "prio", "1", "handle", "0x10", "u32", "match", "ip", "sport", "3389", "0xffff", "flowid", "1:1"])
    run_command(["sudo", "tc", "filter", "add", "dev", ifb0, "parent", "1:", "protocol", "ip", "prio", "1", "handle", "0x20", "u32", "match", "ip", "dport", "22", "0xffff", "flowid", "1:1"])

def clear_qdisc(interface):
    # Delete existing settings to clear configurations
    run_command(["sudo", "tc", "qdisc", "del", "dev", interface, "root"], suppress_errors=True)
    run_command(["sudo", "tc", "qdisc", "del", "dev", "ifb0", "root"], suppress_errors=True)

def fetch_tc_output(interface):
    # Fetch tc qdisc and tc filter show output for the given interface
    qdisc_output = subprocess.run(["sudo", "tc", "qdisc", "show", "dev", interface], capture_output=True, text=True).stdout
    filter_output = subprocess.run(["sudo", "tc", "filter", "show", "dev", interface], capture_output=True, text=True).stdout
    return qdisc_output, filter_output

def setup_ifb0(interface):
    # Load the ifb module if not already loaded
    interfaces = list_interfaces()
    if "ifb0" not in interfaces:
        # Load the ifb module if not already loaded
        run_command(["sudo", "modprobe", "ifb"])
        
        # Set up the ifb0 interface
        run_command(["sudo", "ip", "link", "set", "dev", "ifb0", "up"])

    else:
        print("ifb0 interface already exists - skipping.")
    
    # Clear existing ingress qdisc
    run_command(["sudo", "tc", "qdisc", "del", "dev", interface, "ingress"])
    
    # Add ingress qdisc to the selected interface
    run_command(["sudo", "tc", "qdisc", "add", "dev", interface, "ingress"])
    
    # Redirect ingress traffic from the selected interface to ifb0
    run_command(["sudo", "tc", "filter", "add", "dev", interface, "parent", "ffff:", "protocol", "ip", "u32", "match", "u32", "0", "0", "action", "mirred", "egress", "redirect", "dev", "ifb0"])

def apply_nat_and_forwarding(interface):
    # Apply NAT settings
    run_command(["sudo", "iptables", "-t", "nat", "-A", "POSTROUTING", "-o", interface, "-j", "MASQUERADE"])
    # Enable IP forwarding
    run_command(["sudo", "sh", "-c", "echo 1 > /proc/sys/net/ipv4/ip_forward"])

def clear_nat_and_forwarding(interface):
    # Clear NAT settings
    run_command(["sudo", "iptables", "-t", "nat", "-D", "POSTROUTING", "-o", interface, "-j", "MASQUERADE"], suppress_errors=True)
    # Disable IP forwarding
    run_command(["sudo", "sh", "-c", "echo 0 > /proc/sys/net/ipv4/ip_forward"])

def main():
    interfaces = list_interfaces()
    print("Available Interfaces:")
    for i, interface in enumerate(interfaces):
        print(f"{i+1}. {interface}")

    choice = int(input("Select the interface you want to set up or clear: "))
    selected_interface = interfaces[choice - 1]

    action = input("Do you want to apply or clear configurations? (apply/clear): ").strip().lower()

    if action == "apply":
        apply_nat_and_forwarding(selected_interface)
        setup_ifb0(selected_interface)
        latency = input("Enter latency in ms: ")
        loss = input("Enter loss percentage: ")
        apply_qdisc(selected_interface, latency, loss)
        
        print(f"\nLoss Applied: {loss}% half egress/ingress")
        print(f"Latency Applied: {latency}ms half egress/ingress")

        # Fetch and print tc qdisc and tc filter show outputs
        qdisc_output, filter_output = fetch_tc_output(selected_interface)
        print("\n--- tc qdisc show output ---")
        print(qdisc_output)
        print("--- tc filter show output ---")
        print(filter_output)
    
        # Get the IP address of the selected interface using `ip` command
        ip_output = subprocess.run(["ip", "-4", "addr", "show", selected_interface], capture_output=True, text=True)
        ip_address = None
        for line in ip_output.stdout.strip().split("\n"):
            if "inet" in line:
                ip_address = line.split()[1].split("/")[0]
                break
        if ip_address:
            print(f"Please configure your testing device with {ip_address} of {selected_interface} as the default gateway")
        else:
            print(f"Could not find the IP address for {selected_interface}. Please manually set the default gateway.")
    
    elif action == "clear":
        clear_nat_and_forwarding(selected_interface)
        clear_qdisc(selected_interface)
        print(f"All impairments for {selected_interface} have been cleared.")
        
    else:
        print("Invalid option. Exiting.")

if __name__ == "__main__":
    main()
