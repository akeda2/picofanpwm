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
    print("setFanSpeed: ", str(int(pwm)))
    gc.collect()
        
def temp2pwm(temperature):
    MIN_TEMP = 35
    MIN_TEMP_DEAD_BAND = 5
    MAX_TEMP = 85
    FAN_LOW = 30
    FAN_HIGH = 100
    FAN_OFF = 0
    FAN_MAX = 100
    while True:
        gc.collect()
        if board == "pico":
            led.duty_u16(30000)
        #outside_dead_band_higher = True
        # Turn off the fan if lower than lower dead band 
        if temperature < MIN_TEMP_DEAD_BAND + MIN_TEMP:
            outside_dead_band_higher = False
        else:
            outside_dead_band_higher = True
        
        if outside_dead_band_higher == False:
            duty = FAN_OFF
    # Run fan at calculated speed if being in or above dead zone not having passed lower dead band    
        elif outside_dead_band_higher == True and temperature < MAX_TEMP:
            step = float(FAN_HIGH - FAN_LOW)/float(MAX_TEMP - MIN_TEMP)  
            temperature -= MIN_TEMP
            duty = int(FAN_LOW + ( round(temperature) * step ))
    # Set fan speed to MAXIMUM if the temperature is above MAX_TEMP
        elif temperature > MAX_TEMP:
            duty = FAN_MAX
        return(duty)
        if board == "pico":
            led.duty_u16(0)
        gc.collect()
        break

def readserial():
    global rawdata, data, counter
    while True:
        rawdata = sys.stdin.readline()
        
        if counter < 4:
            counter = 4
        if board == "tiny":
            blue.duty_u16(0)
        else:
            led.duty_u16(30000)
        
        data = int(rawdata)
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
        led.duty_u16(3000)
    
    if counter == 0:
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
        led.duty_u16(100)
    
    utime.sleep(1)
    gc.collect()
