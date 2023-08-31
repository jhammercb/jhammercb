Ahoy! This script's purpose is to similate packet loss and latency.

Why? Because similating packet loss and latency can help show what happens to networks and applications when those conditions are present.

Plus, it's cool.

While i've made every effort to make sure this script works smoothly, some bugs may occur.
It's mostly been tested with raspberry pi and Intel NUC devices running Ubuntu 20.04.
So bear with me, but please do report issues you see to john@cloudbrink.io or impairments@cloudbrink.io. 
We want to fix anything that comes up, so your feedback is extremely important.

Usage:
This is an interactive script, and usage is pretty straight forward.

Download it:
wget https://raw.githubusercontent.com/jhammercb/jhammercb/main/Scripts/Impairments/impairment.py

Make it executable:
chmod +x impairment.py

Run is with sudo. This will install the tc dependency if not already present:
sudo ./impairment.py

Ex:
wget https://raw.githubusercontent.com/jhammercb/jhammercb/main/Scripts/Impairments/impairment.py
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.108.133, 185.199.110.133, 185.199.109.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.108.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 7905 (7.7K) [text/plain]
Saving to: ‘impairment.py’

impairment.py    100%[========>]   7.72K  --.-KB/s    in 0.001s  

2023-08-30 23:19:34 (12.2 MB/s) - ‘impairment.py’ saved [7905/7905]

jw@impairment:~$ chmod +x impairment.py
jw@impairment:~$ sudo ./impairment.py 

The script will first pull your interfaces avilable to select which to use for impairments:
Available Interfaces:
1. eno1
2. ifb0
3. lo
4. wlp58s0
Select the interface you want to set up or clear: 1
Do you want to apply or clear configurations? (apply/clear): apply
Enter latency in ms: 50
Enter loss percentage: 10

Loss Applied: 10% half egress/ingress
Latency Applied: 50ms half egress/ingress

--- tc qdisc show output ---
qdisc prio 1: root refcnt 2 bands 2 priomap 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
qdisc netem 30: parent 1:2 limit 1000 delay 25.0ms loss 5%
qdisc netem 20: parent 1:1 limit 1000 delay 25.0ms
qdisc ingress ffff: parent ffff:fff1 ---------------- 

--- tc filter show output ---
filter parent 1: protocol ip pref 1 u32 chain 0 
filter parent 1: protocol ip pref 1 u32 chain 0 fh 800: ht divisor 1 
filter parent 1: protocol ip pref 1 u32 chain 0 fh 800::10 order 16 key ht 800 bkt 0 flowid 1:1 not_in_hw 
  match 00000d3d/0000ffff at 20
filter parent 1: protocol ip pref 1 u32 chain 0 fh 800::20 order 32 key ht 800 bkt 0 flowid 1:1 not_in_hw 
  match 00160000/ffff0000 at 20

Please configure your testing device with 192.168.100.181 of eno1 as the default gateway

To clear all settings applied from this script, simply select clear on the original interface selected.

Select the interface you want to set up or clear: 1
Do you want to apply or clear configurations? (apply/clear): clear
All impairments for eno1 have been cleared.

Future Plan:
+ Allowing for single line applications (great for scripting) ex: sudo ./impairments -i eth0 -ls 5% -lt 5ms -j 2ms
                                                                  sudo ./impairments clear
+ Setting loss in a single direction (tx or rx)
+ Applying jitter
+ Option for using the gilbert-elliott model of loss
+ Built in download test to baseline measure performance (without CB)
+ Built in SMB, FTP, or other capabilities to show local file transfers.
+ More error validation

If you have ideas, email me! Would love to incorporate as much as possible (within reason).
