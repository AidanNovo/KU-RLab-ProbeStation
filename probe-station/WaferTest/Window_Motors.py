from tkinter import *
import motion

class Window_Motors(Frame):

    def __init__(self, master=None, motors=None, emulate=True):
        Frame.__init__(self, master)        
        self.master = master
        self.emulate = emulate

        self.motors = motors

        self.stepSizeXY = 1
        self.stepSizeZ = 1
        
        self.stepSizeVarXY=StringVar() 
        self.stepSizeVarXY.set(str(self.stepSizeXY))
        stepsLabelXY = Label(self, text="mm")
        self.stepsEntryXY = Entry(self, textvariable=self.stepSizeVarXY, width=10)

        self.stepSizeVarZ=StringVar() 
        self.stepSizeVarZ.set(str(self.stepSizeZ))
        stepsLabelZ = Label(self, text="mm")
        self.stepsEntryZ = Entry(self, textvariable=self.stepSizeVarZ, width=10)

        self.moveToXVar=StringVar() 
        self.moveToXVar.set("0")
        self.moveToXEntry = Entry(self, textvariable=self.moveToXVar, width=10)
        self.moveToYVar=StringVar() 
        self.moveToYVar.set("0")
        self.moveToYEntry = Entry(self, textvariable=self.moveToYVar, width=10)


        # widget can take all window
        self.pack(fill=BOTH, expand=1)

        upButton = Button(self, text="Up", width=10, height=2, command=lambda: self.moveBtn(0,1*float(self.stepsEntryXY.get()),0))
        upRightButton = Button(self, text="U-R", width=10, height=2, command=lambda: self.moveBtn(-1*float(self.stepsEntryXY.get()),1*float(self.stepsEntryXY.get()),0))
        upLeftButton = Button(self, text="U-L", width=10, height=2, command=lambda: self.moveBtn(1*float(self.stepsEntryXY.get()),1*float(self.stepsEntryXY.get()),0))
        downButton = Button(self, text="Down", width=10, height=2, command=lambda: self.moveBtn(0,-1*float(self.stepsEntryXY.get()),0))
        downRightButton = Button(self, text="D-R", width=10, height=2, command=lambda: self.moveBtn(-1*float(self.stepsEntryXY.get()),-1*float(self.stepsEntryXY.get()),0))
        downLeftButton = Button(self, text="D-L", width=10, height=2, command=lambda: self.moveBtn(1*float(self.stepsEntryXY.get()),-1*float(self.stepsEntryXY.get()),0))
        leftButton = Button(self, text="Left", width=10, height=2, command=lambda: self.moveBtn(1*float(self.stepsEntryXY.get()),0,0))
        rightButton = Button(self, text="Right", width=10, height=2, command=lambda: self.moveBtn(-1*float(self.stepsEntryXY.get()),0,0))
        raiseButton = Button(self, text="Raise", width=10, height=2, command=lambda: self.moveBtn(0,0,1*float(self.stepsEntryZ.get())))
        lowerButton = Button(self, text="Lower", width=10, height=2, command=lambda: self.moveBtn(0,0,-1*float(self.stepsEntryZ.get())))

        upFastButton = Button(self, text="10x U", width=10, height=2, command=lambda: self.moveBtn(0,10*float(self.stepsEntryXY.get()),0))
        upRightFastButton = Button(self, text="10x U-R", width=10, height=2, command=lambda: self.moveBtn(-10*float(self.stepsEntryXY.get()),10*float(self.stepsEntryXY.get()),0))
        upLeftFastButton = Button(self, text="10x U-L", width=10, height=2, command=lambda: self.moveBtn(10*float(self.stepsEntryXY.get()),10*float(self.stepsEntryXY.get()),0))
        downFastButton = Button(self, text="10x D", width=10, height=2, command=lambda: self.moveBtn(0,-10*float(self.stepsEntryXY.get()),0))
        downRightFastButton = Button(self, text="10x D-R", width=10, height=2, command=lambda: self.moveBtn(-10*float(self.stepsEntryXY.get()),-10*float(self.stepsEntryXY.get()),0))
        downLeftFastButton = Button(self, text="10x D-L", width=10, height=2, command=lambda: self.moveBtn(10*float(self.stepsEntryXY.get()),-10*float(self.stepsEntryXY.get()),0))
        leftFastButton = Button(self, text="10x L", width=10, height=2, command=lambda: self.moveBtn(10*float(self.stepsEntryXY.get()),0,0))
        rightFastButton = Button(self, text="10x R", width=10, height=2, command=lambda: self.moveBtn(-10*float(self.stepsEntryXY.get()),0,0))
        raiseFastButton = Button(self, text="10X Raise", width=10, height=2, command=lambda: self.moveBtn(0,0,10*float(self.stepsEntryZ.get())))
        lowerFastButton = Button(self, text="10X Lower", width=10, height=2, command=lambda: self.moveBtn(0,0,-10*float(self.stepsEntryZ.get())))

        #CloseButton = Button(self, text="Close Window", width=15, height=2, command=self.exit)

        # place buttons
        stepsLabelXY.place(x=200,y=100)
        self.stepsEntryXY.place(x=200,y=125)
        stepsLabelZ.place(x=575,y=105)
        self.stepsEntryZ.place(x=555,y=130)

        upButton.place(x=200, y=60)
        upRightButton.place(x=300, y=60)
        upLeftButton.place(x=100, y=60)
        downButton.place(x=200, y=160)
        downRightButton.place(x=300, y=160)
        downLeftButton.place(x=100, y=160)
        leftButton.place(x=100, y=110)
        rightButton.place(x=300, y=110)
        upFastButton.place(x=200, y=10)
        upRightFastButton.place(x=400, y=10)
        upLeftFastButton.place(x=10, y=10)
        downFastButton.place(x=200, y=210)
        downRightFastButton.place(x=400, y=210)
        downLeftFastButton.place(x=10, y=210)
        leftFastButton.place(x=10, y=110)
        rightFastButton.place(x=400, y=110)
        
        raiseFastButton.place(x=500, y=60)
        lowerFastButton.place(x=500, y=160)
        raiseButton.place(x=600, y=60)
        lowerButton.place(x=600, y=160)

        #CloseButton.place(x=550, y=250)

    def exit(self):
        print("Closing Motor Window")
        self.destroy()

    def moveBtn(self, x, y, z):
        if x is not 0:
            self.motors.moveFor('x',x)
        if y is not 0:
            self.motors.moveFor('y',y)
        if z is not 0:
            self.motors.moveFor('z',z)

