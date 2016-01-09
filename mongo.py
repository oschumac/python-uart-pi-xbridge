import os
import sys
import pymongo
from bson import BSON
from bson import json_util

MONGODB_URI_REMOTE = 'mongodb://Lars_2009:Lars65535@euve76271.serverprofi24.de:21060/larscgmtest' 
MONGODB_URI_LOCAL = 'mongodb://aps:aps@127.0.0.1:27017/aps' 

def getlast3():
	try:
		client = pymongo.MongoClient(MONGODB_URI_LOCAL)
    
	except:
		print('Error: Unable to Connect')
		connection = None
    
	db = client['aps']
	cursor = db.entries.find({'type':'cal'}).sort('date', -1).limit(3)

	for doc in cursor:
		print (doc)

	client.close()
	
	
	

if __name__ == '__main__':
	getlast3()
