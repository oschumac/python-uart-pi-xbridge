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
    cal= calibration_Data()
    
    data =  cal.allForSensorInLastFourDays()
    for row in data:
        print row
    
if __name__ == "__main__":
    main();

