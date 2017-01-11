import sys
sys.path.insert(0, '../')
import constants
import pymongo
import numpy as np
import matlab.engine
import logging, logging.config
import time

logging.config.fileConfig('logging.conf')
logging.info('Run topic modeling for all tiles using standard NMF')

start_time = time.time()
eng = matlab.engine.start_matlab();
eng.cd('../matlab/standard_nmf/');
elapsed_time = time.time() - start_time;
logging.info('matlab loading time: %.3f ms', elapsed_time);

conn = pymongo.MongoClient("localhost", 27017);

dbname = constants.DB_NAME;
db = conn[dbname];

def get_next_sequence_value(sequence_name):

	db.counters.find_and_modify(
		{'_id':sequence_name}, 
		{'$inc':{'seq':1}}, upsert=True, new=True
	);

	return db.counters.find_one({'_id':sequence_name})['seq']

def del_stored_topics():
	for tile_name in db.collection_names():
		if tile_name.endswith('_topics') == True:
			db.drop_collection(tile_name);

logging.info('loading vocabulary...');
start_time = time.time()
voca = []
idx = 0;
for each in db['vocabulary'].find():
	# idx += 1;
	# if idx > 100:
	# 	break;
	word = each['stem'];
	voca.append(word);

elapsed_time = time.time() - start_time;
logging.info('Done: loading vocabulary: %.3f ms', elapsed_time);

del_stored_topics();

logging.info('Run NMF for all tiles...');
for tile_name in db.collection_names():
	if tile_name.startswith('level') == False or tile_name.endswith('_mtx') == False:
		continue;

	logging.info(tile_name);

	tile_mtx_db = db[tile_name];	

	tile_mtx = [];
	for each in tile_mtx_db.find():
		item = np.array([each['term_idx'], each['doc_idx'], each['freq']], dtype=np.int32);
		tile_mtx = np.append(tile_mtx, item, axis=0);
		
	tile_mtx = np.array(tile_mtx, dtype=np.int32).reshape(tile_mtx_db.count(), 3)
	#print(tile_mtx)

	# run topic modeling
	A = matlab.double(tile_mtx.tolist()) # sparse function in function_runme() only support double type.
	topics_list = eng.function_runme(A, voca, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, nargout=1);

	topics = np.asarray(topics_list);
	topics = np.reshape(topics, (constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K));

	# store topics in DB
	tile = db[tile_name]
	tile_topic_name = tile_name+'_topics'
	tile_topic = db[tile_topic_name]

	topic_id = 0;
	for topic in topics:
		topic_id += 1;
		rank = 0;
		for word in topic: 
			rank += 1;
			tile_topic.insert({'_id': get_next_sequence_value(tile_topic_name), 'topic_id': topic_id, 'rank': rank, 'word': word});

logging.info('Done: NMF');

# eng = matlab.engine.start_matlab()
# eng.cd(constants.MATLAB_DIR)

# ret = eng.triarea(1.0,5.0)