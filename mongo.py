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
import dateutil.parser
from dateutil import tz

MONGODB_URI_LOCAL = 'mongodb://user:passw@mongolab:123456/collectionname' 
MONGODB_COLLECTION = 'collectionname'


def gettreatments():
    try:
        client = pymongo.MongoClient(MONGODB_URI_LOCAL)

    except:
		print('Error: Unable to Connect')
		connection = None
    
    db = client[MONGODB_COLLECTION]
    #cursor = db.entries.find({'type':'cal'}).sort('date', -1).limit(3)
    #cursor = db.entries.find({'type':'sgv'}).sort('date', -1).limit(3)
    cursor = db.treatments.find({'glucose':{"$exists": 'false'}}).sort('_id',-1).limit(1)

    to_zone = tz.tzlocal()


    for doc in cursor:
        print doc
        data = {'created_at':0, '_id':0, 'date':0, 'glucose':0}
        data['_id'] = doc['_id']
        data['created_at'] = doc['created_at']
        newdate = dateutil.parser.parse(doc['created_at']).astimezone(to_zone)
        data['date'] = newdate 
        data['glucose'] = doc['glucose']
        print "Return data"
        client.close()
        return data
    else:
        client.close()
        print "Got nothing to return"
        

	
def sendentries(BG,DATETIME,FILTERED,UNFILTERED):
    try:
        client = pymongo.MongoClient(MONGODB_URI_LOCAL)
        db = client[MONGODB_COLLECTION]

        doc = {'device' : 'pythonuploader', 'date':DATETIME , 'dateString':datetime.datetime.fromtimestamp((DATETIME/1000)).strftime('%Y-%m-%d %H:%M:%S'), 'sgv':BG, 'direction':'Flat', 'type':'sgv', 'filtered':FILTERED, 'unfiltered':UNFILTERED, 'rssi':100, 'noise':0 }
    
        print doc
        db.entries.insert_one(doc)
        
        client.close()
        return 1
    
    except:
        print('Error: Unable to Connect')
        connection = None
        return 0
    
def mongo_getBGReadings():
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

def sendentriescal(row):
    try:
        client = pymongo.MongoClient(MONGODB_URI_LOCAL)
        db = client[MONGODB_COLLECTION]
        
        
    
    except:
        print('Error: Unable to Connect')
        connection = None
        return 0

    TIMESTAMP=row[1]
    BG=row[4]
    UNFILTERED=row[5]
    FILTERED=row[6]
    SLOPE=row[11]
    INTERCEPT=row[12]

    doc = {'device' : 'pythonuploader', 'date':TIMESTAMP , 'dateString':datetime.datetime.fromtimestamp((TIMESTAMP/1000)).strftime('%Y-%m-%d %H:%M:%S'), 'slope':SLOPE, 'intercept':INTERCEPT ,'sgv':BG,  'type':'MBG', 'filtered':FILTERED, 'unfiltered':UNFILTERED, 'scale':1 }

    print doc
    db.entries.insert_one(doc)
    
    client.close()
    return 1



def mongo_GetCalib_send():
    print "mongo_GetCalib_send()"
    calib = calibration_Data()
    data = calib.getallnotuploaded()
    for row in data:
        
        print row
        if sendentriescal(row):
            print "calib.setuploaded(row[0],1)"
            #calib.setuploaded(row[0],1)
    


def mongo_findTreatCall_Calib():
    print "findTreatCall_Calib()"
    BG=BGReadings_Data()
    BG.getlatest()
    BGDateTime = datetime.datetime.fromtimestamp((BG.timestamp/1000))

    
    data = gettreatments()
    print data
    
    treatmentsdate = dateutil.parser.parse(data['created_at']).astimezone(tz.tzlocal()).replace(tzinfo=None)
    
    print "BG    DateTime -> " + BGDateTime.strftime('%Y-%m-%d %H:%M:%S')
    print "Treat DateTime -> " + treatmentsdate.strftime('%Y-%m-%d %H:%M:%S')
    
    delta = abs(treatmentsdate - BGDateTime)
    if delta.total_seconds() < 300:
        print "Dann koennen wir Calibrieren " + str(delta)
        
        
        y = calibration_Data()
        y.getlatest()
        print "OLD Intercept -> " + str(y.intercept)
        print "OLD Slope -> " + str(y.slope)
        print "got " + str(data['glucose']) + " mg/dl as calibration"
        print "xdriplib.create(int(" + str(data['glucose'])  + "))"
        #xdriplib.create(int(calBG))

        x = calibration_Data()
        x.getlatest()
        print "new Intercept -> " + str(x.intercept)
        print "new Slope -> " + str(x.slope)

    else:
        print "So nicht " + str(delta)
        

if __name__ == '__main__':
    mongo_GetCalib_send()
    #findTreatCall_Calib()
