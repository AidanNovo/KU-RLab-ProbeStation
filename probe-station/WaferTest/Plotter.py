import pandas as pd
from pandas.io.json import json_normalize
import json
import matplotlib.pyplot as plt
import matplotlib
import os
import time
import numpy as np
import heapq
import math

path = './'
files = [path+f for f in os.listdir(path) if f.endswith("_resistance.json")]
markers = ['o','x',"*","D","v","<",">","^",'o','x',"*","D","v","<",">","^"]
colors = ['b','g','r','k','c','m','y','b','g','r','k','c','m','y']
plots= []
missingBumpResistance = 30
comparison_files = ["5"]
matplotlib.rc('font', size=15)

def MultiPlot():
    i=0
    for file in files:
        with open(file) as f:
            print(file)
            d=json.load(f)
        df=json_normalize(d,'Values')
        #df = df[df.Resistance > 0]
        #df = df[df.Resistance > 0.01*df.ResistanceError]
        #df = df[df.Resistance < 1e5]
        df = df[df.Pad < 99]
        if i == 0:
            ax = df.plot(x='Pad',y='PositionZ',kind="scatter",figsize=(15,10),title=file,grid=True,marker=markers[i],color=colors[i],label=str(file))
        else:
            df.plot(x='Pad',y='PositionZ',kind="scatter",figsize=(15,10),title=file,grid=True,ax=ax,marker=markers[i],color=colors[i],label=str(file))
        i+=1
    plt.show()

def Histogram():
    for file in files:
        with open(file) as f:
            d=json.load(f)
        df=json_normalize(d,'Values')
        #df = df[df.Pad < 99]
        df=df.loc[df.groupby('Pad').Resistance.idxmin()]
        df.hist(column=['Resistance'])
    plt.title(file)
    plt.xlabel("Resistance")
    plt.ylabel("Events")
    plt.show()

def SinglePlot():
    for file in files:
        with open(file) as f:
            d=json.load(f)
        df=json_normalize(d,'Values')
        df = df[df.Pad < 99]
        df.plot(x='Pad',y='PositionZ',kind="scatter",figsize=(15,10),title=file,grid=True,marker='o')
    plt.show()

def MinSinglePlot():
    for file in files:
        with open(file) as f:
            d=json.load(f)
        df=json_normalize(d,'Values')
        df = df[df.Resistance > 0]
        df = df[df.Resistance > 0.01*df.ResistanceError]
        df = df[df.Pad < 99]
        df=df.loc[df.groupby('Pad').Resistance.idxmin()]
        df.plot(x='Pad',y='Resistance',yerr='ResistanceError',kind="scatter",figsize=(12,8),title=file,grid=True,marker='o',ylim=(0,600))
    plt.show()

def MinMultiPlot():
    i=0
    ##labels = ["100% Yield","Low Yield"]
    for file in files:
        with open(file) as f:
            print(file)
            d=json.load(f)
        if "INVALID" in str(d['Notes']):
              continue
        df=json_normalize(d,'Values')
        df = df[df.Resistance > 0]
        df = df[df.ResistanceError < 0.1*df.Resistance]
        df = df[df.Pad < 99]
        df=df.loc[df.groupby('Pad').Resistance.idxmin()]
        if i == 0:
            ax = df.plot(x='Pad',y='Resistance',yerr='ResistanceError',kind="scatter",figsize=(15,10),title='',grid=True,marker=markers[i],color=colors[i],label=str(file).replace('_resistance.json','').replace('./',''))
            ##ax = df.plot(x='Pad',y='Resistance',yerr='ResistanceError',kind="scatter",figsize=(15,10),title='',grid=True,marker=markers[i],color=colors[i],s=50,label=labels[0
        else:
            df.plot(x='Pad',y='Resistance',yerr='ResistanceError',kind="scatter",figsize=(15,10),title='',grid=True,ax=ax,marker=markers[i],color=colors[i],label=str(file).replace('_resistance.json','').replace('./',''))
            ##df.plot(x='Pad',y='Resistance',yerr='ResistanceError',kind="scatter",figsize=(15,10),title='',grid=True,ax=ax,marker=markers[i],color=colors[i],s=50,label=labels[1])
        i+=1
    #plt.axvline(15.5, color = 'k', linestyle='--')
    #ax.get_legend().remove()
    plt.xlabel('Wire Bond Pad Pair')
    plt.ylabel('Resistance [Ohms]')
    plt.show()

