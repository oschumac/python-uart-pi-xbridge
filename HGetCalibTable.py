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
    cal= calibration_Data()
    
    data =  cal.allForSensorInLastFourDays()
    
    print "_id, time, senor_age_at_estimate, sensorid, bg, raw, filtered, age_adjusted_raw, sensor_convidence, slop_conv, raw_time, slope, intercept, distance_from_estimate, estimate_raw, estimate_bg" 
    for row in data:
        print row
    
    cal.getlatest()
    print "" 
    print "Slope     -> " + str(cal.slope) 
    print "intercept -> " + str(cal.intercept) 

    
if __name__ == "__main__":
    main();


