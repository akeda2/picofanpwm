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

# Default value, change with command line [gpu|cpu]
SOURCE = "gpu"

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
    with open(r"/sys/class/thermal/thermal_zone3/temp") as File:
        res = File.readline()
    temp = float(res) / 1000
    print(str(int(res)))
#    temp = float(res)/1
#    print("temp is {0}".format(temp)) # Uncomment for testing
    return temp


# Get GPU's temperature
def getGpuTemperature():
    #res = 60
    #res = os.popen('cat /sys/class/thermal/thermal_zone0/temp').readline()
    res = os.popen('nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader').readline()
    temp = float(res)/1
#    print("temp is {0}".format(temp)) # Uncomment for testing
    return temp

class Sender:
    TERMINATOR = '\r'.encode('UTF8')
    DEVICE = '/dev/ttyACM'

    def __init__(self, device=DEVICE, baud=115200, timeout=1):
        myDevice = device + '0'
        if os.path.exists(myDevice):
            exDevice = myDevice
        else:
            exDevice = device + '1'

        self.serial = serial.Serial(exDevice, baud, timeout=timeout, write_timeout=2)
    def receive(self) -> str:
        line = self.serial.read_until(self.TERMINATOR)
        return line.decode('UTF8').strip()
    def send(self, text: str) -> bool:
        line = '%s\r\f' % text
        try:
            self.serial.write(line.encode('UTF8'))
        except:
            print("send FAIL!")
            raise
    def close(self):
        self.serial.close() 


# Set fan speed
def setFanSpeed(temperature):
    try:
        setFanSpee(int(temperature+10000))
    except:
        raise
def setFanSpee(speed):
    try:
        trans = Sender()
    except:
        raise
    trans.send(str(int(speed)))
    trans.close()
    return()

# Get data from device
def pingPong():
    try:
        ping = Sender()
    except:
        raise
    ping.send(str(20000))
    pong = ping.receive()
    ping.close()
    return(str(pong))

# Reset fan
def resetFan():
    setFanSpeed(66)


if len(sys.argv) > 1:
    SOURCE = sys.argv[1]
        
try:
    while True:
        if SOURCE == "ping":
            pong = pingPong()
            print(pong)
            break
        elif SOURCE == "gpu":
            temp = float(getGpuTemperature())
        elif SOURCE == "cpu":
            temp = float(getCpuTemperature())
        elif (int(SOURCE)) > 9000:
            setFanSpee(int(SOURCE))
            print(int(SOURCE))
            break
        elif (int(SOURCE)) > 0:
            setFanSpee(int(SOURCE))
            print(int(SOURCE))
            break
        else:
            temp = float(getGpuTemperature())

        try:
            setFanSpeed(temp)
        except:
            print("EPIC FAIL!")
            pass
        #handleFanSpeed(temp, outside_dead_band_higher)
        time.sleep(WAIT_TIME)


except KeyboardInterrupt:
 # trap a CTRL+C keyboard interrupt
    resetFan()
#atexit.register(resetFan)
