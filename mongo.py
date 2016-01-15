#!/usr/bin/python

import os
import sys
import pymongo
import time
import datetime
import math
from bson import BSON
from bson import json_util
from calibration import *


MONGODB_URI_LOCAL = 'mongodb://openapstest:openapstest@cgmcloud.de:21060/openapstest' 

def getlast3():
	try:
		client = pymongo.MongoClient(MONGODB_URI_LOCAL)
    
	except:
		print('Error: Unable to Connect')
		connection = None
    
	db = client['openapstest']
	cursor = db.entries.find({'type':'cal'}).sort('date', -1).limit(3)

	for doc in cursor:
		print (doc)

	client.close()
	
def sendentries(BG,DATETIME,FILTERED,UNFILTERED):
    try:
        client = pymongo.MongoClient(MONGODB_URI_LOCAL)
        db = client['openapstest']

        doc = {'device' : 'pythonuploader', 'date':DATETIME , 'dateString':datetime.datetime.fromtimestamp((DATETIME/1000)).strftime('%Y-%m-%d %H:%M:%S'), 'sgv':BG, 'direction':'Flat', 'type':'sgv', 'filtered':FILTERED, 'unfiltered':UNFILTERED, 'rssi':100, 'noise':0 }
    
        print doc
        db.entries.insert_one(doc)
        
        client.close()
        return 1
    
    except:
        print('Error: Unable to Connect')
        connection = None
        return 0
    
def getBGReadings():
    BGRead = BGReadings_Data()
    data = BGRead.getallnotuploaded()
    for row in data:
       _id=row[0]
       DATETIME=row[1]
       BG=math.ceil(row[3])
       FILTERED=row[6]
       UNFILTERED=row[7]
       # print "BG         ->" +str(BG)
       # print "DATETIME   ->" +str(DATETIME)
       # print "FILTERED   ->" +str(FILTERED)
       # print "UNFILTERED ->" +str(UNFILTERED)
       if sendentries(BG, DATETIME, FILTERED, UNFILTERED):
           BGRead.setuploaded(_id,1)
	   
    return 1


if __name__ == '__main__':
    getBGReadings()
	#sendentries(170,int(time.time())*1000,170000, 175000)
