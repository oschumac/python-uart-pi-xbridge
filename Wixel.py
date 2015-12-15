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

import serial
 
HOST = ''   # All
PORT = 50005 # xdrip standard port



my_TransmitterID="6DGTF";
# my_TransmitterID="66PNX";
Bridge_Tid="";

# Eigenes PID file fuer Service
PIDFILE='/tmp/wixelpid'  

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

# output template

mydata = { "TransmitterId":"0","_id":1,"CaptureDateTime":0,"RelativeTime":0,"ReceivedSignalStrength":0,"RawValue":0,"TransmissionId":0,"BatteryLife":0,"UploadAttempts":0,"Uploaded":0,"UploaderBatteryLife":0,"FilteredValue":0 }
SrcNameTable = ( '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F','G', 'H', 'J', 'K', 'L', 'M', 'N', 'P','Q', 'R', 'S', 'T', 'U', 'W', 'X', 'Y' );


BG=0
LASTBG=0

SrcNameTable = ( '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F','G', 'H', 'J', 'K', 'L', 'M', 'N', 'P','Q', 'R', 'S', 'T', 'U', 'W', 'X', 'Y' );

def calculateAgeAdjustedRawValue(hourssince, raw_data):
	
	
	adjust_for = (86400000 * 1.9) - (hourssince*60*60*1000)
	print "Adjust for -> " + str(adjust_for)
	if adjust_for > 0:
		age_adjusted_raw_value = (((.45) * (adjust_for / (86400000 * 1.9))) * raw_data) + raw_data
		print "RAW VALUE ADJUSTMENT: FROM:" + str(raw_data) + " TO: " + str(age_adjusted_raw_value)
		return age_adjusted_raw_value
	else:
		print "RAW VALUE ADJUSTMENT: FROM:" + str(raw_data) + " TO: " + str(raw_data)
		return raw_data
		
def getSrcValue(srcVal):
	i = 0;
	while i<32:
		if (SrcNameTable[i]==srcVal): 
			break;
		i=i+1
	return i;

def dexcom_src_to_asc( para): 
	src=long(para);
	addr="";
	addr+= SrcNameTable[(src >> 20) & 0x1F];
	addr+= SrcNameTable[(src >> 15) & 0x1F];
	addr+= SrcNameTable[(src >> 10) & 0x1F];
	addr+= SrcNameTable[(src >> 5) & 0x1F];
	addr+= SrcNameTable[(src >> 0) & 0x1F];
	return addr;


def asciiToDexcomSrc(addr):
	src = 0;	
	src |= (getSrcValue(addr[0]) << 20);
	src |= (getSrcValue(addr[1]) << 15);
	src |= (getSrcValue(addr[2]) << 10);
	src |= (getSrcValue(addr[3]) << 5);
	src |= getSrcValue(addr[4]);
	return long(src);

def mergeintbyte(number):
	data[0]=number & 0xff
	data[1]=(number >>8) & 0xff;
	data[2]=(number >>16) & 0xff;
	data[3]=(number >>24) & 0xff;
	return data

def mergebyteint(data):
	number=0
	number |= (long(data[0]) << 20);
	number |= (long(data[1]) << 15);
	number |= (long(data[2]) << 10);
	number |= (long(data[3]) << 5);
	return number	
    
	
