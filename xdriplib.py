#!/usr/bin/python

import json
import socket
import sys
import time
import os
import array
import math

import BGReadings
import sensor
from calibration import *

BESTOFFSET = (60000 * 0) # Assume readings are about x minutes off from actual!

def getTimeDelta(BRReading,CurSensor):
	return ((BRReading.timestamp-CurSensor['started_at'])*1.0)/1000/60/60
		
		
########################################################## 
#  calculateAgeAdjustedRawValue(hourssince, raw_data)
#  As Name say calculates the age adjusted RawValue 
#  

def calculateAgeAdjustedRawValue(hourssince, raw_data):	
	adjust_for = (86400000 * 1.9) - (hourssince*60*60*1000)
	#print "Adjust for -> " + str(adjust_for)
	if adjust_for > 0:
		age_adjusted_raw_value = (((.45) * (adjust_for / (86400000 * 1.9))) * raw_data) + raw_data
		#print "RAW VALUE ADJUSTMENT: FROM:" + str(raw_data) + " TO: " + str(age_adjusted_raw_value)
		return age_adjusted_raw_value
	else:
		#print "RAW VALUE ADJUSTMENT: FROM:" + str(raw_data) + " TO: " + str(raw_data)
		return raw_data
	
	
	

########################################################## 
#  calcCGMVAL(slope,intercept,BG_raw):
#  Calc CGm Value from RAW
#  needs Calibrationdata slope intercept and BG_RAW Value
#  gives back calibration corrected BG

def calcCGMVAL(slope,intercept,raw_data):
	print "(calcCGMVAL) xdrip raw_data 		-> " + str(raw_data/1000)
	print "(calcCGMVAL) xdrip slope 		-> " + str(slope)
	print "(calcCGMVAL) xdrip intercept 		-> " + str(intercept)
	bg=(((slope*1.0))*(raw_data*1.0/1000))+(intercept*1.0)
	print "(calcCGMVAL) xdrip BG 			-> " + str(bg)
	#bg=0
	return bg	
	

    # //*******INSTANCE METHODS***********//
def perform_calculations():
	find_new_curve();
	find_new_raw_curve();
	find_slope();


def find_slope():
	
	latest=BGReadings_Data()
	latest.getlatest()
	second_latest=BGReadings_Data()
	second_latest.getsecondlatest()
	
	if second_latest <> None:
		y1 = latest.bg;
		x1 = latest.timestamp;
		y2 = second_latest.bg;
		x2 = second_latest.timestamp;
		if y1 == y2:
			latest.calculated_value_slope = 0;
		else:
			latest.calculated_value_slope = (y2 - y1)/(x2 - x1);
	
		latest.write2db();

	if latest <> None:
		latest.calculated_value_slope = 0;
		latest.write2db();
	else:
		print "NO BG? COULDNT FIND SLOPE!"

