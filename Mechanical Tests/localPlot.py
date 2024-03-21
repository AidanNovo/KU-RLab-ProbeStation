#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

inputDir= '/home/nminafra/Downloads/03_18_2021/'
files = os.listdir(inputDir)
files.sort(key = lambda s: int(s[-6:-4]) if s[-6:-4].isdigit() else int(s[-5:-4]))

dfs = {}

for file in files:
    with open(inputDir + file) as f:
        data = {}
        data['Strain'] = []
        data['Force'] = []
        data['Time'] = []
        for row in f:
            if row[0].isdigit():
                splitted = row.split('\t')
                if len(splitted) != 3:
                    print("Error at: ", row)
                else:
                    data['Strain'].append(float(splitted[0]))
                    data['Force'].append(float(splitted[1]))
                    data['Time'].append(float(splitted[2]))
    dfs[file] = pd.DataFrame.from_dict(data)

print(dfs.keys())
dfsFiltered = {}
listOfSelectedFiles = ['03_18_2021_3.dat', '03_18_2021_6.dat','03_18_2021_7.dat','03_18_2021_8.dat']
for f in listOfSelectedFiles:
    dfsFiltered[f] = dfs[f]
# dfsFiltered = dfs # Uncomment to plot all files

numOfRuns = len(dfsFiltered.items())
fig, axes = plt.subplots(2,numOfRuns//2)
axes = axes.flatten()

plotIndex = 0
for f,df in dfsFiltered.items():
    sc = axes[plotIndex].scatter(df.Strain, df.Force, c=df.Time, s=2)
    axes[plotIndex].set_title(f)
    axes[plotIndex].set_xlabel('Strain (mm)')
    axes[plotIndex].set_ylabel('Force (N)')

    plotIndex += 1

fig.subplots_adjust(bottom=0.2)
cbar_ax = fig.add_axes([0.15, 0.05, 0.5, 0.05])
fig.colorbar(sc, cax=cbar_ax, label="t", orientation='horizontal')

plt.show()




