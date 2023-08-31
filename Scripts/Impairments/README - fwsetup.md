# Firewall Script

Ahoy! 🏴‍☠️ This script is designed setup a deny all outbound DNS rule, similating some real-world firewall configurations.

---

## Why?

Companies like to put in firewalls that deny all outbound traffic. While this is a noble concept, it makes application developers lives painful.

In this configuration, you have to be sure what the port / protocol / domain / ips being called by a website or app are. Otherwise, it is dropped.

Plus, it's cool! 😎

---

## Disclaimer

While I've made every effort to ensure the script runs smoothly, you may encounter some bugs. The script has been primarily tested on **Raspberry Pi** and **Intel NUC** devices running **Ubuntu 20.04**. Your feedback is crucial for improvements. 🛠️

📧 Report Issues: [john@cloudbrink.io](mailto:john@cloudbrink.io) or [impairments@cloudbrink.io](mailto:impairments@cloudbrink.io)

---

## Pre-reqs

A HW device or virtual machine with two network interfaces
Ubuntu 20.04

---

## Usage

This is an interactive script, and its usage is straightforward.

### Download

```bash
wget https://raw.githubusercontent.com/jhammercb/jhammercb/main/Scripts/Impairments/fwsetup.py
```

### Make It Executable

```bash
chmod +x fwsetup.py
```
### Warning! Running this script will install iptables and dnsmasq, if not already present. 
### It disables systemd-resolved, and clears the current configs in:

### * /etc/netplan/50-cloud-init.yaml
### * /etc/dnsmasq.conf
### * /etc/resolv.conf

### If you have these files set up with custom configs, know that they will be cleared. Please back up accordingly.
### Run with Sudo
```bash
sudo ./fwsetup.py
```
### Follow the prompts:
```bash
Choose an option:
1: Setup DNS FW
2: Unconfigure DNS FW
3: Exit
Enter your choice (1/2/3): 1
```

Enter an IP address, this should be reachable from the network and device you want to test with. 
This IP will be what will need to be manually set for the default GW and DNS server of the testing device.

```bash
Please enter the IP address for eth1 (e.g. 192.168.3.1): 192.168.200.1
You're about to set eth1's IP to 192.168.200.1. Are you sure? (yes/no) yes
Starting DNS FW setup...
Backing up current netplan configuration...
Writing new netplan configuration...
Configuring IP tables...
Installing required packages...
Updating dnsmasq configuration...
Setting nameserver in resolv.conf...
Disabling and stopping systemd-resolved service...
DNS FW setup completed successfully!
```
---

## Configurration outcomes

iptables will be populated with an accept rule for 8.8.8.8 and deny for 1.1.1.1
It will also create an allow rule for udp 443, tcp 22 (ssh), and udp 9993. These are for Cloudbrink to be able to make an outbound connection to the SaaS and Edges.

```bash
Chain INPUT (policy ACCEPT)
target     prot opt source               destination         

Chain FORWARD (policy ACCEPT)
target     prot opt source               destination         

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination         
ACCEPT     udp  --  anywhere             anywhere             udp dpt:443
ACCEPT     tcp  --  anywhere             anywhere             tcp spt:ssh
ACCEPT     udp  --  anywhere             anywhere             udp dpt:9993
ACCEPT     all  --  anywhere             8.8.8.8             
DROP       all  --  anywhere             1.1.1.1   
```

Resolv.conf will get updated so the name server is specfically 1.1.1.1

```bash
nameserver 1.1.1.1
```
Dnsmasq.conf will be updated with the below records, so that when queried, will go the to the IP that is set to **ACCEPT** in iptables.

```bash
server=/.cloudbrink.com/8.8.8.8
server=/.okta.com/8.8.8.8
server=/.oktacdn.com/8.8.8.8
```

In this configuration, you can then allow access to any IP or Application through the Cloudbrink tunnel by configuring the appropriate application or enterprise service.

---

## Future Plans 🚀

- **Single-Line Commands**: Great for scripting. E.g., `sudo ./fwsetup -i eth0 -allow 8.8.4.4 -deny 8.8.8.8`
- **Interface identification**: Pull list of available interfaces and allow selection of interface to be configured
- **Error Validation**: More robust error checks

---

## Contact 💌

If you have ideas or feedback, feel free to email me! I'd love to incorporate as many improvements as possible.

[john@cloudbrink.io](mailto:john@cloudbrink.io)

---