def find_new_curve():
	latest=BGReadings_Data()
	latest.getlatest()
	
	secondlatest=BGReadings_Data()
	secondlatest.getsecondlatest()
	
	thirdlatest=BGReadings_Data()
	thirdlatest.getthirdlatest()
	
	if (thirdlatest.bg<>0 and secondlatest.bg<>0 and latest<>0 and 0):
	
		y3 = latest.bg;
		x3 = latest.timestamp;
		y2 = secondlatest.bg;
		x2 = secondlatest.timestamp;
		y1 = thirdlatest.bg;
		x1 = thirdlatest.timestamp;

		print "find_new_curve latest.bg ->" + str(y3)
		print "find_new_curve latest.timestamp ->" + str(x3)

		print "find_new_curve 2latest.bg ->" + str(y2)
		print "find_new_curve 2latest.timestamp ->" + str(x2)

		print "find_new_curve 3latest.bg ->" + str(y1)
		print "find_new_curve 3latest.timestamp ->" + str(x1)
		
		a = y1/((x1-x2)*(x1-x3)) + y2/((x2-x1)*(x2-x3))+   y3/((x3-x1)*(x3-x2));
		b = (-y1*(x2+x3) / ((x1-x2)*(x1-x3)) -y2*(x1+x3)/((x2-x1)*(x2-x3))-y3*(x1+x2)/((x3-x1)*(x3-x2)));
		c = (y1*x2*x3/((x1-x2)*(x1-x3))+y2*x1*x3/((x2-x1)*(x2-x3))+y3*x1*x2/((x3-x1)*(x3-x2)));

	elif (thirdlatest.bg<>0 and secondlatest.bg<>0):
		print "Not enough data to calculate parabolic rates - assume Linear"

		y2 = latest.bg;
		x2 = latest.timestamp;
		y1 = secondlatest.bg;
		x1 = secondlatest.timestamp;

		if y1 == y2 or x1 == x2:
			b = 0;
		else:
			b = (y2 - y1)/(x2 - x1);
		
		a = 0;
		c = -1 * ((latest.b * x1) - y1);

	else:
		print "Not enough data to calculate parabolic rates - assume static data"
		a = 0;
		b = 0;
		c = latest.calculated_value;

		print ""+str(a)+"x^2 + "+str(b)+"x + "+str(c)

	print "BG PARABOLIC RATES: "+str(a)+"x^2 + "+str(b)+"x + "+str(c)
	latest.a = a
	latest.b = b
	latest.c = c
	latest.write2db

def estimated_bg(timestamp):
	timestamp = timestamp + BESTOFFSET;
	latest = BGReadings_Data()
	latest.getlatest()
	if (latest == None):
		return 0;
	else:
		return (latest.a * timestamp * timestamp) + (latest.b * timestamp) + latest.c;

		
def estimated_raw_bg(timestamp):
	timestamp = timestamp + BESTOFFSET;
	estimate=0;
	latest = BGReadings_Data()
	latest.getlatest()
	if (latest == None):
		# Todo Was soll das ?
		Log.i(TAG, "No data yet, assume perfect!");
		estimate = 160;
	else:
		estimate = (latest.ra * timestamp * timestamp) + (latest.rb * timestamp) + latest.rc;
	
	print "ESTIMATE RAW BG" + str(estimate)
	return estimate;

	
		
def find_new_raw_curve():
	CurSensor=sensor.currentSensor()
	first_latest = BGReadings_Data()
	first_latest.getlatest()
	
	second_latest = BGReadings_Data()
	second_latest.getsecondlatest()
	
	third_latest = BGReadings_Data()
	third_latest.getthirdlatest()
			
	if third_latest.raw_value<>0:
		y3 = calculateAgeAdjustedRawValue(getTimeDelta(first_latest,CurSensor),first_latest.raw_value)
		x3 = first_latest.timestamp;
		y2 = calculateAgeAdjustedRawValue(getTimeDelta(second_latest,CurSensor),second_latest.raw_value);
		x2 = second_latest.timestamp;
		y1 = calculateAgeAdjustedRawValue(getTimeDelta(third_latest,CurSensor),third_latest.raw_value);
		x1 = third_latest.timestamp;
		print "x1" + str(x1) + ", y1 " +str(y1) + ", "
		print "x2" + str(x2) + ", y2 " +str(y2) + ", "
		print "x3" + str(x3) + ", y3 " +str(y3) + ", "
		
		first_latest.ra = y1/((x1-x2)*(x1-x3))+y2/((x2-x1)*(x2-x3))+y3/((x3-x1)*(x3-x2));
		first_latest.rb = (-y1*(x2+x3)/((x1-x2)*(x1-x3))-y2*(x1+x3)/((x2-x1)*(x2-x3))-y3*(x1+x2)/((x3-x1)*(x3-x2)));
		first_latest.rc = (y1*x2*x3/((x1-x2)*(x1-x3))+y2*x1*x3/((x2-x1)*(x2-x3))+y3*x1*x2/((x3-x1)*(x3-x2)));
		
		print "RAW PARABOLIC RATES: "+str(first_latest.ra)+"x^2 + "+str(first_latest.rb)+"x + "+str(first_latest.rc)
		first_latest.write2db();

	elif second_latest.raw_value<>0:
		y2 = calculateAgeAdjustedRawValue(getTimeDelta(first_latest,CurSensor),first_latest.raw_value);
		x2 = first_latest.timestamp;
		y1 = calculateAgeAdjustedRawValue(getTimeDelta(second_latest,CurSensor),second_latest.raw_value);
		x1 = second_latest.timestamp;

		if y1 == y2:
			first_latest.rb = 0;
		else:
			first_latest.rb = (y2 - y1)/(x2 - x1);

		first_latest.ra = 0;
		first_latest.rc = -1 * ((first_latest.rb * x1) - y1);

		print "Not enough data to calculate parabolic rates - assume Linear data"
		print "RAW PARABOLIC RATES: "+str(first_latest.ra)+"x^2 + "+str(first_latest.rb)+"x + "+str(first_latest.rc)
		first_latest.write2db();
	else:
		first_latest.ra = 0;
		first_latest.rb = 0;
		first_latest.rc = first_latest.age_adjusted_raw_value;
		print "Not enough data to calculate parabolic rates - assume static data"
		print "RAW PARABOLIC RATES: "+str(first_latest.ra)+"x^2 + "+str(first_latest.rb)+"x + "+str(first_latest.rc)
		first_latest.write2db();

    
    
		
