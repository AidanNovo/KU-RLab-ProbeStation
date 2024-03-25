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

def FixResistances():
    for file in files:
        with open(file) as f:
            d=json.load(f)
        new_dict = d
        values_dict = new_dict['Values']
        for value in values_dict:
            #print(value['Pad'])
            negitive_value = value['Pad']*-1
            #flip double
            new_value = negitive_value + 63
            #flip single
            #new_value = negitive_value + 33
            #print(new_value)
            value['Pad'] = new_value
        try:
            to_unicode = unicode
        except NameError:
            to_unicode = str
        filename = "Asensor"+"_Run"+"_"+"resistance_fixed.json"
        with open(filename,'a',encoding='utf8') as f:
           dump = json.dumps(new_dict,indent=4,sort_keys=True,separators=(',',": "),ensure_ascii=False)
           f.write(to_unicode(dump))
        print("Writing Resitance for run "+" of sensor: "+" to file: "+filename)

    
FixResistances()
