import json
    
outp = {'Pads':[]}

shift = []
zes = [0]

Short = False
DoubleBump = False
if DoubleBump is True:
    pitch = 3
    gap = 4
    bandaid = -11
    if Short:
        pads = 31
    else:
        pads = 33

else:
    pitch = 3
    gap = 4
    bandaid = -11
    pads = 32 

for pad in range(1,pads):
    for z in zes:
        xx = -1.5
        if pad > int(pads/2):
            yy = ((pad-1)+gap)*pitch + 0.5 + bandaid
        else: yy = (pad-1)*pitch + 0.5
        zz = z
        if DoubleBump and not Short:
            if pad > (int(pads/2)):
                outp['Pads'].append({'Pad':(-1+pad)*2, 'PositionX':xx, 'PositionY':yy, 'ShiftZ':zz})
            else:
                outp['Pads'].append({'Pad':-1+(pad*2), 'PositionX':xx, 'PositionY':yy, 'ShiftZ':zz})
        elif DoubleBump and Short:
            if pad > (int(pads/2)):
                outp['Pads'].append({'Pad':1+(pad*2), 'PositionX':xx, 'PositionY':yy, 'ShiftZ':zz})
            else:
                outp['Pads'].append({'Pad':pad*2, 'PositionX':xx, 'PositionY':yy, 'ShiftZ':zz})
        else:
            outp['Pads'].append({'Pad':pad, 'PositionX':xx, 'PositionY':yy, 'ShiftZ':zz})
    for s in shift:
        xx = 1.5 + s
        if pad > int(pads/2):
            yy = ((pad-1)+gap)*pitch + s + 0.5 + bandaid
        else:
            yy = (pad-1)*pitch + s + 0.5
        zz = z
        if DoubleBump and not Short:
            if pad > (int(pads/2)):
                outp['Pads'].append({'Pad':(-1+pad)*2, 'PositionX':xx, 'PositionY':yy, 'ShiftZ':zz})
            else:
                outp['Pads'].append({'Pad':-1+(pad*2), 'PositionX':xx, 'PositionY':yy, 'ShiftZ':zz})
        elif DoubleBump and Short:
            if pad > (int(pads/2)):
                outp['Pads'].append({'Pad':1+(pad*2), 'PositionX':xx, 'PositionY':yy, 'ShiftZ':zz})
            else:
                outp['Pads'].append({'Pad':pad*2, 'PositionX':xx, 'PositionY':yy, 'ShiftZ':zz})
        else:
            outp['Pads'].append({'Pad':pad, 'PositionX':xx, 'PositionY':yy, 'ShiftZ':zz})
        
print(outp)
if DoubleBump is True:
    if Short:
        with open('PointsPCBShort2.json', 'w') as outfile:
            json.dump(outp, outfile, indent=4)
    else:
        with open('PointsPCBNONShort2.json', 'w') as outfile:
            json.dump(outp, outfile, indent=4)
else:
    with open('PointsPCB.json', 'w') as outfile:
        json.dump(outp, outfile, indent=4)

 
