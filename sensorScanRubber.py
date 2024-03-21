import motion
from keithley import Keithley
import numpy as np
import threading
from tkinter import messagebox
from tkinter import messagebox, Tk
root = Tk()
root.withdraw()

import mapALTIROC

motion = motion.motion()
k = Keithley(port='COM4',accuracy=1)
k.on()
k.setVoltage(-0.5)

x_start = -0.2
x_step = .03
x_max = 0.2
x_nsteps = int( (x_max-x_start)/x_step ) +1

y_start = -0.2
y_step = .03
y_max = .2
y_nsteps = int( (y_max-y_start)/y_step ) +1 

print("Total steps: %d"%(x_nsteps*y_nsteps))

motion.setHome()
print("\t", end ="\t")
for i in range(x_nsteps):
    print('%.2f'%(x_step*i+x_start), end ="\t")
print(" ")
print(" ")

try:
    for j in range(y_nsteps):
        print('%.2f\t'%(y_step*j+y_start), end ="\t")
        for i in range(x_nsteps):
            motion.moveFor('z',-6)
            motion.moveTo('x',x_step*i+x_start)
            motion.moveTo('y',y_step*j+y_start)
            motion.moveFor('z',6)
            m,s = k.precisemeas(skip=5,repeat=1)
            print('%.2f'%(m), end ="\t")
            #print(motion.getPosition())
            #sensorInPosition = messagebox.showinfo("Sensor Locator","ok?")
        print(" ")
except KeyboardInterrupt:   #Avoids disconnection before rampdown
        print("\nReturning home..")
    
motion.moveTo('z',-6)
motion.moveTo('x',0)
motion.moveTo('y',0)
#motion.moveTo('z',0)
