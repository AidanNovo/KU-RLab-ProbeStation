from tkinter import *
from CommonFunctions import *

calibrationComplete = False

class Window_Calibration(Frame):

    def __init__(self, master=None, motors=None, emulate=True):
        Frame.__init__(self, master)
        self.master = master
        self.emulate = emulate

        self.motors = motors

        menu = Menu(self.master)
        self.master.config(menu=menu)
        fileMenu = Menu(menu)
        fileMenu.add_command(label="Clear Calib", command=self.clearCalibrations)
        menu.add_cascade(label="File", menu=fileMenu)
        self.pack(fill=BOTH, expand=1)

        self.sensorsPositions = [[0,0],[0,18.2],[0.45,20.45],[0,21.3],[0,39.5],[0.45,41.85]]
        self.measuredPositions = []



        self.savedLabel = Label(self, text="Saved positions:")
        self.savedPointsVar=StringVar() 
        self.savedPointsVar.set("0")
        self.savedPointsLabel = Label(self, textvariable=self.savedPointsVar, width=10)
        self.saveButton = Button(self, text="Save Calibration Point", width=25, height=2, command=self.savePosition)
        self.calibrateButton = Button(self, text="Calibrate", width=10, height=2, command=self.calibrate)
        self.beginCalibrationButton = Button(self, text="Begin Calibration", width=15, height=2, command=self.beginCalibration)
        self.nextPointButton = Button(self, text="Next Point", width=10, height=2, command=self.nextPoint)


        self.beginCalibrationButton.place(x=50,y=50)

        print('Press "Begin Calibration" Button To Start')

    def beginCalibration(self):
        print("Starting Calibration")
        self.beginCalibrationButton.destroy()
        self.saveButton.place(x=300, y=500)
        self.savedLabel.place(x=300 ,y=550)
        self.savedPointsLabel.place(x=400 ,y=550)
        print('Go to home and click "Save Calibration Point" Button')
        openImage("ImageGUI/Jayhawk.png")
        print("Opened example image of what Home looks like")

    def setHome(self):
        self.motors.setHome()
        self.motors.setSafetyLimit(motor='z',min=None,max=2.0)
        print("New home has been set")
        self.savedLabel['state'] = DISABLED
        self.savedPointsLabel['state'] = DISABLED
        self.saveButton['state'] = DISABLED

    def nextPoint(self):
        measured_points = len(self.measuredPositions)
        sensor_points = len(self.sensorsPositions)
        self.nextPointButton['state'] = DISABLED
        if measured_points == sensor_points:
            print("All necessary points added!")
            print('If ready, press the "Calibrate" button')
            #disable points button and enable calibrate button
            self.calibrateButton.place(x=10,y=450)
            self.nextPointButton.destroy()
            self.savedLabel.destroy()
            self.savedPointsLabel.destroy()
            self.saveButton.destroy()
            self.nextPointButton.destroy()
        else:
            self.saveButton['state'] = ACTIVE
            self.savedLabel['state'] = ACTIVE
            self.savedPointsLabel['state'] = ACTIVE
            print("Opening Image for next point")
            openImage("ImageGUI/Jayhawk.png") # use something like ImageGUI/Jayhawk+"measured_points".png for next point
            print('Move chuck to corresponding point and click "Save Calibration Point" Button')

    def clearCalibrations(self):
        print("Clearing Calibrations")
        self.measuredPositions = []
        self.savedPointsVar.set("0")
        global TM
        TM.Reset()


    def savePosition(self):
        print(f'Saving position at {len(self.measuredPositions)}')
        self.nextPointButton['state'] = ACTIVE
        self.savedLabel['state'] = DISABLED
        self.savedPointsLabel['state'] = DISABLED
        self.saveButton['state'] = DISABLED
        if len(self.measuredPositions) == 0:
            self.setHome()
            self.measuredPositions.append([0,0,0])
            self.savedPointsVar.set(len(self.measuredPositions))
            self.nextPointButton.place(x=300,y=300)
        else:
            lastPosition = self.motors.getPosition()
            self.measuredPositions.append(list([np.round(lastPosition[0],decimals=3),np.round(lastPosition[1],decimals=3),np.round(lastPosition[2],decimals=3)]))
            self.savedPointsVar.set(len(self.measuredPositions))
        print('Continue with calibration procedure by clicking the "Next Point" button')

    def calibrate(self):
        print("Calibrating ")
        print(self.sensorsPositions)
        print(self.measuredPositions)
        global TM
        TM.Calibrate(self.sensorsPositions, self.measuredPositions, weighted=True)   
        self.calibrateButton.destroy()
        print("Calibration Complete!")
        global calibrationComplete
        calibrationComplete = True
        print('Click "Check If Calibration Is Complete" Button In Main Window')
        

    def exit(self):
        print("Closing Calibration Window")
        self.destroy()

def isCalibrationComplete():
    return calibrationComplete
    
