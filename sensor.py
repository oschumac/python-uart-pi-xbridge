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
import db

SensorData = {"_id":0, "started_at":0, "stopped_at":0, "latest_battery_level":0, "uuid":'', "sensor_location":''  }


def StartSensor():

	if SensorisActive()==False:
		tag = 60*60*24
		offset=2*tag
		sql = 'Insert Into ' + db.tableNameSensordata + ' (started_at, stopped_at,latest_battery_level, uuid, sensor_location) VALUES ('
		sql+=" " + str(int(time.time()-offset))+"000"
		sql+=", 0"
		sql+=", 0"
		sql+=", 'UID'"
		sql+=", 'Arsch' )"
		#print "(BGReadings)(StartSensor)  SQL->" + sql
		conn = sqlite3.connect(db.openapsDBName)		
		conn.execute(sql)
		conn.commit()
		conn.close()
		return currentSensor()
	else:
		print "Versuch Sensor zu Starten obwohl noch einer Akitv ist"
		return currentSensor()

	
	
def StopSensor():
	sql = 'Update ' + db.tableNameSensordata + ' set stopped_at='
	sql+=str(int(time.time()))+"000" + "   where stopped_at=0"
	#print "(BGReadings)(StopSensor)  SQL->" + sql
	conn = sqlite3.connect(db.openapsDBName)		
	conn.execute(sql)
	conn.commit()
	conn.close()


def currentSensor():
	sql = 'select _id, started_at, stopped_at, latest_battery_level, uuid, sensor_location from ' + db.tableNameSensordata + ' where started_at !=0 and stopped_at =0 order by _id desc limit 1'
	#print "(BGReadings)(currentSensor)  SQL->" + sql
	conn = sqlite3.connect(db.openapsDBName)		
	cur = conn.cursor()
	cur.execute(sql)
	data = cur.fetchone()
	conn.close()
	sensor=SensorData
	if data!=None:
		sensor['_id']=data[0]
		sensor['started_at']=data[1]
		sensor['stopped_at']=data[2]
		sensor['latest_battery_level']=data[3]
		sensor['uuid']=data[4]
		sensor['sensor_location']=data[5]
	else:
		print "(BGReadings)(currentSensor)  No Sensor active"
	return sensor;
	
def SensorisActive():
	sensor = currentSensor()
	if(sensor['_id'] == 0):
		return False;
	else:
		return True;


def updateSensor(sensor):
	conn = sqlite3.connect(db.openapsDBName)
	sql = "Update " + db.tableNameSensordata + " set "
	sql+= "latest_battery_level=" + str(sensor['latest_battery_level']) + " "
	sql+= ",sensor_location='" + str(sensor['sensor_location']) + "' "
	sql+= "where _id=" + str(sensor['_id'])
	#print "(BGReadings)(updateSensor)  SQL->" + sql
	conn.execute(sql)
	conn.commit()
	conn.close()

def updateSensorLocation(sensor_location):
	sensor = currentSensor()
	if sensor['_id']==0:
		print "(BGReadings)(updateSensorLocation)  But Sensor is not Active"
		return;
	
	sensor['sensor_location']=str(sensor_location)
	updateSensor(sensor);

def updateSensorBatterieLevel(Level):
	sensor = currentSensor()
	if sensor['_id']==0:
		print "(BGReadings)(updateSensorBatterieLevel)  But Sensor is not Active"
		return;
	
	sensor['latest_battery_level']=str(Level)
	updateSensor(sensor);