def ComparePlot():
    df = pd.DataFrame()
    compare_df = pd.DataFrame()
    for file in files:
        with open(file) as f:
            d=json.load(f)
        if str(d['Notes']) == "INVALID":
              continue
        current_df=json_normalize(d,'Values')
        current_df = current_df[current_df.Resistance > 0]
        current_df = current_df[current_df.ResistanceError < 0.1*current_df.Resistance]
        current_df = current_df[current_df.Pad < 99]
        current_df=current_df.loc[current_df.groupby('Pad').Resistance.idxmin()]
        for compare_index in comparison_files:
            if str("Run"+str(comparison_files)) in str(file):
                compare_df.append(current_df)
        else:
            df.append(current_df)
    ax = df.plot(x='Pad',y='Resistance',yerr='ResistanceError',kind="scatter",figsize=(15,10),title='',grid=True,marker=markers[0],color=colors[0],label="Previous Measurements")
    compare_df.plot(x='Pad',y='Resistance',yerr='ResistanceError',kind="scatter",figsize=(15,10),title='',grid=True,ax=ax,marker=markers[1],color=colors[1],label="New Measurements")
    #plt.axvline(15.5, color = 'k', linestyle='--')
    plt.xlabel('Wire Bond Pad Pair')
    plt.ylabel('Resistance [Ohms]')
    plt.show()

def minSTD(values):
    min_val = min(values)
    N = len(values)
    sum_val = 0
    for val in values:
        sum_val += ((val - min_val)*(val-min_val))
    return math.sqrt((1./(N-1))*sum_val)

def MinAllSinglePlot():
    fig, axes = plt.subplots(1,1, figsize=(20,10))
    title = files[0].replace('_resistance.json','')
    axes.set_xlabel('Pad')
    axes.set_ylabel('Resistance (Ohm)')
    axes.grid()
    axes.set_title(title)

    with open(files[0]) as f:
        d=json.load(f)
        df=json_normalize(d,'Values')
    for i in range(1,len(files)):
        with open(files[i]) as f:
            d=json.load(f)
            df_add = json_normalize(d,'Values')
            df = df[df.ResistanceError < 0.1*df.Resistance]
            df = df.loc[df.groupby('Pad').Resistance.idxmin()]
            df = df.append(df_add,ignore_index=True,sort=True)
    df = df[df.Resistance > 0]
    df = df[df.Pad < 99]
    NPads = df.Pad.max()
    ResistanceSTD = []
    if len(files) is 1:
        df['ResistanceSTD'] =  df.ResistanceError
        df=df.loc[df.groupby('Pad').Resistance.idxmin()]
    else:
        for pad in range(1,NPads+1):
            resistances = df[df['Pad'] == pad].Resistance.to_list()
            if len(resistances) == 0:
                continue
            ResistanceSTD.append(minSTD(resistances))
        df=df.loc[df.groupby('Pad').Resistance.idxmin()]
        df['ResistanceSTD'] = ResistanceSTD

    ##df.plot(x='Pad',y='Resistance',kind="scatter",figsize=(15,10),title=files[0],grid=True,marker=markers[i],color=colors[i])
    axes.plot(df.Pad,df.Resistance,label=title,ls='',marker='p')
    minRes = np.min(list(df.Resistance))
    maxRes = np.max(list(df.Resistance))
    maxAxes = (int)(maxRes/missingBumpResistance)*1.2
    major_ticks = np.arange(0, maxAxes*missingBumpResistance, missingBumpResistance)

    _=axes.set_yticks(major_ticks)
    axes.set_ylim(-0.5*missingBumpResistance,maxAxes*missingBumpResistance)

    ax_right = axes.twinx()
    ax_right.set_ylim(-0.5,maxAxes)
    ax_right.set_ylabel("Missing bumps")
    major_ticks_right = np.arange(0, maxAxes, 1)
    _=ax_right.set_yticks(major_ticks_right)
    plt.draw()
    plt.savefig(title+".pdf")
    #plt.show()

