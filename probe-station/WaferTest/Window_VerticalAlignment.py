from tkinter import *
from CommonFunctions import *

verticalAlignmentComplete = False

class Window_VerticalAlignment(Frame):

    def __init__(self, master=None, motors=None, keithley=None, emulate=True):
        Frame.__init__(self, master)        
        self.master = master
        self.emulate = emulate

        self.motors = motors
        self.kt = keithley
        self.safetyResist = 50000

        menu = Menu(self.master)
        self.master.config(menu=menu)
        fileMenu = Menu(menu)
        menu.add_cascade(label="File", menu=fileMenu)
        self.pack(fill=BOTH, expand=1)

        self.beginVerticalAlignmentButton = Button(self, text="Begin Vertical Alignment", width=20, height=2, command=self.beginVerticalAlignment)
        self.raiseToContactButton=Button(self, text="Raise To Contact", width=15, height=2, command=self.raiseToContact)
        self.finishVerticalAlignmentButton = Button(self, text="Finished Alignment", width=15, height=2, command=self.finishVerticalAlignment)

        self.beginVerticalAlignmentButton.place(x=50,y=50)

        print('Press "Begin Vertical Alignment" Button To Start')

    def beginVerticalAlignment(self):
        print("Starting Vertical Alignment")
        self.beginVerticalAlignmentButton.destroy()
        print('Use chuck to move the assembly under the needles as shown in the corresponding image')
        openImage("ImageGUI/Jayhawk.png")
        print("Opened example image of where needles should be in relation to pads")
        print('Once needles are aligned, use "Raise To Contact" Button to raise chuck until needles make contact with assembly')
        self.raiseToContactButton.place(x=100,y=100)
        self.finishVerticalAlignmentButton.place(x=100,y=300)

    def raiseToContact(self):
        raiseToContact(self.kt,self.motors,self.emulate,self.safetyResist,0.1,2)

    def finishVerticalAlignment(self):
        print("Checking For Contact")
        contact = checkContact(self.kt,self.emulate,self.safetyResist)
        if contact:
            print('Click "Check If Vertical Alignment Is Complete" Button In Main Window')
            global verticalAlignmentComplete
            verticalAlignmentComplete = True
            self.destroy()
        else:
            print("Needles not in contact!")
            print("Check Vertical Alignment!")

    def exit(self):
        print("Closing Vertical Alignment Window")
        self.destroy()

def isVerticalAlignmentComplete():
    return verticalAlignmentComplete
    
