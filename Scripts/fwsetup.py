#!/usr/bin/env python3
import os
import subprocess

def execute_command(cmd, suppress_errors=False):
    """Execute the given command on the shell and return its output."""
    stderr_dest = subprocess.DEVNULL if suppress_errors else None

    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=stderr_dest).strip()
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute command: {cmd}. Error: {e}")
        return ""

def backup_file(filename):
    """Backup the given file with a .backup extension."""
    os.system(f"sudo cp {filename} {filename}.backup")

def restore_backup(filename):
    """Restore a previously backed up file."""
    if os.path.exists(f"{filename}.backup"):
        os.system(f"sudo mv {filename}.backup {filename}")

def write_to_file(filename, content):
    """Write content to a given file."""
    with open(filename, 'w') as f:
        f.write(content)

def check_netplan_config(ip_address):
    content = execute_command("sudo cat /etc/netplan/50-cloud-init.yaml")
    expected_eth1_config = f"addresses: [{ip_address}/24]"
    return expected_eth1_config in content

def check_iptables_rules():
    output = execute_command("sudo iptables -t nat -L -v -n")
    return "MASQUERADE  all  --  anywhere             anywhere" in output

def check_ip_forward():
    return execute_command("sudo cat /proc/sys/net/ipv4/ip_forward") == "1"

def check_dns_forwarders():
    content = execute_command("sudo cat /etc/dnsmasq.conf")
    return all(domain in content for domain in [".cloudbrink.com", ".okta.com", ".oktacdn.com"])

def check_nameserver():
    content = execute_command("sudo cat /etc/resolv.conf")
    return "nameserver 1.1.1.1" in content

def setup_dns_fw(ip_address):
    # Backup existing configurations
    backup_file('/etc/netplan/50-cloud-init.yaml')
    backup_file('/etc/dnsmasq.conf')
    backup_file('/etc/resolv.conf')

    # Configure the netplan
    netplan_content = f'''# This file is generated from information provided by the datasource.  Changes
# to it will not persist across an instance reboot.  To disable cloud-init's
# network configuration capabilities, write a file
# /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg with the following:
# network: {{config: disabled}}
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

    # Set up IP tables
    iptables_commands = [
        "sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE",
        "echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward",
        "sudo iptables -I OUTPUT -o eth0 -d 8.8.8.8 -j ACCEPT",
        "sudo iptables -I OUTPUT -o eth0 -p udp --dport 9993 -j ACCEPT",
        "sudo iptables -I OUTPUT -o eth0 -p tcp --sport 22 -j ACCEPT",
        "sudo iptables -I OUTPUT -o eth0 -p udp --dport 443 -j ACCEPT",
        "sudo iptables -A OUTPUT -o eth0 -d 1.1.1.1 -j DROP"
    ]
    for cmd in iptables_commands:
        execute_command(cmd, suppress_errors=True)

    # Install required packages
    packages = ["iptables", "dnsmasq"]
    for pkg in packages:
        execute_command(f"sudo apt install -y {pkg}", suppress_errors=True)

    # Add entries to dnsmasq.conf
    dnsmasq_entries = [
        "server=/.cloudbrink.com/8.8.8.8",
        "server=/.okta.com/8.8.8.8",
        "server=/.oktacdn.com/8.8.8.8"
    ]
    with open('/etc/dnsmasq.conf', 'a') as f:
        for entry in dnsmasq_entries:
            f.write(entry + "\n")

    # Set nameserver in resolv.conf
    write_to_file('/etc/resolv.conf', "nameserver 1.1.1.1")

    # Disable and stop systemd-resolved service
    execute_command("sudo systemctl disable systemd-resolved", suppress_errors=True)
    execute_command("sudo systemctl stop systemd-resolved", suppress_errors=True)

    # Verification checks
    if not check_netplan_config(ip_address):
        print("Error: Netplan configuration for eth1 is not as expected.")
    if not check_iptables_rules():
        print("Error: IPTABLES MASQUERADE rule not found.")
    if not check_ip_forward():
        print("Error: IP Forwarding is not enabled.")
    if not check_dns_forwarders():
        print("Error: DNS forwarders not configured correctly in dnsmasq.conf.")
    if not check_nameserver():
        print("Error: Nameserver in resolv.conf is not as expected.")
    else:
        print("All configurations seem to be applied correctly!")

def unconfigure_dns_fw():
    restore_backup('/etc/netplan/50-cloud-init.yaml')
    restore_backup('/etc/dnsmasq.conf')
    restore_backup('/etc/resolv.conf')
    print("All configurations have been restored to their previous state!")

def main():
    choice = input("Choose an option:\n1: Setup DNS FW\n2: Unconfigure DNS FW\nEnter your choice (1/2): ")
    if choice == "1":
        ip_address = input("Please enter the IP address for eth1 (e.g. 192.168.3.1): ")
        setup_dns_fw(ip_address)
    elif choice == "2":
        unconfigure_dns_fw()
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()