#!/usr/bin/python
# 
# Orginal Script was writen by jamorham.
# Thanks for the Idea
# 
# Basic changes are Wixel is connected via UART
# Wixel app is xbridge so Transmitter ID got send from Python
# 
# xbridge app needs to be changed so it sends <CR> <LF>
# void send_data( uint8 *msg, uint8 len)
# {
#	uint8 i = 0;
#	//wait until uart1 Tx Buffer is empty
#	while(uart1TxAvailable() < len) {};
#	for(i=0; i < len; i++)
#	{
#		uart1TxSendByte(msg[i]);
#	}
#	msg[i+1]=10;                                                <- This ones are not in the org Wixel app
#	msg[i+2]=13;                                                <- This ones are not in the org Wixel app
#	uart1TxSendByte(msg[i+1]);                                  <- This ones are not in the org Wixel app
#	uart1TxSendByte(msg[i+2]);                                  <- This ones are not in the org Wixel app
#	
#	while(uart1TxAvailable()<255) waitDoingServices(20,0,1);
#	if(usb_connected) {
#		printf_fast("Sending: ");
#		while(usbComTxAvailable() < len) {};
#		for(i=0; i < len; i++)
#		{
#			usbComTxSendByte(msg[i]);
#		}
#		while(usbComTxAvailable()<128) waitDoingServices(20,0,1);
#		printf_fast("\r\nResponse: ");
#	}
# }

import json
import socket
import sys
import time
import os
import array
import math
from thread import *
import datetime
                    
import serial

# Project imports
import wixellib
import xdriplib
import BGReadings
from calibration import *
import db

# Display imports
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import Image
import ImageFont
import ImageDraw

# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0


 
HOST = ''   # All
PORT = 50005 # xdrip standard port



my_TransmitterID="6DGTF";
#my_TransmitterID="6BBL0";
#my_TransmitterID="00000";

Bridge_Tid="";

# Eigenes PID file fuer Service
PIDFILE='/home/pi/Wixel/pid'  


mydata = { "TransmitterId":"0","_id":1,"CaptureDateTime":0,"RelativeTime":0,"ReceivedSignalStrength":0,"RawValue":0,"TransmissionId":0,"BatteryLife":0,"UploadAttempts":0,"Uploaded":0,"UploaderBatteryLife":0,"FilteredValue":0 }


BG=0
LASTBG=0

    
########################################################## BGlatest
#  sendScreen():
#  Sends Textdata to Adafrout OLED Display SPI
#  
	
def sendScreen():
	global disp
	
	
	
	width = disp.width
	height = disp.height
	padding = 2
	shape_width = 20
	top = padding
	bottom = height-padding
	x = 10

	BGlatest=BGReadings_Data()
	BGlatest.getlatest()

	BGsecondlatest=BGReadings_Data()
	BGsecondlatest.getsecondlatest()
	
	
	image = Image.new('1', (width, height))
	# Load default font.
	# font = ImageFont.load_default()
	font = ImageFont.truetype('Verdana.ttf', 11)
		
	draw = ImageDraw.Draw(image)
	draw.text((x, top),    '* TEST *',  font=font, fill=255)
	#draw.text((x, top+12), 'Raw: '+ str(mydata['RawValue']), font=font, fill=255)
	draw.text((x, top+12), 'CGM   : ' + str(math.ceil(BGlatest.bg)) + '(' + str(BGlatest.bg-BGsecondlatest.bg) + ')' , font=font, fill=255)
	draw.text((x, top+24), 'Zeit: ' + str(BGlatest.DateTime), font=font, fill=255)
	draw.text((x, top+36), 'Signal: ' + str(mydata['ReceivedSignalStrength']), font=font, fill=255)
	draw.text((x, top+48), 'Dex ID: ' + wixellib.dexcom_src_to_asc(mydata['TransmitterId']) , font=font, fill=255)

	# Display image.
	disp.image(image)
	disp.display()


########################################################## 
#  send_TID_wixel(ser,Tid):
#  sends Transmitter ID to Wixel
#  is needed if Wixel sends Beacon Telgrammms or
#  if aplication sens wixel sending wrong Tid's
#  to correct Wixels behavour

