from tkinter import *
from CommonFunctions import *

procedureComplete = False

class Window_Procedure(Frame):

    def __init__(self, master=None, motors=None, keithley=None, emulate=True):
        Frame.__init__(self, master)        
        self.master = master
        self.emulate = emulate

        self.motors = motors
        self.kt = keithley
        self.safetyResist = 50000

        self.cam = cv2.VideoCapture(1)
        time.sleep(1)

        self.sensor = "defaultSensor"
        self.run = "0"
        self.notes = "Notes"

        self.resistanceMeasurement = {
            'Sensor': self.sensor,
            'Measurement': "resistance",
            'Notes': self.notes,
            'Run': self.run,
            'Values': []
        }


        menu = Menu(self.master)
        self.master.config(menu=menu)
        fileMenu = Menu(menu)
        menu.add_cascade(label="File", menu=fileMenu)
        self.pack(fill=BOTH, expand=1)

        self.beginProcedureButton = Button(self, text="Begin Procedure", width=15, height=2, command=self.beginProcedure)
        self.finishProcedureButton = Button(self, text="Finished Procedure", width=15, height=2, command=self.finishProcedure)
        self.saveSensorNameButton = Button(self, text="Save Sensor Name", width=15, height=2, command=self.saveSensorName)
        self.saveRunNumberButton = Button(self, text="Save Run Number", width=15, height=2, command=self.saveRunNumber)
        #self.saveNotesButton = Button(self, text="Save Notes", width=10, height=2, command=self.saveNotes)
        self.startMeasurementButton = Button(self, text="Start Measurement", width=20, height=3, command=self.startMeasurement)
        self.plotResultsButton = Button(self, text="Plot Results", width=10, height=2, command=self.plotResults)
       
        self.notesVar=StringVar() 
        self.notesVar.set(str(self.notes))
        self.notesLabel = Label(self, text="Notes:")
        self.notesEntry = Entry(self, textvariable=self.notesVar, width=15)

        self.runVar=StringVar() 
        self.runVar.set(str(self.run))
        self.runLabel = Label(self, text="Run:")
        self.runEntry = Entry(self, textvariable=self.runVar, width=5)

        self.sensorVar=StringVar() 
        self.sensorVar.set(str(self.sensor))
        self.sensorLabel = Label(self, text="Sensor:")
        self.sensorEntry = Entry(self, textvariable=self.sensorVar, width=15)



        #self.notesLabel.place(x=575,y=350)
        #self.notesEntry.place(x=575,y=375)
        

        self.beginProcedureButton.place(x=50,y=50)

        print('Press "Begin Procedure" Button To Start')

    def beginProcedure(self):
        print("Starting Procedure Setup")
        self.beginProcedureButton.destroy()
        print('Input name of assembly')
        self.sensorLabel.place(x=625,y=400)
        self.sensorEntry.place(x=625,y=425)
        self.saveSensorNameButton.place(x=600, y=300)
        with open("PointsCNM_VQ_Testing.json") as f:
            points=json.load(f)
        self.resistanceMeasurement.update(points)

    def saveSensorName(self):
        self.sensor = str(self.sensorEntry.get())
        temp_dict = {'Sensor': self.sensor}
        self.resistanceMeasurement.update(temp_dict)
        self.sensorLabel.destroy()
        self.sensorEntry.destroy()
        self.saveSensorNameButton.destroy()
        print('Saved name of sensor as: '+self.sensor)
        self.runLabel.place(x=650,y=350)
        self.runEntry.place(x=650,y=375)
        self.saveRunNumberButton.place(x=400, y=300)
        print('Input run number')

    def saveRunNumber(self):
        self.run = str(self.runEntry.get())
        temp_dict = {'Run': self.run}
        self.resistanceMeasurement.update(temp_dict)
        self.runLabel.destroy()
        self.runEntry.destroy()
        self.saveRunNumberButton.destroy()
        print('Saved run number as: '+self.run)
        self.startMeasurementButton.place(x=200,y=200)
        print('Click "Start Measurement" Button if ready to start taking data')

    def startMeasurement(self):
        if self.sensor is "defaultSensor" or self.run is "0":
            print("Sensor or run number not updated!")
            print("Will not start until these are updated!")
        else:
            self.measureAllPoints(test=True)


    def finishProcedure(self):
        results = False
        expectedResultsFile = self.sensor+"_Run"+self.run+"_"+"resistance.json"
        if os.path.exists(expectedResultsFile) and os.path.getsize(expectedResultsFile) > 0:
            print('Results Saved!')
            global procedureComplete
            procedureComplete = True
            self.destroy()
        else:
            print("Results of procedure not found!")

    def loadCalibration(self):
        with open("Calibration.json") as f:
            calibration=json.load(f)
        sensorsPositions = calibration.get('sensorsPositions')
        measuredPositions = calibration.get('measuredPositions')
        self.calibrate()
        global TM
        TM.Calibrate(self.sensorsPositions, self.measuredPositions, weighted=True)

    def measureAllPoints(self,test=True):
        lastContactZ = 0
        total_attempts = 3
        if test:
            self.motors.moveFor('z',-0.5)
        else:
            if not os.path.exists("img/"+self.sensor+"_Run"+self.run):
                os.makedirs("img/"+self.sensor+"_Run"+self.run)

        for p in self.resistanceMeasurement['Pads']:
            print("Measuring Pad: "+str(p.get('Pad')))
            x_given = p.get('PositionX')
            y_given = p.get('PositionY')

            attempt = 0

            moveToPosition(self.motors,self.emulate,x_given,y_given,2)
            if p.get('Pad') == 12345:
                lastContactZ = lastContactZ-0.1
                self.writeResistance()
                print("Waiting for needles to be setup for next run...")
                input("Press Enter twice to continue...")
                continue
            if test:
                continue

            if lastContactZ is 0:
                self.motors.moveTo('z',0.0)
                if raiseToContact(self.kt,self.motors,self.emulate,self.safetyResist,0.2,1.5):
                    lastContactZ = self.motors.getPosition('z')
                    print(f"Setting {lastContactZ:.3f} as lastContactZ")
                    raiseToContact(self.kt,self.motors,self.emulate,self.safetyResist,0.1,1.)
            else:
                self.motors.moveTo('z',(lastContactZ-0.2))
                if raiseToContact(self.kt,self.motors,self.emulate,self.safetyResist,0.1,0.8):
                    lastContactZ = self.motors.getPosition('z')
                    print(f"Setting {lastContactZ:.3f} as lastContactZ")
                    raiseToContact(self.kt,self.motors,self.emulate,self.safetyResist,0.1,0.5)

            while attempt <= total_attempts:
                if attempt > 0:
                    self.motors.moveFor('z',0.05)
                attempt += 1
                frame = None
                while frame is None:
                    pad = p.get('Pad')
                    time.sleep(0.25)
                    ret, frame = self.cam.read()
                    cv2.imwrite(f"img/"+sensor+"_Run"+run+"/Pad"+str(pad)+"_"+str(attempt)+".png", frame)
                results = readResistance(kt=self.kt,emulate=self.emulate,debug=True)
                self.saveResistance(self.sensor,p.get('Pad'),self.notes,run,x_given,y_given,results) # save it in any case, we take care in data analysis
            self.motors.moveTo('z',-0.1)

        self.motors.moveFor('z',-5.0)
        self.motors.goHome()
        self.cam.release()
        if not test:
            self.writeResistance()

    def writeResistance(self):
        try:
            to_unicode = unicode
        except NameError:
            to_unicode = str
        filename = self.sensor+"_Run"+self.run+"_"+"resistance.json"
        self.resistanceMeasurement["Notes"] =  str(self.notes)
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename,'a',encoding='utf8') as f:
           dump = json.dumps(self.resistanceMeasurement,indent=4,sort_keys=True,separators=(',',": "),ensure_ascii=False)
           f.write(to_unicode(dump))
        print("Writing Resitance for run "+self.run+" of sensor: "+self.sensor+" to file: "+filename)
        self.plotResultsButton.place(x=100,y=100)
        self.startMeasurementButton.destroy()

    def plotResults(self):
        with open(self.sensor+"_Run"+self.run+"_"+"resistance.json") as f:
            d=json.load(f)
        df=json_normalize(d,'Values')
        df = df[df.Resistance > 0]
        df = df[df.ResistanceError < 0.1*df.Resistance]
        df = df[df.Pad < 99]
        df=df.loc[df.groupby('Pad').Resistance.idxmin()]
        ax = df.plot(x='Pad',y='Resistance',yerr='ResistanceError',kind="scatter",figsize=(15,10),title='',grid=True,marker=markers[i],color=colors[i],label=str(file).replace('_resistance.json','').replace('./',''))
        plt.xlabel('Wire Bond Pad Pair')
        plt.ylabel('Resistance [Ohms]')
        self.finishProcedureButton.place(x=100,y=200)
        self.plotResultsButton.destroy()
        plt.show()

    def exit(self):
        print("Closing Calibration Window")
        self.destroy()

def isProcedureComplete():
    return procedureComplete
    
