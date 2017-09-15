import logging, logging.config
import constants
import os

logging.config.fileConfig('logging.conf')

def parse_UB_log():

	datapath = constants.LOG_DIR + '/'

	for root, directories, files in os.walk(datapath):

		for filename in files: 

			with open(datapath + filename, 'r', encoding = 'UTF-8') as f:
				lines = f.readlines()				
				for line in lines: 
					if line.find("Zoom") > 0:
						print(line)



parse_UB_log()



