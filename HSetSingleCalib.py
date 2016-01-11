#!/usr/bin/python

import json
import socket
import sys
import time
import os
from thread import *
from struct import *

import serial

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import Image
import ImageFont
import ImageDraw
import wixellib
import xdriplib
import BGReadings
import db
import sensor


from calibration import *

import sys

def main():
    print "***********************************" 
    print "Calibration routine"
    
    print " " + str(sys.argv[0])
    if len(sys.argv)==2:
        calBG = sys.argv[1]
        
        y = calibration_Data()
        y.getlatest()
        print "OLD Intercept -> " + str(y.intercept)
        print "OLD Slope -> " + str(y.slope)
        print "got " + str(calBG) + " mg/dl as calibration"
        xdriplib.create(int(calBG))

        x = calibration_Data()
        x.getlatest()
        print "new Intercept -> " + str(x.intercept)
        print "new Slope -> " + str(x.slope)
    
    
    else:
        print "Error called script with one parameter like:"
        print "-> python " + str(sys.argv[0]) + " BGVAL"
        print "   BGVAL = bloodsugar value in mg/dl"
        
if __name__ == "__main__":
    main();


