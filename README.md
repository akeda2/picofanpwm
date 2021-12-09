# picofanpwm
Tools for using the pico (rd2040) as a pwm fan controller

## Includes
```
pfp.sh - bash script to run as is or as service
pifanpwm.service - service
main.py - program to run on controller (rd2040 like the Raspberry Pi Pico)
```
## Usage:
Place symlink in /usr/local/bin:
```
sudo ln -s $(pwm)/pfp.sh /usr/local/bin/pfp
```
Copy service, enable it and run:
```
sudo cp pifanpwm.service /etc/systemd/system/
sudo systemctl enable pifanpwm.service
sudo systemctl start pifanpwm.service
```
