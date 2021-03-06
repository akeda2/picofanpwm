class FanSettings:
    
    # Which board are we using?:
    board = "pico"
    #board = "tiny"
    
    # What path to use for CPU-temp?:
    cpupath = '/sys/class/thermal/thermal_zone3/temp'
    #cpupath = '/sys/class/thermal/thermal_zone0/temp'
    def getcpupath(self):
        return self.cpupath
    
    def whichboard(self):
        return self.board
    
    
    #The first is a default dummy (to make easier reading):
    fansett0 = [15, 30, 60, 30, 100]
    # GPU-fan:
    fansett1 = [15, 30, 55, 30, 100]
    # CPU-fan:
    fansett2 = [15, 30, 65, 30, 100]
    fansetts = [fansett0, fansett1, fansett2]
    
    def getsett(self, myfan: int):
        return self.fansetts[myfan]
    def howmany(self):
        return len(self.fansetts) - 1
    