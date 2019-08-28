# coding=utf-8
# 
# Store some records in MySQL database
#

import pymysql
from tradefeed_cmbhk.utility import getDbName, getDbHost, getDbUser, getDbPassword
from toolz import curried
import logging
logger = logging.getLogger(__name__)



def lookupIDFromHash(hashValue):
	"""
	[String] hashValue => [Int] trade id with that hash value.

	if lookup does not find any record in database, return None
	"""
	try:
		with getConnection().cursor() as cursor:
			sql = "SELECT tradeid FROM trades WHERE hash='{0}'".format(hashValue)
			cursor.execute(sql)
			row = cursor.fetchone()
			if row == None:
				logger.debug('lookupIDFromHash(): id not found for {0}'.format(hashValue))
				return None
			else:
				return row['tradeid']

	except:
		logger.exception('lookupIDFromHash(): ')



def addHashToDB(hashValue):
	"""
	[String] hashValue

	Add the hash value as a new record to the database, no matter whether
	the hash value exists.
	"""
	try:
		with getConnection().cursor() as cursor:
			sql = "INSERT INTO trades (hash) VALUES ('{0}')".format(hashValue)
			cursor.execute(sql)
			getConnection().commit()
	except:
		logger.exception('addHashToDB(): ')



def findOrCreateIdFromHash(hashValue):
	"""
	[String] hashValue => [Int] trade id with that hash value.

	If a record with the hash value exists in database, find the id
	associated with it;

	If not, then create a new record for the hash value and return the id 
	associated with it.
	"""
	return (lambda x: x if x != None else \
						lookupIDFromHash(curried.do(addHashToDB)(hashValue)))\
				(lookupIDFromHash(hashValue))



connection = None
def getConnection():
	global connection
	if connection == None:
		logger.info('getConnection(): establish DB connection')
		connection = pymysql.connect(host=getDbHost(),
									user=getDbUser(),
									password=getDbPassword(),
									db=getDbName(),
									cursorclass=pymysql.cursors.DictCursor)
	return connection



def closeConnection():
	global connection
	if connection != None:
		logger.info('DB connection closed')
		connection.close()



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	"""
	1. convert trades to dictionary
	2. dictionary to hash value: str(hash(frozenset(d.items())))
	3. hash value into database, create new if not there.
	"""

	print(lookupIDFromHash('-123'))
	print(findOrCreateIdFromHash('-123'))
	print(findOrCreateIdFromHash('-456'))
	closeConnection()