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

conn = pymongo.MongoClient("localhost", constants.DEFAULT_MONGODB_PORT);

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

	for item in db.counters.find():
		name = item['_id']
		if name.endswith('_topics') == True:
			db.counters.delete_one({'_id':name})

logging.info('loading vocabulary...');
start_time = time.time()
voca = []
idx = 0;
for each in db['vocabulary'].find():
	word = each['stem'];
	voca.append(word);

elapsed_time = time.time() - start_time;
logging.info('Done: loading vocabulary: %.3f ms', elapsed_time);

del_stored_topics();

logging.info('Run NMF for all tiles...');
start_time = time.time()
for tile_name in db.collection_names():
	if tile_name.endswith('_mtx') == False:
		continue;

	logging.info('Running NMF for %s...', tile_name);
	start_time_detail = time.time()

	tile_mtx_db = db[tile_name];

	tile_mtx = [];
	for each in tile_mtx_db.find():
		item = np.array([each['term_idx'], each['doc_idx'], each['freq']], dtype=np.int32);
		tile_mtx = np.append(tile_mtx, item, axis=0);
		
	tile_mtx = np.array(tile_mtx, dtype=np.int32).reshape(tile_mtx_db.count(), 3)

	if len(tile_mtx) < constants.MIN_ROW_FOR_TOPIC_MODELING:
		logging.debug('# of row is too small(%d). --> continue', len(tile_mtx))
		continue;

	elapsed_time_detail = time.time() - start_time_detail
	logging.info('Done: Running NMF for %s, elapse: %.3fms', tile_name, elapsed_time_detail);

	# run topic modeling
	logging.info('Running the Topic Modeling for %s...', tile_name);
	start_time_detail = time.time()
	A = matlab.double(tile_mtx.tolist()) # sparse function in function_runme() only support double type.
	[topics_list, w_scores, t_scores] = eng.function_runme(A, voca, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, nargout=3);

	topics = np.asarray(topics_list);
	topics = np.reshape(topics, (constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K));

	word_scores = np.asarray(w_scores);
	word_scores = np.reshape(word_scores, (constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K));

	topic_scores = np.asarray(t_scores)[0];

	# find original word and replace
	for topic in topics:
		for word in topic:
			s_count=0
			for each in db['vocabulary_hashmap'].find():
				if((word==each['stem']) and (s_count==0)):
					temp_word=each['word']
					temp_count=each['count']
					#logging.info('the word is :  %s  %s...', temp_word, each['stem'])
				if(word==each['stem']):
					if(each['count']>temp_count):
						temp_count=each['count']
						temp_word=each['word']
					s_count+=1	
			logging.debug('the result is %s   %s', word, temp_word)		
			word=temp_word			

	# store topics in DB
	tile = db[tile_name]
	tile_topic_name = tile_name.replace('_mtx','')+'_topics'
	tile_topic = db[tile_topic_name]	

	logging.debug(word_scores)
	logging.debug(topic_scores)

	topic_id = 0;
	for topic in topics:
		
		topic_id += 1;
		rank = 0;

		tile_topic.insert({'_id': get_next_sequence_value(tile_topic_name), 'topic_id': (constants.TOPIC_ID_MARGIN_FOR_SCORE+topic_id), 'topic_score': topic_scores[topic_id-1]})

		for word in topic: 

			word_score = word_scores[topic_id-1, rank];

			rank += 1;
			
			tile_topic.insert({'_id': get_next_sequence_value(tile_topic_name), 'topic_id': topic_id, 'rank': rank, 'word': word, 'score': word_score});

	elapsed_time_detail = time.time() - start_time_detail
	logging.info('Done: Running the Topic Modeling for %s, elapse: %.3fms', tile_name, elapsed_time_detail);

elapsed_time = time.time() - start_time;
logging.info('Done: NMF, elapsed: %.3fms', elapsed_time);

# eng = matlab.engine.start_matlab()
# eng.cd(constants.MATLAB_DIR)

# ret = eng.triarea(1.0,5.0)