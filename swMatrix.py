from serial import Serial

mappingAltiroc = [30,29,28,27,26,
                  22,21,20,19,18,
                  9,7,12,6,15,
                  2,11,5,14,8,
                  10,4,13,7,16]

mappingAltirocBlack = [24,23,22,21,20,
                       32,31,30,29,28,
                       19,18,17,27,26,
                       3,4,5,6,7,
                       11,12,13,14,15]

class swMatrix:
    """Class to control the switching matrix"""

    def __init__(self, port='COM18'):
        answ = ''
        self.serial = Serial(port, timeout=2)
        while 'R' not in answ:
          print(answ)
          self.serial.close()
          self.serial = Serial(port, timeout=2)
          answ = str(self.reset(), 'ascii')
        print('Switching Matrix Initialized')


    def __del__(self):
        self.reset()
        self.serial.close()
        del self.serial

    def select(self, channel):
        self.serial.write(b'TEST %d\n'%channel)
        return self.serial.readline()

    def light(self, on):
        if on:
          value = 1
        else:
          value = 0
        self.serial.write(b'LIGHT %d\n'%value)
        print(f'LIGHT set to {value}')
        return self.serial.readline()

    def othersToGND(self, gnd):
        gndInt = 0
        if gnd:
          gndInt = 1
        self.serial.write(b'GND %d\n'%gndInt)
        print(f'GND set to {gnd}')
        return self.serial.readline()

    def reset(self):
        self.serial.write(b'RESET\n')
        return self.serial.readline()

if __name__ == '__main__':
   import time
   s = swMatrix('COM10')
   for i in mappingAltirocBlack:
       s.select(i)
       time.sleep(3)
