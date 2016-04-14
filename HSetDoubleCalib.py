#!/usr/bin/python

import json
import socket
import sys
import time
import os
from thread import *
from struct import *

import serial


import wixellib
import xdriplib
#import BGReadings
import db
import sensor


from calibration import *

import sys

def main():
    print "***********************************" 
    print "Calibration routine"
    
    print " " + str(sys.argv[0])
    if len(sys.argv)==3:
        calBG1 = sys.argv[1]
        calBG2 = sys.argv[2]
        
        y = calibration_Data()
        y.getlatest()
        print "OLD Intercept -> " + str(y.intercept)
        print "OLD Slope -> " + str(y.slope)
        print "got " + str(calBG1) + " mg/dl and " + str(calBG2) + " mg/dl as calibration"
        xdriplib.initialCalibration( int(calBG1),  int(calBG2))

        x = calibration_Data()
        x.getlatest()
        print "new Intercept -> " + str(x.intercept)
        print "new Slope -> " + str(x.slope)
    
    
    else:
        print "Error called script with one parameter like:"
        print "-> python " + str(sys.argv[0]) + " BGVAL1 BGVAL2"
        print "   BGVAL1 = bloodsugar value one in mg/dl"
        print "   BGVAL2 = bloodsugar value two in mg/dl"
        
if __name__ == "__main__":
    main();


