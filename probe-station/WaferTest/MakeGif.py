import imageio
import os

directory = './img/'
runs = os.listdir(directory)

for run in runs:
    filenames = [directory+run+'/'+f for f in os.listdir(directory+run+'/') if f.endswith(".png")]
    if len(filenames) < 10:
        continue
    print("Making .gif for "+run)
    with imageio.get_writer(directory+run+'/'+run+'.gif',mode='I',duration=0.2) as writer:
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)
