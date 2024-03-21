import numpy as np


#voltages = np.array([0, 25, 50, 75, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250])
voltages = np.array([0, 50, 75, 100, 125, 150, 175, 200, 210, 220, 225])
#voltages = np.linspace(0,175,10)
##voltages = np.array([0, 5])

from measureALTIROC import measureALTIROC
measureALTIROC(sensorName=f'ALTIROC_w13_b1_22-2_GND_Rubber_2', voltages=voltages, imax=500, safeFraction=0.2, firstChannel=1, ground=True)

from measureSingle import measureSingle
#measureSingle(sensorName=f'W1_B1_16-1_pad1', voltages=voltages)
#measureSingle(sensorName=f'altiroc_w13_pad7_6gnd', voltages=voltages)




                
        
                
                

            

    
    
