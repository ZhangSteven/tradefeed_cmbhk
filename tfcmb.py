# coding=utf-8
# 
from xlrd import open_workbook
import logging
logger = logging.getLogger(__name__)



def readHolding(ws, startRow):
	"""
	[Worksheet] ws, [Int] startRow => [Iterable] rows
	
	Read the Excel worksheet containing the holdings, return an iterable object
	on the list of holding positions. Each position is a dictionary.
	"""
	headers = readHeaders(ws, startRow)
	position = lambda headers, values: dict(zip(headers, values))
	emptyString = lambda s: s == ''

	return map(partial(position, headers)
			  , map(partial(filterfalse, emptyString)
			  	   , takewhile(firstCellNotEmpty
						 	  , worksheetToLines(ws, getStartRow()+2))))



def readHeaders(ws, startRow):
    """
    [Worksheet] ws, [Int] startRow => [List] headers
    """
    toString = lambda s: str(s)
    firstLine = lambda s: s.split('\n')[0].strip()
    nonEmptyString = lambda s: s != ''

    return list(filter(nonEmptyString
                      , map(firstLine
                           , map(toString
                                , rowToList(ws, startRow)))))



def readCash(ws):
	"""
	[Worksheet] ws => [List] list of (currency, amount)

	Return looks like [('HKD', 1234.67), ('USD', 89.88)]
	"""
	isClosingBalance = lambda s: True if isinstance(s, str) and s.startswith('Closing Balance') \
									else False
	isCashLine = lambda L: True if any(isClosingBalance(x) for x in L) else False


	def cashEntry(lineItems):
		"""
		[List] lineItems => [Tuple] (currency, amount)
		"""
		isFloat = lambda x: True if isinstance(x, float) else False
		isCurrencyString = lambda x: True if isinstance(x, str) \
											and len(x) > 6 and x[0] == '(' \
											and x[6] == ')' \
											else False
		amount = firstOf(isFloat, lineItems)
		currencyString = firstOf(isCurrencyString, lineItems)
		if amount == None or currencyString == None:
			raise ValueError('cashEntry(): cannot parse cash entry: {0}'.format(lineItems))

		return (currencyString.strip()[2:5], amount)


	return map(cashEntry, filter(isCashLine, worksheetToLines(ws)))



def firstCellNotEmpty(lineItems):
	"""
	[List] lineItems => [Boolean] is the first item an empty string?

	If the list has a first cell and it is an empty string, return False;
	else return True.
	"""
	try:
		return lineItems[0] != ''

	except IndexError:
		return False



def genevaPosition(portId, date, position):
	"""
	[String] portId, [String] date, [Dictionary] position => 
		[Dictionary] gPosition
	
	A Geneva position is a dictionary object that has the following
	keys:

	portfolio|custodian|date|geneva_investment_id|ISIN|bloomberg_figi|name
	|currency|quantity
	
	"""
	genevaPos = {}
	genevaPos['portfolio'] = portId
	genevaPos['custodian'] = getCustodian()
	genevaPos['date'] = date
	genevaPos['name'] = position['Securities Name']
	genevaPos['currency'] = position['Ccy']
	genevaPos['quantity'] = position['Traded Quantity (Ledger Balance)']
	genevaPos['geneva_investment_id'] = ''
	genevaPos['ISIN'] = position['Securities Identifier']
	genevaPos['bloomberg_figi'] = ''
	
	return genevaPos



def genevaCash(portId, date, cash):
	"""
	[String] portId, [String] date, [Tuple] cash => 
		[Dictionary] gCash

	cash: a tuple like ('HKD', 1234.56)

	A Geneva cash position is a dictionary object that has the following
	keys:

	portfolio|custodian|date|currency|balance
	
	"""
	genevaCash = {}
	genevaCash['portfolio'] = portId
	genevaCash['custodian'] = getCustodian()
	genevaCash['date'] = date
	(genevaCash['currency'], genevaCash['balance']) = cash
	
	return genevaCash



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


    # inputFile = join(getCurrentDirectory(), 'samples', 'DailyCashHolding-client name-20190531.XLS')
    inputFile = join(getCurrentDirectory(), 'samples', 'SecurityHoldingPosition-client name-20190531.XLS')
    toCsv('40017', inputFile, getCurrentDirectory(), 'global_spc_')