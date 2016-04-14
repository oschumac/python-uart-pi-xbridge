# python-uart-pi-xbridge

Hope you guys having fun with this Repo.
It is not finished yet.
Things working so far are wixel Python communication (I think needs a bit more testing but runs well).
Sending data as wifi-wixel to xdrip.
Calculate cgm Blood Glucose based of xdrip calc and hardcoded intercept and slope.

# Implemented functionality

- calculate calibrations double calibration
- calculate single calibrations.
- Start/Stop Sensor
- All data stored in sqllite db
- calculate CGM BG based on received raw data and determined calibration
- upload entries to mongo
- export data from sqllite2json


# If using rpi to get Started you will need to:
1a. deactivate ttyAMA0 on Kernel via raspconfig
   Otherwise the one and only UART is used for Kernel messages and login

# If using Intel Edison you can use /dev/ttyMFD1
1b. you have to change ser = serial.Serial('/dev/ttyMFD2', 9600) to ser = serial.Serial('/dev/ttyMFD1', 9600)
   and change os.system('systemctl stop serial-getty@ttyMFD2.service') to #os.system('systemctl stop serial-getty@ttyMFD2.service')
   
# If using Intel Edison you can use /dev/ttyMFD1
1c. Script will deaktivate Kernel Konsole on ttyMFD2 on startup.


2. You can use xBridge2 excample or xBridgeOaps excample.
   For best results use xBridgeOaps there is a bootup delay implemented to prevent edison to not boot while edison 
   is sending beacon telegramms at startup to console ttyMFD2.

3. Connect Wixel to pi via GPIO
   See -> Hardware for rpi or See edison_hardware.pdf

4. Use Wixel.py for test. Put your Transmitter ID as an constant in the Script.
   
5. Take the red pill and stay in Wonderland. :-)



# Hardware
use org wixel pinout atached directly to pi

Wixel             /  PI Pin connections

Wixel TX  Pin 1_6 -> PI GPIO PIN 10 RX

Wixel RX  Pin 1_7 -> PI GPIO PIN  8 TX

Wixel 3V3 Pin     -> PI GPIO Pin 17 3v3 Power

Wixel GND Pin     -> PI GPIO Pin 14 GND




