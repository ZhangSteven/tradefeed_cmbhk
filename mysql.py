# coding=utf-8
# 
# Store some records in MySQL database
#

import pymysql
from tradefeed_cmbhk.utility import getDbName, getDbHost, getDbUser, getDbPassword
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



def saveResultsToDB(directory, resultList):
	"""
	input: [String] directory, [Iterable] resultList
	output: save the results into database

	where directory is the directory containing the files, and resultList
	is a list of tuple (file, status), status is either 0 or 1.
	"""
	def toDBRecord(result):
		"""
		([String] file, [Int] status) => 
			([String] file, [String] datetime, [String] status)
		"""
		file, status, _, _ = result
		return (file
				, strftime('%Y-%m-%d %H:%M:%S', localtime(getmtime(join(directory, file))))
				, str(status))

	# we need to convert to list first and tell whether it's empty because
	# emtpy list will cause cursor.executemany() to fail
	records = list(map(toDBRecord, resultList))
	if records == []:
		logger.debug('saveResultsToDB(): no records to save')
		return


	try:
		with connection.cursor() as cursor:
			sql = "REPLACE INTO file (file_name, last_modified, status) \
					VALUES (%s, %s, %s)"
			cursor.executemany(sql, records)

			# save changes
			connection.commit()

	except:
		logger.exception('saveResultsToDB(): ')



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
	closeConnection()