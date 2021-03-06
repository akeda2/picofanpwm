# Sending PWM from temperature input on USB serial
# David Åkesson 2021

# Blinking syntax: 0 = 20C, "_ ." = 19 (one under 0), "._ .." = 8 (10 under 0, 2 under 0)

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

degree = chr(176)
gc.enable()

sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)

#FAN
fan = PWM(Pin(15))
#fan = PWM(Pin(7))
fan.freq(25000)
fanPWM = 66

#LED
led = PWM(Pin(25))
led.freq(1000)
temperature = 21
    
def duty2u16(duty):
    return int(duty*65535/100)

def setFanSpeed(pwm):
    fan.duty_u16(duty2u16(pwm))
    print("setFanSpeed: ", str(int(pwm)), '%')
    gc.collect()

def temp2pwm(temperature):
    print("Temperature: ", str(temperature)+degree+"C")
    TEMP_OFF = 22
    TEMP_MIN = 30
    TEMP_MAX = 40
    FAN_lowest = 30
    FAN_highest = 100
    FAN_OFF = 0
    FAN_MAX = 100
    FAN_CHANGE = float(FAN_highest - FAN_lowest) / float(TEMP_MAX - TEMP_MIN)
    
    if temperature >= TEMP_MIN:
        diff = min(temperature, TEMP_MAX) - TEMP_MIN
        duty = FAN_lowest + diff * FAN_CHANGE
        led.duty_u16(30000)
    elif temperature <= TEMP_OFF:
        duty = FAN_OFF
        led.duty_u16(0)
    elif temperature >= TEMP_MAX:
        duty = FAN_MAX
        led.duty_u16(65535)
    elif temperature < TEMP_MIN:
        duty = FAN_lowest
        led.duty_u16(1000)
    else:
        duty = 66

    gc.collect()
    return(duty)

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
    setFanSpeed(temp2pwm(round(temperature)))
    gc.collect()
    #handleFanSpeed()
    #memprint()