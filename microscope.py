from threading import Thread
from collections import deque
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import cv2 as cv
import numpy as np
import time
import logging
from copy import copy

__logLevel__ = logging.DEBUG

altirocParameters = dict(pads=(5,5), interpadDistance=(1.25,1.25), name='FBK_ALTIROC', matchingThreshold=0.4, epsilonPercentage=0.01)

class microscope(Thread):
    def __init__(self, log=None, camera=0, average=10, sensorParameters=altirocParameters):
        ''' Constructor. '''
        if log is None:
            log=self.__class__.__name__+'Log.log'
        hdlr = logging.FileHandler(log,mode='w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger = logging.getLogger()
        self.logger.addHandler(hdlr) 
        self.logger.setLevel(__logLevel__)

        self.inqueue = deque(maxlen=1)
        self.outqueue = deque(maxlen=1)
        self.centerQueque = deque(maxlen=average)
        self.p2mmQueque = deque(maxlen=average)

        self.camera = camera
        self.cameraStarted = False

        self.microscopeImgSize = (2592,1944)
        microscopeImgArea = self.microscopeImgSize[0] * self.microscopeImgSize[1]
        self.minimumArea = (0.03**2)*microscopeImgArea
        self.maximumArea = (0.5**2)*microscopeImgArea
        self.pixel2mmConstants = (212.6,212.6)
        self.ratio = 1
        self.shapeTimeout = 2
        self.threshold = 125
        self.skipFrames = average
        self.displayHeight = 512
        self.clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        self.aspectRatio = self.microscopeImgSize[0]/self.microscopeImgSize[1]

        ## Sensor's parameters:
        self.sensorParameters = sensorParameters
 
        Thread.__init__(self) 

    def __del__(self):
        cv.destroyAllWindows()

    def stop(self):
        self.outqueue.clear()
        cv.destroyAllWindows()

    def getOutQueue(self):
        return self.outqueue

    def getInQueue(self):
        return self.inqueue

    def pixel2mm(self, pixel):
        center = np.divide(self.microscopeImgSize,2)
        mm = np.divide(pixel-center,self.pixel2mmConstants)
        return np.round(mm, decimals=3)

    def computePixel2mmConstants(self, interpadDistance=(1.25,1.25)):
        self.p2mmQueque.append((np.mean(self.cXdists)/interpadDistance[0], np.mean(self.cYdists)/interpadDistance[0]))
        self.pixel2mmConstants = np.mean(self.p2mmQueque,axis=0)
        # print(f'Computed: {self.pixel2mmConstants}')



    def run(self):
        contTemplate = loadTemplate(self.sensorParameters['name'])
        vs = VideoStream(src=self.camera, resolution=self.microscopeImgSize, framerate=60)
        vs.start()
        self.cameraStarted = True
        centroidSet = dict()
        timerToClearCenters = time.time() 
        outDict = dict()

        minimumX = int(self.microscopeImgSize[0]/50)
        minimumY = int(self.microscopeImgSize[1]/50)

        while vs.read() is None:
            print('camera not available... ')
            time.sleep(1)

        while vs.read().shape[0] != self.microscopeImgSize[1]:
            pass
        
        fps = FPS().start()
        tpr = time.time()

        while True:
            if cv.waitKey(1) & 0xFF == ord('q'):
                outDict = dict(close=True)
                self.outqueue.append(outDict)    #poison pill
                break
            if len(self.inqueue)>0:
                if 'pause' in self.inqueue:
                    # print(f'waiting... {self.inqueue}')
                    if self.cameraStarted:
                        vs.stop()
                        del vs
                        self.cameraStarted = False
                    time.sleep(1)
                    continue
                if 'exit' in self.inqueue:
                    break

            if not self.cameraStarted:
                vs = VideoStream(src=self.camera, resolution=self.microscopeImgSize, framerate=60)
                vs.start()
                self.cameraStarted = True
                while vs.read() is None:
                    print('camera not available... ')
                    time.sleep(1)

            image = vs.read()
            if np.max(image) == 0:
                continue
            fps.update()
            if fps._numFrames % self.skipFrames != 0:
                continue

            imageR = cv.resize(image, (int(self.microscopeImgSize[0]*self.ratio),int(self.microscopeImgSize[1]*self.ratio)), interpolation=cv.INTER_AREA   )
            imageR = cv.flip( imageR, 0 )
            imageBW = cv.cvtColor(imageR, cv.COLOR_BGR2GRAY)
            focus = cv.Laplacian(imageBW, cv.CV_64F).var()
            imageBW = cv.GaussianBlur(imageBW, (5, 5), 10)
            histoBW = makeHistoImgBW(imageBW, width=self.displayHeight, height=int(self.displayHeight/self.aspectRatio/2), bins=256)
            imageBW2 = imageBW
            # imageBW2 = self.clahe.apply(imageBW)
            histoBW2 = makeHistoImgBW(imageBW2, width=self.displayHeight, height=int(self.displayHeight/self.aspectRatio/2), bins=256)

            _, imgBinary = cv.threshold(imageBW, self.threshold, 255, cv.THRESH_BINARY)
            
            imageDisplay = cv.resize(imageBW2, (self.displayHeight,int(self.displayHeight/self.aspectRatio)), interpolation=cv.INTER_AREA)
            imgBinaryDisplay = cv.resize(imgBinary, (self.displayHeight,int(self.displayHeight/self.aspectRatio)), interpolation=cv.INTER_AREA   )
            histConcat = np.concatenate((histoBW,histoBW2),axis=0)
            cv.putText(histConcat, f'focus {int(focus)}', (10,30), cv.FONT_HERSHEY_SIMPLEX,1, (0), 2)
            edgeConcat = np.concatenate((histConcat,imgBinaryDisplay),axis=1)
            
            cnts,_ = cv.findContours(imgBinary.copy(),cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)

            # loop over the contours
            for c in cnts:
                epsilon = self.sensorParameters['epsilonPercentage']*cv.arcLength(c,True)
                c = cv.approxPolyDP(c,epsilon,True)
                M = cv.moments(c)

                
                if M['m00'] < self.minimumArea or M['m00'] > self.maximumArea:
                    continue
                
                
                ret = cv.matchShapes(c,contTemplate,1,0.0)
                # print(f"M['m00'] {M['m00']} {ret}")
                if ret < self.sensorParameters['matchingThreshold']:
                    try:
                        cX,cY = (M["m10"] / M["m00"], M["m01"] / M["m00"])
                        centroidSet[(int(cX//minimumX*minimumX),int(cY//minimumY*minimumY))] = (time.time(),c)
                    except:
                        pass

            keyToDelete = [k for k,(t,c) in centroidSet.items() if time.time()-t>self.shapeTimeout]
            for k in keyToDelete: del centroidSet[k]

            cXarray = [cX for (cX,cY),_ in centroidSet.items()]
            cXarray = np.sort(cXarray)
            cXdists = [cXarray[i+1]-cXarray[i] for i in range(len(cXarray)-1)]
            self.cXdists = [d for d in cXdists if d>minimumX]
            cYarray = [cY for (cX,cY),_ in centroidSet.items()]
            cYarray = np.sort(cYarray)
            cYdists = [cYarray[i+1]-cYarray[i] for i in range(len(cYarray)-1)]
            self.cYdists = [d for d in cYdists if d>minimumY]

            if tuple([len(self.cXdists),len(self.cYdists)])==self.sensorParameters['pads']:
                self.computePixel2mmConstants(interpadDistance=self.sensorParameters['interpadDistance'])
            
            for (cX,cY),(t,cont) in centroidSet.items():
                cv.drawContours(imageR, [cont], 0, (0, 0, 255), 10)
                # cv.putText(imageR, f'{M["m00"]}', (cX, cY), cv.FONT_HERSHEY_SIMPLEX,3, (255, 255, 255), 10)
            
            if (time.time()-timerToClearCenters)>self.shapeTimeout:
                    self.centerQueque.clear()

            try:
                maxX = np.max([np.max([cc[0][0] for cc in c]) for p,(t,c) in centroidSet.items()])
                maxY = np.max([np.max([cc[0][1] for cc in c]) for p,(t,c) in centroidSet.items()])
                minX = np.min([np.min([cc[0][0] for cc in c]) for p,(t,c) in centroidSet.items()])
                minY = np.min([np.min([cc[0][1] for cc in c]) for p,(t,c) in centroidSet.items()])

                if abs((maxX-minX) - self.sensorParameters['pads'][0]*250)<100 and abs((maxY-minY) - self.sensorParameters['pads'][1]*250)<100:
                    centerCoordinates = ((maxX+minX)/2,self.microscopeImgSize[1]-(maxY+minY)/2)

                    self.logger.debug(f'{maxX}    {maxY}    {minX}    {minY}: {centerCoordinates}')
                    self.centerQueque.append(self.pixel2mm(centerCoordinates))
                    timerToClearCenters = time.time()           
                    cv.rectangle(imageR,(minX,minY),(maxX,maxY),(0,0,255),10)

            except:
                pass

            if len(self.centerQueque)>0:
                outDict['center'] = np.mean(self.centerQueque,axis=0)
                outDict['time'] = time.time()
            else:
                outDict['center'] = None
                outDict['time'] = None
            self.outqueue.append(outDict)
            # print(f'outDict {outDict}')

            imageRDisplay = cv.resize(imageR, (self.displayHeight,int(self.displayHeight/self.aspectRatio)), interpolation=cv.INTER_AREA )
            if len(self.centerQueque)>0:
                cv.putText(imageRDisplay, 'Center: ({0[0]:.2f},{0[1]:.2f})'.format(np.mean(self.centerQueque,axis=0)), (10, 30), cv.FONT_HERSHEY_SIMPLEX,1, (0, 255, 0), 2)
            edgeConcat = cv.cvtColor(edgeConcat, cv.COLOR_GRAY2BGR)
            edgeConcat = np.concatenate((imageRDisplay,edgeConcat),axis=1)
            cv.imshow('Microscope', edgeConcat)
             
            if fps._numFrames % 100 == 0 and fps._numFrames>0:
                deltat = time.time() - tpr
                self.logger.info(100./deltat)
                tpr = time.time()

            
        # stop the timer and display FPS information
        fps.stop()
        try:
            vs.stop()
        except:
            pass
        self.logger.info("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        self.logger.info("[INFO] approx. FPS: {:.2f}".format(fps.fps()))




def makeHistoImgBW(img, width=512, height=256, bins=256):
    histBW,binsH = np.histogram(img,bins,[0,256])
    hist_image = np.zeros((int(height),int(width)), np.uint8)
    binwidth=int(width/256)
    if np.max(histBW[2:-2]) == 0:
        return hist_image
    try:
        histBW = [1-(h/np.max(histBW[2:-2])) for h in histBW]
    except:
        pass
    else:
        for n,h in enumerate(histBW[:-1]):
            hist_image[:int(h*height),int(binsH[n]*binwidth):int(binsH[n+1]*binwidth)] = 255
        hist_image[:int(histBW[-1]*height),int(binsH[-1]*binwidth):] = 255

    return hist_image

def loadTemplate(sensor):
    try:
        contTemplate = np.load(sensor+'_template_np.npy')
    except:
        contTemplate = None
    if contTemplate is None:
        templateOrig = cv.imread(sensor+'_template.jpg',cv.IMREAD_COLOR)
        template = cv.cvtColor(templateOrig, cv.COLOR_BGR2GRAY)
        template = cv.GaussianBlur(template, (5, 5), 10)
        template = (255-template)
        v = np.median(template)
        # sigma = 0.15
        # lower_thresh = int(max(0, (1.0 - sigma) * v))
        # upper_thresh = int(min(255, (1.0 + sigma) * v))
        # template = cv.Canny(template,lower_thresh,upper_thresh)
        _,template = cv.threshold(template, 100, 255, cv.THRESH_BINARY)
        
        contTemplate,_ = cv.findContours(template, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        cv.drawContours(templateOrig, contTemplate, 0, (0, 255, 0), 3)
        np.save(sensor+'_template_np.npy',contTemplate)

        
        cv.imshow("template", template)
        cv.imshow("templateO", templateOrig)
        
    return contTemplate[0]


def waitForOutput(queue, timeout=10):
    waitingCounter = 0
    while waitingCounter<10:
        try:
            q = queue.popleft()
            if ('time' in q.keys() and q['time'] is not None) or 'time' not in q.keys():
                return q
        except IndexError:
            waitingCounter += 1
            # print(f"waiting for camera to start {waitingCounter}")
            time.sleep(1)
            continue
    print("Pattern not found!")

def waitForStableOutput(queue, timeout=10, tolerance=0.01, key='center'):   #TODO
    while True:
        out1 = copy(waitForOutput(queue, timeout))
        if 'time' not in out1.keys():
            return out1
        time.sleep(1)
        out2 = waitForOutput(queue, timeout)
        if 'time' not in out2.keys():
            return out2
        if out2['time'] > out1['time']:
            if max(np.abs(out1['center']-out2['center']))<tolerance:
                return out2



if __name__ == '__main__':
    m = microscope()
    m.start()
