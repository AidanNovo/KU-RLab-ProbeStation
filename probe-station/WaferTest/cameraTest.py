import cv2
import time
import motion
import os

def rescale_frame(frame, factor=0.1):
    width = int(frame.shape[1] * factor)
    height = int(frame.shape[0] * factor)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

cam = cv2.VideoCapture(1)
time.sleep(3)
cam.set(3, 2592)  #width
cam.set(4, 1944)  #height
##cam.set(21,0.5)     #auto exposire

time.sleep(3)

motors = motion.motion(port='COM4', emulate=False)
motors.setHome()

x_range = 36
y_range = 41

assembly = 'Bond1_MSp_BNL_Micross'
if not os.path.isdir('scanImg/'+assembly+'/'):
    os.makedirs('scanImg/'+assembly+'/')

positions = []
for x in range(0,x_range,5):
    for y in range(0,y_range,5):
        positions.append([-x,-y,0])
positions.append([0,0,0])

for coords in positions:
    print(coords)
    print("Position: ",motors.moveTo(coordinates=coords))
    time.sleep(5)
    frame = None
    while frame is None:
        ret, frame = cam.read()
##    cv2.imshow('frame', rescale_frame(frame,0.1))
    cv2.imwrite(f"scanImg/{assembly}/scan_{coords[0]}_{coords[1]}_{coords[2]}.png", frame)
    time.sleep(5)

motors.goHome()
cam.release()
cv2.destroyAllWindows()
