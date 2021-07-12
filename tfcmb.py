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
import hashlib, csv
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
	headerLine = lambda L: L[0] == 'Trader Name' if len(L) > 0 else False
	nomuraOnly = lambda p: p['Trader Name'] == '40017-B'
	toDateString = lambda f: fromExcelOrdinal(f).strftime('%d%m%Y')

	def updateValue(p):
		p['As of Date'] = toDateString(p['As of Date'])
		p['Settlement Date'] = toDateString(p['Settlement Date'])
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
																  , '%d/%m/%y')\
										       , '%d%b%Y')
	getDateString = lambda x: x.split()[-1]

	return transformDate(getDateString(itertoolz.second(lines)[0]))



def cmbPosition(mode, ap):
	"""
	[String] mode, [Dictionary] ap => [Dictionary] position in CMBHK format
	
	mode: database mode
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
	position['CLIENT A/C NO.'] = '20190519052401	'	# add a tab so that it
														# won't be treated as number
	position['SEC ID TYPE'] = '11'
	position['SEC ID'] = ap['ISIN Number']
	position['SEC NAME'] = ap['Security Description']
	position['TRAN TYPE'] = {'B': 'BUY', 'S': 'SELL'}[ap['Buy/Sell']]
	position['TRADE DATE'] = ap['As of Date']
	position['SETT DATE'] = ap['Settlement Date']
	position['QTY/NOMINAL'] = ap['Amount (Pennies)']
	position['SEC CCY'] = ap['View in Currency']
	position['PRICE'] = ap['Trade price']
	position['GROSS AMT'] = ap['Principal']
	position['FEE CCY'] = ap['View in Currency']
	position['ACCRUED INT'] = ap['Accrued Interest']
	position['NET AMT'] = ap['Settlement Total in Settlemen']
	position['SETT CCY'] = ap['View in Currency']
	position['NET AMT BASE'] = ap['Settlement Total in Settlemen']
	position['CORRESPONDENT'] = 'NOMURA'

	toString = lambda p: ''.join([str(p[h]) for h in \
									[ 'ISIN Number', 'Security Description', 'Buy/Sell'\
									, 'As of Date', 'Settlement Date', 'Amount (Pennies)'\
									, 'Trade price', 'View in Currency', 'Firm Account Long Name'\
									, 'Accrued Interest', 'Settlement Total in Settlemen']])
	position['REF NO.'] = getReference(mode, hashlib.md5(toString(ap).encode()).hexdigest())
	return position



def getReference(mode, hashValue):
	"""
	[String] hashValue => [String] reference code.
	"""
	return 'GFI' + str(1000 + findOrCreateIdFromHash(mode, hashValue))



def toCsv(inputFile, outputDir, mode):
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
	outputFile = join(outputDir, 'Trade Blotter ' + date + '_Nomura.csv')
	positionToRow = lambda position: [(lambda h: position[h] if h in position else '')(h) \
										for h in headers]
	writeCsv( outputFile
			, chain( [headers]
				   , map( positionToRow
						, map( partial(cmbPosition, mode)\
							 , positions)))\
			, quotechar='"'\
			, quoting=csv.QUOTE_NONNUMERIC)

	return outputFile




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	from tradefeed_cmbhk.utility import getCurrentDir
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('file', metavar='trade file')
	parser.add_argument('--mode', metavar='database mode', default='test')
	args = parser.parse_args()

	"""
	To do test in command line mode, do:

	$ python tfcmb.py <input_file>

	The above connects to the test database and creates the output file
	in the local directory.

	To connect to production database in command line, do:

	$ python tfcmb.py <input_file> --mode production
	"""
	print(toCsv(join(getCurrentDir(), args.file), '', args.mode))
