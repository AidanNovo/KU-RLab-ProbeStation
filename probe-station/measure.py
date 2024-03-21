from keithley import Keithley
from caen import CAENHV
from swMatrix import swMatrix
import numpy as np
from time import sleep
import matplotlib.pyplot as plt # for python-style plottting, like 'ax1.plot(x,y)'

import argparse

parser = argparse.ArgumentParser(description='Run info.')
parser.add_argument('--sensor', metavar='sensorType', type=str, default = 'TEST', help='Sensor model',required=True)
parser.add_argument('--Vmax', metavar='Vmax', type=int, default=300, help='Maximum voltage applied to the sensor',required=False)
parser.add_argument('--Imax',metavar='Imax', type=int,default=100, help='Current compliance level (default 100uA)',required=False)
parser.add_argument('--step',metavar='step', type=int,default=10,help='Voltage steps for the IV scan',required=False)
parser.add_argument('--Fsafe',metavar='Fsafe', type=float, default= 0.2, help='Fraction of the current to trigger the compliance',required=False)
parser.add_argument('--Fch',metavar='Fch', type=int, default= 1, help='First channel to analyze',required=False)
parser.add_argument('--Lch',metavar='Lch', type=int, default= 32, help='Last channel to analyze',required=False)
args = parser.parse_args()

sensor = str(args.sensor)
maxVoltage = int(args.Vmax)
voltageStep = int(args.step)
imax = float(args.Imax)  #uA
safeFraction = float(args.Fsafe)
firstChannel = int(args.Fch)
lastChannel = int(args.Lch)

k = Keithley(port='COM6',accuracy=1)
sw = swMatrix('COM10')
hv = CAENHV(port='COM9', imax=imax, vsec=50, channel=2)


#voltages = np.linspace(0,maxVoltage,maxVoltage//voltageStep+1)
#voltages = np.concatenate((voltages, np.linspace(maxVoltage-voltageStep,0,maxVoltage//voltageStep)))

# voltages = np.array([0,20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 115, 120, 130, 140, 150, 155, 160, 165, 170, 175, 180, 185, 190])


voltages = np.array([0, 50, 100, 150, 175, 185, 190, 200, 205, 210, 215, 220])
firstChannel = 1


voltages = np.concatenate((voltages,voltages[::-1][1:]))

import logging
logging.basicConfig(filename='data/%s.out'%sensor, level=logging.INFO, filemode='w', format='%(message)s')

np.random.seed(1)
colors = np.random.rand(lastChannel,3)
fig = plt.figure()
fig.set_size_inches(30/2.54,20/2.54)
plt.subplots_adjust(hspace = 0.3)

results = dict()

logging.info('ch\tV (V)\ti (uA)\t\terr')
k.on()


try:
    for channel in range(firstChannel,lastChannel+1):
        logging.info('Channel %d'%channel)
        hv.setVolt(0)
        sw.select(channel)
        hv.on()
        results[channel] = []
        vMaxLocal = maxVoltage*1.1
        for v in voltages:
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
                vMaxLocal = v
            i,std = k.precisemeas(skip=5)
            results[channel].append([v,i,std])
            print('ch %d: %.2f V\t%.3f +- %.3f uA'%(channel,v,i,std))
            logging.info('%d\t%.2f\t%.6f\t%.6f'%(channel,v,i,std))

        v, i, err = np.transpose(results[channel])
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

        if channel >1:
            plt.errorbar(v, np.absolute(i), yerr=err, color=colors[channel-1], label='ch %d'%channel)
            plt.legend(loc='lower right')
            plt.savefig(  'data/IV_%s.png'%sensor, dpi=300 )

except KeyboardInterrupt:   #Avoids disconnection before rampdown
    hv.rampDown()
    exit()
