# -*- coding: utf-8 -*-
import sys, os
import pymongo
sys.path.insert(0, '../')
import constants
import numpy as np
import collections
import logging, logging.config
from datetime import datetime 

import constants

logging.config.fileConfig('logging.conf')

arglen = len(sys.argv)
if arglen != 4:
	print("Usage: python export_rawdata.py [DB Name(IN)] [Collection Name(IN) [FilePath(OUT)]]")
	print("For example, python export_rawdata.py salt_rawdata_131103-131105 SALT_DB_131103-131105 ./rawdata/raw_131103-131105")
	exit(0)

module_name = sys.argv[0]
db_name = sys.argv[1]
col_name = sys.argv[2]
res_file_name = sys.argv[3]

# for mongodb
conn = pymongo.MongoClient("localhost", constants.DEFAULT_MONGODB_PORT);

# dbname = constants.DB_NAME;
db = conn[db_name];
col = db[col_name];

raw_dir = './rawdata/'
if not os.path.exists(raw_dir):
    os.makedirs(raw_dir)

logging.info('size: %d', col.count())

raw_file = open(res_file_name, 'w', encoding='UTF8')
for doc in col.find().sort('_id', pymongo.ASCENDING):
	# logging.info('_id: %s, text: %s', doc['_id'], doc['text']);

	# doc_time = util.getTwitterDate(doc['created_at'])
	# day_of_year = doc_time.timetuple().tm_yday

	name = str(doc['user']['name'].replace('\n', ' ').replace('\r', ' '))
	text = str(doc['text'].replace('\n', ' ').replace('\r', ' '))

	raw_file.write(str(doc['_id']) + '\t' + str(doc['created_at']) + '\t' + str(doc['coordinates']['coordinates'][0]) + '\t' + str(doc['coordinates']['coordinates'][1]) + '\t' + name + '\t' + text + '\n')

raw_file.close()
