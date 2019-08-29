# coding=utf-8
# 
from xlrd import open_workbook
from utils.excel import worksheetToLines
from utils.utility import fromExcelOrdinal
from utils.iter import firstOf
from toolz import itertoolz
from tradefeed_cmbhk.mysql import findOrCreateIdFromHash
from os.path import join
from datetime import datetime
from itertools import takewhile, dropwhile
from functools import partial
import logging
logger = logging.getLogger(__name__)



toDateString = lambda f: fromExcelOrdinal(f).strftime('%m%d%Y')



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
	headerLine = lambda L: L[0] == 'ISIN' if len(L) > 0 else False

	def updateValue(p):
		p['As of Dt'] = toDateString(p['As of Dt'])
		p['Stl Date'] = toDateString(p['Stl Date'])
		return p

	headers = list(takewhile(nonEmptyString, firstOf(headerLine, lines)))
	return map( updateValue
			  , map( partial(position, headers)
			  	   , takewhile( nonEmptyLine, lines)))



def getDate(lines):
	"""
	[Iterable] lines => [String] date (mmddyyyy)
	
	lines: from the Bloomberg exported trade file (Excel)
	"""
	transformDate = lambda x: datetime.strftime( datetime.strptime( x
																  , '%m/%d/%y')\
										       , '%m%d%Y')
	getDateString = lambda x: x.split()[-1]

	return transformDate(getDateString(itertoolz.second(lines)[0]))



def cmbPosition(ap):
	"""
	[Dictionary] ap => [Dictionary] position in CMBHK format

	ap: position in AIM format (from AIM holding file)
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
	position['REF NO.'] = getReference(str(hash(frozenset(position.items()))))
	return position



def getReference(hashValue):
	"""
	[String] hashValue => [String] reference code.
	"""
	return 'GFI' + str(1000 + findOrCreateIdFromHash(hashValue))



def fileNameFromPath(inputFile):
	"""
	[String] inputFile => [String] the file name after stripping the path

	Assuming the path is Windows style, i.e., C:\Temp\File.txt
	"""
	return inputFile.split('\\')[-1]



def getOutputFileName(inputFile, outputDir, prefix):
	"""
	[String] inputFile, [String] outputDir, [String] prefix =>
		[String] output file name (with path)
	"""
	return join(outputDir, prefix + getDateFromFilename(inputFile) + '.csv')



def getDateFromFilename(inputFile):
    """
    [String] inputFile => [String] date (yyyy-mm-dd)

    inputFile filename looks like:

    SecurityHoldingPosition-CMFHK XXX SP-20190531.XLS
    DailyCashHolding-CMFHK XXX SP-20190531.XLS
    """
    dateString = fileNameFromPath(inputFile).split('.')[0].split('-')[2]
    return dateString[0:4] + '-' + dateString[4:6] + '-' + dateString[6:8]



def toCsv(portId, inputFile, outputDir, prefix):
	"""
	[String] portId, [String] intputFile, [String] outputDir, [String] prefix
		=> [String] outputFile name (including path)

	Side effect: create an output csv file

	This function is to be called by the recon_helper.py from reconciliation_helper
	package.
	"""
	if isHoldingFile(inputFile):
		gPositions = map(partial(genevaPosition, portId, getDateFromFilename(inputFile))
	                            , readHolding(open_workbook(inputFile).sheet_by_index(0)
	                             			 , getStartRow()))
		headers = ['portfolio', 'custodian', 'date', 'geneva_investment_id',
					'ISIN', 'bloomberg_figi', 'name', 'currency', 'quantity']
		prefix = prefix + 'holding_'

	elif isCashFile(inputFile):
		gPositions = map(partial(genevaCash, portId, getDateFromFilename(inputFile))
                        , readCash(open_workbook(inputFile).sheet_by_index(0)))
		headers = ['portfolio', 'custodian', 'date', 'currency', 'balance']
		prefix = prefix + 'cash_'

	else:
		raise ValueError('toCsv(): invalid input file {0}'.format(inputFile))

	rows = map(partial(dictToValues, headers), gPositions)
	outputFile = getOutputFileName(inputFile, outputDir, prefix)
	writeCsv(outputFile, chain([headers], rows), '|')
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
	inputFile = join(getCurrentDir(), 'samples', 'TD08082019.xlsx')
	for x in readHolding(open_workbook(inputFile).sheet_by_index(0), 3):
		print(x)
