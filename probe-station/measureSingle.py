from keithley import Keithley
from caen import CAENHV
import numpy as np
from time import sleep
import matplotlib.pyplot as plt # for python-style plottting, like 'ax1.plot(x,y)'
import logging

def measureSingle(
    sensorName='standalone_test',
    maxVoltage = 300,
    imax = 200, # uA
    voltages = np.array([0, 50, 100, 150, 175, 185, 190, 200, 205, 210, 215, 220]),
    safeFraction = 0.1,
    portHV='COM9',
    portKeithley='COM4'
    ):

    k = Keithley(port=portKeithley,accuracy=1)
    hv = CAENHV(port=portHV, imax=imax, vsec=50, channel=2)

    #voltages = np.linspace(0,maxVoltage,maxVoltage//voltageStep+1)
    voltagesLocal = np.concatenate((voltages,voltages[::-1][1:]))

    # logging.basicConfig(filename='data/%s.out'%sensorName, level=logging.INFO, filemode='w', format='%(message)s')
    hdlr = logging.FileHandler('data/%s.out'%sensorName,mode='w')
    formatter = logging.Formatter('%(message)s')
    hdlr.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(hdlr) 
    logger.setLevel(logging.INFO)

    fig = plt.figure()
    fig.set_size_inches(30/2.54,20/2.54)
    plt.subplots_adjust(hspace = 0.3)

    results = dict()

    logger.info('ch\tV (V)\ti (uA)\t\terr')
    k.on()

    try:
        # sleep(5)
        hv.setVolt(0)
        hv.on()
        results = []
        vMaxLocal = maxVoltage*1.1
        for v in voltagesLocal:
            if v > vMaxLocal:
                print('Skipping...%.2f'%v)
                continue
            hv.setVolt(v)
            sleep(1)
            #print(hv.readCurrent())
            for i in range(300):
                if i==299:
                    exit()
                if i>100 and i%100==0:
                    print('Waiting for CAEN...')
                if hv.readStatus() == b'#CMD:OK,VAL:00001;\r\n':
                    break
                sleep(0.1)
            iCaen = hv.readCurrent()
            print('V: %d, i_hv: %.2f'%(hv.readVolt(),iCaen))
            if iCaen > imax*safeFraction:
                print('Overcurrent protection!')
                vMaxLocal = v
            i,std = k.precisemeas(skip=5)
            results.append([v,i,std])
            print('%.2f V\t%.3f +- %.3f uA'%(v,i,std))
            logger.info('%.2f\t%.6f\t%.6f'%(v,i,std))

            v, i, err = np.transpose(results)
            plt.title(sensorName)
            axes = plt.gca()
            # axes.set_ylim([0.01,1])
            plt.xlabel('Voltage (V)')
            plt.ylabel('Current (uA)')
            plt.yscale("log")
            plt.grid(True)

            plt.errorbar(v, np.absolute(i), yerr=err)
            plt.savefig(  'data/IV_%s.png'%sensorName, dpi=300 )


    except KeyboardInterrupt:   #Avoids disconnection before rampdown
        hv.rampDown()
        return
