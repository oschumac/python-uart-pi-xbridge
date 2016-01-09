#!/usr/bin/python

import json
import socket
import sys
import time
import os
import array
import math
import sqlite3
import xdriplib
import mongo

# Datenhaendling zur Mongodatenbank. BG Values

openapsDBName='openaps.sqlite'
DBVersion=1
tableNameDBVersion='DBVersion'
tableNameWixeldata='WixelData'
tableNameSensordata='SensorData'
tableNameCalibrationdata='CalibrationData'
tableNameBGReadingsdata='BGReadingsData'

old_calibration={ "_id":0 ,"timestamp":0, "sensor_age_at_time_of_estimation":0 , "sensorid":0, "bg":0, "raw_value":0, "filtered_value":0, "age_adjusted_raw_value":0, "sensor_confidence":0, "slope_confidence":0, "raw_timestamp":0, "slope":0, "intercept":0, "distance_from_estimate":0, "estimate_raw_at_time_of_calibration":0, "estimate_bg_at_time_of_calibration":0, "uuid":'uid', "sensor_uuid":'SensorUID', "possible_bad":False, "check_in":False, "first_decay":0, "second_decay":0, "first_slope":0, "second_slope":0, "first_intercept":0, "second_intercept":0, "first_scale":0, "second_scale":0}
WixelData = {"_id":0,"TransmitterId":"00000","CaptureDateTime":0,"RelativeTime":0,"ReceivedSignalStrength":0,"RawValue":0,"TransmissionId":0,"BatteryLife":0,"UploadAttempts":0,"Uploaded":0,"UploaderBatteryLife":0,"FilteredValue":0 }
BGReadings={"mussnoch":0}

def exists():
	conn = sqlite3.connect(openapsDBName)
	ret=-3
	try:
		cur = conn.cursor()
		sql='SELECT * FROM ' + tableNameDBVersion 
		#print "(BGReadings)(exists)  SQL->" + sql
		cur.execute(sql)

		data = cur.fetchone()
		#print "(BGReadings)(exists) Version ->" + str(data[0])
		
		if data[0]==DBVersion:
			ret=2
		else:
			print "(BGReadings)(exists)  DBVersion vorgegeben -> " + DBVersion + ' ungleich DBVersion in DB ->' + str(data[0])
			ret=-2
		
	
	except sqlite3.Error, e:
		print "(BGReadings)(exists) Error %s:" % e.args[0]
		ret=-1
    
	finally:
		conn.close()
		return ret
		
