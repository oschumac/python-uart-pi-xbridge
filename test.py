import json
import socket
import sys
import time
import os
from thread import *
from struct import *

import serial

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import Image
import ImageFont
import ImageDraw
import wixellib
import xdriplib
import BGReadings
import db
import sensor


from calibration import *



# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0


def sendScreen(Tid):
	disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
	disp.begin()
	width = disp.width
	height = disp.height
	padding = 2
	shape_width = 20
	top = padding
	bottom = height-padding
	x = 10
	
	image = Image.new('1', (width, height))
	# Load default font.
	# font = ImageFont.load_default()
	font = ImageFont.truetype('Verdana.ttf', 12)

	
	
	draw = ImageDraw.Draw(image)
	draw.text((x, top),    '* TEST *',  font=font, fill=255)
	draw.text((x, top+12), 'Raw (5m) IOB:0.4 U ', font=font, fill=255)
	draw.text((x, top+24), 'Basal 0.7 U (120%)', font=font, fill=255)
	draw.text((x, top+36), 'BG Rising', font=font, fill=255)
	draw.text((x, top+48), 'TiD->' + Tid , font=font, fill=255)

	# Display image.
	disp.image(image)
	disp.display()


db.initDB()


# ID=BGReadings.StartSensor()
# BGReadings.StopSensor()

if sensor.SensorisActive():
	CurSensor=sensor.currentSensor()
	data=BGReadings.getrawData()
	TimeDelta=((data['CaptureDateTime']-CurSensor['started_at'])*1.0)/1000/60/60
	Adjusted_raw=xdriplib.calculateAgeAdjustedRawValue(TimeDelta,int(data['RawValue']))

	#BGReadings.updateSensorLocation('BUTT')

	
# WixelData = {"_id":1,"TransmitterId":"12345","CaptureDateTime":0,"RelativeTime":0,"ReceivedSignalStrength":0,"RawValue":155000,"TransmissionId":0,"BatteryLife":240,"UploadAttempts":0,"Uploaded":0,"UploaderBatteryLife":123,"FilteredValue":160000 }

# BGReadings.insertIntoWixeldata(WixelData)
	
print "BGReadings Current Transmitter id 	-> " + str(wixellib.dexcom_src_to_asc(data['TransmitterId']))
print "BGReadings Current RawValue 		-> " + str(data['RawValue'])

print "BGReadings Current CaptureDateTime 	-> " + str(long(data['CaptureDateTime']))
print "BGReadings Current CaptureDateTime 	-> " + time.strftime("%d.%m.%Y -%H:%M:%S", time.localtime(long(data['CaptureDateTime'])/1000))
print "BGReadings AgeAdjustedRaw 		-> " + str(Adjusted_raw)
print "BGReadings Time since Sensor Start 	-> " + str(TimeDelta) + " Stunden"






print "***********************************************************************************"
Y=BGReadings_Data()
Y.getlatest()
print "latest BG        ->" + str(Y.bg)	
Y.getsecondlatest()
print "secondlatest BG  ->" + str(Y.bg)	
Y.getthirdlatest()
print "thirdlatest BG   ->" + str(Y.bg)	



print "***********************************************************************************"

#xdriplib.initialCalibration( 106,  107 )
#xdriplib.find_new_curve();
#xdriplib.find_new_raw_curve();
#xdriplib.find_slope()

#xdriplib.create(82)



#Calib=calibration_Data()
#calibdata = Calib.allForSensorInLastFourDays()
#if calibdata<>None:
#	print "calibdata = Calib.allForSensorInLastFourDays() brachte " + str(len(calibdata)) + " Datenreihen zurueck"
#	print calibdata
#else:
#	print "calibdata = Calib.allForSensorInLastFourDays() brachte keine Datenreihen zurueck"
	