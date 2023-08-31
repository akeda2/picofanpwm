import time
import machine
#import utime
#import sys
#import _thread
#from _thread import start_new_thread
import gc
from machine import Pin, Timer, PWM

class Fan:
    # Constants for the PID controller
    P_CONSTANT = 0.5
    I_CONSTANT = 0.1
    D_CONSTANT = 0.2
    TARGET_TEMPERATURE = 69.0  # Target temperature in degrees Celsius
    MIN_FAN_SPEED = 20  # Minimum fan speed (%)
    MAX_FAN_SPEED = 80  # Maximum fan speed (%)

    # Initial values
    previous_error = 0
    integral = 0
    def __init__(self, mypin: int, fandata):
        self.PWM = PWM(Pin(mypin))
        self.PWM.freq(25000)
        self.TEMP_OFF = int(fandata[0])
        self.TEMP_MIN = int(fandata[1])
        self.TEMP_MAX = int(fandata[2])
        self.FAN_lowest = int(fandata[3])
        self.FAN_highest = int(fandata[4])
        self.FAN_type = fandata[5]

        self.MIN_FAN_SPEED = self.FAN_lowest
        self.MAX_FAN_SPEED = self.FAN_highest
        self.TARGET_TEMPERATURE = self.TEMP_MAX

    def temp2pwm(self, temperature: int):
        # Simulate reading the current temperature (replace with actual reading)
        current_temperature = temperature

        # Calculate error
        error = self.TARGET_TEMPERATURE - current_temperature

        # Proportional term
        p_term = self.P_CONSTANT * error

        # Integral term
        integral += error
        i_term = self.I_CONSTANT * integral

        # Derivative term
        derivative = error - previous_error
        d_term = D_CONSTANT * derivative

        # Calculate control output
        control_output = p_term + i_term + d_term

        # Apply saturation limits
        if control_output > self.MAX_FAN_SPEED:
            control_output = self.MAX_FAN_SPEED
        elif control_output < self.MIN_FAN_SPEED:
            control_output = self.MIN_FAN_SPEED

        # Set fan speed or PWM signal based on control output (replace with actual fan control)
        #set_fan_speed(control_output)

        # Store current error for the next iteration
        previous_error = error
        return control_output

    def duty2u16(self, duty):
        return int(duty*65535/100)
    def setpwm(self, myduty):
        print("Setting pwm from temp-data:", myduty)
        self.PWM.duty_u16(self.duty2u16(self.temp2pwm(myduty)))
    def setpwmfrompwm(self, myduty):
        print("Setting pwm from pwm-data:", myduty)
        self.current_PWM = myduty
        self.PWM.duty_u16(self.duty2u16(myduty))
    def setpwmfromtemp(self, myduty):
        print("Setting pwm from temp-data:", myduty)
        self.PWM.duty_u16(self.duty2u16(self.temp2pwm(myduty)))
    
    def getPWM(self):
        return self.current_PWM
    def getType(self):
        return self.FAN_type