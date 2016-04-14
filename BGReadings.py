#!/usr/bin/python

import json
import socket
import sys
import time
import os
import array
import math
import sqlite3
import mongo
import db
import sensor
import xdriplib

WixelData = {"_id":0,"TransmitterId":"00000","CaptureDateTime":0,"RelativeTime":0,"ReceivedSignalStrength":0,"RawValue":0,"TransmissionId":0,"BatteryLife":0,"UploadAttempts":0,"Uploaded":0,"UploaderBatteryLife":0,"FilteredValue":0 }

def oldinsertIntoWixeldata_(data) :
	
	if sensor.SensorisActive():
		CurSensor=sensor.currentSensor()
		print "CurSensor->" + str(CurSensor['started_at'])
		TimeDelta=((long(data['CaptureDateTime'])-long(CurSensor['started_at']))*1.0)/1000/60/60
		Adjusted_raw=xdriplib.calculateAgeAdjustedRawValue(TimeDelta,int(data['RawValue']))
		print "BGReadings AgeAdjustedRaw 		-> " + str(Adjusted_raw)
		Adjusted_raw=xdriplib.calculateAgeAdjustedRawValue(TimeDelta,int(data['RawValue']))
	else:
		print "No Sensor Active"
		Adjusted_raw=0
		
	conn = sqlite3.connect(db.openapsDBName)
	sql='insert into ' + db.tableNameWixeldata
	sql+='(TransmitterId, CaptureDateTime, RelativeTime, ReceivedSignalStrength, RawValue, TransmissionId, BatteryLife, UploadAttempts, Uploaded, UploaderBatteryLife, FilteredValue, age_adjusted_raw_value ) VALUES ('
	sql+="  '" + str(data['TransmitterId']) + "'"
	sql+=', ' + str(data['CaptureDateTime']) 
	sql+=', ' + str(data['RelativeTime']) 
	sql+=', ' + str(data['ReceivedSignalStrength'])
	sql+=', ' + str(data['RawValue']) 
	sql+=', ' + str(data['TransmissionId']) 
	sql+=', ' + str(data['BatteryLife']) 
	sql+=', ' + str(data['UploadAttempts']) 
	sql+=', ' + str(data['Uploaded']) 
	sql+=', ' + str(data['UploaderBatteryLife']) 
	sql+=', ' + str(Adjusted_raw)
	sql+=', ' + str(data['FilteredValue']) + ' )'
	#print "(BGReadings)(insertIntoWixel)  SQL->" + sql
	conn.execute(sql)
	conn.commit()
	print "Records created successfully";
	conn.close()

	
def oldgetrawData_():
	wdata=WixelData
	sql = 'select _id, TransmitterId, CaptureDateTime, RelativeTime, ReceivedSignalStrength, RawValue, TransmissionId, BatteryLife, UploadAttempts, Uploaded, UploaderBatteryLife, FilteredValue '   
	sql+= 'from ' + db.tableNameWixeldata + ' order by CaptureDateTime desc limit 1'
	#print "(BGReadings)(getrawData)  SQL->" + sql
	conn = sqlite3.connect(db.openapsDBName)		
	cur = conn.cursor()
	cur.execute(sql)
	data = cur.fetchone()
	conn.close()
	wdata=WixelData
	if data!=None:
		wdata['_id']=data[0]
		wdata['TransmitterId']=data[1]
		wdata['CaptureDateTime']=data[2]
		wdata['RelativeTime']=data[3]
		wdata['ReceivedSignalStrength']=data[4]
		wdata['RawValue']=data[5]
		wdata['TransmissionId']=data[6]
		wdata['BatteryLife']=data[7]
		wdata['UploadAttempts']=data[8]
		wdata['Uploaded']=data[9]
		wdata['UploaderBatteryLife']=data[10]
		wdata['FilteredValue']=data[11]
	else:
		print "(BGReadings)(getrawData)  No data available"
	return wdata;

	
def oldinitBGReadings_():
	initDB()


def oldlatestRaw_(anzahl):
	sql = 'select RawValue, CaptureDateTime, age_adjusted_raw_value as Timestamp '   
	sql+= 'from ' + db.tableNameWixeldata + ' order by CaptureDateTime desc limit ' + str(anzahl)
	
	conn = sqlite3.connect(db.openapsDBName)		
	cur = conn.cursor()
	cur.execute(sql)
	data = cur.fetchall()

	conn.close()
	return data;

	
def oldtest_():

	mydata = {"_id":1,"TransmitterId":"66PNX","CaptureDateTime":0,"RelativeTime":0,"ReceivedSignalStrength":0,"RawValue":0,"TransmissionId":0,"BatteryLife":0,"UploadAttempts":0,"Uploaded":0,"UploaderBatteryLife":0,"FilteredValue":0 }
		
	mydata['CaptureDateTime']=long(time.time())
	mydata['RelativeTime']=2121313
	mydata['RawValue']="155000"

	mydata['FilteredValue']="155000"
	mydata['BatteryLife']="240"
	mydata['TransmitterId']="00000"
	mydata['ReceivedSignalStrength']=0
	mydata['TransmissionId']=0
	print "Time adjusted raw" + str(xdriplib.calculateAgeAdjustedRawValue(5,155000))
		
	insertIntoWixeldata(mydata)



if __name__ == "__main__":
	test()
