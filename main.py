import machine
import utime
import sys
import _thread
from _thread import start_new_thread
import gc
from machine import Pin, Timer, PWM

gc.enable()

#board = "pico"
board = "tiny"

# For regular RPi-pico
if board == "pico":
    fan = PWM(Pin(12))
    
    led = PWM(Pin(25))
    led.freq(1000)

# For tiny2040
if board == "tiny":
    fan = PWM(Pin(7))
    
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

def duty2u16(duty):
    return int(duty*65535/100)

def setFanSpeed(pwm):
    fan.duty_u16(duty2u16(pwm))
    print("setFanSpeed: ", str(int(pwm)), '%')
    gc.collect()

def temp2pwm(temperature):
    print("Temperature: ", str(temperature), "C")
    TEMP_OFF = 30
    TEMP_MIN = 35
    TEMP_MAX = 80
    FAN_lowest = 30
    FAN_highest = 100
    FAN_OFF = 0
    FAN_MAX = 100
    FAN_CHANGE = float(FAN_highest - FAN_lowest) / float(TEMP_MAX - TEMP_MIN)
    
    if temperature >= TEMP_MIN:
        diff = min(temperature, TEMP_MAX) - TEMP_MIN
        duty = FAN_lowest + diff * FAN_CHANGE
    elif temperature <= TEMP_OFF:
        duty = FAN_OFF
    elif temperature >= TEMP_MAX:
        duty = FAN_MAX
    elif temperature < TEMP_MIN:
        duty = FAN_lowest
    else:
        duty = 66

    gc.collect()
    return(duty)

def readserial():
    global rawdata, data, counter
    while True:
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
        #print(str(data)+'\r')
        if data > 19000:
            print(str(data)+'\r')
            #sys.stdout.write("GLENN")
            data = 66 #str(data) + '\r')
        gc.collect()

readserialThread = _thread.start_new_thread(readserial, ())

while True:
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
    if data > 9000:
        setFanSpeed(temp2pwm(data - 10000))
    else:
        # Or just pwm duty?
        setFanSpeed(data)
    
    if board == "tiny":
        blue.duty_u16(65535)
    
    utime.sleep(1)
    
    if board == "tiny":
        red.duty_u16(65535)
    else:
        led.duty_u16(600)
    
    utime.sleep(1)
    gc.collect()