def MinAllAssembliesPlot():
    directory = "../../SavedMeasurements"
    directories = os.listdir(directory)
    directories = [i for i in directories if "Micross" in i]
    
    for assembly in directories:
        files = os.listdir(directory+"/"+assembly)
        files = [i for i in files if i.endswith("_resistance.json")]
        files = [i for i in files if not "_A_" in i or not "_B_" in i]
        if len(files) < 1:
            continue
        fig, axes = plt.subplots(1,1, figsize=(20,10))
        title = files[0].replace('_resistance.json','')
        axes.set_xlabel('Pad')
        axes.set_ylabel('Resistance (Ohm)')
        axes.grid()
        axes.set_title(title)

        with open(directory+"/"+assembly+"/"+files[0]) as f:
            d=json.load(f)
            df=json_normalize(d,'Values')
        for i in range(1,len(files)):
            with open(directory+"/"+assembly+"/"+files[i]) as f:
                d=json.load(f)
                df_add = json_normalize(d,'Values')
                df = df[df.ResistanceError < 0.1*df.Resistance]
                df = df.loc[df.groupby('Pad').Resistance.idxmin()]
                df = df.append(df_add,ignore_index=True,sort=True)
        df = df[df.Resistance > 0]
        balcony_DF = df[df.Pad > 99]
        if len(balcony_DF.Resistance.to_list()) > 0:
            balcony_DF = df[df.Pad > 99]
            balcony_DF = balcony_DF[df.Pad < 190]
            balcony_A = balcony_DF.Resistance.to_list()[0]
            balcony_DF = df[df.Pad > 190]
            balcony_B = balcony_DF.Resistance.to_list()[0]
        else:
            print("Need balcony for: "+assembly)
            balcony_A = -1
            balcony_B = -1
        df = df[df.Pad < 99]
        NPads = df.Pad.max()
##        ResistanceSTD = []
##        if len(files) is 1:
##            df['ResistanceSTD'] =  df.ResistanceError
##            df=df.loc[df.groupby('Pad').Resistance.idxmin()]
##        else:
##            for pad in range(1,NPads+1):
##                resistances = df[df['Pad'] == pad].Resistance.to_list()
##                if len(resistances) == 0:
##                    continue
##                ResistanceSTD.append(minSTD(resistances))
##            df=df.loc[df.groupby('Pad').Resistance.idxmin()]
##            df['ResistanceSTD'] = ResistanceSTD

        df=df.loc[df.groupby('Pad').Resistance.idxmin()]
        ##df.plot(x='Pad',y='Resistance',kind="scatter",figsize=(15,10),title=files[0],grid=True,marker=markers[i],color=colors[i])
        axes.plot(df.Pad,df.Resistance,label=title,ls='',marker='p')
        minRes = np.min(list(df.Resistance))
        maxRes = np.max(list(df.Resistance))
        maxAxes = (int)(maxRes/missingBumpResistance)*1.2
        major_ticks = np.arange(0, maxAxes*missingBumpResistance, missingBumpResistance)

        _=axes.set_yticks(major_ticks)
        axes.set_ylim(-0.5*missingBumpResistance,maxAxes*missingBumpResistance)

        ax_right = axes.twinx()
        ax_right.set_ylim(-0.5,maxAxes)
        ax_right.set_ylabel("Missing bumps")
        major_ticks_right = np.arange(0, maxAxes, 1)
        _=ax_right.set_yticks(major_ticks_right) 
        axes.text(0.1,0.9,f"Balcony A: {balcony_A:.0f} Ohms  Balcony B: {balcony_B:.0f} Ohms",transform=axes.transAxes,fontsize=18)
        plt.draw()
        plt.savefig(title+".pdf")
        plt.close()
        #plt.show()

#ComparePlot()
#MinSinglePlot()
MinMultiPlot()
#SinglePlot()
#MultiPlot()
#MinAllSinglePlot()
#MinAllAssembliesPlot()
#Histogram()
