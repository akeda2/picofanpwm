import machine
import utime
import sys
import _thread
from _thread import start_new_thread
import gc
from machine import Pin, Timer, PWM

gc.enable()

#fan = PWM(Pin(12))
fan = PWM(Pin(7))
fan.freq(25000)

# For regular RPi-pico
led = PWM(Pin(25))
led.freq(1000)

# For tiny2040
#red = PWM(Pin(18))
#red.freq(1000)
#green = PWM(Pin(19))
#green.freq(1000)
#green.duty_u16(65535)
#blue = PWM(Pin(20))
#blue.freq(1000)

data = 66
rawdata = 0

def setFanSpeed(pwm):
    fan.duty_u16(int(pwm))
    #print("FANDUTY SET!", str(int(pwm)))
    gc.collect()
        
def temp2pwm(temperature):
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
        #global fanPWM
        #global temperature
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

def readserial():
    global rawdata, data
    while True:
        rawdata = sys.stdin.readline()
        
        led.duty_u16(30000)
        #blue.duty_u16(0)
        
        data = int(rawdata)
        #sys.stdout.write(str(data))
        #print(data)
        gc.collect()

readserialThread = _thread.start_new_thread(readserial, ())

while True:
    led.duty_u16(3000)
    
    #red.duty_u16(0)
    if data > 10000:
        setFanSpeed(temp2pwm(data - 10000))
    else:
        fan.duty_u16(int(data*65535/100))
    
    #blue.duty_u16(65535)
    
    utime.sleep(1)
    
    led.duty_u16(100)
    #red.duty_u16(65535)
    utime.sleep(1)
    gc.collect()
