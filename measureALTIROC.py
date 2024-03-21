from keithley import Keithley
from caen import CAENHV
from swMatrix import *
import numpy as np
from time import sleep
import matplotlib.pyplot as plt # for python-style plottting, like 'ax1.plot(x,y)'
import logging

def measureALTIROC(
    sensorName='ALTIROC_test',
    maxVoltage = 300,
    imax = 100, # uA
    firstChannel = 1,
    lastChannel = 25,
    voltages = np.array([0, 50, 100, 150, 175, 185, 190, 200, 205, 210, 215, 220]),
    safeFraction = 0.1,
    portSwMatrix='COM18',
    portHV='COM9',
    portKeithley='COM4',
    ground=False
    ):

    k = Keithley(port=portKeithley,accuracy=1)
    sw = swMatrix(portSwMatrix)
    sw.othersToGND(ground)
    sw.light(False)
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

    np.random.seed(1)
    colors = np.random.rand(lastChannel,3)
    fig = plt.figure()
    fig.set_size_inches(30/2.54,20/2.54)
    plt.subplots_adjust(hspace = 0.3)

    results = dict()

    logger.info('ch\tV (V)\ti (uA)\t\terr')
    k.on()

    try:
        # sleep(5)
        for channel in range(firstChannel,lastChannel+1):
            logger.info('Channel %d'%channel)
            hv.setVolt(0)
            sw.select(mappingAltiroc[channel-1])
            hv.on()
            results[channel] = []
            vMaxLocal = maxVoltage*1.1
            for v in voltagesLocal:
                if v > vMaxLocal:
                    print('Skipping...%.2f'%v)
                    continue
                hv.setVolt(v)
                sleep(1)
                #print(hv.readCurrent())
                i = 0
                while i<100:
                    if hv.readStatus() == b'#CMD:OK,VAL:00001;\r\n':
                        break
                    sleep(0.5)
                    i += 1
                else:
                    hv.initialize()
                    vMaxLocal = v*0.99
                    print(f'Reinit CAEN')
                
                iCaen = hv.readCurrent()
                actualV = hv.readVolt()
                print('V: %d, i_hv: %.2f'%(actualV,iCaen))
                if iCaen > imax*safeFraction:
                    print('Overcurrent protection!')
                    vMaxLocal = v
                i,std = k.precisemeas(skip=5)
                if i > 5:
                    print('Overcurrent protection Keithley!')
                    vMaxLocal = v
                results[channel].append([actualV,i,std])
                print('ch %d: %.2f V\t%.4f +- %.4f uA'%(channel,actualV,i,std))
                logger.info('%d\t%.2f\t%.6f\t%.6f'%(channel,actualV,i,std))

            actualV, i, err = np.transpose(results[channel])
            splitEvery = lastChannel//4
            if lastChannel%4!=0:
                splitEvery += 1
            if (channel-1)%splitEvery==0 or channel==firstChannel:
                plt.subplot(2,2,(channel-1)//splitEvery+1)
                plt.title('channels %d to %d'%(channel,channel+splitEvery-1))
                axes = plt.gca()
                # axes.set_ylim([0.01,1])
                plt.xlabel('Voltage (V)')
                plt.ylabel('Current (uA)')
                plt.yscale("log")
                plt.grid(True)

            plt.errorbar(actualV, np.absolute(i), yerr=err, color=colors[channel-1], label='ch %d'%channel)
            plt.legend(loc='lower right')
            plt.savefig(  'data/IV_%s.png'%sensorName, dpi=300 )


    except KeyboardInterrupt:   #Avoids disconnection before rampdown
        hv.rampDown()
        return

    finally:
        sw.light(True)
        sw.reset()
        del sw