def initDB():
	test=exists()
	
	if test<0:
		print "Weiter ->" + str(test)
		conn = sqlite3.connect(openapsDBName)		
		sql = 'drop table if exists ' + tableNameDBVersion 
		print "(BGReadings) initDB SQL->" + sql
		conn.execute(sql)
		sql = 'create table if not exists ' + tableNameDBVersion 
		sql +='(version Long) '
		print "(BGReadings) initDB SQL->" + sql
		conn.execute(sql)
		sql = 'Insert into ' + tableNameDBVersion + ' (version) VALUES (' + str(DBVersion) + ')'
		print "(BGReadings) initDB SQL->" + sql
		conn.execute(sql)
		
		sql = 'drop table if exists ' + tableNameWixeldata 
		print "(BGReadings)(initDB)  SQL->" + sql
		conn.execute(sql)
		sql = 'create table if not exists ' + tableNameWixeldata 
		sql +='(_id INTEGER PRIMARY KEY AUTOINCREMENT, '
		sql +='TransmitterId String , '   
		sql +='CaptureDateTime Long , '
		sql +='RelativeTime Long , '
		sql +='ReceivedSignalStrength Long , '
		sql +='Rawvalue Long , ' 
		sql +='age_adjusted_raw_value Long , ' 
		sql +='FilteredValue Long , ' 
		sql +='TransmissionId Long , ' 
		sql +='BatteryLife Long , ' 
		sql +='UploadAttempts Long, '
		sql +='Uploaded Long , '
		sql +='UploaderBatteryLife Long) ' 

		print "(BGReadings)(initDB)  SQL->" + sql
		conn.execute(sql)
		
		sql = 'drop table if exists ' + tableNameSensordata 
		conn.execute(sql)
		sql = 'create table if not exists ' + tableNameSensordata
		sql +='(_id INTEGER PRIMARY KEY AUTOINCREMENT, '
		sql +='started_at Long , '
		sql +='stopped_at Long , '
		sql +='latest_battery_level Long , '
		sql +='uuid String , '
		sql +='sensor_location String ) ' 

		print "(BGReadings)(initDB)  SQL->" + sql
		conn.execute(sql)
		sql = "CREATE INDEX IF NOT EXISTS " +tableNameSensordata+ "_idx ON " +tableNameSensordata+ "( started_at,stopped_at )"
		conn.execute(sql)

		sql = 'drop table if exists ' + tableNameCalibrationdata
		conn.execute(sql)
		sql = 'create table if not exists ' + tableNameCalibrationdata
		sql +='(_id INTEGER PRIMARY KEY AUTOINCREMENT, '
		sql +=' timestamp Long, '
		sql +='sensor_age_at_time_of_estimation Long ,' 
		sql +='sensorid Long, ' 
		sql +='bg Long, ' 
		sql +='raw_value Long, ' 
		sql +='filtered_value Long, ' 
		sql +='age_adjusted_raw_value Long, ' 
		sql +='sensor_confidence Long, ' 
		sql +='slope_confidence Long, ' 
		sql +='raw_timestamp Long, '
		sql +='slope Long , ' 
		sql +='intercept Long, '  
		sql +='distance_from_estimate Long , ' 
		sql +='estimate_raw_at_time_of_calibration Long, ' 
		sql +='estimate_bg_at_time_of_calibration Long, ' 
		sql +='uuid String , ' 
		sql +='sensor_uuid String, ' 
		sql +='possible_bad Boolean, ' 
		sql +='check_in Boolean, ' 
		sql +='first_decay Long, ' 
		sql +='second_decay Long, ' 
		sql +='first_slope Long, ' 
		sql +='second_slope Long, ' 
		sql +='first_intercept Long, ' 
		sql +='second_intercept Long, ' 
		sql +='first_scale Long,' 
		sql +='second_scale Long) '
		print "(BGReadings)(initDB)  SQL->" + sql
		conn.execute(sql)
		sql = "CREATE INDEX IF NOT EXISTS " +tableNameCalibrationdata+ "_idx ON " +tableNameCalibrationdata+ "( timestamp,raw_timestamp )"
		conn.execute(sql)

		sql = 'drop table if exists ' + tableNameBGReadingsdata
		conn.execute(sql)
		sql = 'create table if not exists ' + tableNameBGReadingsdata
		sql +='(_id INTEGER PRIMARY KEY AUTOINCREMENT, '
		sql +='timestamp Long, '
		sql +='DateTime String, '
		sql +='bg Long, ' 
		sql +='raw_value Long, ' 
		sql +='raw_timestamp Long, ' 
		sql +='age_adjusted_raw_value Long, '
		sql +='filtered_value Long, ' 
		sql +='sensor_age_at_time_of_estimation Long ,' 
		sql +='possible_bad Boolean, ' 
		sql +='slope Long , ' 
		sql +='intercept Long, '  
		sql +='sensor_confidence Long, ' 
		sql +='uploaded Long, ' 
		sql +='a Long, '
		sql +='b Long, '
		sql +='c Long, '
		sql +='ra Long, '
		sql +='rb Long, '
		sql +='rc Long) '
		conn.execute(sql)
		sql = "CREATE INDEX IF NOT EXISTS " +tableNameBGReadingsdata+ "_idx ON " +tableNameBGReadingsdata+ "( timestamp,raw_timestamp )"
		conn.execute(sql)
		
		conn.commit()
		conn.close()
