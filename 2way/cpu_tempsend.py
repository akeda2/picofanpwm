#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import RPi.GPIO as GPIO
import time
import signal
import sys
import os
import atexit
import subprocess
import io
import serial

# Configuration
#FAN_PIN = 14            # BCM pin used to drive PWM fan
WAIT_TIME = 2           # [s] Time to wait between each refresh
PWM_FREQ = 25           # [kHz] 25kHz for Noctua PWM control

# Configurable temperature and fan speed
MIN_TEMP = 35
MIN_TEMP_DEAD_BAND = 5
MAX_TEMP = 75
FAN_LOW = 30
FAN_HIGH = 100
FAN_OFF = 30
FAN_MAX = 100

# Variable definition
outside_dead_band_higher = True

# Get CPU's temperature
def getCpuTemperature():
    #res = 60
    #res = os.popen('cat /sys/class/thermal/thermal_zone0/temp').readline()
#    res = os.popen('nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader').readline()
    with open(r"/sys/class/thermal/thermal_zone0/temp") as File:
        res = File.readline()
    temp = float(res) / 1000
    print(str(int(res)))
#    temp = float(res)/1
#    print("temp is {0}".format(temp)) # Uncomment for testing
    return temp

class Sender:
    TERMINATOR = '\r'.encode('UTF8')
    DEVICE = '/dev/ttyACM'

    def __init__(self, device=DEVICE, baud=9600, timeout=1):
        myDevice = device + '0'
        if os.path.exists(myDevice):
            exDevice = myDevice
        else:
            exDevice = device + '1'

        try:
            self.serial = serial.Serial(exDevice, baud, timeout=timeout)
        except:
            print("fail")
    def receive(self) -> str:
        line = self.serial.read_until(self.TERMINATOR)
        return line.decode('UTF8').strip()
    def send(self, text: str) -> bool:
        line = '%s\r\f' % text
        self.serial.write(line.encode('UTF8'))
    def close(self):
        self.serial.close() 


# Set fan speed
def setFanSpeed(temperature):
    setFanSpee(int(temperature+10000))

def setFanSpee(speed):
    trans = Sender()
    trans.send(str(int(speed)))
    trans.close()
    return()

# Reset fan
def resetFan():
    setFanSpeed(66)
#    GPIO.cleanup() # resets all GPIO ports used by this function

try:
    while True:
        temp = float(getCpuTemperature())
        setFanSpeed(temp)
        #handleFanSpeed(temp, outside_dead_band_higher)
        time.sleep(WAIT_TIME)


except KeyboardInterrupt:
 # trap a CTRL+C keyboard interrupt
    resetFan()
atexit.register(resetFan)
