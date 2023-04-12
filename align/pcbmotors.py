"""Communicate with a Thorlabs elliptec controller."""

import io
import serial
import time
import sys 
import logging
from myexperiment_log import logger as log
class ParameterException(BaseException):
    """Parameter out of bounds or invalid."""
    pass

class MotorException(BaseException):
    """ Motor does not respond or is stuck """
    pass


class PCBmotors:
    def __init__(self,path,order):
        self.log = logging.getLogger('myexperiment.waveplates.pcbmotor')
        if sys.platform == "linux" or platform == "linux2":
            self.os="linux"
            self.eol='\r'
        elif sys.platform == "darwin":
            self.os="mac"
            self.eol='\r'
        elif sys.platform == "win32":
            self.os="win"
            self.eol='\r\n'
            
        self.motororder=order
        
        self.ser=self.dev_open(path)

    def dev_open(self,path):
        """ open waveplate connection """
        #path: device path (str)
        ser=serial.Serial(path,19200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.2, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False)
        #pySerial does not honour Flow contrl options during init. Wasted a f*ing day figuring this out
        ser.dtr=False
        ser.rts=False
        return ser
    
    def close(self):
        """ close waveplate controller """
        self.ser.close()

    def moveabsolute(self, m, angle):
        success = False
        tries = 0
        if (0):
            while not success:
                self.__motor_home(m)
                time.sleep(0.5)
                ret=self.__motor_move(m,self.__getsteps(self.__boundangle(angle)))
                time.sleep(0.5)
                if not (ret == 0):
                    tries = tries + 1
                    if tries == 5:
                        raise MotorException("PCBMotor movement failed with error code {0:d}. (-1: seems to be stuck))".format(ret))
                else:
                    success = True
        else:
            self.__motor_home(m)
            time.sleep(0.5)
            self.__motor_move(m,self.__getsteps(self.__boundangle(angle)))
            time.sleep(0.5)
    
    #def calmove(self,morder,angle):
        #""" move m1, m2, m3, ... to angle[0], angle[1], angle[2], ... 
            #skip motors with angle[i]=None"""
        #for i in range(0,len(angle)):
            #if angle[i] == None:
                #pass
            #else:
                #self.moveabsolute(morder[i],angle[i])
            
    
    def moverelative(self,m,delta):
        """ delta in degrees """
        self.__motor_move(m,self.__getsteps(delta))
    
    def step(self,steps):
        """ move waveplates by specified amount of steps 
            steps in degrees"""
        if len(steps)==3:
            for m, s in zip(self.motororder, steps):
                self.__motor_move(m,self.__getsteps(s))
        else:
            raise ParameterException
    
    def __motor_home(self, m):
        """ Home a single motor """
        #c: controller (serial.Serial)
        #m: motor (str)
        cmd=m+',s-2880'+self.eol
        self.ser.write(cmd.encode())
        while(1):
            line=self.ser.readline()
            if ('Steps' in str(line)):
                break
            else:
                time.sleep(0.05)
    
    def __motor_move(self, m, steps):
        """ Move a single motor """
        #m: motor (str)
        #steps: number of steps to go
        cmd=m+',s'+str(int(steps))+self.eol
        self.ser.write(cmd.encode())
        while(1):
            line=self.ser.readline()
            #print(line)
            if ('Steps' in str(line)):
                #print('x:', line)
                confstepsstr=str(line).strip().split("=")[1][:-3]
                confsteps=int(confstepsstr)
                #print('went {0:d} steps'.format(confsteps))
                if not (confsteps==steps):
                    self.log.error("ERROR: Tried to go {0:f} steps, but moved by {1:f} steps".format(steps,confsteps))
                    return -1
                else:
                    return 0
                break
            else:
                time.sleep(0.05)
                
    
    def __getsteps(self,angle):
        """ convert angle to number o steps """
        return int(angle*8)
    
    def __boundangle(self,angle):
        if angle>0:
            while angle > 320:
                angle = angle-180
        else:
            while angle < 0:
                angle = angle + 180
        
        return angle