def weightedAverageRaw(timeA, timeB, calibrationTime, rawA, rawB):
	relativeSlope = (rawB -  rawA)/(timeB - timeA);
	relativeIntercept = rawA - (relativeSlope * timeA);
	return ((relativeSlope * calibrationTime) + relativeIntercept);
	
	
def ___calcCGMVAL(slope,BG_raw,intercept):
	raw_data=calculateAgeAdjustedRawValue(66,BG_raw)
	bg=(((slope*1.0)/1000)*(raw_data*1.0/1000))+(intercept*1.0)
	print "xdrip raw_data ->" + str(raw_data/1000)
	print "xdrip slope ->" + str(slope/1000)
	print "xdrip intercept ->" + str(intercept)
	print "xdrip BG ->" + str(bg)
	return bg

def slopeOOBHandler(status):
	#// If the last slope was reasonable and reasonably close, use that, otherwise use a slope that may be a little steep, but its best to play it safe when uncertain
	#List<Calibration> calibrations = Calibration.latest(3);
	#Calibration thisCalibration = calibrations.get(0);
	#// Status = 0 niedrig 1 hoch
	#if(status == 0) {
	#    if (calibrations.size() == 3) {
	#        if ((Math.abs(thisCalibration.bg - thisCalibration.estimate_bg_at_time_of_calibration) < 30) && (calibrations.get(1).possible_bad != null && calibrations.get(1).possible_bad == true)) {
	#            return calibrations.get(1).slope;
	#        } else {
	#            return Math.max(((-0.048) * (thisCalibration.sensor_age_at_time_of_estimation / (60000 * 60 * 24))) + 1.1, 1.08);
	#        }
	#    } else if (calibrations.size() == 2) {
	#        return Math.max(((-0.048) * (thisCalibration.sensor_age_at_time_of_estimation / (60000 * 60 * 24))) + 1.1, 1.15);
	#    }
	#    return 1;
	#} else {
	#    if (calibrations.size() == 3) {
	#        if ((Math.abs(thisCalibration.bg - thisCalibration.estimate_bg_at_time_of_calibration) < 30) && (calibrations.get(1).possible_bad != null && calibrations.get(1).possible_bad == true)) {
	#            return calibrations.get(1).slope;
	#        } else {
	#            return 1.3;
	#        }
	#    } else if (calibrations.size() == 2) {
	#        return 1.2;
	#    }
	#}
	#return 1;
	return 1.08



	
