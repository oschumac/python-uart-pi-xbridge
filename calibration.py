import json
import socket
import sys
import time
import os
from thread import *
from struct import *

import sensor
import db
import sqlite3

class calibration_Data: 
	
	def __init__(self):
		self._id=0
		self.uuid='uid'
		self.sensor_uuid='SensorUID'
		self.timestamp=0
		self.sensor_age_at_time_of_estimation=0 
		self.sensorid=0
		self.SensorData=sensor.SensorData
		self.bg=0
		self.filtered_value=0
		self.raw_timestamp=0
		self.raw_value=0
		self.age_adjusted_raw_value=0
		
		self.sensor_confidence=0
		self.slope_confidence=0
		self.slope=0
		self.intercept=0
		
		self.distance_from_estimate=0
		self.estimate_raw_at_time_of_calibration=0
		self.estimate_bg_at_time_of_calibration=0
		self.possible_bad=False
		
		self.first_decay=0
		self.second_decay=0
		self.first_slope=0
		self.second_slope=0
		self.first_intercept=0
		self.second_intercept=0
		self.first_scale=0
		self.second_scale=0
		self.check_in=False
		self.uploaded=0


		#print "Klasse " + " wurde erzeugt"
		if sensor.SensorisActive():
			SensorData=sensor.currentSensor()
			self.sensorid=SensorData['_id']
			#print "Aktiver Sensor vorhanden _id->" + str(self.sensor)
		else:
			print "Kein Aktiver Sensor vorhanden "
	#def __del__(self):
		#print "Klasse " + " zerstoert"
		
		
	def createnew(self):
		sql="insert into " + db.tableNameCalibrationdata + " (timestamp, sensor_age_at_time_of_estimation, sensorid, "
		sql+="bg, raw_value, filtered_value, age_adjusted_raw_value, sensor_confidence, slope_confidence, raw_timestamp, "
		sql+="slope, intercept, distance_from_estimate, estimate_raw_at_time_of_calibration, estimate_bg_at_time_of_calibration, "
		sql+="uuid, sensor_uuid, possible_bad, check_in, first_decay, second_decay, first_slope, second_slope, "
		sql+="first_intercept, second_intercept, first_scale, second_scale, uploaded ) values ( "
		sql+=str(self.timestamp)+ ", "
		sql+=str(self.sensor_age_at_time_of_estimation)+ ", "
		sql+=str(self.sensorid)+ ", "
		sql+=str(self.bg)+ ", "
		sql+=str(self.raw_value)+ ", "
		sql+=str(self.filtered_value)+ ", "
		sql+=str(self.age_adjusted_raw_value)+ ", "
		sql+=str(self.sensor_confidence)+ ", "
		sql+=str(self.slope_confidence)+ ", "
		sql+=str(self.raw_timestamp)+ ", "
		sql+=str(self.slope)+ ", "
		sql+=str(self.intercept)+ ", "
		sql+=str(self.distance_from_estimate)+ ", "
		sql+=str(self.estimate_raw_at_time_of_calibration)+ ", "
		sql+=str(self.estimate_bg_at_time_of_calibration)+ ", "
		sql+="'"+str(self.uuid)+ "', "
		sql+="'"+str(self.sensor_uuid)+"', "
		sql+="'"+str(self.possible_bad)+ "', "
		sql+="'"+str(self.check_in)+ "', "
		sql+=str(self.first_decay)+ ", "
		sql+=str(self.second_decay)+ ", "
		sql+=str(self.first_slope)+ ", "
		sql+=str(self.second_slope)+ ", "
		sql+=str(self.first_intercept)+ ", "
		sql+=str(self.second_intercept)+ ", "
		sql+=str(self.first_scale)+ ", "
		sql+=str(self.second_scale)+ ", "
		sql+=str(self.uploaded)+ ") "
		
		#print "createnew SQL->" + sql
		conn = sqlite3.connect(db.openapsDBName)
		conn.execute(sql)
		conn.commit()
		#print "Records created successfully";
		sql="Select _id from " + db.tableNameCalibrationdata + " ORDER BY _id desc LIMIT 1"
		#print "Select SQL->" + sql
		cur = conn.cursor()
		cur.execute(sql)
		data = cur.fetchone()
		self._id=data[0]
		conn.commit()
		conn.close()
		

	def updateSensor(self):
		sql="update " + db.tableNameCalibrationdata + " SET "
		sql+="timestamp="+str(self.timestamp)+ ", "
		sql+="sensor_age_at_time_of_estimation="+str(self.sensor_age_at_time_of_estimation)+ ", "
		sql+="sensorid="+str(self.sensorid)+ ", "
		sql+="bg="+str(self.bg)+ ", "
		sql+="raw_value="+str(self.raw_value)+ ", "
		sql+="filtered_value="+str(self.filtered_value)+ ", "
		sql+="age_adjusted_raw_value="+str(self.age_adjusted_raw_value)+ ", "
		sql+="sensor_confidence="+str(self.sensor_confidence)+ ", "
		sql+="slope_confidence="+str(self.slope_confidence)+ ", "
		sql+="raw_timestamp="+str(self.raw_timestamp)+ ", "
		sql+="slope="+str(self.slope)+ ", "
		sql+="intercept="+str(self.intercept)+ ", "
		sql+="distance_from_estimate="+str(self.distance_from_estimate)+ ", "
		sql+="estimate_raw_at_time_of_calibration="+str(self.estimate_raw_at_time_of_calibration)+ ", "
		sql+="estimate_bg_at_time_of_calibration="+str(self.estimate_bg_at_time_of_calibration)+ ", "
		sql+="uuid='"+str(self.uuid)+ "', "
		sql+="sensor_uuid='"+str(self.sensor_uuid)+"', "
		sql+="possible_bad='"+str(self.possible_bad)+ "', "
		sql+="check_in='"+str(self.check_in)+ "', "
		sql+="first_decay="+str(self.first_decay)+ ", "
		sql+="second_decay="+str(self.second_decay)+ ", "
		sql+="first_slope="+str(self.first_slope)+ ", "
		sql+="second_slope="+str(self.second_slope)+ ", "
		sql+="first_intercept="+str(self.first_intercept)+ ", "
		sql+="second_intercept="+str(self.second_intercept)+ ", "
		sql+="first_scale="+str(self.first_scale)+ ", "
		sql+="second_scale="+str(self.second_scale)+ ", "
		sql+="uploaded="+str(self.uploaded)
		sql+=" where _id="+str(self._id)
		#print "updatesensor SQL->" + sql
		conn = sqlite3.connect(db.openapsDBName)
		conn.execute(sql)
		conn.commit()
		#print "Records updated successfully";
		conn.close()
		
	def save(self):
		if self._id >0:
			self.updateSensor()
		else:
			self.createnew()
			
	def getfirst(self):
		sql="Select _id, timestamp, sensor_age_at_time_of_estimation, sensorid, "
		sql+="bg, raw_value, filtered_value, age_adjusted_raw_value, sensor_confidence, slope_confidence, raw_timestamp, "
		sql+="slope, intercept, distance_from_estimate, estimate_raw_at_time_of_calibration, estimate_bg_at_time_of_calibration, "
		sql+="uuid, sensor_uuid, possible_bad, check_in, first_decay, second_decay, first_slope, second_slope, "
		sql+="first_intercept, second_intercept, first_scale, second_scale, uploaded from " + db.tableNameCalibrationdata + " where sensorid=" + str(self.sensorid) + " "
		sql+="ORDER BY _id asc LIMIT 1"
		#print "Select SQL->" + sql
		conn = sqlite3.connect(db.openapsDBName)		
		cur = conn.cursor()
		cur.execute(sql)
		data = cur.fetchone()
		conn.close()
		if data<>None:
			if len(data)==29:
				#print data
				self._id=data[0]
				self.timestamp=data[1]
				self.sensor_age_at_time_of_estimation=data[2]
				self.sensorid=data[3]
				self.bg=data[4]
				self.raw_value=data[5]
				self.filtered_value=data[6]
				self.age_adjusted_raw_value=data[7]
				self.sensor_confidence=data[8]
				self.slope_confidence=data[9]
				self.raw_timestamp=data[10]
				self.slope=data[11]
				self.intercept=data[12]
				self.distance_from_estimate=data[13]
				self.estimate_raw_at_time_of_calibration=data[14]
				self.estimate_bg_at_time_of_calibration=data[15]
				self.uuid=data[16]
				self.sensor_uuid=data[17]
				self.possible_bad=data[18]
				self.check_in=data[19]
				self.first_decay=data[20]
				self.second_decay=data[21]
				self.first_slope=data[22]
				self.second_slope=data[23]
				self.first_intercept=data[24]
				self.second_intercept=data[25]
				self.first_scale=data[26]
				self.second_scale=data[27]
				self.uploaded=data[28]

	def getlatest(self):
		sql="Select _id, timestamp, sensor_age_at_time_of_estimation, sensorid, "
		sql+="bg, raw_value, filtered_value, age_adjusted_raw_value, sensor_confidence, slope_confidence, raw_timestamp, "
		sql+="slope, intercept, distance_from_estimate, estimate_raw_at_time_of_calibration, estimate_bg_at_time_of_calibration, "
		sql+="uuid, sensor_uuid, possible_bad, check_in, first_decay, second_decay, first_slope, second_slope, "
		sql+="first_intercept, second_intercept, first_scale, second_scale, uploaded from " + db.tableNameCalibrationdata + " where sensorid=" + str(self.sensorid) + " "
		sql+="ORDER BY _id desc LIMIT 1"
		print "Select SQL->" + sql
		conn = sqlite3.connect(db.openapsDBName)		
		cur = conn.cursor()
		cur.execute(sql)
		data = cur.fetchone()
		conn.close()
		if data<>None:
			if len(data)==29:
				print data
				self._id=data[0]
				self.timestamp=data[1]
				self.sensor_age_at_time_of_estimation=data[2]
				self.sensorid=data[3]
				self.bg=data[4]
				self.raw_value=data[5]
				self.filtered_value=data[6]
				self.age_adjusted_raw_value=data[7]
				self.sensor_confidence=data[8]
				self.slope_confidence=data[9]
				self.raw_timestamp=data[10]
				self.slope=data[11]
				self.intercept=data[12]
				self.distance_from_estimate=data[13]
				self.estimate_raw_at_time_of_calibration=data[14]
				self.estimate_bg_at_time_of_calibration=data[15]
				self.uuid=data[16]
				self.sensor_uuid=data[17]
				self.possible_bad=data[18]
				self.check_in=data[19]
				self.first_decay=data[20]
				self.second_decay=data[21]
				self.first_slope=data[22]
				self.second_slope=data[23]
				self.first_intercept=data[24]
				self.second_intercept=data[25]
				self.first_scale=data[26]
				self.second_scale=data[27]
				self.uploaded=data[28]

	def first_sensor_age_at_time_of_estimation(self):
		sql="Select sensor_age_at_time_of_estimation, sensorid "
		sql+= "from " + db.tableNameCalibrationdata + " where sensorid=" + str(self.sensorid) + " "
		sql+="ORDER BY _id asc LIMIT 1"
		#print "Select SQL->" + sql
		conn = sqlite3.connect(db.openapsDBName)		
		cur = conn.cursor()
		cur.execute(sql)
		data = cur.fetchone()
		conn.close()
		if data<>None:
			if len(data)==4:
				return data[0]
			else:
				return 0
		else:
			return 0

	def last_first_sensor_age_at_time_of_estimation(self):
		sql="Select sensor_age_at_time_of_estimation, sensorid "
		sql+= "from " + db.tableNameCalibrationdata + " where sensorid=" + str(self.sensorid) + " "
		sql+="ORDER BY _id desc LIMIT 1"
		#print "Select SQL->" + sql
		conn = sqlite3.connect(db.openapsDBName)		
		cur = conn.cursor()
		cur.execute(sql)
		data = cur.fetchone()
		conn.close()
		if data<>None:
			if len(data)==4:
				return data[0]
			else:
				return 0
		else:
			return 0


	def calculateWeight(self):
		firstTimeStarted =   first_sensor_age_at_time_of_estimation();
		lastTimeStarted =   last_first_sensor_age_at_time_of_estimation();
		time_percentage = min(((self.sensor_age_at_time_of_estimation - firstTimeStarted) / (lastTimeStarted - firstTimeStarted)) / (.85), 1);
		time_percentage = (time_percentage + .01);
		print "CALIBRATIONS TIME PERCENTAGE WEIGHT: " + str(time_percentage)
		return max((((((slope_confidence + sensor_confidence) * (time_percentage))) / 2) * 100), 1);

	def clear_all_existing_calibrations(self):
		if self.sensorid<>0:
			sql = "delete from " + db.tableNameCalibrationdata + " where sensorid=" + str(self.sensorid) + " "
			#print "SQL->" + sql
			conn = sqlite3.connect(db.openapsDBName)
			conn.execute(sql)
			conn.commit()
			conn.close()
			
	def allForSensorInLastFourDays(self):
		if self.sensorid<>0:
			sql="Select _id, timestamp, sensor_age_at_time_of_estimation, sensorid, "
			sql+="bg, raw_value, filtered_value, age_adjusted_raw_value, sensor_confidence, slope_confidence, raw_timestamp, "
			sql+="slope, intercept, distance_from_estimate, estimate_raw_at_time_of_calibration, estimate_bg_at_time_of_calibration, "
			sql+="uuid, sensor_uuid, possible_bad, check_in, first_decay, second_decay, first_slope, second_slope, "
			sql+="first_intercept, second_intercept, first_scale, second_scale, uploaded from " + db.tableNameCalibrationdata 
			sql+= " where sensorid=" + str(self.sensorid) + " "
			sql+= " and slope_confidence!=0 "
			sql+= " and sensor_confidence!=0 "
			sql+= " and timestamp > " + str(long (time.time()*100) - (60000 * 60 * 24 * 4) ) + " "
			sql+= "ORDER BY _id desc"
			#print "SQL->" + sql
			conn = sqlite3.connect(db.openapsDBName)		
			cur = conn.cursor()
			cur.execute(sql)
			data = cur.fetchall()
			conn.close()
			
			return data
		else:
			print "Kein Sensor aktiv"	

	def getallnotuploaded(self):
		sql="Select _id, timestamp, sensor_age_at_time_of_estimation, sensorid, "
		sql+="bg, raw_value, filtered_value, age_adjusted_raw_value, sensor_confidence, slope_confidence, raw_timestamp, "
		sql+="slope, intercept, distance_from_estimate, estimate_raw_at_time_of_calibration, estimate_bg_at_time_of_calibration, "
		sql+="uuid, sensor_uuid, possible_bad, check_in, first_decay, second_decay, first_slope, second_slope, "
		sql+="first_intercept, second_intercept, first_scale, second_scale, uploaded from " + db.tableNameCalibrationdata 
		sql+= " where uploaded = 0 ORDER BY _id desc LIMIT 500"
		print "SQL->" + sql
		conn = sqlite3.connect(db.openapsDBName)		
		cur = conn.cursor()
		cur.execute(sql)
		data = cur.fetchall()
		conn.close()
		if data<>None:
			return data
			
			
			
