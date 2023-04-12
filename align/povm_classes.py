#!/usr/bin/env python3
import threading
import waveplates
import numpy as np



class PPBS():
    def __init__(self, config, name):
        self.cfg = config
        self.name = name

        self.Ymotor1 = self.cfg['gadgets'][self.name]['Ymotor1']
        self.Ymotor2 = self.cfg['gadgets'][self.name]['Ymotor2']
        self.Ytmotor = self.cfg['gadgets'][self.name]['Ytmotor']

        self.Y1zero = [self.cfg['gadgets'][self.name]['wpzero'][int(e)] for e in self.cfg['gadgets'][self.name]['Ymotor1']]
        self.Y2zero = [self.cfg['gadgets'][self.name]['wpzero'][int(e)] for e in self.cfg['gadgets'][self.name]['Ymotor2']]
        self.Ytzero = [self.cfg['gadgets'][self.name]['wpzero'][int(e)] for e in self.cfg['gadgets'][self.name]['Ytmotor']]

        self.NOHW_DEBUG = False


    def open_gadget(self):
        self.wps = waveplates.Waveplates(config=self.cfg['gadgets'])
        self.wps.open_unitary(self.name) if not self.NOHW_DEBUG else print('open ', self.name)

    def set_splitting(self, ratio):
        phase = self.splitting_to_phase(ratio)
        self.set_phase(phase)


    def hwp(self, phi):
        return(np.array([[np.cos(2*phi), np.sin(2*phi)],[np.sin(2*phi),-np.cos(2*phi)]]))

    def qwp(self, phi):
        return(np.e**(-1j*np.pi/4)*np.array([[np.cos(phi)**2+1j*np.sin(phi)**2, (1-1j)*np.sin(phi)*np.cos(phi)],[(1-1j)*np.sin(phi)*np.cos(phi),1j*np.cos(phi)**2+np.sin(phi)**2]]))

    def far(self, phi):
        return(np.array([[np.cos(phi), np.sin(phi)],[-np.sin(phi), np.cos(phi)]]))

    def phase_to_angle(self, phase):
        Ytangle = (phase/4)* 180/np.pi
        Yangle1 = 0
        Yangle2 = (phase/4 + np.pi/2) * 180/np.pi #0#(phase/4)* 180/np.pi#0
        return Yangle2, Yangle1, Ytangle #THE RIGHT WAY HOW ITS ROTATING



    def find_nearest(self, array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx

    def splitting_to_phase(self, ratio):
        #approximate it the first time
        pbsv = np.array([[0,0],[0,1]])
        V = np.array([[0],[1]])
        n = 300
        x = np.linspace(0,2*np.pi,n)
        y = np.zeros((n,1))
        for i in range(n):
            theta = x[i]
            bwm = self.qwp(-np.pi/4)@self.far(-np.pi/4)@self.qwp(-np.pi/2)@self.hwp(-theta/4)@self.qwp(np.pi/2)@self.far(np.pi/4)@self.qwp(np.pi/4)@self.hwp(0)@self.hwp(-theta/4-np.pi/2)
            anew= pbsv@bwm@V
            y[i,0] = abs(anew[1][0])**2

        #found the best first approximation
        #idx = self.find_nearest(y, )
        #array = np.asarray(y)
        idx = (np.abs(y - ratio)).argmin()
        #approximate it the second time
        n = 300
        x = np.linspace(x[idx]-5*np.pi/180,x[idx]+5*np.pi/180,n)
        y = np.zeros((n,1))
        for i in range(n):
            theta = x[i]
            bwm = self.qwp(-np.pi/4)@self.far(-np.pi/4)@self.qwp(-np.pi/2)@self.hwp(-theta/4)@self.qwp(np.pi/2)@self.far(np.pi/4)@self.qwp(np.pi/4)@self.hwp(0)@self.hwp(-theta/4-np.pi/2)
            anew= pbsv@bwm@V
            y[i,0] = abs(anew[1][0])**2

        #idx = self.find_nearest(y, ratio)
        #array = np.asarray(y)
        idx = (np.abs(y - ratio)).argmin()
        # y[idx] we have the approximated high
        # x[idx] we have the phase for the approximated high

        return x[idx]




    def phase_to_angle_plus(self, phase):
        #TODO
        #my guess: we have a phase in the PPBS(phase) and we want the angles for the hwp and qwp? exactamente
        Ytangle = (phase/4) * 180/np.pi#phase*180/np.pi
        Yangle1 = 0#(phase/4) * 180/np.pi #
        Yangle2 = (phase/4 + np.pi/2 ) * 180/np.pi
        return Ytangle, Yangle1, Yangle2


    def set_phase(self, phase):
        angles = self.phase_to_angle(phase)
        self.wps.move(angles)


    def set_phase_plus(self, phase):
        angles = self.phase_to_angle_plus(phase)
        self.wps.move(angles)

    def fwd_unitary(self, phase):
        # un = waveplates.Unitaries()
        # u = np.eye(2,dtype='complex')
        # u = u.dot(un.hwp(phase/4+np.pi/2)*r2d)
        # u = u.dot(un.hwp(0))
        # u = u.dot(un.qwp(-45))
        # u = u.dot(un.fm())
        # u = u.dot(un.qwp(90))
        # u = u.dot(un.hwp(phase*r2d/4))
        # u = u.dot(un.qwp(90))
        # u = u.dot(un.fp())
        # u = u.dot(un.qwp(45))
        u = hwp(theta/4 + np.pi/2)@hwp(0)@qwp(-np.pi/4)@far(-np.pi/4)@qwp(-np.pi/2)@hwp(theta/4)@qwp(np.pi/2)@far(np.pi/4)@qwp(np.pi/4)
        return u

    def bwd_unitary(self, phase):
        # un = waveplates.Unitaries()
        # u = np.eye(2,dtype='complex')
        # u = u.dot(un.qwp(-45))
        # u = u.dot(un.fm())
        # u = u.dot(un.qwp(-90))
        # u = u.dot(un.hwp(-phase*r2d/4))
        # u = u.dot(un.qwp(-90))
        # u = u.dot(un.fp())
        # u = u.dot(un.qwp(45))
        # u = u.dot(un.hwp(0))
        # u = u.dot(un.hwp((-phase/4+np.pi/2))*r2d)
        u = qwp(-np.pi/4)@far(-np.pi/4)@qwp(-np.pi/2)@hwp(-theta/4)@qwp(np.pi/2)@far(np.pi/4)@qwp(np.pi/4)@hwp(0)@hwp(-theta/4-np.pi/2)
        return u

class POVM():
    def __init__(self, config, name):
        #this will be 2 ppbs / gadgets and 2 unitaries
        self.cfg = config
        self.name = name

        self.unitarynames = [e['unitary'] for e in self.cfg['povms'][self.name]['ppbs']]
        self.ppbsnames = [e['gadget'] for e in self.cfg['povms'][self.name]['ppbs']]

        self.u1 = None
        self.u2 = None
        self.ppbs1 = None
        self.ppbs2 = None

    def open_u1(self):
        self.u1 = waveplates.Waveplates(self.cfg["waveplates"])
        self.u1.open_unitary(self.unitarynames[0]) if not self.NOHW_DEBUG else print('open ', self.unitarynames[0])

    def open_u2(self):
        self.u1 = waveplates.Waveplates(self.cfg["waveplates"])
        self.u1.open_unitary(self.unitarynames[1]) if not self.NOHW_DEBUG else print('open ', self.unitarynames[1])

    def open_ppbs1(self):
        self.ppbs1 = PPBS(self.cfg,self.ppbsnames[0])
        self.ppbs1.open_gadget() if not self.NOHW_DEBUG else print('open ', self.ppbsnames[0])

    def open_ppbs2(self):
        self.ppbs2 = PPBS(self.cfg, self.ppbsnames[1])
        self.ppbs2.open_gadget() if not self.NOHW_DEBUG else print('open ', self.ppbsnames[1])

    def open_devices(self):
        threads = []
        threads.append(threading.Thread(target=self.open_u1))
        threads.append(threading.Thread(target=self.open_u2))
        threads.append(threading.Thread(target=self.open_ppbs1))
        threads.append(threading.Thread(target=self.open_ppbs2))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
