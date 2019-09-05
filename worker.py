# coding=utf-8
# 
from tradefeed_cmbhk.utility import getInputDirectory, getOutputDirectory\
						, getMailSender, getMailRecipients, getMailServer\
						, getMailTimeout
from tradefeed_cmbhk.tfcmb import toCsv
from IB.worker import sendNotification
from utils.file import getFiles
from utils.mail import sendMail
from os.path import join
import logging
logger = logging.getLogger(__name__)



def main():
	"""
	The function performs:

	1. Read input file and convert it to csv.
	2. Move the input file to another location. 
	3. Send email notification about the result.
	"""
	result = ''
	try:
		inputFile = getInputFile()
		result = toCsv(inputFile, getOutputDirectory(), 'production')
	except:
		logger.exception('main()')

	sendNotification(result)



def sendNotification(result):
	"""
	input: [String] result (file name)
	
	side effect: send notification email to recipients about the results.
	"""
	if result == '':
		sendMail( '', 'Error occurred during nomura trade conversion'
				, getMailSender(), getMailRecipients()\
				, getMailServer(), getMailTimeout())
	else:
		sendMail( 'result file: {0}'.format(result)
				, 'Successfully performed nomura trade conversion'
				, getMailSender(), getMailRecipients()\
				, getMailServer(), getMailTimeout())



def getInputFile():
	logger.debug('getInputFile(): searching for files in {0}'.format(getInputDirectory()))
	files = list(filter( lambda f: f.startswith('TD') and f.endswith('.xlsx')
					   , getFiles(getInputDirectory())))
	if len(files) != 1:
		raise ValueError('invalid number of files')
	else:
		return join(getInputDirectory(), files[0])



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	main()