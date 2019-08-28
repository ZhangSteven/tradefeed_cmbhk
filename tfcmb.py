# coding=utf-8
# 
from xlrd import open_workbook
from utils.excel import rowToList, worksheetToLines
from utils.utility import fromExcelOrdinal
from os.path import join
from itertools import takewhile
import logging
logger = logging.getLogger(__name__)



def readHolding(ws, startRow):
	"""
	[Worksheet] ws, [Int] startRow => [Iterable] rows
	
	Read the Excel worksheet containing the holdings, return an iterable object
	on the list of holding positions. Each position is a dictionary.
	"""
	nonEmptyString = lambda s: s != ''
	headers = list(takewhile(nonEmptyString, rowToList(ws, startRow)))
	position = lambda values: dict(zip(headers, values))
	nonEmptyLine = lambda L: False if len(L) == 0 else nonEmptyString(L[0])
	toDateString = lambda f: fromExcelOrdinal(f).strftime('%m%d%Y')

	def updateValue(p):
		p['As of Dt'] = toDateString(p['As of Dt'])
		p['Stl Date'] = toDateString(p['Stl Date'])
		return p


	return map( updateValue
			  , map( position
			  	   , takewhile( nonEmptyLine
						 	  , worksheetToLines(ws, startRow+1))))



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
