#!/bin/bash
set -e

mkdir -p /opt/remote-run/bin
cp remote-run.py /opt/remote-run/bin
chmod +x /opt/remote-run/bin/remote-run.py

cp remote-run /usr/bin
chmod +x /usr/bin/remote-run

cp requirements.txt /opt/remote-run/bin
cd /opt/remote-run/bin
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
deactivate

echo "remote-run installed successfully"
     
exit 0


#     This script installs the remote-run script in  /usr/bin  and the remote-run.py script in  /opt/remote-run/bin . It also creates a virtual environment in  /opt/remote-run/bin/venv  and installs the required packages. 
#     To install the remote-run script, run the following command: 
#     $ sudo bash install.sh
#     
#     The script will install the remote-run script and print the following message: 
#     remote-run installed successfully
#     
#     To uninstall the remote-run script, run the following command: 
#     $ sudo bash uninstall.sh
#     
#     The script will remove the remote-run script and print the following message: 
#     remote-run uninstalled successfully
