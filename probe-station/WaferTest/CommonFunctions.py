from tkinter import *
import motion
import keithley
import numpy as np
from PIL import ImageTk,Image
import time
import cv2
import json
import os
import TransformMatrix

TM = TransformMatrix.TransformMatrix()

def openImage(filename):
    window = Toplevel(width=1400,height=1400)
    img = ImageTk.PhotoImage(Image.open(filename))
    label = Label(window,image=img)
    label.image = img
    label.place(x=100,y=100)

def readResistance(kt=None, emulate=False, debug=True, points=10, powerLimit=1e-2, currentLimit=10e-3):
    print("Measuring Resistance")
    time.sleep(0.5)
    resist = 0
    resistErr = 0
    if emulate:
        print("In emulation Mode")
        print("Will not check resistance")
        return resist, resistErr
    results = kt.measresist(debug=debug,points=points,powerLimit=powerLimit,currentLimit=currentLimit)
    resist = results['R']
    resistErr = results['Rerr']
    print(f"{results['R']:.3f} +- {results['Rerr']:.3f}")
    return results



def checkContact(kt=None, emulate=False, safetyResist=50000):
    print("Checking for contact with resistance threshold of: "+str(safetyResist)+" Ohms")
    results = readResistance(kt,debug=True,points=5)
    if emulate:
        print("In emulation mode")
        return False
    resist = results['R']
    resistErr = results['Rerr']
    if 0 < resist < safetyResist and resistErr < 0.001*resist:
        print("Probe Needle is touching")
        kt.keithley.beep(frequency=2700,duration=0.5)
        kt.keithley.beep(frequency=2700,duration=0.5)
        return True
    else:
        print("Probe Needle is NOT touching")
        return False

    
def raiseToContact(kt=None, motors=None, emulate=False, safetyResist=50000, step=0.05, maxMovement=1):
    print("Raising Until Made Contact")
    totMovement = 0.0
    firstContact = True
    contact = False
    while totMovement < maxMovement:
        contact = checkContact(kt)
        if contact is False:
            motors.moveFor('z',step)
            totMovement += step
            firstContact = True
        elif firstContact:
            firstContact = False
        else:
            break
    if contact:
        print("Made Contact")
        kt.keithley.beep(frequency=2700,duration=1)
        kt.keithley.beep(frequency=2700,duration=1)
        
    else:
        print("Could not make contact in: "+str(maxMovement/step)+" attempts")
        kt.keithley.beep(frequency=1000,duration=1)
    return contact

def moveToPosition(motors=None, emulate=False, x=-10000, y=-10000, zRetraction=2):
        if emulate is True:
            return
        motors.moveFor('z',-1*zRetraction)
        print(f"Position non corrected: {x}, {y}")
        padPos = TM.Transform(np.array([x,y]))
        print(f"Position corrected: {padPos[0]}, {padPos[1]}")
        motors.moveTo('x',padPos[0])
        motors.moveTo('y',padPos[1])
        motors.moveFor('z',zRetraction)
