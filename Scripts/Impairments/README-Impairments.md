# Impairment Script

Ahoy! 🏴‍☠️ This script is designed to simulate packet loss and latency.

## Why?

Simulating packet loss and latency can provide insights into how networks and applications behave under these conditions. Plus, it's cool! 😎

## Disclaimer

While I've made every effort to ensure the script runs smoothly, you may encounter some bugs. The script has been primarily tested on **Raspberry Pi** and **Intel NUC** devices running **Ubuntu 20.04**. Your feedback is crucial for improvements. 🛠️

📧 Report Issues: [john@cloudbrink.io](mailto:john@cloudbrink.io) or [impairments@cloudbrink.io](mailto:impairments@cloudbrink.io)

---

## Usage

This is an interactive script, and its usage is straightforward.

### Download

```bash
wget https://raw.githubusercontent.com/jhammercb/jhammercb/main/Scripts/Impairments/impairment.py
```

### Make It Executable

```bash
chmod +x impairment.py
```

### Run with Sudo

This will install the `tc` dependency if it's not already present.

```bash
sudo ./impairment.py
```

---

## Example

```bash
wget https://raw.githubusercontent.com/jhammercb/jhammercb/main/Scripts/Impairments/impairment.py
#... output omitted ...
chmod +x impairment.py
sudo ./impairment.py
```

The script will first list your available interfaces, allowing you to select which one to use for impairments:

### Available Interfaces:

1. eno1
2. ifb0
3. lo
4. wlp58s0

---

## Future Plans 🚀

- **Single-Line Commands**: Great for scripting. E.g., `sudo ./impairments -i eth0 -ls 5% -lt 5ms -j 2ms`
- **Directional Loss**: Set loss in a single direction (tx or rx)
- **Jitter**: Add jitter option
- **Gilbert-Elliott Model**: Implement this model of loss
- **Built-In Tests**: Include a download test for baseline performance (without CB)
- **File Transfer Capabilities**: Offer built-in SMB, FTP, or other features
- **Error Validation**: More robust error checks

---

## Contact 💌

If you have ideas or feedback, feel free to email me! I'd love to incorporate as many improvements as possible.

[john@cloudbrink.io](mailto:john@cloudbrink.io)

---
