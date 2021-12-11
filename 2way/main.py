import machine
import utime
import sys
import _thread
from _thread import start_new_thread
import gc
from machine import Pin, Timer, PWM

gc.enable()

fan = PWM(Pin(12))
#fan = PWM(Pin(7))
fan.freq(25000)

board = "pico"
#board = tiny

# For regular RPi-pico
if board == "pico":
    led = PWM(Pin(25))
    led.freq(1000)

# For tiny2040
if board == "tiny":
    red = PWM(Pin(18))
    red.freq(1000)
    green = PWM(Pin(19))
    green.freq(1000)
    green.duty_u16(65535)
    blue = PWM(Pin(20))
    blue.freq(1000)

data = 66
rawdata = 0
counter = 8


def setFanSpeed(pwm):
    fan.duty_u16(int(pwm*65535/100))
    #print("FANDUTY SET!", str(int(pwm)))
    print("setFanSpeed: ", str(pwm))
    gc.collect()
        
def temp2pwm(temperature):
    # Configurable temperature and fan speed
    MIN_TEMP = 35
    MIN_TEMP_DEAD_BAND = 5
    MAX_TEMP = 85
    FAN_LOW = 30
    FAN_HIGH = 100
    FAN_OFF = 0
    FAN_MAX = 100
    while True:
        print("temp2pwm", temperature)
        gc.collect()
        if board == "pico":
            led.duty_u16(30000)
        #outside_dead_band_higher = True
        #global fanPWM
        #global temperature
        #print("Temperature: ", temperature)
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
            #print("FANDUTY = ", str(int(FAN_LOW + ( round(temperature) * step )))) # Uncomment for testing
#            return
    # Set fan speed to MAXIMUM if the temperature is above MAX_TEMP
        elif temperature > MAX_TEMP:
            setFanSpeed(FAN_MAX)
            print("Fan MAX") # Uncomment for testing
#            return
        #print("PWM BOTTOM")
        #utime.sleep(1)
        if board == "pico":
            led.duty_u16(0)
        #print("temp2pwm END!")
        gc.collect()
        #utime.sleep(1)
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
        #sys.stdout.write(str(data) + '\r')
        #print(data)
        gc.collect()

readserialThread = _thread.start_new_thread(readserial, ())

while True:
    if board == "tiny":
        red.duty_u16(0)
    else:
        led.duty_u16(3000)
    
    
    #print(str(counter))
    if counter == 0:
        print("No serial data since 4 iterations, defaulting to PWM=80")
        data = 80
    else:
        counter -= 1
    if data > 9000:
        temp2pwm(data - 10000)
    else:
        #mypwm = (int(data*65535/100))
        fan.duty_u16(int(data*65535/100))
        #setFanSpeed(mypwm)
        #sys.stdout.write(str(int(data*65535/100)))
        print(str(int(data*65535/100)))
    if board == "tiny":
        blue.duty_u16(65535)
    
    utime.sleep(1)
    
    if board == "tiny":
        red.duty_u16(65535)
    else:
        led.duty_u16(100)
    
    utime.sleep(1)
    gc.collect()
