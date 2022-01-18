import machine
#import utime
#import sys
#import _thread
#from _thread import start_new_thread
import gc
from machine import Pin, Timer, PWM

class Fan:
    TEMP_OFF = None
    TEMP_MIN = None
    TEMP_MAX = None
    FAN_lowest = None
    FAN_highest = None
    
    FAN_CHANGE = None
    
    FAN_OFF = 0
    FAN_MAX = 100
    
    def __init__(self, mypin: int, fandata):
        self.PWM = PWM(Pin(mypin))
        self.PWM.freq(25000)
        self.TEMP_OFF = int(fandata[0])
        self.TEMP_MIN = int(fandata[1])
        self.TEMP_MAX = int(fandata[2])
        self.FAN_lowest = int(fandata[3])
        self.FAN_highest = int(fandata[4])
        
    def temp2pwm(self, temperature: int):
        self.FAN_CHANGE = float(self.FAN_highest - self.FAN_lowest) / float(self.TEMP_MAX - self.TEMP_MIN)
        
        if temperature >= self.TEMP_MAX:
            duty = self.FAN_MAX
        elif temperature >= self.TEMP_MIN:
            diff = min(temperature, self.TEMP_MAX) - self.TEMP_MIN
            duty = self.FAN_lowest + diff * self.FAN_CHANGE
        elif temperature <= self.TEMP_OFF:
            duty = self.FAN_OFF
        
        elif temperature < self.TEMP_MIN:
            duty = self.FAN_lowest
        else:
            duty = 66

        gc.collect()
        return(duty)
    def duty2u16(self, duty):
        return int(duty*65535/100)
    def setpwm(self, myduty):
        print("Setting pwm from temp-data:", myduty)
        self.PWM.duty_u16(self.duty2u16(self.temp2pwm(myduty)))
    def setpwmfrompwm(self, myduty):
        print("Setting pwm from pwm-data:", myduty)
        self.PWM.duty_u16(self.duty2u16(myduty))
    def setpwmfromtemp(self, myduty):
        print("Setting pwm from temp-data:", myduty)
        self.PWM.duty_u16(self.duty2u16(self.temp2pwm(myduty)))
