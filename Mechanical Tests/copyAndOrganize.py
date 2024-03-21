#!/usr/bin/python3

import os
import shutil

def order(s):
    if s[-2:].isdigit():
        return int(s[-2:])
    elif s[-1:].isdigit():
        return int(s[-1:])
    else:
        return 0


inputDir = '/home/nminafra/Downloads/03_16_2021 Sensor Shear Tests/'
outputNames = '/home/nminafra/Downloads/03_16_2021/03_16_2021_'

os.makedirs(outputNames[:outputNames.rindex('/')])

dirs = os.walk(inputDir)
testNames = [d for d in list(dirs)[0][1]]
testNames.sort(key = order)

testNames = [inputDir + d + '/data.dat' for d in testNames]

for i,name in enumerate(testNames):
    outname = outputNames + str(i) + '.dat'
    try:
        shutil.copy(name, outname)
    except:
        print("Copy of ", name, " failed")

