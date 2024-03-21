from pymeasure.instruments.keithley import Keithley2400
import numpy as np
from time import sleep

class Keithley:
    """Class to control the Keithley 2410"""

    def __init__(self, port='ASRL/dev/ttyUSB0::INSTR', vmax=1, accuracy=1):
        self.port_ = port
        self.vmax_ = vmax
        self.keithley = Keithley2400(port)
        self.keithley.write("*RST")
        print(self.keithley.ask("*IDN?"))
        self.keithley.write(":SENS:CURR:RANGE:AUTO 1")
        self.keithley.write('voltage:nplc %2f'%(accuracy))
        self.keithley.write(":OUTP ON")
        data = self.keithley.ask(":READ?")
        print(data)
        volt = float(data.split(',')[0])
        if abs(volt)>vmax:
            print("Che cazz fe?")
            exit()
        print("Keithley Initialized")

    def meascurr(self, units=1e-6, debug=False):
        data = self.keithley.ask(":READ?")
        if debug:
            print(data)
        string = data.split(',')
        current = float(string[1])/units
        return current

    def precisemeas(self, repeat=10, units=1e-6, debug=False, skip=50):
        for i in range(skip):
            self.meascurr(units,debug)
            sleep(0.1)
        meas = np.zeros(repeat)
        for i in range(repeat):
            meas[i] = self.meascurr(units,debug)
            sleep(0.2)
        return np.average(meas), np.std(meas)

    def reset(self):
        return self.keithley.write("*RST")

    def on(self):
        return self.keithley.write(":OUTP ON")

    def off(self):
        return self.keithley.write(":OUTP OFF")

    def setVoltage(self, voltage=0):
        self.keithley.source_voltage = voltage
        self.keithley.apply_voltage(compliance_current=10e-6)

    # def __del__(self):
    #    self.keithley.write(":OUTP OFF")     # turn off
    #    self.keithley.write("SYSTEM:KEY 23") # go to local control
    #    self.keithley.close()
