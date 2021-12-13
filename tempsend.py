#!/usr/bin/env python3
import time
import signal
import sys
import os
#import atexit
#import subprocess
import io
import serial

def printHelp():
    print('\nCommand line options:\n\n  help        -        Show (this) help\n  gpu         -        Send temperature data from GPU (continuously)\n  cpu         -        Send temperature data from CPU (continuously)\n  nn (ex: 66) -        Send fan PWM duty value\n  10nnn (ex: 10066) -  Send temperature value\n')


# Default source, change with command line [gpu|cpu]
SOURCE = "gpu"

SLEEPTIME = 2
PWM_FREQ = 25     # 25kHz is the default

# Get CPU temp from sys/class/thermal:
def getCpuTemperature():
    with open(r"/sys/class/thermal/thermal_zone3/temp") as File:
        res = File.readline()
    temp = float(res) / 1000
    #print(str(int(res)))
    return temp


# Get Nvidia GPU temp from 'mvidia-smi':
def getGpuTemperature():
    res = os.popen('nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader').readline()
    temp = float(res)/1
    return temp

# This is the class used for serial communication with the Pico:
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


# Send temperature data to sendFanData() below.
def setFanSpeed(temperature):
    try:
        sendFanData(int(temperature+10000))
    except:
        raise
# Send temperature or pwm duty to Pico using serial
# Plain pwm data is sent as is.
# Temperature is added to 10000 above, which is cought and handled by main.py in the Pico.
# All speed calculations are done on the Pico.
def sendFanData(speed):
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
    sendFanData(66)


if len(sys.argv) > 1:
    SOURCE = sys.argv[1]
        
try:
    while True:
        if SOURCE == 'help':
            printHelp()
            break
        elif SOURCE == "ping":
            pong = pingPong()
            print(pong)
            break
        elif SOURCE == "gpu":
            temp = float(getGpuTemperature())
        elif SOURCE == "cpu":
            temp = float(getCpuTemperature())
        elif (int(SOURCE)) > 9000:
            sendFanData(int(SOURCE))
            print(int(SOURCE))
            break
        elif (int(SOURCE)) > 0:
            sendFanData(int(SOURCE))
            print(int(SOURCE))
            break
        else:
            temp = float(getGpuTemperature())

        try:
            setFanSpeed(temp)
        except:
            print("EPIC FAIL!")
            pass

        time.sleep(SLEEPTIME)


except KeyboardInterrupt:
 # ctrl + c trap
    resetFan()
