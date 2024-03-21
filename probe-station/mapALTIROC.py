from keithley import Keithley
from swMatrix import *
import numpy as np
from time import sleep
import matplotlib.pyplot as plt # for python-style plottting, like 'ax1.plot(x,y)'
import logging

def mapALTIROC(
    sensorName='ALTIROC_test',
    firstChannel = 1,
    lastChannel = 25,
    portSwMatrix='COM18',
    portKeithley='COM4'
    ):

    k = Keithley(port=portKeithley,accuracy=1)
    sw = swMatrix(portSwMatrix)
    sw.othersToGND(False)


    hdlr = logging.FileHandler('data/%s.out'%sensorName,mode='w')
    formatter = logging.Formatter('%(message)s')
    hdlr.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(hdlr) 
    logger.setLevel(logging.INFO)

    results = dict()

    logger.info('ch\tV (V)\ti (uA)\t\terr')
    k.on()

    try:
        # sleep(5)
        for it in range(10):
            for channel in range(firstChannel,lastChannel+1):
                logger.info('Channel %d'%channel)
                sw.select(mappingAltiroc[channel-1])
                i,std = k.precisemeas(skip=1, repeat=1)
                print('%.3f'%(i), end ="\t")
                if channel%5==0:
                    print(" ")
                logger.info('%d\t%.6f\t%.6f'%(channel,i,std))
            print(' ')


    except KeyboardInterrupt:   #Avoids disconnection before rampdown
        hv.rampDown()
        return

    finally:
        sw.reset()
        del sw



if __name__ == '__main__':
   mapALTIROC()
   
