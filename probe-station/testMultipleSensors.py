import microscope
import motion
import time
from queue import Queue
import numpy as np
import threading
from tkinter import messagebox, Tk
root = Tk()
root.withdraw()

from measureALTIROC import measureALTIROC

testName = 'autoTest'

m = microscope.microscope(camera=1)
queue = m.getOutQueue()
inQueue = m.getInQueue()
m.start()

sensorInPosition = messagebox.showinfo("Question","Is the first sensor in position?")

##voltages = np.array([0,10 ,50, 100, 150, 185, 200, 210, 220, 225, 230])
voltages = np.linspace(0,200,5)
##voltages = np.array([0, 5])

motion = motion.motion()
motion.setHome()
startPosition = motion.getPosition()
print(f'Start position: {startPosition}')
motion.setSafetyLimit('z',max=startPosition[2]+0.1)      ## IMPORTANT!!!

sensorsPositions = [(0, 0)]
#sensorsPositions = [(0, 0)]


##motion.moveFor('z',-2)
microscopeOut = microscope.waitForStableOutput(queue)
shift = microscopeOut['center']
print(f'center: {shift}')
##motion.moveTo('z',-0.4)
##motion.moveTo('z',-0.2)
##motion.moveTo('z',-0.1)
##motion.moveTo('z',0)


for sensorCounter in range(len(sensorsPositions)):
    microscopeOut = microscope.waitForStableOutput(queue)       
    if 'close' in microscopeOut.keys():
        break

    if sensorCounter>0:
        print(f'moving to next sensor {sensorsPositions[sensorCounter]}')
        motion.moveFor('z',-2)
        time.sleep(1)
       
        motion.moveTo('x',sensorsPositions[sensorCounter][0])
        motion.moveTo('y',sensorsPositions[sensorCounter][1])

        while True:
            microscopeOut = microscope.waitForStableOutput(queue)
            if 'close' in microscopeOut.keys():
                break
            center = microscopeOut['center']
            if max(np.abs(center-shift))<0.05:
                break
            print(f'center in {center} instead of {shift}')
            print(f'moving for {shift[0]-center[0]},{center[1]-shift[1]}')
            motion.moveFor('x',shift[0]-center[0])
            motion.moveFor('y',center[1]-shift[1])
            time.sleep(3)            

        if 'close' in microscopeOut.keys():
            break
        print(f'sensor found and centered')
        motion.moveTo('z',-0.4)
        motion.moveTo('z',-0.2)
        motion.moveTo('z',-0.1)
        motion.moveTo('z',0)
        print(motion.getPosition())

    lightOff = messagebox.showinfo("Question","Turn off the light and click on Yes to proceed")
    inQueue.append('pause')
    time.sleep(1)
    measureALTIROC(sensorName=f'ALTIROC_{testName}_{sensorCounter}', voltages=voltages)
    lightOff = messagebox.showinfo("Question","Turn on the light and click on Yes to proceed")
    microscopeOut.clear()
    inQueue.clear()

print("Going home...")
motion.moveTo('z',-4)
motion.moveTo('x',0)
motion.moveTo('y',0)
inQueue.append('exit')
m.join()

                
        
                
                

            

    
    
