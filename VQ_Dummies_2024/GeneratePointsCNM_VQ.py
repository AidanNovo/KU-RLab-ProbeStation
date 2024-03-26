import json
    
outp = {'Pads':[]}

shift = []
zes = [0]

Assembly = True

pitch = 0.858
gap = 0.
x_offset = -0.15
y_offset = 3.03
pads = 21 ## Column Pairs
    
for pad in range(1,pads):
    for z in zes:
        xx = x_offset
        yy = (pad-1)*pitch+y_offset
        zz = z
        outp['Pads'].append({'Pad':pad, 'PositionX':f'{xx:.3f}', 'PositionY':f'{yy:.3f}', 'ShiftZ':f'{zz:.3f}'})

print(outp)
with open('PointsCNM_VQ.json', 'w') as outfile:
    json.dump(outp, outfile, indent=4)
 