def calculateWeight(sensor_age_at_time_of_estimation,slope_confidence,sensor_confidence):
	calibration=calibration_Data()
	calibration.getfirst()
	firstTimeStarted =   calibration.sensor_age_at_time_of_estimation
	
	calibration.getlatest()
	lastTimeStarted =   calibration.sensor_age_at_time_of_estimation;
	
	print "(calculateWeight) lastTimeStarted->" + str(lastTimeStarted) + " firstTimeStarted " + str(firstTimeStarted)
	print "(calculateWeight) sensor_age_at_time_of_estimation " + str(sensor_age_at_time_of_estimation)
	
	# HMM irgendwie gibt es da verschiedene Versionen
	if (sensor_age_at_time_of_estimation<>firstTimeStarted):
		time_percentage = min(((sensor_age_at_time_of_estimation - firstTimeStarted) / (lastTimeStarted - firstTimeStarted)) / (.85), 1);
	else:
		time_percentage=0
		
	time_percentage = (time_percentage + .01);
	print "(calculateWeight) CALIBRATIONS TIME PERCENTAGE WEIGHT: " + str(time_percentage)
	return max((((((slope_confidence + sensor_confidence) * (time_percentage))) / 2) * 100), 1);

	
	
def calculate_w_l_s():

	calibration=calibration_Data()
	calibration.getlatest()
	
	if calibration.sensorid<>0:
		l = 0;
		m = 0;
		n = 0;
		p = 0;
		q = 0;
		
		
		calibrations = calibration.allForSensorInLastFourDays() # 5 days was a bit much, dropped this to 4
		
		# Also eigentlich kann der code hier nie durchkommen. Versteckter Hinweis bei der initial calibrierung werden bereits 2 objecte erzeugt.
		if (len(calibrations) == 1):
			calibration.slope = 1;
			calibration.intercept = calibration.bg - (calibration.raw_value * calibration.slope);
		else:
			for c in calibrations:
				sensor_age_at_time_of_estimation=c[2]
				bg=c[4]
				sensor_confidence=c[8]
				slope_confidence=c[9]
				estimate_raw_at_time_of_calibration=c[14]
				
				print "sensor_age_at_time_of_estimation " + str(sensor_age_at_time_of_estimation)
				print "bg " + str(bg)
				print "sensor_confidence " + str(sensor_confidence)
				print "slope_confidence  " + str(slope_confidence)
				print "estimate_raw_at_time_of_calibration " + str(estimate_raw_at_time_of_calibration)
				
				
				w = calculateWeight(sensor_age_at_time_of_estimation,slope_confidence,sensor_confidence);
				l += (w);
				m += (w * estimate_raw_at_time_of_calibration);
				q += (w * estimate_raw_at_time_of_calibration * bg);

				n += (w * estimate_raw_at_time_of_calibration * estimate_raw_at_time_of_calibration);
				p += (w * bg);


			last_calibration = calibration_Data()
			last_calibration.getlatest()
			
			w = ( calculateWeight(last_calibration.sensor_age_at_time_of_estimation,last_calibration.slope_confidence,last_calibration.sensor_confidence) * (len(c) * 0.14));
			l += (w);
			m += (w * last_calibration.estimate_raw_at_time_of_calibration);
			n += (w * last_calibration.estimate_raw_at_time_of_calibration * last_calibration.estimate_raw_at_time_of_calibration);
			p += (w * last_calibration.bg);
			q += (w * last_calibration.estimate_raw_at_time_of_calibration * last_calibration.bg);
			
			d = (l * n) - (m * m);
			
			
			print "w ->" + str(w)
			print "l ->" + str(l)
			print "n ->" + str(n)
			print "p ->" + str(p)

			print "m ->" + str(m)
			print "q ->" + str(q)

			print "d ->" + str(d)
			
			print "n*p" + str(n*p)
			print "m*q" + str(m*q)
			
			calibration.intercept = ((n * p) - (m * q)) / d;
			calibration.slope = ((l * q) - (m * p)) / d;
			print "(1) Calculated Calibration Slope: " + str(calibration.slope)
			print "(1) Calculated Calibration intercept: " + str(calibration.intercept)
			
		# TODO Denke hier ist einer der interessantesten Teile der Software.
		if 1==1:
			if ((len(calibrations) == 2 and calibration.slope < 0.95) or (calibration.slope < 0.85)): 
				# I have not seen a case where a value below 7.5 proved to be accurate but we should keep an eye on this
				calibration.slope = slopeOOBHandler(0);
				if(len(calibrations) > 2):
					calibration.possible_bad = True
				
				print "calibration.bg->										" +  str(calibration.bg)
				print "calibration.estimate_raw_at_time_of_calibration -> 	" + str(calibration.estimate_raw_at_time_of_calibration)
				print "calibration.slope ->									" + str(calibration.slope) 
				calibration.intercept = calibration.bg - ((calibration.estimate_raw_at_time_of_calibration*1.0/1000) * calibration.slope)
				# CalibrationRequest.createOffset(calibration.bg, 25);
				
				
			if ((len(calibrations) == 2 and calibration.slope > 1.3) or (calibration.slope > 1.4)):
				calibration.slope = slopeOOBHandler(1);
				if(calibrations.size() > 2):
					calibration.possible_bad = True

				print "(calibration.bg) ->" + str(calibration.bg)
				
				# Hier ist eine Null drin !!!!
				
				print "(calibration.estimate_raw_at_time_of_calibration) ->" + str(calibration.estimate_raw_at_time_of_calibration)
				print "(calibration.slope) ->" + str(calibration.slope)
				calibration.intercept = calibration.bg - ((calibration.estimate_raw_at_time_of_calibration*1.0/1000) * calibration.slope)
				# CalibrationRequest.createOffset(calibration.bg, 25);
		
		
		print "(2) Calculated Calibration Slope: " + str(calibration.slope)
		print "(2) Calculated Calibration intercept: " + str(calibration.intercept)
		calibration.save();
	else:
		print "NO Current active sensor found!!"

		