def sendScreen():
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
	BGD=BG-LASTBG
	
	draw = ImageDraw.Draw(image)
	draw.text((x, top),    '* TEST *',  font=font, fill=255)
	#draw.text((x, top+12), 'Raw: '+ str(mydata['RawValue']), font=font, fill=255)
	draw.text((x, top+12), 'CGM   : ' + str(BG) + '(' + str(BGD) + ')' , font=font, fill=255)
	draw.text((x, top+24), 'DexBat: ' + str(mydata['BatteryLife']), font=font, fill=255)
	draw.text((x, top+36), 'Signal: ' + str(mydata['ReceivedSignalStrength']), font=font, fill=255)
	draw.text((x, top+48), 'Dex ID: ' + dexcom_src_to_asc(mydata['TransmitterId']) , font=font, fill=255)

	# Display image.
	disp.image(image)
	disp.display()
	


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
				#print serial_line 

			if ((serial_line[1]=="\xf1" ) or firstrun):
				if (firstrun==False):
					print "Beacon Empfangen!!"
				else:
					print "Startup Transmitter ID senden ->" + str(my_TransmitterID)
					firstrun=False
				
				# Bridge_Tid=hex([2]+serial_line[3]+serial_line[4]+serial_line[5]);
				# print "BridgeID->" + Bridge_Tid;
				# 0 0x06 Number of bytes in the packet (6).
				# 1 0x01 Code for Data Packet
				# 2:5 TxID Encoded 32 bit integer representing the Dexcom G4 Transmitter ID that the bridge is filtering packets on.
				#  6512350
				# Todo Senden Tid
				#int sendbytes[5];

				number=asciiToDexcomSrc(my_TransmitterID)
				#print "myID "+ str(number)
				sendbytes=[0]*6
				sendbytes[0]=0x06
				sendbytes[1]=0x01
				sendbytes[2]=number & 0xff
				sendbytes[3]=(number >>8) & 0xff;
				sendbytes[4]=(number >>16) & 0xff;
				sendbytes[5]=(number >>24) & 0xff;
				#sendbytes[2]=0
				#sendbytes[3]=0
				#sendbytes[4]=0
				#sendbytes[5]=0
				
				print "Daten Senden ->" + ":".join("{:02x}".format(c) for c in sendbytes)
				
				ser.write(sendbytes)
				
			
			if (serial_line[1]=="\x00"):
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

				slope=860.0
				intercept=17.85
				scale=1.0
				
				print "raw BG" + str((int(mydata['RawValue'])-intercept)/slope)
				print "Filtered BG" + str((int(mydata['FilteredValue'])-intercept)/slope)
				
				
				# SGV=`awk -v r=$RAW -v f=$FILTERED -v s=$SLOPE -v i=$INT -v c=$SCALE 'BEGIN { printf "%2.0f\n", c*(((r+f)/2)-i)/s }'`
				# Ochenmillers implementation
				# print "OM BG" + str((((scale*(int(mydata['FilteredValue'])+int(mydata['RawValue']))/2))-intercept)/slope)
				# print "OM BG RAW" + str(((int(mydata['RawValue']))-intercept)/slope)
				# print "OM BG SGV" + str(((int(mydata['FilteredValue']))-intercept)/slope)
				
				
				# bgReading.calculated_value = ((calibration.slope * bgReading.age_adjusted_raw_value) + calibration.intercept);
				raw_data=int(mydata['RawValue'])
				filtered_data=int(mydata['FilteredValue'])
				bg=(slope/1000*(raw_data/1000))+intercept
				print "xdrip BG ->" + str(bg)
				
				# bgReading.calculated_value = (((calSlope * bgReading.raw_data) + calIntercept) - 5);
				bg=((slope/1000*(raw_data/1000))+intercept)-5
				print "xdrip BG Dex->" + str(bg)
				

				BG_raw=int(mydata['RawValue'])
				BG_filtered=int(mydata['RawValue'])

				raw_data=calculateAgeAdjustedRawValue(49,BG_raw)

                #################################################################################################################################
				# bgReading.calculated_value = ((calibration.slope * bgReading.age_adjusted_raw_value) + calibration.intercept);
				LASTBG=BG
				BG=math.ceil((slope/1000*(raw_data/1000))+intercept)
				print "1st xdrip BG w age adj.->" + str(BG)

				#################################################################################################################################
				slope=1300
				intercept=-45.33
				
				bgn=(slope/1000*(raw_data/1000))+intercept
				print "2nd xdrip BG w age adj.->" + str(bg)

				

				
				mydata['BatteryLife']=str(ord(serial_line[10]))
				BatterieLife=str(ord(serial_line[11]))
				
				data=ord(serial_line[12])+(ord(serial_line[13])*256)+(ord(serial_line[14])*65536)+(ord(serial_line[15])*16777216)
				mydata['TransmitterId']=str(int(ord(serial_line[12])+(ord(serial_line[13])*256)+(ord(serial_line[14])*65536)+(ord(serial_line[15])*16777216)))
				
				mydata['ReceivedSignalStrength']=0
				mydata['TransmissionId']=0

				print "Receive" + json.dumps(mydata)
				sendbytes=[0]*2
				sendbytes[0]=0x02
				sendbytes[1]=0xF0
				
				print "ACK Senden ->" + ":".join("{:02x}".format(c) for c in sendbytes)
				
				ser.write(sendbytes)

				
				print "Tid->"+dexcom_src_to_asc(mydata['TransmitterId'])
				if dexcom_src_to_asc(mydata['TransmitterId'])==my_TransmitterID:
					print "Found MY_ID->"+dexcom_src_to_asc(mydata['TransmitterId'])+"\n";
					sendScreen()
				else:
					print "Found ID->"+dexcom_src_to_asc(mydata['TransmitterId'])+" MyID-> "+  my_TransmitterID +"\n";

			
		except serial.serialutil.SerialException,e:
			print "Serial exception ",e
			time.sleep(1)
			
		ser.close() 
		time.sleep(6) 



# Create socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
		
		mydata['RelativeTime']=str((int(time.time())*1000)-int(mydata['CaptureDateTime']))

		if (mydata['RawValue']!=0):
			reply = reply + json.dumps(mydata) + "\n"
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
BG=0
LASTBG=0
sendScreen()

while 1:
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    start_new_thread(clientthread ,(conn,))
 
s.close()

