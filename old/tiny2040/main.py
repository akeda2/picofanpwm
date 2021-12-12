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

#led = PWM(Pin(25))
#led.freq(1000)

red = PWM(Pin(18))
red.freq(1000)
green = PWM(Pin(19))
green.freq(1000)
green.duty_u16(65535)
blue = PWM(Pin(20))
blue.freq(1000)

data = 66
rawdata = 0

def readserial():
    global rawdata, data
    while True:
        rawdata = sys.stdin.readline()
        #led.duty_u16(30000)
        blue.duty_u16(0)
        data = int(rawdata)
        #sys.stdout.write(str(data))
        #print(data)
        gc.collect()

readserialThread = _thread.start_new_thread(readserial, ())

while True:
    #led.duty_u16(3000)
    red.duty_u16(0)

    fan.duty_u16(int(data*65535/100))
    blue.duty_u16(65535)
    utime.sleep(1)
    #led.duty_u16(100)
    red.duty_u16(65535)
    utime.sleep(1)
    gc.collect()
