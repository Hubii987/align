#!/usr/bin/env python3
import os
import sys
import argparse
import numpy as np
import pandas as pd
import ruamel.yaml as yaml
import matplotlib.pyplot as plt
import matplotlib.pyplot as pyplot


#importiere die datein von file außerhalb
sys.path.insert(0, '/Users/hubertuslauterbacher/labdata/projects/povm/char/ppbs/waveplates')
#import waveplates
#import elliptec




parser = argparse.ArgumentParser(description='Characterize POVM experiment Y-Yt gadget.\n'
                                             'rotates motorized waveplates as defined in povm.conf\n'
                                             'uses Thorlabs PM100D powermeter, as defined in povm.conf',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-f', '--file_id', type=str, help='Name of file you wanna analyse', default="")

args = parser.parse_args()
FILE = args.file_id

GID = FILE[5:8].upper()
DIR = FILE[9:12].lower()
NUMPHASE = FILE[14:-1]
NUMPHASES = NUMPHASE[0:-2]
#print(FILE)

#uh = waveplates.Unitaries()

if os.path.exists(FILE):
    store = pd.HDFStore(FILE)

    df = store['df']
    store.close()
else:
    print("ERROR: File not found")


#we need this for the calculation of the fit-function
def hwp(phi):
    return(np.array([[np.cos(2*phi), np.sin(2*phi)],[np.sin(2*phi),-np.cos(2*phi)]]))

def qwp(phi):
    return(np.e**(-1j*np.pi/4)*np.array([[np.cos(phi)**2+1j*np.sin(phi)**2, (1-1j)*np.sin(phi)*np.cos(phi)],[(1-1j)*np.sin(phi)*np.cos(phi),1j*np.cos(phi)**2+np.sin(phi)**2]]))

def far(phi):
    return(np.array([[np.cos(phi), np.sin(phi)],[-np.sin(phi), np.cos(phi)]]))




def give_matrix(theta,DIR):
    phase = theta
    if DIR == 'fwd':
        matrix = hwp(theta/4 + np.pi/2)@hwp(0)@qwp(-np.pi/4)@far(-np.pi/4)@qwp(-np.pi/2)@hwp(theta/4)@qwp(np.pi/2)@far(np.pi/4)@qwp(np.pi/4)
    elif DIR == 'bwd':
        matrix = qwp(-np.pi/4)@far(-np.pi/4)@qwp(-np.pi/2)@hwp(-theta/4)@qwp(np.pi/2)@far(np.pi/4)@qwp(np.pi/4)@hwp(0)@hwp(-theta/4-np.pi/2)
    return matrix#asdf


# This is the theoretical function, with inside the already calculated values:
# We have to take out the theoretical function before we calculate it.
# So that we can make use of the fit function with the given function which predictes
# the behaviour of our model. So that we can extract the angles for the waveplates for an given theta

def simulation():


    theta = np.array(df.phase.values.tolist())
    htomo_sim = np.zeros((int(NUMPHASES),6))
    ptomo_sim = np.zeros((int(NUMPHASES),6))

    h_inp = np.matmul( np.array([[1],[0]]), np.array([[1],[0]]).T)
    p_inp = np.matmul( 1/np.sqrt(2)*np.array([[1],[1]]),np.array([[1],[1]]).T)

    pbs  = np.array([[1,0],[0,0]])

    htom = hwp(0)@qwp(0)
    vtom = hwp(45*np.pi/180)@qwp(0)

    ptom = hwp(22.5*np.pi/180)@qwp(45*np.pi/180)
    mtom = hwp(67.5*np.pi/180)@qwp(45*np.pi/180)

    rtom = hwp(22.5*np.pi/180)@qwp(0)
    ltom = hwp(67.5*np.pi/180)@qwp(0)

#   tomography in htom,vtom,ptom,mtom,rtom,ltom
    for i in range(int(NUMPHASES)):
        # H input
        temp = abs( np.trace(pbs@htom@give_matrix(theta[i],DIR)@h_inp) )**2
        htomo_sim[i,0] = temp

        temp = abs( np.trace(pbs@vtom@give_matrix(theta[i],DIR)@h_inp) )**2
        htomo_sim[i,1] = temp

        temp = abs( np.trace(pbs@ptom@give_matrix(theta[i],DIR)@h_inp) )**2
        htomo_sim[i,2] = temp

        temp = abs( np.trace(pbs@mtom@give_matrix(theta[i],DIR)@h_inp) )**2
        htomo_sim[i,3] = temp

        temp = abs( np.trace(pbs@rtom@give_matrix(theta[i],DIR)@h_inp) )**2
        htomo_sim[i,4] = temp

        temp = abs( np.trace(pbs@ltom@give_matrix(theta[i],DIR)@h_inp) )**2
        htomo_sim[i,5] = temp



        # P input  pbs@htom@give_matrix(theta[i],DIR)@
        temp = abs( np.trace(pbs@htom@give_matrix(theta[i],DIR)@p_inp) )**2
        ptomo_sim[i,0] = temp

        temp = abs( np.trace(pbs@vtom@give_matrix(theta[i],DIR)@p_inp) )**2
        ptomo_sim[i,1] = temp

        temp = abs( np.trace(pbs@ptom@give_matrix(theta[i],DIR)@p_inp) )**2
        ptomo_sim[i,2] = temp

        temp = abs( np.trace(pbs@mtom@give_matrix(theta[i],DIR)@p_inp) )**2
        ptomo_sim[i,3] = temp

        temp = abs( np.trace(pbs@rtom@give_matrix(theta[i],DIR)@p_inp) )**2
        ptomo_sim[i,4] = temp

        temp = abs( np.trace(pbs@ltom@give_matrix(theta[i],DIR)@p_inp) )**2
        ptomo_sim[i,5] = temp


    return htomo_sim, ptomo_sim
htomo_sim, ptomo_sim = simulation()







#schreibe das dataframe mit den listen um zu einem array
htomo_array = np.array(df.htomo.values.tolist())
ptomo_array = np.array(df.ptomo.values.tolist())
grid_lines  = np.array([45,90,135,180,225,270,315])

#rufe die Funktion auf welche die Simulierten werte hergibt




plt.plot(htomo_array)
plt.show()







#
# #TO - DO:
# 1. Mache eine Klasse
# 2. mache einen konstruktor der mir den gesuchten winkel raussucht damit ich das gewünschte theta rausbekomme
#         # aindex = int(np.where(y == max(y[peak]))[0])
#         # pindex = int(np.where(peak == aindex)[0])
#



















##