def send_TID_wixel(ser,Tid):
	# 0 0x06 Number of bytes in the packet (6).
	# 1 0x01 Code for Data Packet
	# 2:5 TxID Encoded 32 bit integer representing the Dexcom G4 Transmitter ID that the bridge is filtering packets on.

	number=wixellib.asciiToDexcomSrc(Tid)
	sendbytes=[0]*6
	sendbytes[0]=0x06
	sendbytes[1]=0x01
	sendbytes[2]=number & 0xff
	sendbytes[3]=(number >>8) & 0xff;
	sendbytes[4]=(number >>16) & 0xff;
	sendbytes[5]=(number >>24) & 0xff;

	print "Daten Senden ->" + ":".join("{:02x}".format(c) for c in sendbytes)

	ser.write(sendbytes)

	
########################################################## 
#  send_ACK_wixel(ser):
#  sends ACK Telegramm to Wixel
#  is needed to ACK a Data Telegramm 
#

def send_ACK_wixel(ser):
	sendbytes=[0]*2
	sendbytes[0]=0x02   # Lenght of Telegramm
	sendbytes[1]=0xF0   # Telegrammcode for ack Datatelegramm
	print "ACK Senden ->" + ":".join("{:02x}".format(c) for c in sendbytes)
	ser.write(sendbytes)

	
# threads

