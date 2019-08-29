# coding=utf-8
# 
from xlrd import open_workbook
from utils.excel import worksheetToLines
from utils.utility import fromExcelOrdinal, writeCsv
from utils.iter import firstOf
from toolz import itertoolz
from tradefeed_cmbhk.mysql import findOrCreateIdFromHash
from os.path import join
from datetime import datetime
from itertools import takewhile, dropwhile, chain
from functools import partial
import hashlib
import logging
logger = logging.getLogger(__name__)



def readHolding(file):
	"""
	[String] file => ([String] date, [Iterable] positions)
	"""
	return (lambda lines: (getDate(lines), getPosition(lines)))\
			(worksheetToLines(open_workbook(file).sheet_by_index(0)))



def getPosition(lines):
	"""
	[Iterable] lines => [Iterable] positions
	
	lines: from the Excel worksheet containing the holdings

	Return an iterable object on the list of holding positions. Each position
	is a dictionary.
	"""
	nonEmptyString = lambda s: s != ''
	position = lambda headers, values: dict(zip(headers, values))
	nonEmptyLine = lambda L: False if len(L) == 0 else nonEmptyString(L[0])
	headerLine = lambda L: L[0] == 'Fund' if len(L) > 0 else False
	nomuraOnly = lambda p: p['Fund'] == '40017-B'
	toDateString = lambda f: fromExcelOrdinal(f).strftime('%d%m%Y')

	def updateValue(p):
		p['As of Dt'] = toDateString(p['As of Dt'])
		p['Stl Date'] = toDateString(p['Stl Date'])
		return p

	headers = list(takewhile(nonEmptyString, firstOf(headerLine, lines)))
	return map( updateValue
			  , filter( nomuraOnly
			  		  , map( partial(position, headers)
			  	   		   , takewhile(nonEmptyLine, lines))))



def getDate(lines):
	"""
	[Iterable] lines => [String] date (mmddyyyy)
	
	lines: from the Bloomberg exported trade file (Excel)
	"""
	transformDate = lambda x: datetime.strftime( datetime.strptime( x
																  , '%m/%d/%y')\
										       , '%Y-%m-%d')
	getDateString = lambda x: x.split()[-1]

	return transformDate(getDateString(itertoolz.second(lines)[0]))



def cmbPosition(ap):
	"""
	[Dictionary] ap => [Dictionary] position in CMBHK format

	ap: position in AIM format (from AIM holding file)

	NOTE: here we use hashlib.md5() instead of hash() to generate the
	unique hash value for a trade. Because for the same string, different
	invocations of python gives difference results, i.e., if we open Python
	and calculates hash() for the same string a few times, gives the same
	result; However if we close Python and invoke again, hash() for the
	same string give different result!

	Therefore we use md5() because it always gives the same result for the
	same string.
	"""
	position = {}
	position['CLIENT A/C NO.'] = '20190519052401'
	position['SEC ID TYPE'] = '11'
	position['SEC ID'] = ap['ISIN']
	position['SEC NAME'] = ap['Long Description']
	position['TRAN TYPE'] = {'B': 'BUY', 'S': 'SELL'}[ap['B/S']]
	position['TRADE DATE'] = ap['As of Dt']
	position['SETT DATE'] = ap['Stl Date']
	position['QTY/NOMINAL'] = ap['Amount Pennies']
	position['SEC CCY'] = ap['VCurr']
	position['PRICE'] = ap['Price']
	position['GROSS AMT'] = ap['Settle Amount'] - ap['Accr Int']
	position['FEE CCY'] = ap['VCurr']
	position['ACCRUED INT'] = ap['Accr Int']
	position['NET AMT'] = ap['Settle Amount']
	position['SETT CCY	'] = ap['VCurr']
	position['NET AMT BASE'] = ap['Settle Amount']
	position['CORRESPONDENT'] = 'NOMURA'

	toString = lambda p: ''.join([str(p[h]) for h in \
									[ 'ISIN', 'Long Description', 'B/S'\
									, 'As of Dt', 'Stl Date', 'Amount Pennies'\
									, 'Price', 'VCurr', 'FACC Long Name'\
									, 'Accr Int', 'Settle Amount']])
	position['REF NO.'] = getReference(hashlib.md5(toString(ap).encode()).hexdigest())
	return position



def getReference(hashValue):
	"""
	[String] hashValue => [String] reference code.
	"""
	return 'GFI' + str(1000 + findOrCreateIdFromHash(hashValue))



def toCsv(inputFile, outputDir):
	"""
	[String] intputFile, [String] outputDir => 
		[String] outputFile name (including path)

	Side effect: create an output csv file
	"""
	headers = [ 'CLIENT A/C NO.', 'REF NO.', 'SEC ID TYPE', 'SEC ID'\
			  , 'SEC NAME',	'TRAN TYPE', 'TRADE DATE', 'SETT DATE',	'QTY/NOMINAL'\
			  ,	'SEC CCY', 'PRICE',	'GROSS AMT', 'FEE CCY',	'COMMISSION'\
			  , 'STAMP DUTY', 'TAXES AND OTHER FEES', 'ACCRUED INT', 'NET AMT'\
			  ,	'SETT CCY', 'NET AMT BASE',	'CORRESPONDENT', 'BROKER', 'BROKER A/C'\
			  ,	'CLEARER AGENT', 'CLEARER AGENT A/C', 'INTERMEDIATE AGENT'\
			  , 'INTERMEDIATE AGENT A/C', 'PSET', 'PLACE OF SAFEKEEPING'\
			  ,	'REMARKS', 'MESSAGE FUNCTION']

	date, positions = readHolding(inputFile)
	outputFile = join(outputDir, 'Trade Blotter Nomura ' + date + '.csv')
	positionToRow = lambda position: [(lambda h: position[h] if h in position else '')(h) \
										for h in headers]
	writeCsv(outputFile, chain( [headers]
							  , map( positionToRow
								   , map(cmbPosition, positions))))
	return outputFile



def isHoldingFile(filename):
	"""
	[String] filename => [Bool] is this a holding file
	"""
	return fileNameFromPath(filename).split('.')[0].\
			lower().startswith('securityholdingposition')



def isCashFile(filename):
	"""
	[String] filename => [Bool] is this a holding file
	"""
	return fileNameFromPath(filename).split('.')[0].\
			lower().startswith('dailycashholding')



def isValidFile(filename):
	return isHoldingFile(filename) or isCashFile(filename)



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	from tradefeed_cmbhk.utility import getCurrentDir
	inputFile = join(getCurrentDir(), 'samples', 'TD22082019.xlsx')
	print(toCsv(inputFile, ''))
