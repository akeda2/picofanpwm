#Blinking thermometer
#David Åkesson 2021

#Blinking syntax: 0 = 20C, "_ ." = 19 (one under 0), "._ .." = 8 (10 under 0, 2 under 0)

import machine
import utime
import _thread
from _thread import start_new_thread
import gc
import sys
from machine import Pin, Timer, PWM

# Configuration
#FAN_PIN = 14            # BCM pin used to drive PWM fan
WAIT_TIME = 2           # [s] Time to wait between each refresh
PWM_FREQ = 25           # [kHz] 25kHz for Noctua PWM control

gc.enable()

sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)

#FAN
fan = PWM(Pin(12))
#fan = PWM(Pin(7))
fan.freq(25000)
fanPWM = 66

#LED
pwm = PWM(Pin(25))
pwm.freq(1000)
temperature = 21

def setFanSpeed(pwm):
    fan.duty_u16(int(pwm))
    print("FANDUTY SET!", str(int(pwm)))
    gc.collect()
    utime.sleep(2)
# Handle fan speed
def handleFanSpeed():
    # Configurable temperature and fan speed
    MIN_TEMP = 18
    MIN_TEMP_DEAD_BAND = 5
    MAX_TEMP = 40
    FAN_LOW = 30
    FAN_HIGH = 100
    FAN_OFF = 0
    FAN_MAX = 100
    while True:
        print("ENTERING PWM")
        gc.collect()
        pwm.duty_u16(30000)
        #outside_dead_band_higher = True
        global fanPWM
        global temperature
        print("PWM ", temperature)
        # Turn off the fan if lower than lower dead band 
        if temperature < MIN_TEMP_DEAD_BAND + MIN_TEMP:
            outside_dead_band_higher = False
        else:
            outside_dead_band_higher = True
        
        if outside_dead_band_higher == False:
            setFanSpeed(FAN_OFF)
            print("Fan OFF") # Uncomment for testing
#            return
    # Run fan at calculated speed if being in or above dead zone not having passed lower dead band    
        elif outside_dead_band_higher == True and temperature < MAX_TEMP:
            step = float(FAN_HIGH - FAN_LOW)/float(MAX_TEMP - MIN_TEMP)  
            temperature -= MIN_TEMP
            setFanSpeed(int(FAN_LOW + ( round(temperature) * step )))
            print("FANDUTY = ", str(int(FAN_LOW + ( round(temperature) * step )))) # Uncomment for testing
#            return
    # Set fan speed to MAXIMUM if the temperature is above MAX_TEMP
        elif temperature > MAX_TEMP:
            setFanSpeed(FAN_MAX)
            print("Fan MAX") # Uncomment for testing
#            return
        print("PWM BOTTOM")
        #utime.sleep(1)
        pwm.duty_u16(0)
        print("PWM END!")
        gc.collect()
        #utime.sleep(1)
        break

def round_to(n, precision):
    correction = 0.5 if n >= 0 else -0.5
    return int( n/precision+correction ) * precision
def round_to_05(n):
    return round_to(n, 0.5)

def templist(iter):
    list = []
    list.append(sensor_temp.read_u16() * conversion_factor)
    for i in range(0,iter):
        
        ratio = 0.025
        list.append((list[i-1])*(1 - ratio) + ((sensor_temp.read_u16() * conversion_factor) * (ratio)))
        #gc.collect()
        utime.sleep(0.001)
    gc.collect()
    return list
def multilist(times,iter):
    gc.collect()
    global kickstart
    global threadfinish
    print("kickstart =", kickstart)
    #print("threadfinish =", threadfinish)
    pal = []
    plist = templist(iter)
    pal.append(sum(plist) / len(plist))
    plist = []
    q = 0
    q += 1
    gc.collect()
    r = 0
    if kickstart == 1:
        p = 0
        while p < times:
            plist = templist(iter)
            pal.append(sum(plist) / len(plist))
            print("Kickstarting", p, times)
            p += 1
            gc.collect()
    else:
        r = 0
        while r < 3:
            plist = templist(1000)
            pal.append(sum(plist) / len(plist))
            print("\nLarge burst ",r)
            r += 1
            gc.collect()
    plist = []
    #memprint()
    gc.collect()
    return pal

def memprint():
    print("Mem alloc: ",gc.mem_alloc(),"Mem free: ",gc.mem_free())

global threadfinish
threadfinish = 1

global kickstart
kickstart = 1

#_thread.start_new_thread(handleFanSpeed, ())

while True:
    print("\n\n(Re)starting main loop")
    
    pal = multilist(6,500)
    print(pal)
    reading = sum(pal) / len(pal)
    pal = []
    print(reading)
    #temperature = round_to_05(27 - (reading - 0.706)/0.001721)
    temperature = 27 - (reading - 0.706)/0.001721
    print("temperature = ", temperature)
    global kickstart
    kickstart = 0
    gc.collect()
    handleFanSpeed()
    #memprint()