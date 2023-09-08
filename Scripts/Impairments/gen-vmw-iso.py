import subprocess
import sys
import getopt
from datetime import datetime

def update_sshd_config():
    with open("/etc/ssh/sshd_config", "a") as f:
        f.write("\nPermitRootLogin yes\n")
    subprocess.run("systemctl restart sshd", shell=True)

def log_message(message):
    print(f"[LOG] {message}")

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute command: {e}")

def update_systemd_resolve_config():
    with open("/etc/systemd/resolved.conf", "a") as f:
        f.write(f"\n[Resolve]\nDNS={NAME_SERVERS_INET}\nFallbackDNS={NAME_SERVERS_DC}\n")
    subprocess.run("systemctl restart systemd-resolved", shell=True)

def update_dl_config():
    with open("/etc/dlagent.conf", "a") as f:
        f.write(f"\n[CLOUD]\nProvider={CLOUD_PROVIDER}\nSAAS={SAAS_FLAG}\n")
        f.write(f"\n[VERSION]\nConnector={CONNECTOR_VERSION}\nConnPilot={CONN_PILOT_VERSION}\n")

def create_iso():
    subprocess.run(f"genisoimage -o {ISO_FILE} -V cidata -r -J {ISO_DIR}/user-data.txt", shell=True)

def upload_iso():
    subprocess.run(f"mv {ISO_FILE} /vmfs/volumes/{DS_NAME}/{DS_ISO_FILE}", shell=True)

def main(argv):
    global NAME_SERVERS_INET, NAME_SERVERS_DC, CLOUD_PROVIDER, SAAS_FLAG, CONNECTOR_VERSION, CONN_PILOT_VERSION, ISO_DIR, ISO_FILE, DS_NAME, DS_ISO_FILE

    try:
        opts, args = getopt.getopt(argv, "o:a:i:g:d:w:s:n:m:f:y:r:p:e:c:b:")
    except getopt.GetoptError:
        print("Invalid option")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-o':
            CB_OTP = arg
        elif opt == '-a':
            ARM_MODE = int(arg)
        elif opt == '-i':
            INET_IP = arg
        # Add other options here
        # ...

    log_message("Initializing Deployment and Checking Prerequisites")

    # Initialize Variables from Options
    NAME_SERVERS_INET = "8.8.8.8,8.8.4.4"
    NAME_SERVERS_DC = "192.168.1.1,192.168.1.2"
    CLOUD_PROVIDER = "aws"
    SAAS_FLAG = "flag_here"
    CONNECTOR_VERSION = "1.0"
    CONN_PILOT_VERSION = "1.0"
    ISO_DIR = "/path/to/iso_dir"
    TEMP_DIR = "/tmp"
    TIMESTAMP = datetime.now().strftime("%m%d%Y_%H%M%S")
    ISO_FILE = f"{TEMP_DIR}/cbuserdata_{TIMESTAMP}.iso"
    DS_NAME = "datastore_name"
    DS_ISO_DIR = "/CB-USERDATA-ISO"
    DS_ISO_FILE = f"{DS_ISO_DIR}/cbuserdata_{TIMESTAMP}.iso"

    # Function Calls
    update_sshd_config()
    update_systemd_resolve_config()
    update_dl_config()
    create_iso()
    upload_iso()
    log_message("Exiting Deployment script")

if __name__ == "__main__":
    main(sys.argv[1:])
