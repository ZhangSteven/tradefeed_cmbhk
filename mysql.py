# coding=utf-8
# 
# Store some records in MySQL database
#

import pymysql
from tradefeed_cmbhk.utility import getDbName, getDbHost, getDbUser, getDbPassword
from toolz import curried
import logging
logger = logging.getLogger(__name__)



def findOrCreateIdFromHash(mode, hashValue):
	"""
	[String] mode, [String] hashValue=> [Int] trade id with that hash value.

	mode: database mode, it is either 'test' (use test database) or
		something else (use production database)

	If a record with the hash value exists in database, find the id
	associated with it;

	If not, then create a new record for the hash value and return the id 
	associated with it.
	"""
	id = lookupIDFromHash(mode, hashValue)
	if id == None:
		addHashToDB(mode, hashValue)
		return lookupIDFromHash(mode, hashValue)
	else:
		return id



def lookupIDFromHash(mode, hashValue):
	"""
	[String] mode, [String] hashValue => [Int] trade id with that hash value.

	if lookup does not find any record in database, return None
	"""
	try:
		with getConnection(mode).cursor() as cursor:
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



def addHashToDB(mode, hashValue):
	"""
	[String] mode, [String] hashValue

	Add the hash value as a new record to the database, no matter whether
	the hash value exists.
	"""
	try:
		with getConnection(mode).cursor() as cursor:
			sql = "INSERT INTO trades (hash) VALUES ('{0}')".format(hashValue)
			cursor.execute(sql)
			getConnection(mode).commit()
	except:
		logger.exception('addHashToDB(): ')



connection = {}
def getConnection(mode):
	global connection
	if not mode in connection:
		logger.info('getConnection(): establish DB connection, mode {0}'.format(mode))
		connection[mode] = pymysql.connect( host=getDbHost(mode)\
										  , user=getDbUser(mode)\
										  ,	password=getDbPassword(mode)\
										  , db=getDbName(mode)\
										  , cursorclass=pymysql.cursors.DictCursor)
	return connection[mode]



def closeConnection(mode):
	global connection
	if mode in connection:
		logger.info('DB connection closed')
		connection[mode].close()

	return connection.pop(mode, None)



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