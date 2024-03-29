#!/usr/bin/env python3
import time
import signal
import sys
import os
#import atexit
#import subprocess
import io
import serial
from fansettings import FanSettings

def printHelp():
    print('\n## picofanpwm - tempsend\n\
Command line options:\n\n\
\thelp        -        Show (this) help\n\
\tgpu         -        Send temperature data from GPU (continuously)\n\
\tcpu         -        Send temperature data from CPU (continuously)\n\
\tboth        -        Send temperature data from CPU (continuously)\n\
\tservice     -        Start service using fansettings file\n\
\t10nnn (ex: 10066) -  Send temperature value\n\
\tnn (ex: 66) -        Send fan PWM duty value\n')

fansett = FanSettings()
# Default source, change with command line [gpu|cpu|both|service]
SOURCE = "gpu"

SLEEPTIME = 1
PWM_FREQ = 25     # 25kHz is the default

# Get CPU temp:
def getCpuTemperature(myPath = fansett.getcpupath()):
    #cpupath = fansett.getcpupath()
    cpupath = myPath
    #with open(r"/sys/class/thermal/thermal_zone0/temp") as File:
    try:
        with open(cpupath) as File:
            res = File.readline()
        temp = float(res) / 1000
    except:
        temp = 80
        print("Failed to read CPU-temp")
        pass
    #print(str(int(res)))
    return temp


# Get GPU temp:
def getGpuTemperature(myPath = fansett.getgpupath()):
    try:
        #gpupath = fansett.getgpupath()
        gpupath = myPath
        #res = os.popen('nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader').readline()
        res = os.popen(gpupath).readline()
        temp = float(res)/1
    except:
        temp = 80
        print("Failed to read GPU-temp")
        pass
    return temp

# This is the class used for serial communication with the Pico:
class Sender:
    TERMINATOR = '\r'.encode('UTF8')
    DEVICE = '/dev/ttyACM'

    def __init__(self, device=DEVICE, baud=115200, timeout=1):
        i = 0
        while i <= 20:
            myDevice = device + str(i)
            if os.path.exists(myDevice):
                exDevice = myDevice
                break
            else:
                i+=1
        try:
            self.serial = serial.Serial(exDevice, baud, timeout=timeout, write_timeout=2)
        except:
            print("ERROR! Could not connect with serial port!")
            raise
    
    def old__init__(self, device=DEVICE, baud=115200, timeout=1):
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
    if SOURCE == "service":
        # Make some fans:
        fans = []
        for p in range(1,fansett.howmany()+1):
            fans.append(fansett.getsett(p))
        print(len(fans)+1, "fan objects including dummy '0'")
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
            try:
                setFanSpeed(temp)
            except:
                print("EPIC FAIL!")
                pass
        elif SOURCE == "cpu":
            temp = float(getCpuTemperature())
            try:
                setFanSpeed(temp)
            except:
                print("EPIC FAIL!")
                #pass
        elif SOURCE == "both":
            temp2 = float(getCpuTemperature() + 200000)
            temp1 = float(getGpuTemperature() + 100000)
            try:
                sendFanData(temp1)
            except:
                print("EPIC FAIL temp1")
                pass
            time.sleep(SLEEPTIME)
            try:
                sendFanData(temp2)
            except:
                print("EPIC FAIL temp2")
                pass
        elif SOURCE == "service":
            # Make some fans:
            for p in range(0,fansett.howmany()):
                try:
                    fandata = fans[p]
                    if fandata[5] == 'gpu':
                        #print(fandata, "GPU")
                        #mytemp = float(getGpuTemperature() + ((p+1) * 100000))
                        mytemp = float(getGpuTemperature(fandata[6]) + ((p+1) * 100000))
                        sendFanData(mytemp)
                        time.sleep(SLEEPTIME)
                    elif fandata[5] == 'cpu':
                        #print(fandata, "CPU")
                        #mytemp = float(getCpuTemperature() + ((p+1) * 100000))
                        mytemp = float(getCpuTemperature(fandata[6]) + ((p+1) * 100000))
                        sendFanData(mytemp)
                        time.sleep(SLEEPTIME)
                    elif fandata[5] == 'other':
                        mytemp = float(1 + ((p+1) * 100000))
                        sendFanData(mytemp)
                        time.sleep(SLEEPTIME)
                        #print(fandata, "ELSE")
                    #print(mytemp)
                except:
                    print("FAILED HARD")
                    raise
                #elif fandata[5] == 'case' and casefan > 0:
                #    pass
#        elif (int(SOURCE)) > 9000:
#            sendFanData(int(SOURCE))
#            print(int(SOURCE))
#            break
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
