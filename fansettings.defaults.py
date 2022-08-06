class FanSettings:
    
    # Which board are we using? (the LED:s will be different):
    board = "pico"
    #board = "tiny"
    def whichboard(self):
        return self.board
    
    # What path to use for CPU-temp?:
    #cpupath = '/sys/class/thermal/thermal_zone3/temp'
    cpu0 = '/sys/class/thermal/thermal_zone0/temp'
    #cpu1 = '/sys/class/thermal/thermal_zone1/temp'
    cpupath = cpu0
    def getcpupath(self):
        return self.cpupath
    
    # What path/string to use for GPU-temp?:
    gpu0 = 'nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader'
    #gpu1 = ...
    gpupath = gpu0
    def getgpupath(self):
        return self.gpupath
    
    #The first is a dummy (for dev/debugging):
    fansett0 = [15, 30, 55, 10, 100, "dummy", 'dummy0']
    
    # SYNTAX: [fan off-temp, min temp for scaling, max-temp, min-pwm, max-pwm, "type", string/path to temp-value]
    # GPU-fan:
    fansett1 = [15, 30, 50, 10, 100, "gpu", gpu0]
    # CPU-fan:
    fansett2 = [15, 30, 75, 30, 100, "cpu", cpu0]
    # Case-fan, will get PWM-value from the highest of the above:
    fansett3 = [15, 30, 75, 30, 100, "case", 'case0']
    fansetts = [fansett0, fansett1, fansett2, fansett3]
    
    def getsett(self, myfan: int):
        return self.fansetts[myfan]
    def howmany(self):
        return len(self.fansetts) - 1
    # LEGACY, If using a casefan as fansett3 and want it to recieve the current highest PWM-value from the other fans (to disable, set to '0'):
    def casefan(self):
        return 3