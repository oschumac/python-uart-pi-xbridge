#!/usr/bin/python

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


db.initDB()


ID=sensor.StartSensor()


if sensor.SensorisActive():
	CurSensor=sensor.currentSensor()
