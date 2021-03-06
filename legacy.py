import machine
import utime
import sys
import _thread
#from fan import Fan
from _thread import start_new_thread
import gc
from machine import Pin, Timer, PWM

class SFan:
    TEMP_OFF = None
    TEMP_MIN = None
    TEMP_MAX = None
    FAN_lowest = None
    FAN_highest = None
    
    FAN_CHANGE = None
    
    FAN_OFF = 0
    FAN_MAX = 100
    #myfan = PWM(pin(15))
    
    def __init__(self, mypin: int, fandata):
        self.PWM = PWM(Pin(mypin))
        #print("object created")
        self.TEMP_OFF = int(fandata[0])
        self.TEMP_MIN = int(fandata[1])
        self.TEMP_MAX = int(fandata[2])
        self.FAN_lowest = int(fandata[3])
        self.FAN_highest = int(fandata[4])
        
    def temp22pwm(self, temperature: int):
        self.FAN_CHANGE = float(self.FAN_highest - self.FAN_lowest) / float(self.TEMP_MAX - self.TEMP_MIN)
    
        if temperature >= self.TEMP_MIN:
            diff = min(temperature, self.TEMP_MAX) - self.TEMP_MIN
            duty = self.FAN_lowest + diff * self.FAN_CHANGE
        elif temperature <= self.TEMP_OFF:
            duty = self.FAN_OFF
        elif temperature >= self.TEMP_MAX:
            duty = self.FAN_MAX
        elif temperature < self.TEMP_MIN:
            duty = self.FAN_lowest
        else:
            duty = 66

        gc.collect()
        return(duty)
    def duty22u16(duty):
        return int(duty*65535/100)
    def setpwm(self, myduty):
        print("setting pwm from data:", myduty)
        self.PWM.duty_u16(self.duty22u16(self.temp22pwm(myduty)))

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
        ##print(str(data)+'\r')
        ##if data > 90000:
        ##    gc.collect()
          #  #print(str(data))
        ##elif data > 19000:
        # #   print(str(data)+'\r')
          #  #sys.stdout.write("GLENN")
        #  #  data = 66 #str(data) + '\r')
        gc.collect()

#utime.sleep(1)
#readserialThread = _thread.start_new_thread(readserial, ())
#utime.sleep(5)