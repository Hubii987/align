#Jenkes import
from graphene_lab_gui.drivers.ESP8266DRV8825 import ESP8266DRV8825
# from qubib.adapters.LocalSerial import LocalSerial
from qubib.adapters.NetworkSocket import NetworkSocket


import matplotlib.pyplot as plt
import numpy as np
import os
import ruamel.yaml as yaml
import time
import sys
import pyvisa
import visa
from ThorlabsPM100 import ThorlabsPM100, USBTMC

print("stufe 1")
adapter1 = NetworkSocket('10.42.0.112', port=5045) #neu: 10.42.0.112
print("starte timeout")
adapter1.timeout = 10
print("schreibe irgendwas")
adapter1.write_termination = '\n'
print("definieren den esp")
esp1 = ESP8266DRV8825(inst=adapter1)

print("blinki die blink")
#esp1.blink()
print("und los gehts")

LINUX=sys.platform=="linux"

def openpm(cfg):
    #
    # use VISA to connect to PM100D on MacOS and Windows
    # use USBTMC on linux
    #
    idVendor = cfg['powermeter']['tomo']['idVendor']
    idProduct = cfg['powermeter']['tomo']['idProduct']
    sn = cfg['powermeter']['tomo']['serial_number']
    key = True
    if key == True:
        print("es ist linux")
        usbtmc_devlist = [f for f in os.listdir('/dev/') if 'usbtmc' in f]
        instruments = [USBTMC('/dev/' + udev) for udev in usbtmc_devlist]
        sns = [i.query('*IDN?').strip().split(',')[2] for i in instruments]
        if sn in sns:
            pm = ThorlabsPM100(inst=instruments[sns.index(sn)])
            print('powermeter connected')
            pm.sense.average.count = 100
            pm.sense.correction.wavelength = 1550
            return pm
        else:
            print('Error: powermeter with right serial number not found!')
            sys.exit()
    elif key == False:
        import pyvisa
        print('es ist windows')
        eol = '\r\n'
        sn = cfg['powermeter']['tomo']['serial_number']
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource("USB0::0x1313::0x8078::" + sn + "::INSTR")
        inst.read_termination = '\n'
        inst.write_termination = '\n'
        inst.timeout = 1000
        pm = ThorlabsPM100(inst=inst)
        pm.sense.average.count = 100
        pm.sense.correction.wavelength = 1550
        return pm

with open('povm.conf', 'r') as f:
    cfg = yaml.YAML(typ='safe').load(f)

print("importiere pm")
pm = openpm(cfg)
print("richtig importiert")


#n = 200

#meas_arr = np.zeros((n,))
#steps_arr = np.linspace(0,n,n)
n = 4
for i in range(n):
    #meas_arr[i] = pm.read * 1000000
    print(pm.read * 1000000)
    time.sleep(0.5)
    esp1.move_dir_steps_div(1, 2, 2) #direction, steps, divider):
    print(pm.read * 1000000)
    time.sleep(0.5)
esp1.close()


#plt.plot(steps_arr, meas_arr)
#plt.show()