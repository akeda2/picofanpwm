import machine
import utime
import sys
import _thread
from fan import Fan
from _thread import start_new_thread
import gc
from machine import Pin, Timer, PWM
#import legacy
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
# CPU-fan:

# For regular RPi-pico
if board == "pico":
    # Which pin to begin with (the first '0' is the dummy):
    pinbegin = 17
    
    led = PWM(Pin(25))
    led.freq(1000)

# For tiny2040
if board == "tiny":
    # Which pin to begin with (the first '0' is the dummy):
    pinbegin = 7
    
    red = PWM(Pin(18))
    red.freq(1000)
    green = PWM(Pin(19))
    green.freq(1000)
    green.duty_u16(65535)
    blue = PWM(Pin(20))
    blue.freq(1000)

# Make some fans:
i = 0
fans = []
for p in range(fanconf.howmany()+1):
    #print(str(p))
    fans.append(Fan(pinbegin-i, fanconf.getsett(p)))
    i+=1
print(len(fans), "fan objects including dummy '0'")

data = 66
rawdata = 0
counter = 64

def readser():
    global rawdata, counter
    while True:
        arawdata = sys.stdin.readline()
        rawdata = arawdata
        
        if counter < 64:
            counter = 64
        
        if board == "tiny":
            blue.duty_u16(0)
            green.duty_u16(65535)
        else:
            led.duty_u16(65535)

        gc.collect()

readserialThread = _thread.start_new_thread(readser, ())

last = 66
manual = False

while True:
    utime.sleep(0.2)
    # Try to read data from serial thread global var
    try:
        data = int(rawdata)
    except:
        print("Currupt serial input?", data)
        data = 65
        pass

    changed = last != data
    if changed:
        #print("Value changed")
        #print("Rawdata:", str(int(rawdata)),"Data:", str(int(data)))
        last = data
        manual = False
    elif data == 0:
        data = 66
    else:
        #print("No change...")
        data = last
        #manual = False

    if board == "tiny":
        red.duty_u16(0)
    else:
        led.duty_u16(6000)
        
    # For safety - if no data has come in since n iterations - set all fans to 80% pwm
    if counter <= 0 and not bool(manual):
        if board == "tiny":
            green.duty_u16(0)
        print("No serial data since 64 iterations. Defaulting to 80% PWM on all fans.")
        data = 80
    else:
        if counter > 0:
            counter -= 1
        else:
            counter = 0
        #print(counter)
        
    # Did we just receive temperature?
    # And more than one fan?
    if data > 99000 and changed:
        print(str(data))
        try:
            d = str(data)
            e = int(d[0])
            print("Fan", str(e))
            fans[e].setpwmfromtemp(data - (e * 100000))
            
        except:
            print("Fail", str(data))
        data = None
        
    elif data > 9000 and changed:
        #for u in fans:
        #    u.setpwmfromtemp(data - 10000)
        #print("FAIL!")
        try:
            fans[int(str(data)[0])].setpwmfromtemp(data - (int(str(data)[0]) * 10000))
        except:
            print("Fail", str(data))
        data = None
    elif data > 1000 and data < 9000 and changed:
        try:
            fans[int(str(data)[0])].setpwmfrompwm(data - (int(str(data)[0]) * 1000))
        except:
            print("Fail", str(data))
        data = None
        manual = True
    elif data <= 100 and data > 0:
        # Or just pwm duty?
        #manual = True
        #print("Manual mode is ON")
        for u in fans:
            u.setpwmfrompwm(data)
        data = None
    if board == "tiny":
        blue.duty_u16(65535)
        red.duty_u16(65535)
    else:
        led.duty_u16(600)
    gc.collect()
    