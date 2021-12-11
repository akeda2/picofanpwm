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
    res = os.popen('nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader').readline()
    temp = float(res)/1
    print("temp is {0}".format(temp)) # Uncomment for testing
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

        self.serial = serial.Serial(exDevice, baud, timeout=timeout)
    def receive(self) -> str:
        line = self.serial.read_until(self.TERMINATOR)
        return line.decode('UTF8').strip()
    def send(self, text: str) -> bool:
        line = '%s\r\f' % text
        self.serial.write(line.encode('UTF8'))
    def close(self):
        self.serial.close() 

# Get data from device
def getData():
    get = Sender()
    received = get.receive()
    get.close()
    print(str(received))

# Set fan speed
def setFanSpeed(temperature):
    setFanSpee(int(temperature+10000))

def setFanSpee(speed):
#    fan.start(speed)
    #a = 'echo "' + str(int(speed)) + '" > /dev/ttyACM0'
    #a = '%s %s%s%s %s %s %s%s%s %s %s' % ('[ -c /dev/ttyACM0 ] && echo', '"', str(int(speed)), '"', '>', '/dev/ttyACM0 ; [ -c /dev/ttyACM1 ] && echo', '"', str(int(speed)), '"', '>', '/dev/ttyACM1')
    #os.popen(a)
#'echo "speed" > /dev/ttyACM0')
#    print(a)
    print(str(speed))
    trans = Sender()
    trans.send(str(int(speed)))
    trans.close()

#    proc = subprocess.Popen(a, shell=True, stdin=subprocess.PIPE, bufsize=-1)
#    print(proc.communicate())
    return()

# Handle fan speed
def handleFanSpeed(temperature, outside_dead_band_higher):
    # Turn off the fan if lower than lower dead band 
    if outside_dead_band_higher == False:
        setFanSpeed(FAN_OFF)
#        print("Fan OFF") # Uncomment for testing
        return
    # Run fan at calculated speed if being in or above dead zone not having passed lower dead band    
    elif outside_dead_band_higher == True and temperature < MAX_TEMP:
        step = float(FAN_HIGH - FAN_LOW)/float(MAX_TEMP - MIN_TEMP)  
        temperature -= MIN_TEMP
        setFanSpeed(FAN_LOW + ( round(temperature) * step ))
#        print(FAN_LOW + ( round(temperature) * step )) # Uncomment for testing
        return
    # Set fan speed to MAXIMUM if the temperature is above MAX_TEMP
    elif temperature > MAX_TEMP:
        setFanSpeed(FAN_MAX)
#        print("Fan MAX") # Uncomment for testing
        return
    else:
        return

# Handle dead zone bool
def handleDeadZone(temperature):
    if temperature > (MIN_TEMP + MIN_TEMP_DEAD_BAND/2):
        return True
    elif temperature < (MIN_TEMP - MIN_TEMP_DEAD_BAND/2):
        return False

# Reset fan to 100% by cleaning GPIO ports
def resetFan():
    setFanSpeed(66)
#    GPIO.cleanup() # resets all GPIO ports used by this function

try:
    getData()
    #time.sleep(WAIT_TIME)


except KeyboardInterrupt:
 # trap a CTRL+C keyboard interrupt
#    try:
    resetFan()
#        trans.close()
    #except KeyboardInterrupt:
        #resetFan()

    #resetFan()

atexit.register(resetFan)