def create(bg):


	calibration = calibration_Data();
	#sens = sensor();
	bgReading=BGReadings_Data()
	
	if (sensor.SensorisActive()):
		sens = sensor.currentSensor()
		bgReading.getlatest()
		if (bgReading._id <> 0):
			calibration.sensor = sensor;
			calibration.bg = bg;
			calibration.check_in = False;
			calibration.timestamp = long(str(int(time.time()))+"000")
			calibration.raw_value = bgReading.raw_value;
			calibration.age_adjusted_raw_value = bgReading.age_adjusted_raw_value;
			calibration.sensor_uuid = "Sensor_uuid";
			calibration.slope_confidence = min(max(((4 - abs((bgReading.slope) * 60000))/4), 0), 1);

			estimated_raw_bg_value = estimated_raw_bg(long(str(int(time.time()))+"000"));

			calibration.raw_timestamp = bgReading.timestamp;
			
			print "(create) estimated_raw_bg_value ->" + str(estimated_raw_bg_value)
			print "(create) bgReading.age_adjusted_raw_value ->" + str(bgReading.age_adjusted_raw_value)
			
			if (abs(estimated_raw_bg_value - bgReading.age_adjusted_raw_value) > 20):
				print "create(bg) bgReading.age_adjusted_raw_value ->" + str(bgReading.age_adjusted_raw_value)
				calibration.estimate_raw_at_time_of_calibration = bgReading.age_adjusted_raw_value
			else:
				print "create(bg)estimated_raw_bg_value ->" + str(estimated_raw_bg_value)
				calibration.estimate_raw_at_time_of_calibration = estimated_raw_bg_value
				
			calibration.distance_from_estimate = abs(calibration.bg - bgReading.calculated_value);
			calibration.sensor_confidence = max(((-0.0018 * bg * bg) + (0.6657 * bg) + 36.7505) / 100, 0);
			calibration.sensor_age_at_time_of_estimation = calibration.timestamp - sens['started_at'];
			calibration.uuid = "CalUUI"
			calibration.save();

			bgReading.calibration = calibration;
			bgReading.calibration_flag = True;
			bgReading.write2db();
			#BgSendQueue.handleNewBgReading(bgReading, "update", context);

			calculate_w_l_s();
			#adjustRecentBgReadings();
			#CalibrationSendQueue.addToQueue(calibration, context);
			#context.startService(new Intent(context, Notifications.class));
			#Calibration.requestCalibrationIfRangeTooNarrow();
	else:
            print "CALIBRATION", "No sensor, cant save!"


