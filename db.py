#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Copyright (c) 2014 mad_dev, mad_dev@linuxmail.org

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import MySQLdb
import ConfigParser



class sql:

	def __init__(self, host, user, pwd, dbname):
		self.host = host
		self.user = user
		self.pwd = pwd
		self.dbname = dbname

	def create_database(self):
	    db = MySQLdb.connect(host=self.host, user=self.user, passwd=self.pwd)
	    cur = db.cursor()
	    sql_create = 'CREATE DATABASE %s' %self.dbname 
	    sql_use = 'USE %s' %self.dbname
	    cur.execute(sql_create)
	    cur.execute(sql_use)
	    cur.execute('''CREATE TABLE fbids (
	                    	fbid BIGINT(20),
	                      	sent TEXT,
	                      	crawled VARCHAR(20)
	                                         )'''
	                    )

	    cur.execute('''CREATE TABLE checkins (
	    					checkin_id CHAR(32),
	    					fbid BIGINT(20),
	    					message TEXT,
	    					coords TEXT,
	    					timestamp TIMESTAMP
	    									 )'''
	    				)

	    cur.execute('''CREATE TABLE users (
	    					fbid BIGINT(20),
	    					profile_url TEXT,
	    					name TEXT,
	    					contact_email TEXT,
	    					interests TEXT,
	    					birthday VARCHAR(20),
	    					hometown_location TEXT,
	    					relationship_status TEXT,
	    					significant_other_id TEXT,
	    					education TEXT,
	    					work VARCHAR(100),
	    					sex TEXT,
	    					devices VARCHAR(100)
	    									)'''

	    				)

	    cur.execute('''CREATE TABLE family (
	    					fbid BIGINT(20),
	    					relative_id CHAR(32),
	    					name VARCHAR(80),
	    					relationship VARCHAR(100)
	    									)'''
	    			)

	    db.commit()
	    cur.close()
	    db.close()


class Conf:

	def __init__(self):
		pass

	def getConf(self):
		configData = {}
		config = ConfigParser.ConfigParser()
		config.read('conf/info.conf')
		options = config.options('SYS')
		for i in options:
			configData[i] = config.get('SYS', i)

		return configData

