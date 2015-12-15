# python-uart-pi-xbridge

Hope you guys having fun with this Repo.
It is not finished yet.
Things working so far are wixel Python communication. (I think needs a bit more testing but runs well)
Sending data as wifi/wixel to xdrip

Todo -> 3 Steps are in my mind
1. Get a functional formular to calculate BG based on calibrations out of Mongodb
2. Start to generate an own calibration algorythm in the pi
   Would give the advantage for loopers to put in BG in Bolus expert in pump.
   And pi could calculate the next cal without an other user attention
3. Send data to mongo (BG,CAL) 


# to get Started you will need to:
1. deactivate ttyAMA0 on Kernel via raspconfig
   Otherwise the one and only UART us used for Kernel messages and login

2. Programm wixel xbridge with the small changes as descripted in the head of  Wixel.py

3. Connect Wixel to pi via GPIO

4. Use Wixel.py for test. Put your Transmitter ID as an constant in the Script.
   you maybe have to uncommend sendScreen() if you don't have a adafruit display atached to the pi.




# Hardware
use org wixel pinout atached directly to pi

Wixel / Pi Pin connections
Wixel TX  Pin 1_6 -> PI GPIO PIN 10 RX

Wixel RX  Pin 1_7 -> PI GPIO PIN  8 TX

Wixel 3V3 Pin     -> PI GPIO Pin 17 3v3 Power

Wixel GND Pin     -> PI GPIO Pin 14 GND