def initialCalibration( bg1,  bg2 ):
	unit = "mg/DL"

	#if(unit.compareTo("mgdl") != 0 ) :
	#	bg1 = bg1 * Constants.MMOLL_TO_MGDL;
	#	bg2 = bg2 * Constants.MMOLL_TO_MGDL;
	
	
	# muss noch.
	calib = calibration_Data()
	calib.clear_all_existing_calibrations()

	
	higherCalibration =  calibration_Data();
	lowerCalibration =  calibration_Data();
	sens = sensor.currentSensor()
	
	Last2 = BGReadings.latestRaw(2)
	if len(Last2)<2:
		print "(initialCalibration) Hmm benoetige ersteinmal 2 BG Readings"
		return False
	
	bgReading1 = Last2[0];
	bgReading2 = Last2[1];
	higher_bg = max(bg1, bg2);
	lower_bg = min(bg1, bg2);

	highBgReading=BGReadings_Data()
	lowBgReading=BGReadings_Data()
	
	
	if (bgReading1[0] > bgReading2[0]) :
		highBgReading.raw_value = bgReading1[0]
		highBgReading.raw_timestamp = bgReading1[1]
		highBgReading.age_adjusted_raw_value = bgReading1[2]

		lowBgReading.raw_value = bgReading2[0]
		lowBgReading.raw_timestamp = bgReading2[1]
		lowBgReading.age_adjusted_raw_value = bgReading2[2]
	else:
		highBgReading.raw_value = bgReading2[0]
		highBgReading.raw_timestamp = bgReading2[1]
		highBgReading.age_adjusted_raw_value = bgReading2[2]

		lowBgReading.raw_value = bgReading1[0]
		lowBgReading.raw_timestamp = bgReading1[1]
		lowBgReading.age_adjusted_raw_value = bgReading1[2]
	
	
	
	print "highBgReading.raw_value -> " + str(highBgReading.raw_value)
	print "lowBgReading.raw_value -> " + str(lowBgReading.raw_value)
	
	higherCalibration.bg = higher_bg
	higherCalibration.slope = 1
	higherCalibration.intercept = higher_bg

	print "cal high intercept " + str(higherCalibration.intercept)
	print "cal high adjraw    " + str(highBgReading.age_adjusted_raw_value)
	print "cal high higherbg  " + str(higher_bg)

	higherCalibration.sensor = sens
	higherCalibration.estimate_raw_at_time_of_calibration = highBgReading.age_adjusted_raw_value
	higherCalibration.age_adjusted_raw_value = highBgReading.age_adjusted_raw_value
	higherCalibration.raw_value = highBgReading.raw_value
	higherCalibration.raw_timestamp = highBgReading.raw_timestamp
	higherCalibration.save()

	highBgReading.bg = higher_bg
	highBgReading.calibration_flag = True
	highBgReading.calibration = higherCalibration
	higherCalibration.save()

	lowerCalibration.bg = lower_bg
	lowerCalibration.slope = 1
	
	lowerCalibration.intercept = lower_bg
	print "cal low intercept " + str(lowerCalibration.intercept)
	print "cal low adjraw    " + str(lowBgReading.age_adjusted_raw_value)
	print "cal low higherbg  " + str(lower_bg)
	
	lowerCalibration.sensor = sens
	lowerCalibration.estimate_raw_at_time_of_calibration = lowBgReading.age_adjusted_raw_value
	lowerCalibration.age_adjusted_raw_value = lowBgReading.age_adjusted_raw_value
	lowerCalibration.raw_value = lowBgReading.raw_value
	lowerCalibration.raw_timestamp = lowBgReading.raw_timestamp
	
	lowBgReading.bg = lower_bg
	lowBgReading.calibration_flag = True
	lowBgReading.calibration = lowerCalibration
	lowerCalibration.save()

	
	lowBgReading.timestamp=long(str(int(time.time()))+"000")
	lowBgReading.sensor_uuid='Sensor_uuid'
	lowBgReading.slope_confidence = 0.5
	lowBgReading.distance_from_estimate = 0
	lowBgReading.check_in = False
	lowBgReading.sensor_confidence = ((-0.0018 * lowBgReading.bg * lowBgReading.bg) + (0.6657 * lowBgReading.bg) + 36.7505) / 100;
	lowBgReading.sensor_age_at_time_of_estimation = lowBgReading.timestamp - sens['started_at']
	lowBgReading.uuid = 'randomUUID'
	lowBgReading.write2db()
	
	highBgReading.timestamp=long(str(int(time.time()))+"000")	
	highBgReading.sensor_uuid='Sensor_uuid'
	highBgReading.slope_confidence = 0.5
	highBgReading.distance_from_estimate = 0
	highBgReading.check_in = False
	highBgReading.sensor_confidence = ((-0.0018 * highBgReading.bg * highBgReading.bg) + (0.6657 * highBgReading.bg) + 36.7505) / 100;
	highBgReading.sensor_age_at_time_of_estimation = highBgReading.timestamp - sens['started_at']
	highBgReading.uuid = 'randomUUID'
	highBgReading.write2db()
	
	
	
	find_new_curve()
	find_new_raw_curve()

	#highBgReading.find_new_raw_curve();
	#lowBgReading.find_new_curve();
	#lowBgReading.find_new_raw_curve();

	
	
	lowerCalibration.timestamp = long(str(int(time.time()))+"000")
	lowerCalibration.sensor_uuid = sens['uuid']
	lowerCalibration.slope_confidence = 0.5
	lowerCalibration.distance_from_estimate = 0
	lowerCalibration.check_in = False
	lowerCalibration.sensor_confidence = ((-0.0018 * lowerCalibration.bg * lowerCalibration.bg) + (0.6657 * lowerCalibration.bg) + 36.7505) / 100
	lowerCalibration.sensor_age_at_time_of_estimation = lowerCalibration.timestamp - sens['started_at']
	lowerCalibration.uuid = "CALIBRATION UUID"
#	lowerCalibration.calculate_w_l_s()
	lowerCalibration.save()

	higherCalibration.timestamp = long(str(int(time.time()))+"000")
	higherCalibration.sensor_uuid = sens['uuid']
	higherCalibration.slope_confidence = 0.5
	higherCalibration.distance_from_estimate = 0
	higherCalibration.check_in = False
	higherCalibration.sensor_confidence = ((-0.0018 * higherCalibration.bg * higherCalibration.bg) + (0.6657 * higherCalibration.bg) + 36.7505) / 100
	higherCalibration.sensor_age_at_time_of_estimation = higherCalibration.timestamp - sens['started_at']
	higherCalibration.uuid = "CALIBRATION UUID"
	higherCalibration.save()

	calculate_w_l_s()
	


	# Todo macht sinn umzusetzen !!
	#adjustRecentBgReadings(5);
	
	
	#CalibrationRequest.createOffset(lowerCalibration.bg, 35);
	
	#context.startService(new Intent(context, Notifications.class));