def serialthread(dummy):
    global mydata
    global BG
    global LASTBG
    print "start serial com"
    firstrun=True 
    while 1:
        try:
            # sometimes the wixel reboots and comes back as a different
            # device - this code seemed to catch that happening
            # more complex code might be needed if the pi has other
            # ACM type devices.
            
            ser = serial.Serial('/dev/ttyAMA0', 9600)
            serial_line="00000"
			
            if (firstrun==False):
                serial_line = ser.readline()
                print "Laenge->" + str(len(serial_line))
                print "Daten Empfangen->" + ":".join("{:02x}".format(ord(c)) for c in serial_line)
                if ord(serial_line[0])>len(serial_line):
                    print "Huston wir haben ein Prob"
                    serial_line="00000"
					
            else:
                print "Startup Transmitter ID senden ->" + str(my_TransmitterID)
                send_TID_wixel(ser,my_TransmitterID)
                firstrun=False

            if ((serial_line[1]=="\xf1")):
                print "Beacon Empfangen!!"
                send_TID_wixel(ser,my_TransmitterID)
                # Testdaten
                #mydata['CaptureDateTime']=str(int(time.time()))+"000"
                #mydata['RelativeTime']="0"
                #mydata['RawValue']="155000"
                
                #mydata['FilteredValue']="155000"
                #mydata['BatteryLife']="240"
                #mydata['TransmitterId']="00000"
                #mydata['ReceivedSignalStrength']=0
                #mydata['TransmissionId']=0
                # BGReadings.insertIntoWixeldata(mydata)
                
                # print "Time adjusted raw" + str(xdriplib.calculateAgeAdjustedRawValue(5,155000))
                # 1,080-80,36
	
            if (serial_line[1]=="\x00") and (len(serial_line)==18):
                print "Dexcom Daten empfangen"
                # simple space delimited data records
                # update dictionary - no sanity checking here
                #  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17
                # 11:00:00:00:00:00:00:00:00:00:bc:00:de:5e:63:00:01:0a
                # 		 |		  | 		     |  |  |		   | Protokoll Level
                #        |        |              |  |  |-------------Transmitter ID
                #        |        |              |  |----------------Bridge Batterie
                #        |        |              |-------------------Dexcom batterie
                #        |        |----------------------------------Filtered Data
                #		 |-------------------------------------------Raw
                
                				
                mydata['CaptureDateTime']=str(int(time.time()))+"000"
                mydata['RelativeTime']="0"
                mydata['RawValue']=str(int(ord(serial_line[2])+(ord(serial_line[3])*256)+(ord(serial_line[4])*65536)+(ord(serial_line[5])*16777216)))
                
                mydata['FilteredValue']=str(int(ord(serial_line[6])+(ord(serial_line[7])*256)+(ord(serial_line[8])*65536)+(ord(serial_line[9])*16777216)))
                mydata['BatteryLife']=str(ord(serial_line[10]))
                mydata['TransmitterId']=str(int(ord(serial_line[12])+(ord(serial_line[13])*256)+(ord(serial_line[14])*65536)+(ord(serial_line[15])*16777216)))
                mydata['ReceivedSignalStrength']=0
                mydata['TransmissionId']=0
                print "Receive" + json.dumps(mydata)


                send_ACK_wixel(ser)
				
                if wixellib.dexcom_src_to_asc(mydata['TransmitterId'])==my_TransmitterID:
                    print "Neue daten Da !!!!!"
                    BGReadings.insertIntoWixeldata(mydata)
                    
                    BGData=BGReadings_Data()
                    CurSensor=sensor.currentSensor()
                    Calib=calibration_Data()
                    Calib.getlatest()
                    
                    BGData.raw_value=long(ord(serial_line[2])+(ord(serial_line[3])*256)+(ord(serial_line[4])*65536)+(ord(serial_line[5])*16777216))
                    BGData.filtered_value=int(ord(serial_line[6])+(ord(serial_line[7])*256)+(ord(serial_line[8])*65536)+(ord(serial_line[9])*16777216))
                    BGData.raw_timestamp=long(str(int(time.time()))+"000")
					
                    
                    BGData.timestamp = BGData.raw_timestamp
                    BGData.DateTime = datetime.datetime.fromtimestamp((BGData.timestamp/1000)).strftime('%Y-%m-%d %H:%M:%S')
                    print "BGData.Datetime -> " + BGData.DateTime 
                    
                    BGData.slope = Calib.slope
                    BGData.intercept = Calib.intercept
                    BGData.sensor_confidence = Calib.sensor_confidence

                    
                    BGData.age_adjusted_raw_value= xdriplib.calculateAgeAdjustedRawValue(xdriplib.getTimeDelta(BGData,CurSensor),BGData.raw_value)
                    BGData.sensor_age_at_time_of_estimation=CurSensor['started_at']
                    
                    
                    BGData.bg=xdriplib.calcCGMVAL(Calib.slope,Calib.intercept,BGData.age_adjusted_raw_value)
                    print "Calib.slope 					 -> " + str(Calib.slope)
                    print "Calib.intercept 				 -> " + str(Calib.intercept)
                    print "BGData.age_adjusted_raw_value -> " + str(BGData.age_adjusted_raw_value)
                    print "BGData.bg 					 -> " + str(BGData.bg)
                    
                    
                    BGData.write2db()
                    xdriplib.find_new_curve()
                    xdriplib.find_new_raw_curve()
                    print "Neue Daten in die DB eingetragen ->  \n";
                    sendScreen()
					
                else:
                    print "Error Found Wrong ID->"+wixellib.dexcom_src_to_asc(mydata['TransmitterId'])+" MyID-> "+  my_TransmitterID +"\n";
                    send_TID_wixel(ser,my_TransmitterID)

			
        except serial.serialutil.SerialException,e:
            print "Serial exception ",e
            time.sleep(1)
			
        ser.close() 
        time.sleep(6) 



# Create socket

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print 'Socket created'
 
# Bind socket to local host and port

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
 
s.listen(10)

start_new_thread(serialthread,("",))


# socket thread
 
def clientthread(conn):

    while True:
		data = conn.recv(1024)
		reply = ''
		if not data: 
			break
		decoded = json.loads(data)     
		# print json.dumps(decoded,sort_keys=True,indent=4)
		
		DBData=BGReadings.getrawData()
		DBData['RelativeTime']=str((int(time.time())*1000)-int(DBData['CaptureDateTime']))

		if (DBData['RawValue']!=0):
			reply = reply + json.dumps(DBData) + "\n"
		else:
			print "we do not have any data to send yet"
		
		print reply

		conn.sendall(reply)
    conn.close()

# thread end
 
# main busy loop 
# wait for connections and start a thread

# PIDFILE erzeugen
pid = os.getpid()
print("Pid->" + str(pid))
outpidf = open(PIDFILE,"w")
outpidf.write("%s"% pid)
outpidf.flush()        # make sure it actually gets written out
outpidf.close
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
disp.begin()
BG=0
LASTBG=0
db.initDB()
sendScreen()

while 1:
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    start_new_thread(clientthread ,(conn,))
 
s.close()

