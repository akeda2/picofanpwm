# picofanpwm
Tools for using the pico (rd2040) as a pwm fan controller

## Includes
```
tempsend.py - Python-script to run as service
pifanpwm.service - service
main.py - program to run on controller (rd2040 like the Raspberry Pi Pico)
```
## Usage:
Place symlink in /usr/local/bin:
```
sudo ln -s $(pwm)/tempsend.py /usr/local/bin/tempsend.py
```
Copy service, enable it and run:
```
sudo cp pifanpwm.service /etc/systemd/system/
sudo systemctl enable pifanpwm.service
sudo systemctl start pifanpwm.service
```
### Interactive use:
Sending temperature (adding 10000):
```
python3 tempsend.py 10045
```
Or just send pwm duty:
```
python3 tempsend.py 66
```
Use GPU/CPU-data:
```
python3 tempsend.py gpu
python3 tempsend.py cpu
```
All this might change a lot!