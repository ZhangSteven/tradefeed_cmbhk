# coding=utf-8
# 
# Converts an input file to the output and send notification email
# 
from tradefeed_cmbhk.utility import getInputDirectory, getOutputDirectory\
						, getMailSender, getMailRecipients, getMailServer\
						, getMailTimeout, getMoveDirectory
from tradefeed_cmbhk.tfcmb import toCsv
from IB.worker import sendNotification
from utils.file import getFiles
from utils.mail import sendMail
from os.path import join
import shutil
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
	inputFile = getInputFile()
	try:
		result = toCsv( join(getInputDirectory(), inputFile)
					  , getOutputDirectory(), 'production')

		shutil.move( join(getInputDirectory(), inputFile)
				   , join(getMoveDirectory(), inputFile))
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
	if len(files) == 0:
		raise ValueError('No input file found')
	elif len(files) > 1:
		raise ValueError('Too many input files: {0}'.format(files))
	else:
		return files[0]



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	"""
	Read an input file from the input directory, defined in tfcmbhk.config,
	then:

	1. Convert it to the output csv file
	2. Send notification email
	3. Move the input to another directory.
	"""
	main()