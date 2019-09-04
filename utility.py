# coding=utf-8
# 
# Read configure file and return values from it.
#

from os.path import join, dirname, abspath
import configparser



def getCurrentDir():
	"""
	Get the absolute path to the directory where this module is in.

	This piece of code comes from:

	http://stackoverflow.com/questions/3430372/how-to-get-full-path-of-current-files-directory-in-python
	"""
	return dirname(abspath(__file__))



def _load_config():
	"""
	Read the config file, convert it to a config object. The config file is 
	supposed to be located in the same directory as the py files, and the
	default name is "config".

	Caution: uncaught exceptions will happen if the config files are missing
	or named incorrectly.
	"""
	cfg = configparser.ConfigParser()
	cfg.read(join(getCurrentDir(), 'tfcmbhk.config'))
	return cfg



# initialized only once when this module is first imported by others
if not 'config' in globals():
	config = _load_config()



def getInputDirectory():
	global config
	if config['directory']['input'] == '':
		return getCurrentDir()
	else:
		return config['directory']['input']



def getOutputDirectory():
	global config
	if config['directory']['output'] == '':
		return getCurrentDir()
	else:
		return config['directory']['output']



def getDbName(mode):
	global config
	if mode == 'test':
		return config['testdatabase']['name']
	else:
		return config['database']['name']



def getDbHost(mode):
	global config
	if mode == 'test':
		return config['testdatabase']['host']
	else:
		return config['database']['host']



def getDbUser(mode):
	global config
	if mode == 'test':
		return config['testdatabase']['username']
	else:
		return config['database']['username']



def getDbPassword(mode):
	global config
	if mode == 'test':
		return config['testdatabase']['password']
	else:
		return config['database']['password']



def getMailSender():
	global config
	return config['email']['sender']



def getMailRecipients():
	global config
	return config['email']['recipents']



def getMailServer():
	global config
	return config['email']['server']



def getMailTimeout():
	global config
	return float(config['email']['timeout'])