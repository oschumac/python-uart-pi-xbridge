#!/usr/bin/python

import sqlite3

def insertinto():
	conn = sqlite3.connect('test.db')
	print "Opened database successfully";

	conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
		  VALUES (1, 'Paul', 32, 'California', 20000.00 )");

	conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
		  VALUES (2, 'Allen', 25, 'Texas', 15000.00 )");

	conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
		  VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )");

	conn.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
		  VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00 )");

	conn.commit()
	print "Records created successfully";

def create_database():
	sql = 'drop table if exists COMPANY'
	conn.execute(sql)
    
	sql = 'create table if not exists COMPANY (id integer, Name String, AGE integer, Address String ,  SALARY Float)'
	conn.execute(sql)
	conn.commit()


conn = sqlite3.connect('test.db')
print "Opened database successfully";
	
create_database()
insertinto()

conn.close()
