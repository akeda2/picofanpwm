# picofanpwm
Tools for using the pico (rd2040) as a pwm fan controller

## Use-case
I use this for controlling fans for case, gpu and cpu, letting the case fan get it's pwm data from the gpu temperature

## Includes
```
tempsend.py - Python-script to run as service
pifanpwm.service - service to run on linux host.
main.py - program to run on controller (rd2040 like the Raspberry Pi Pico)
fan.py - fanlib
settings.py - both tempsend.py and main.py will look for this,
create one from settings.defaults.py and customise as you wish.

Copy main.py, fan.py and settings.py to a Pico-board and connect pins to fan pwm.
```
## Usage:
### Semi-auto:
```
sudo make_install.sh
```
### Or manually:
Copy or symlink to /usr/local/bin:
```
sudo cp tempsend.py /usr/local/bin
OR:
sudo ln -s $(pwm)/tempsend.py /usr/local/bin/tempsend.py
```
Copy service, enable it and run:
```
sudo cp pifanpwm.service /etc/systemd/system/
cd /etc/systemd/system
sudo systemctl enable pifanpwm.service
sudo systemctl start pifanpwm.service
```
### Interactive use:
Getting help:
```
python3 tempsend.py help
```
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
python3 tempsend.py both
```
The service will run "both" as default, which will send two values to the pico:
ex: 100045 for fan1 and 200034 for fan2. Fan1 defaults to reading temperature data from the gpu through nvidia-smi, but this can of course be customized.
The CPU-mode will use '/sys/class/thermal/thermal_zone3/temp' as default, change this in your fansettings.py.

This is an ongoing project which might change a lot!
