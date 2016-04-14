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
import json

def main():
    
    #print "_id, timestamp, DateTime, bg, raw_value, raw_timestamp, age_adjusted_raw_value, filtered_value, sensor_age_at_time_of_estimation, possible_bad, slope, intercept, sensor_confidence, uploaded, a, b, c, ra, rb, rc "
    # {"_id":"56d9fd4fe9014906a2410493",
    # "trend_arrow":"Flat",
    # "noise":0,
    # "display_time":"2016-03-04 22:25:35",
    # "glucose":222,
    # "device":"pythonuploader",
    # "filtered":240576,"date":1457126735000,
    # "unfiltered":244192,
    # "rssi":100,
    # "type":"glucose"}

    readings=20
    
    if len(sys.argv)==2:
        readings = int(sys.argv[1])
        
    BGR = BGReadings_Data()
    data =  BGR.getlastBG(readings)
    datajson = []

    for datal in data:
        dataj = {
            '_id' : datal[0],
	    'date' : datal[1],
            'display_time' : datal[2],
            'device':'pythonuploader',
            'glucose' : int(datal[3]),
            'type' : 'glucose'}
        datajson.append(dataj)

    print json.dumps(datajson)


    
    
if __name__ == "__main__":
    main();


