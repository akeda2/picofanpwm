import machine
import utime
import sys
import _thread
from fan import Fan
from _thread import start_new_thread
import gc
from machine import Pin, Timer, PWM
import legacy
from fansettings import FanSettings

gc.enable()

# Set clock to 250MHz since we're not running on batteries:
machine.freq(250000000)
print(str(int(machine.freq()/1000000)), "MHz clock")

fanconf = FanSettings()
board = fanconf.whichboard()
print("Running on",board)
howmany = fanconf.howmany()
print(howmany, "fans")

# GPU-fan:
#fan1sett = [15, 30, 55, 30, 100]
fan1sett = fanconf.getsett(1)
print(str(fan1sett))

# CPU-fan:
#fan2sett = [15, 30, 65, 30, 100]
fan2sett = fanconf.getsett(2)
print(str(fan2sett))

# For regular RPi-pico
if board == "pico":
    fan = PWM(Pin(12))
    fan1 = Fan(16, fan1sett)
    fan2 = Fan(15, fan2sett)
    
    led = PWM(Pin(25))
    led.freq(1000)

# For tiny2040
if board == "tiny":
    fan = PWM(Pin(7))
    fan1 = Fan(6, fan1sett)
    fan2 = Fan(5, fan2sett)
    
    red = PWM(Pin(18))
    red.freq(1000)
    green = PWM(Pin(19))
    green.freq(1000)
    green.duty_u16(65535)
    blue = PWM(Pin(20))
    blue.freq(1000)

fan.freq(25000)
data = 66
rawdata = 0
counter = 8

def readser():
    global rawdata, data, counter
    rawdata = sys.stdin.readline()
        
    if counter < 4:
        counter = 4
        
    if board == "tiny":
        blue.duty_u16(0)
        green.duty_u16(65535)
    else:
        led.duty_u16(65535)
        
    try:
        data = int(rawdata)
    except:
        print(str(rawdata))
        pass
    gc.collect()

while True:
    readser()
    if board == "tiny":
        red.duty_u16(0)
    else:
        led.duty_u16(6000)
    
    if counter == 0:
        if board == "tiny":
            green.duty_u16(0)
        print("No serial data since 4 iterations, defaulting to PWM=80")
        data = 80
    else:
        counter -= 1
    # Did we just receive temperature?
    # And more than one fan?
    try:
        data = int(data)
    except:
        print("Currupt serial input?", data)
        data = 1000065
        pass
    if data > 199000:
        print(str(data))
        try:
            fan2.setpwm(data - 200000)
        except:
            print("Fail 2")
        data = ''
    elif data > 99000:
        print(str(data))
        try:
            fan1.setpwm(data - 100000)
        except:
            print("Fail 1")
            pass
        data = ''
    elif data > 9000:
        setFanSpeed(temp2pwm(data - 10000))
    else:# data > 0:
        # Or just pwm duty?
        setFanSpeed(data)
    
    if board == "tiny":
        blue.duty_u16(65535)
        
    if board == "tiny":
        red.duty_u16(65535)
    else:
        led.duty_u16(600)
    gc.collect()
