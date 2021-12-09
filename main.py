import machine
import utime
import sys
import _thread
from _thread import start_new_thread
import gc
from machine import Pin, Timer, PWM

gc.enable()

fan = PWM(Pin(12))
fan.freq(25000)

led = PWM(Pin(25))
led.freq(1000)

data = 60
#data = 40000
rawdata = 0

#rawdata = sys.stdin.readline()
#data = int(rawdata) #.decode("utf-8")

def readserial():
    global rawdata, data
    while True:
        rawdata = sys.stdin.readline()
        data = int(rawdata)
        #utime.sleep(2)
        
#def percent2data(myData):
#    print("glenn")
    #return int(65535*myData//1000)
#    return dataout

readserialThread = _thread.start_new_thread(readserial, ())

while True:
#    data = percent2data(data)
    led.duty_u16(20000)
#    fan.duty_u16(40000)
    fan.duty_u16(int(data*65535/100))
    utime.sleep(5)
    led.duty_u16(0)
    utime.sleep(1)
    gc.collect()
    
