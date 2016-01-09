#!/usr/bin/python

import json
import socket
import sys
import time
import os
import array
import math


SrcNameTable = ( '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F','G', 'H', 'J', 'K', 'L', 'M', 'N', 'P','Q', 'R', 'S', 'T', 'U', 'W', 'X', 'Y' );

########################################################## 
#  getSrcValue(srcVal)
#  Is copied out of wixel C func 
#  Used to get index from srcVal
		
def getSrcValue(srcVal):
	i = 0;
	while i<32:
		if (SrcNameTable[i]==srcVal): 
			break;
		i=i+1
	return i;


########################################################## 
#  dexcom_src_to_asc(para):
#  Is copied out of wixel C func 
#  Used to get ASCII values out of 32UInt Bin Dexcom Values

def dexcom_src_to_asc(para): 
	src=long(para);
	addr="";
	addr+= SrcNameTable[(src >> 20) & 0x1F];
	addr+= SrcNameTable[(src >> 15) & 0x1F];
	addr+= SrcNameTable[(src >> 10) & 0x1F];
	addr+= SrcNameTable[(src >> 5) & 0x1F];
	addr+= SrcNameTable[(src >> 0) & 0x1F];
	return addr;


########################################################## 
#  asciiToDexcomSrc(addr):
#  Is copied out of wixel C func 
#  Used to get 32UINT Bin Dexcom Values out of ASCII Values

def asciiToDexcomSrc(addr):
	src = 0;	
	src |= (getSrcValue(addr[0]) << 20);
	src |= (getSrcValue(addr[1]) << 15);
	src |= (getSrcValue(addr[2]) << 10);
	src |= (getSrcValue(addr[3]) << 5);
	src |= getSrcValue(addr[4]);
	return long(src);

def _mergeintbyte(number):
	data[0]=number & 0xff
	data[1]=(number >>8) & 0xff;
	data[2]=(number >>16) & 0xff;
	data[3]=(number >>24) & 0xff;
	return data

def _mergebyteint(data):
	number=0
	number |= (long(data[0]) << 20);
	number |= (long(data[1]) << 15);
	number |= (long(data[2]) << 10);
	number |= (long(data[3]) << 5);
	return number	



