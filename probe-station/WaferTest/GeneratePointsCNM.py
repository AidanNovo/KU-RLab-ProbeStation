import json
    
outp = {'Pads':[]}

shift = []
zes = [0]

Assembly = True
DoubleBump = True
CNM = True
if DoubleBump is True:
    pitch = 0.65
    gap = 1.8
    bandaid = -0.02
    if DoubleBump:
        pads = 63 ## Assemblies
    else:
        pads = 32 ## Wafers
else:
    pitch = 1.25
    gap = 3.1
    bandaid = -2.23
    pads = 31 ## Assemblies
    
for pad in range(1,pads):
    for z in zes:
        xx = 0.1
        if pad > int(pads/2)-1:
            yy = ((pad-1)+gap)*pitch + bandaid
        else: yy = (pad-1)*pitch
        zz = z
        outp['Pads'].append({'Pad':pad, 'PositionX':f'{xx:.3f}', 'PositionY':f'{yy:.3f}', 'ShiftZ':f'{zz:.3f}'})

print(outp)
if DoubleBump is True:
    with open('PointsCNM2.json', 'w') as outfile:
        json.dump(outp, outfile, indent=4)
else:
    with open('PointsCNM.json', 'w') as outfile:
        json.dump(outp, outfile, indent=4)
 
