#!/usr/bin/env python3

import os
import subprocess
import json

# Function to run shell commands
def run_command(command):
    subprocess.run(command, shell=True, check=True)

# Update and upgrade packages
run_command("sudo apt update")
run_command("sudo apt upgrade -y")

# Install redis-server
run_command("sudo apt install redis-server -y")

# Download .deb packages using curl
run_command("curl -o edgeagent-12.2.7-amd64.deb https://storage.cloud.google.com/cb-edge-store-us/wren/edgeagent-12.2.7-amd64.deb")
run_command("curl -o cbpop-12.2.415-ubuntu2004-amd64.deb https://storage.cloud.google.com/cb-edge-store-us/wren/cbpop-12.2.415-ubuntu2004-amd64.deb")

# Install .deb packages
run_command("sudo dpkg -i edgeagent-12.2.7-amd64.deb")
run_command("sudo dpkg -i cbpop-12.2.415-ubuntu2004-amd64.deb")

# Get vendor input from user
vendor = input("Enter the vendor name: ")

# JSON configuration
config = {
    "schema": "",
    "uuid": "",
    "vendor": vendor,
    "provider": "PVT",
    "region": "",
    "flags": "wren",
    "agntver": "0.4.0",
    "agnttype": "Edge",
    "pkgver": "latest",
    "pkgname": "cbpop",
    "duration": 10,
    "upgrade": False,
    "debug": False,
    "dryrun": False,
    "srv_provider": "CLB",
    "metric_pipeline": True
}

# Create directory if it doesn't exist
os.makedirs("/opt/edgeagent", exist_ok=True)

# Write configuration to file
with open("/opt/edgeagent/config", "w") as file:
    json.dump(config, file, indent=4)

# Enable and start services
run_command("sudo systemctl enable edgeagent")
run_command("sudo systemctl start edgeagent")
run_command("sudo systemctl enable cbpop")
run_command("sudo systemctl start cbpop")

print("Setup completed successfully.")