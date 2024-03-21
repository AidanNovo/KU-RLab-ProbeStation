from serial import Serial
from time import sleep

class CAENHV:
    """Class to control the HV Power supply DT5533EM"""

    def __init__(self, port='/dev/ttyACM0', channel=2, imax=10, vmax=500 , vsec=50):
        self.port_ = port
        self.channel_ = channel
        self.imax_ = imax
        self.vmax_ = vmax
        self.vsec = vsec
        self.serial_ = Serial(port)
        self.initialize()

    def __del__(self):
        self.serial_.close()
        del self.serial_

    def initialize(self):
        self.serial_.write(b'$CMD:SET,PAR:BDCLR\n')
        self.serial_.readline()
        self.serial_.write(b'$CMD:SET,CH:%d,PAR:ISET,VAL:%2f\n'%(self.channel_,self.imax_))
        self.serial_.readline()
        self.serial_.write(b'$CMD:SET,CH:%d,PAR:VSET,VAL:%2f\n'%(self.channel_,0))
        self.serial_.readline()
        self.serial_.write(b'$CMD:SET,CH:%d,PAR:RUP,VAL:%d\n'%(self.channel_,self.vsec))
        self.serial_.readline()
        self.serial_.write(b'$CMD:SET,CH:%d,PAR:RDW,VAL:%d\n'%(self.channel_,self.vsec))
        self.serial_.readline()
        self.serial_.write(b'$CMD:SET,CH:%d,PAR:TRIP,VAL:%1f\n'%(self.channel_,2))
        self.serial_.readline()

    def on(self):
        self.serial_.write(b'$CMD:SET,CH:%d,PAR:ON\n'%self.channel_)
        return self.serial_.readline()

    def off(self):
        self.serial_.write(b'$CMD:SET,CH:%d,PAR:OFF\n'%self.channel_)
        return self.serial_.readline()

    def rampDown(self):
        print('Ramping down....')
        self.setVolt(0)
        v = 100
        while v>10:
            v = self.readVolt()
            print('Ramping down... %d V'%v)
            sleep(1)
        self.serial_.write(b'$CMD:SET,CH:%d,PAR:OFF\n'%self.channel_)
        return self.serial_.readline()

    def setChannel(self, channel):
        self.channel_ = channel
        self.serial_.write(b'$CMD:SET,CH:%d,PAR:ISET,VAL:%2f\n'%(channel,self.imax_ ))
        self.serial_.write(b'$CMD:SET,CH:%d,PAR:VSET,VAL:%2f\n'%(self.channel_,0))
        self.serial_.readline()
        return self.serial_.readline()

    def setMaxCurrent(self, imax):
        self.serial_.write(b'$CMD:SET,CH:%d,PAR:ISET,VAL:%2f\n'%(self.channel_,imax))
        return self.serial_.readline()

    def setVolt(self, volt):
        if volt<self.vmax_:
            self.serial_.write(b'$CMD:SET,CH:%d,PAR:VSET,VAL:%2f\n'%(self.channel_,volt))
            return self.serial_.readline()
        else:
            return "%2f > than vmax (%2f)"%(volt,self_vmax_)

    def readCurrent(self):
        self.serial_.write(b'$CMD:MON,CH:%d,PAR:IMON\n'%self.channel_)
        str = self.serial_.readline()
        str1 = str.split(b';')
        str2 = str1[0].split(b':')
        i = float(str2[-1])
        return i

    def readVolt(self):
        self.serial_.write(b'$CMD:MON,CH:%d,PAR:VMON\n'%self.channel_)
        str = self.serial_.readline()
        str1 = str.split(b';')
        str2 = str1[0].split(b':')
        i = float(str2[-1])
        return i

    def readStatus(self):
        self.serial_.write(b'$CMD:MON,CH:%d,PAR:STAT\n'%self.channel_)
        str = self.serial_.readline()
        # print(str)
        return str
