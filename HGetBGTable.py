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
    BGR = BGReadings_Data()
    
    data =  BGR.getlastBG(20)
    
    print "_id, timestamp, DateTime, bg, raw_value, raw_timestamp, age_adjusted_raw_value, filtered_value, sensor_age_at_time_of_estimation, possible_bad, slope, intercept, sensor_confidence, uploaded, a, b, c, ra, rb, rc "
    for row in data:
        print row
    

    
if __name__ == "__main__":
    main();


