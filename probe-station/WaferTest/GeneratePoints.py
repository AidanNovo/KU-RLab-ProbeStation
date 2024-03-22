import json
    
outp = {'Pads':[]}

shift = []
zes = [0]

Flip = True
DoubleBump = False
Micross = True
if DoubleBump is True:
    pitch = 0.65
    gap = 1.8
    bandaid = -0.02
    if Micross:
        pads = 63 ## Micross Assemblies
    else:
        pads = 32 ## BNL Wafers
else:
    pitch = 1.3
    gap = 3.1
    bandaid = -2.23
    if Micross:
        pads = 31 ## Micross Assemblies
    else:
        pads = 16 ## BNL Wafers

for pad in range(1,pads):
    for z in zes:
        xx = 0.15
        if Micross:
            if pad > int(pads/2):
                yy = ((pad-1)+gap)*pitch + 0.05 + bandaid
            else: yy = (pad-1)*pitch + 0.05
        else:
            yy = (pad-1)*pitch + 0.05
        if Flip:
            xx = -1.0*xx
            yy = -1.0*yy
        zz = z
        outp['Pads'].append({'Pad':pad, 'PositionX':f'{xx:.3f}', 'PositionY':f'{yy:.3f}', 'ShiftZ':f'{zz:.3f}'})
    for s in shift:
        xx = 0.15 + s
        if Micross:
            if pad > int(pads/2):
                yy = ((pad-1)+gap)*pitch + s + 0.05 + bandaid
            else:
                yy = (pad-1)*pitch + s + 0.05
        else:
            yy = (pad-1)*pitch + s + 0.05
        if Flip:
            xx = -1.0*xx
            yy = -1.0*yy
        zz = z
        outp['Pads'].append({'Pad':pad, 'PositionX':f'{xx:.3f}', 'PositionY':f'{yy:.3f}', 'ShiftZ':f'{zz:.3f}'})
        
print(outp)
if DoubleBump is True:
    if Micross:
        if Flip:
            with open('PointsMicrossFlip2.json', 'w') as outfile:
                json.dump(outp, outfile, indent=4)
        else:
            with open('PointsMicross2.json', 'w') as outfile:
                json.dump(outp, outfile, indent=4)
    else:
        with open('Points2.json', 'w') as outfile:
            json.dump(outp, outfile, indent=4)
else:
    if Micross:
        if Flip:
            with open('PointsMicrossFlip.json', 'w') as outfile:
                json.dump(outp, outfile, indent=4)
        else:
            with open('PointsMicross.json', 'w') as outfile:
                json.dump(outp, outfile, indent=4)
    else:
        with open('Points.json', 'w') as outfile:
            json.dump(outp, outfile, indent=4)

 