class BGReadings_Data:
	
	WixelData = {"_id":0,"TransmitterId":"00000","CaptureDateTime":0,"RelativeTime":0,"ReceivedSignalStrength":0,"RawValue":0,"TransmissionId":0,"BatteryLife":0,"UploadAttempts":0,"Uploaded":0,"UploaderBatteryLife":0,"FilteredValue":0 }

	def __init__(self):
		#print "BGReadings_Data initialisiert"
		self._id=0
		self.timestamp=0
		self.DateTime=''
		self.bg=0 
		self.raw_value=0 
		self.raw_timestamp=0 
		self.age_adjusted_raw_value=0
		self.filtered_value=0 
		self.sensor_age_at_time_of_estimation=0 
		self.possible_bad=False 
		self.slope=0 
		self.intercept=0  
		self.sensor_confidence=0 
		self.uploaded=0
		self.a=0  
		self.b=0 
		self.c=0
		self.ra=0  
		self.rb=0 
		self.rc=0
		
		self.calculated_value=0
		
		# print "Klasse BGReadings wurde erzeugt"
		if sensor.SensorisActive():
			SensorData=sensor.currentSensor()
			self.sensor=SensorData['_id']
		else:
			print "Kein Aktiver Sensor vorhanden "

			
	def write2db(self):
		if (self._id==0):
			sql="insert into " + db.tableNameBGReadingsdata + " ( timestamp, DateTime, bg, raw_value, raw_timestamp, age_adjusted_raw_value, filtered_value,"
			sql+=" sensor_age_at_time_of_estimation, possible_bad, slope, intercept, sensor_confidence, uploaded, a, b, c, ra, rb, rc ) Values ( "
			sql+="'" + str(self.timestamp)+ "', "
			sql+="'"+ self.DateTime +"' ,"
			sql+=str(self.bg)+", "
			sql+=str(self.raw_value)+", " 
			sql+=str(self.raw_timestamp)+", " 
			sql+=str(self.age_adjusted_raw_value)+", "
			sql+=str(self.filtered_value)+", " 
			sql+=str(self.sensor_age_at_time_of_estimation)+", " 
			sql+="'" + str(self.possible_bad)+"', " 
			sql+=str(self.slope)+", " 
			sql+=str(self.intercept)+", "  
			sql+=str(self.sensor_confidence)+", " 
			sql+=str(self.uploaded)+", " 
			sql+=str(self.a)+", " 
			sql+=str(self.b)+", " 
			sql+=str(self.c)+", " 
			sql+=str(self.ra)+", " 
			sql+=str(self.rb)+", " 
			sql+=str(self.rc)+") " 
			
			
			
			conn = sqlite3.connect(db.openapsDBName)
			conn.execute(sql)
			conn.commit()
			print "Records created successfully";
			sql="Select _id from " + db.tableNameBGReadingsdata + " ORDER BY _id desc LIMIT 1"
			# print "Select SQL->" + sql
			cur = conn.cursor()
			cur.execute(sql)
			data = cur.fetchone()
			self._id=data[0]
			conn.commit()
			conn.close()
		else:
			sql="update " + db.tableNameBGReadingsdata + " SET "
			sql+="timestamp='" + str(self.timestamp)+ "', "
			sql+="DateTime='"+ str(self.DateTime) +"', "
			sql+="bg="+str(self.bg)+", "
			sql+="raw_value="+str(self.raw_value)+", " 
			sql+="raw_timestamp="+str(self.raw_timestamp)+", " 
			sql+="age_adjusted_raw_value="+str(self.age_adjusted_raw_value)+", "
			sql+="filtered_value="+str(self.filtered_value)+", " 
			sql+="sensor_age_at_time_of_estimation="+str(self.sensor_age_at_time_of_estimation)+", " 
			sql+="possible_bad='" + str(self.possible_bad)+"', " 
			sql+="slope="+str(self.slope)+", " 
			sql+="intercept="+str(self.intercept)+", "  
			sql+="sensor_confidence="+str(self.sensor_confidence)+", " 
			sql+="uploaded="+str(self.uploaded)+", "
			sql+="a="+str(self.a)+", "
			sql+="b="+str(self.b)+", "
			sql+="c="+str(self.c)+", "
			sql+="ra="+str(self.ra)+", "
			sql+="rb="+str(self.rb)+", "
			sql+="rc="+str(self.rc)+" "
			sql+=" where _id="+str(self._id)
			conn = sqlite3.connect(db.openapsDBName)
			print "SQL -> " + sql;
			conn.execute(sql)
			conn.commit()
			print "Records update successfully";


	def getrawData(self):
		wdata=self.WixelData
		#sql = 'select _id, TransmitterId, CaptureDateTime, RelativeTime, ReceivedSignalStrength, RawValue, TransmissionId, BatteryLife, UploadAttempts, Uploaded, UploaderBatteryLife, FilteredValue '   
		#sql+= 'from ' + db.tableNameWixeldata + ' order by CaptureDateTime desc limit 1'

		sql="Select _id, timestamp, DateTime, bg, raw_value, raw_timestamp, age_adjusted_raw_value, filtered_value, sensor_age_at_time_of_estimation, "
		sql+="possible_bad, slope, intercept, sensor_confidence, uploaded, a, b, c, ra, rb, rc  from " + db.tableNameBGReadingsdata + " ORDER BY _id desc LIMIT 1"

		#print "(BGReadings)(getrawData)  SQL->" + sql
		conn = sqlite3.connect(db.openapsDBName)		
		cur = conn.cursor()
		cur.execute(sql)
		data = cur.fetchone()
		conn.close()
		if data!=None:
			wdata['_id']=data[0]
			wdata['TransmitterId']='0'
			wdata['CaptureDateTime']=data[1]
			wdata['RelativeTime']='0'
			wdata['ReceivedSignalStrength']='0'
			wdata['RawValue']=data[4]
			wdata['TransmissionId']='0'
			wdata['BatteryLife']=240
			wdata['UploadAttempts']='0'
			wdata['Uploaded']='0'
			wdata['UploaderBatteryLife']='0'
			wdata['FilteredValue']=data[7]
		else:
			print "(BGReadings)(getrawData)  No data available"
		return wdata;


	def getfirst(self):
		#print "getlatest"
		sql="Select _id, timestamp, DateTime, bg, raw_value, raw_timestamp, age_adjusted_raw_value, filtered_value, sensor_age_at_time_of_estimation, "
		sql+="possible_bad, slope, intercept, sensor_confidence, uploaded, a, b, c, ra, rb, rc  from " + db.tableNameBGReadingsdata + " ORDER BY _id asc LIMIT 1"
		conn = sqlite3.connect(db.openapsDBName)		
		cur = conn.cursor()
		cur.execute(sql)
		data = cur.fetchone()
		conn.close()
		if data<>None:
			if len(data)==20:
				self._id=data[0]
				self.timestamp=data[1]
				self.DateTime=data[2]
				self.bg=data[3]
				self.raw_value=data[4] 
				self.raw_timestamp=data[5] 
				self.age_adjusted_raw_value=data[6]
				self.filtered_value=data[7]
				self.sensor_age_at_time_of_estimation=data[8]
				self.possible_bad=data[9]
				self.slope=data[10]
				self.intercept=data[11]  
				self.sensor_confidence=data[12] 
				self.uploaded=data[13]
				self.a=data[14]
				self.b=data[15]
				self.c=data[16]
				self.ra=data[17]
				self.rb=data[18]
				self.rc=data[19]

	def getlatest(self):
		#print "getlatest"
		sql="Select _id, timestamp, DateTime, bg, raw_value, raw_timestamp, age_adjusted_raw_value, filtered_value, sensor_age_at_time_of_estimation, "
		sql+="possible_bad, slope, intercept, sensor_confidence, uploaded, a, b, c, ra, rb, rc  from " + db.tableNameBGReadingsdata + " ORDER BY _id desc LIMIT 1"
		conn = sqlite3.connect(db.openapsDBName)		
		cur = conn.cursor()
		cur.execute(sql)
		data = cur.fetchone()
		conn.close()

		if data<>None:
			if len(data)==20:
				self._id=data[0]
				self.timestamp=data[1]
				self.DateTime=data[2]
				self.bg=data[3]
				self.raw_value=data[4] 
				self.raw_timestamp=data[5] 
				self.age_adjusted_raw_value=data[6]
				self.filtered_value=data[7]
				self.sensor_age_at_time_of_estimation=data[8]
				self.possible_bad=data[9]
				self.slope=data[10]
				self.intercept=data[11]  
				self.sensor_confidence=data[12] 
				self.uploaded=data[13]
				self.a=data[14]
				self.b=data[15]
				self.c=data[16]
				self.ra=data[17]
				self.rb=data[18]
				self.rc=data[19]

	def getsecondlatest(self):
		sql="Select _id, timestamp, DateTime, bg, raw_value, raw_timestamp, age_adjusted_raw_value, filtered_value, sensor_age_at_time_of_estimation, "
		sql+="possible_bad, slope, intercept, sensor_confidence, uploaded, a, b, c, ra, rb, rc from " + db.tableNameBGReadingsdata + " ORDER BY _id desc LIMIT 2"
		conn = sqlite3.connect(db.openapsDBName)		
		cur = conn.cursor()
		cur.execute(sql)
		data1 = cur.fetchone()		
		data = cur.fetchone()
		conn.close()
		if data<>None:
			if len(data)==20:
				self._id=data[0]
				self.timestamp=data[1]
				self.DateTime=data[2]
				self.bg=data[3]
				self.raw_value=data[4] 
				self.raw_timestamp=data[5] 
				self.age_adjusted_raw_value=data[6]
				self.filtered_value=data[7]
				self.sensor_age_at_time_of_estimation=data[8]
				self.possible_bad=data[9]
				self.slope=data[10]
				self.intercept=data[11]  
				self.sensor_confidence=data[12] 
				self.uploaded=data[13]
				self.a=data[14]
				self.b=data[15]
				self.c=data[16]
				self.ra=data[17]
				self.rb=data[18]
				self.rc=data[19]

	def getthirdlatest(self):
		sql="Select _id, timestamp, DateTime, bg, raw_value, raw_timestamp, age_adjusted_raw_value, filtered_value, sensor_age_at_time_of_estimation, "
		sql+="possible_bad, slope, intercept, sensor_confidence, uploaded, a, b, c, ra, rb, rc from " + db.tableNameBGReadingsdata + " ORDER BY _id desc LIMIT 3"
		conn = sqlite3.connect(db.openapsDBName)		
		cur = conn.cursor()
		cur.execute(sql)
		data1 = cur.fetchone()		
		data2 = cur.fetchone()
		data = cur.fetchone()
		conn.close()
		if data<>None:
			if len(data)==20:
				self._id=data[0]
				self.timestamp=data[1]
				self.DateTime=data[2]
				self.bg=data[3]
				self.raw_value=data[4] 
				self.raw_timestamp=data[5] 
				self.age_adjusted_raw_value=data[6]
				self.filtered_value=data[7]
				self.sensor_age_at_time_of_estimation=data[8]
				self.possible_bad=data[9]
				self.slope=data[10]
				self.intercept=data[11]  
				self.sensor_confidence=data[12] 
				self.uploaded=data[13]
				self.a=data[14]
				self.b=data[15]
				self.c=data[16]
				self.ra=data[17]
				self.rb=data[18]
				self.rc=data[19]

	def getallnotuploaded(self):
		sql="Select _id, timestamp, DateTime, bg, raw_value, raw_timestamp, age_adjusted_raw_value, filtered_value, sensor_age_at_time_of_estimation, "
		sql+="possible_bad, slope, intercept, sensor_confidence, uploaded, a, b, c, ra, rb, rc from " + db.tableNameBGReadingsdata + " where uploaded = 0 ORDER BY _id desc LIMIT 500"
		print "SQL->" + sql
		conn = sqlite3.connect(db.openapsDBName)		
		cur = conn.cursor()
		cur.execute(sql)
		data = cur.fetchall()
		conn.close()
		if data<>None:
			return data

	def getlastBG(self,num):
		sql="Select _id, timestamp, DateTime, bg, raw_value, raw_timestamp, age_adjusted_raw_value, filtered_value, sensor_age_at_time_of_estimation, "
		sql+="possible_bad, slope, intercept, sensor_confidence, uploaded, a, b, c, ra, rb, rc from " + db.tableNameBGReadingsdata + " ORDER BY _id desc LIMIT " + str(num)
		#print "SQL->" + sql
		conn = sqlite3.connect(db.openapsDBName)		
		cur = conn.cursor()
		cur.execute(sql)
		data = cur.fetchall()
		conn.close()
		if data<>None:
			return data



	def setuploaded(self,_id,value):
		sql="update " + db.tableNameBGReadingsdata + " SET "
		sql+="uploaded="+str(value)+" "
		sql+=" where _id="+str(_id)
		conn = sqlite3.connect(db.openapsDBName)
		print "SQL -> " + sql;
		conn.execute(sql)
		conn.commit()
		print "Records update successfully";

		

if __name__ == "__main__":
	x = calibration_Data()
	x.slope=1.08
	x.intercept=-16.55
	x.save()
	
	y = calibration_Data()
	y.getlatestCal()
	print " Intercept -> " + str(y.intercept)
	print " Slope -> " + str(y.slope)
	

	
	
#dsfdsf