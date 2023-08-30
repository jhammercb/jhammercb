#!/usr/bin/env python3

import subprocess
import sys

def run_command(command):
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command {e.cmd} failed with error code {e.returncode}")

def list_interfaces():
    output = subprocess.run(["ls", "/sys/class/net"], capture_output=True, text=True)
    return output.stdout.strip().split("\n")

def apply_qdisc(interface, latency, loss):
    # Delete existing settings first
    run_command(["sudo", "tc", "qdisc", "del", "dev", interface, "root"])
    run_command(["sudo", "tc", "qdisc", "del", "dev", "ifb0", "root"])
    
    # Convert the latency and loss into integers and then into two halves for applying on interface and ifb0
    latency_half = str(int(round(float(latency) / 2)))
    loss_half = str(int(round(float(loss) / 2)))

    # Add prio qdiscs and filters
    run_command(["sudo", "tc", "qdisc", "add", "dev", interface, "root", "handle", "1:", "prio"])
    run_command(["sudo", "tc", "qdisc", "add", "dev", interface, "parent", "1:1", "handle", "10:", "netem", "delay", latency_half + "ms"])
    run_command(["sudo", "tc", "qdisc", "add", "dev", interface, "parent", "1:2", "handle", "20:", "netem", "loss", loss_half + "%"])
    
    # Excluding RDP and SSH from impairment on selected interface
    run_command(["sudo", "tc", "filter", "add", "dev", interface, "parent", "1:", "protocol", "ip", "prio", "1", "handle", "0x10", "u32", "match", "ip", "dport", "3389", "0xffff", "flowid", "1:1"])
    run_command(["sudo", "tc", "filter", "add", "dev", interface, "parent", "1:", "protocol", "ip", "prio", "1", "handle", "0x20", "u32", "match", "ip", "sport", "22", "0xffff", "flowid", "1:1"])
    
    # Excluding RDP and SSH from impairment on ifb0
    run_command(["sudo", "tc", "qdisc", "add", "dev", "ifb0", "root", "handle", "1:", "prio"])
    run_command(["sudo", "tc", "qdisc", "add", "dev", "ifb0", "parent", "1:1", "handle", "10:", "netem", "delay", latency_half + "ms"])
    run_command(["sudo", "tc", "qdisc", "add", "dev", "ifb0", "parent", "1:2", "handle", "20:", "netem", "loss", loss_half + "%"])
    run_command(["sudo", "tc", "filter", "add", "dev", "ifb0", "parent", "1:", "protocol", "ip", "prio", "1", "handle", "0x10", "u32", "match", "ip", "sport", "3389", "0xffff", "flowid", "1:1"])
    run_command(["sudo", "tc", "filter", "add", "dev", "ifb0", "parent", "1:", "protocol", "ip", "prio", "1", "handle", "0x20", "u32", "match", "ip", "dport", "22", "0xffff", "flowid", "1:1"])

def clear_qdisc(interface):
    # Delete existing settings to clear configurations
    run_command(["sudo", "tc", "qdisc", "del", "dev", interface, "root"])
    run_command(["sudo", "tc", "qdisc", "del", "dev", "ifb0", "root"])

def fetch_tc_output(interface):
    # Fetch tc qdisc and tc filter show output for the given interface
    qdisc_output = subprocess.run(["sudo", "tc", "qdisc", "show", "dev", interface], capture_output=True, text=True).stdout
    filter_output = subprocess.run(["sudo", "tc", "filter", "show", "dev", interface], capture_output=True, text=True).stdout
    return qdisc_output, filter_output

def main():
    interfaces = list_interfaces()
    print("Available Interfaces:")
    for i, interface in enumerate(interfaces):
        print(f"{i+1}. {interface}")

    choice = int(input("Select the interface you want to set up or clear: "))
    selected_interface = interfaces[choice - 1]

    action = input("Do you want to apply or clear configurations? (apply/clear): ").strip().lower()

    if action == "apply":
        latency = input("Enter latency in ms: ")
        loss = input("Enter loss percentage: ")
        
        apply_qdisc(selected_interface, latency, loss)
        
        print(f"\nLoss Applied: {loss}%")
        print(f"Latency Applied: {latency}ms")

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
        clear_qdisc(selected_interface)
        print(f"All impairments for {selected_interface} have been cleared.")
        
    else:
        print("Invalid option. Exiting.")

if __name__ == "__main__":
    main()
