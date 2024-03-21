from motion import *
from swMatrix import *

sw = swMatrix()
m = motion()

def moveRubber(x,y):
    m.moveFor('z',-5)
    m.moveFor('x',x)
    m.moveFor('y',y)
    m.moveFor('z',5)
    print(m.getPosition())

def setGND(gnd=True):
    sw.othersToGND(gnd)
    sw.select(0)
