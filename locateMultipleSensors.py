import microscope
import motion
from time import sleep
from queue import Queue
import numpy as np
import threading
from tkinter import messagebox
from tkinter import messagebox, Tk
root = Tk()
root.withdraw()

from measureALTIROC import measureALTIROC

m = microscope.microscope(camera=1)
queue = m.getOutQueue()
inQueue = m.getInQueue()
m.start()

sensorInPosition = messagebox.showinfo("Sensor Locator","Is the first sensor in position?")

motion = motion.motion()
motion.setHome()
motion.setSafetyLimit('z',max=-2)      ## IMPORTANT!!!
motion.moveFor('z',-5)
sensorsPositions = [(0,0)]

while True:
    answer = messagebox.askyesno("Sensor Locator", "Next sensor in position? No to cancel")
    if answer is False:
        break
    lastPosition = motion.getPosition()
    sensorsPositions.append(tuple([np.round(lastPosition[0],decimals=1),np.round(lastPosition[1],decimals=1)]))
    print(sensorsPositions[-1])

print(f'sensorsPositions = {sensorsPositions}')

motion.moveFor('x',0)
motion.moveFor('y',0)
inQueue.append('exit')
m.join()



                
        
                
                

            

    
    
