# python-uart-pi-xbridge

Hope you guys having fun with this Repo.
It is not finished yet.
Things working so far are wixel Python communication (I think needs a bit more testing but runs well).
Sending data as wifi-wixel to xdrip.
Calculate cgm Blood Glucose based of xdrip calc and hardcoded intercept and slope.

Todo -> 3 Steps are in my mind

1. Get a functional algorithm to calculate BG based on calibrations out of Mongodb

2. Start to generate an own calibration algorythm in the pi
   Would give the advantage for loopers to get BG from Bolus expert inputs out of the pump.
   Pi could calculate the next calalibration without any other user attention or any other devices

3. Send data to mongo (BG,CAL) 


# to get Started you will need to:
1. deactivate ttyAMA0 on Kernel via raspconfig
   Otherwise the one and only UART is used for Kernel messages and login

2. Programm wixel xBridge2 with the small changes as descripted in the head of  Wixel.py.
   Cause it es much easier in Python to use serial.readline. But this need <CR><LF> in the end of the Telegramm 
   See -> https://github.com/jstevensog/wixel-sdk

3. Connect Wixel to pi via GPIO
   See -> Hardware

4. Use Wixel.py for test. Put your Transmitter ID as an constant in the Script.
   You may have to uncommend sendScreen() and adafriut imports  
   if you don't have a adafruit display atached to the pi. From my prospective it is very helpfull.
   
5. Take the red pill and stay in Wonderland. :-)



# Hardware
use org wixel pinout atached directly to pi

Wixel             /  PI Pin connections

Wixel TX  Pin 1_6 -> PI GPIO PIN 10 RX

Wixel RX  Pin 1_7 -> PI GPIO PIN  8 TX

Wixel 3V3 Pin     -> PI GPIO Pin 17 3v3 Power

Wixel GND Pin     -> PI GPIO Pin 14 GND

