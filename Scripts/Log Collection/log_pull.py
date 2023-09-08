#!/usr/bin/env python3

import zipfile
import platform
import os
from datetime import datetime

# Paths for each operating system
windows_paths = [
    r"C:\Windows\System32\cbagent_stats.txt",
    r"C:\Windows\System32\cbagent_wtun.txt",
    r"C:\Windows\System32\cbagent_dump.log.0",
    r"C:\Windows\System32\cbagent_dump.log.0.bk",
    r"C:\Windows\System32\cbagent_dump.log.bk",
    r"C:\Windows\System32\cbagent_dump.log",
    r"C:\Windows\System32\cbdevsaas.cert",
    r"C:\Program Files\BrinkAgent\resources\src-electron\main-process\brinkagent\BrinkAgent.log",
    r"C:\Program Files\BrinkAgent\resources\src-electron\main-process\brinkagent\Installer.log",
    r"C:\Program Files\BrinkAgent\resources\src-electron\main-process\brinkagent\cb_starter_service.txt",
    r"C:\Program Files\BrinkAgent\resources\src-electron\main-process\brinkagent\iplist.txt",
    r"C:\Program Files\BrinkAgent\resources\src-electron\main-process\brinkagent\agent-log.txt",
    os.path.join(os.path.expanduser('~'), r"AppData\Roaming\BrinkAgent\logs\main.log"),
    r"C:\ProgramData\BrinkAgent\config.json",
    r"C:\ProgramData\BrinkAgent\config.json_sup",
    r"C:\Windows\System32\LogFiles\Firewall\pfirewall.log"
]

ubuntu_paths = [
    "/opt/bragent-log.txt",
    "/opt/brinkagent/control.json",
    "/opt/brinkagent/gatewayif.txt",
    "/opt/brinkagent/gatewayip.txt",
    "/opt/brinkagent/gatewaymac.txt",
    "/opt/brinkagent/iplist.txt",
    "/opt/brinkagent/iplist_delete.txt",
    "/opt/brinkagent/iplistgwif.txt",
    "/opt/brinkagent/cb_metrics.log.inf",
    "/opt/brinkagent/brinkagent.log",
    "/opt/brinkagent/cbagent_mdump",
    "/opt/brinkagent/cbagent_mexpiry",
    "/opt/brinkagent/agent_stats.txt",
    "/opt/brinkagent/installer_log.txt",
    "/opt/brinkagent/cbagent_tcpstats.txt",
    "/opt/brinkagent/cbagent_dump.log.0",
    "/opt/brinkagent/cbagent_dump.log.0.bk",
    "/opt/brinkagent/cbagent_dump.log.bk",
    "/opt/brinkagent/cbagent_dump.log",
    "/opt/BrinkAgent/Diagnostics",
    "/opt/BrinkAgent/DPAPolicy.json",
    "/opt/BrinkAgent/DPATestResults.json",
    os.path.expandvars("/home/$USER/.config/BrinkAgent/logs/main*.log")
]

macos_paths = [
    "/opt/brinkagent/control.json",
    "/opt/brinkagent/control.json_sup",
    "/opt/brinkagent/gatewayif.txt",
    "/opt/brinkagent/gatewayip.txt",
    "/opt/brinkagent/gatewaymac.txt",
    "/opt/brinkagent/iplist.txt",
    "/opt/brinkagent/iplist_delete.txt",
    "/opt/brinkagent/iplistgwif.txt",
    "/opt/brinkagent/cb_metrics.log.inf",
    "/opt/brinkagent/brinkagent.log",
    "/opt/brinkagent/cbagent_mdump",
    "/opt/brinkagent/cbagent_mexpiry",
    "/opt/brinkagent/agent_stats.txt",
    "/opt/brinkagent/installer_log.txt",
    "/opt/brinkagent/cbagent_tcpstats.txt",
    "/opt/brinkagent/cbagent_dump.log.0",
    "/opt/brinkagent/cbagent_dump.log.0.bk",
    "/opt/brinkagent/cbagent_dump.log.bk",
    "/opt/brinkagent/cbagent_dump.log",
    "/opt/BrinkAgent/Diagnostics",
    "/opt/BrinkAgent/DPAPolicy.json",
    "/opt/BrinkAgent/DPATestResults.json"
]

# Determine the current OS
current_os = platform.system()

# Select the correct set of paths for the current OS
if current_os == "Windows":
    paths = windows_paths
elif current_os == "Linux":
    paths = ubuntu_paths
elif current_os == "Darwin":  # MacOS
    paths = macos_paths
else:
    raise SystemExit("Unsupported operating system")

def compress_files(file_paths, output_file):
    # Check if the output file exists. If yes, delete it.
    if os.path.exists(output_file):
        os.remove(output_file)

    # Create a zip file and add each file
    try:
        with zipfile.ZipFile(output_file, 'w') as zipf:
            for file_path in file_paths:
                # Check if the file exists
                if not os.path.exists(file_path):
                    print(f"The specified file does not exist: {file_path}")
                    continue
                # Add file to zip
                zipf.write(file_path, os.path.basename(file_path))
        print(f"Files have been successfully compressed and saved as {output_file}")
    except Exception as e:
        print(f"An error occurred while compressing the files: {e}")

# Example usage
timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
output_zip_file = os.path.join(os.path.expanduser('~'), 'Downloads', f'cb-logs-{timestamp}.zip')
compress_files(paths, output_zip_file)