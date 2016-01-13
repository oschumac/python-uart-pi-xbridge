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
import db
import sensor
import calibration


from calibration import *


db.initDB()

	



print "***********************************************************************************"
Y=BGReadings_Data()
Y.getlatest()
print "latest BG        ->" + str(Y.bg)	
Y.getsecondlatest()
print "secondlatest BG  ->" + str(Y.bg)	
Y.getthirdlatest()
print "thirdlatest BG   ->" + str(Y.bg)	



print "***********************************************************************************"

xdriplib.find_new_curve()
xdriplib.find_new_raw_curve()
