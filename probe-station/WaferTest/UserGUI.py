import tkinter as tk
from Window_Motors import *
import keithley
from Window_Calibration import *
from Window_VerticalAlignment import *
from Window_Procedure import *

class Window(tk.Frame):

    def __init__(self, master=None, motorsPort='COM4', keithleyPort='COM13', emulate=False):
        tk.Frame.__init__(self, master)        
        self.master = master
        self.emulate = emulate

        self.motorsPort = motorsPort
        self.motors = motion.motion(port=self.motorsPort, emulate=emulate)
        
        self.kt = keithley.Keithley(port=keithleyPort, emulate=emulate)
        self.kt.reset()
        self.kt.on()

        menu = Menu(self.master)
        self.master.config(menu=menu)
        self.pack(fill=BOTH, expand=1)

        self.motorWindow()
        self.showCalibrationWindowButton = Button(self, text="Open Calibration Window", width=25, height=2, command=self.calibrationWindow)
        self.showVerticalAlignmentWindowButton = Button(self, text="Open Vertical Alignment Window", width=30, height=2, command=self.verticalAlignmentWindow)
        self.showProcedureWindowButton = Button(self, text="Open Procedure Window", width=20, height=2, command=self.procedureWindow)

        self.startSetupButton = Button(self, text="Start Setup", width=10, height=2, command=self.startSetup)
        
        self.startSetupButton.place(x=200,y=400)

    def startSetup(self):
        self.startSetupButton.destroy()
        self.showVerticalAlignmentWindowButton.place(x=100,y=300)

    def checkVAComplete(self):
        complete = isVerticalAlignmentComplete()
        if complete is True:
            print("Vertical Alignment Complete! Lowering needles away by 1 mm")
            self.motors.moveFor('z',-0.75)
            print("Continue On To Calibration Step")
            self.showCalibrationWindowButton.place(x=100,y=200)
            self.showVerticalAlignmentWindowButton.destroy()
            self.checkVACompleteButton.destroy()
        else:
            print("Vertical Alignment Is Not Complete")
            return False

    def checkCalibrationComplete(self):
        complete = isCalibrationComplete()
        if complete is True:
            print("Calibration Complete! Going Home")
            self.motors.moveFor('z',-5)
            self.motors.goHome()
            print("Continue On To Procedure Step")
            self.showProcedureWindowButton.place(x=100,y=200)
            self.showCalibrationWindowButton.destroy()
            self.checkCalibrationCompleteButton.destroy()
        else:
            print("Calibration Is Not Complete")
            return False

    def checkProcedureComplete(self):
        complete = isProcedureComplete()
        if complete is True:
            print("Procedure Complete!")
            self.showProcedureWindowButton.destroy()
            self.checkProcedureCompleteButton.destroy()
        else:
            print("Procedure Is Not Complete")
            return False
            
## check with Nicola about how to (automatically) upload results to database

    def motorWindow(self):
        window = tk.Toplevel()
        motor_window = Window_Motors(window,self.motors,self.emulate)
        window.geometry("700x300")


    def verticalAlignmentWindow(self):
        self.showVerticalAlignmentWindowButton.destroy()
        self.checkVACompleteButton = Button(self, text="Check If Vertical Alignment Is Complete", width=30, height=2, command=self.checkVAComplete)
        self.checkVACompleteButton.place(x=300,y=350)
        window = tk.Toplevel()
        vertical_alignment_window = Window_VerticalAlignment(window,self.motors,self.kt,self.emulate)
        window.geometry("400x400")

    def calibrationWindow(self):
        self.showCalibrationWindowButton.destroy()
        self.checkCalibrationCompleteButton = Button(self, text="Check If Calibration Is Complete", width=30, height=2, command=self.checkCalibrationComplete)
        self.checkCalibrationCompleteButton.place(x=300,y=350)
        window = tk.Toplevel()
        calibration_window = Window_Calibration(window,self.motors,self.emulate)
        window.geometry("800x600")

    def procedureWindow(self):
        self.showProcedureWindowButton.destroy()
        self.checkProcedureCompleteButton = Button(self, text="Check If Procedure Is Complete", width=30, height=2, command=self.checkProcedureComplete)
        self.checkProcedureCompleteButton.place(x=300,y=350)
        window = tk.Toplevel()
        procedure_window = Window_Procedure(window,self.motors,self.kt,self.emulate)
        window.geometry("800x800")
    



if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    Window(root)
    root.mainloop()
