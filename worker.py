# coding=utf-8
# 
from tradefeed_cmbhk.utility import getInputDirectory
from utils.file import getFiles
import logging
logger = logging.getLogger(__name__)



def main():
	"""
	The function performs:

	1. Read input file and convert it to csv.
	2. Move the input file to another location. 
	3. Send email notification about the result.
	"""



def getInputFile():
	files = list(filter( lambda f: f.startswith('TD') and f.endswith('.xlsx')
					   , getFiles(getInputDirectory())))
	if len(files) != 1:
		raise ValueError('invalid number of files')
	else:
		return files[0]



if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	print(getInputFile())