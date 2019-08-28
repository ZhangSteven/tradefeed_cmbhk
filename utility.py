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



def getDbName():
	global config
	return config['database']['name']



def getDbHost():
	global config
	return config['database']['host']



def getDbUser():
	global config
	return config['database']['username']



def getDbPassword():
	global config
	return config['database']['password']