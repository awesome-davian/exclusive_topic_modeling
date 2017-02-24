import sys
import pymongo
import constants
import numpy as np


#import constants
# import matlab.engine
# eng = matlab.engine.start_matlab()
# eng.cd(constants.MATLAB_DIR)

# for mongodb
# conn = pymongo.MongoClient("localhost", constants.DEFAULT_MONGODB_PORT);
# dbname = constants.DB_NAME;
# db = conn[dbname];

#------------------------------------------------------------------------------------------------
# read top 50 line

max_num = int(sys.argv[2])
print('max_num: %d' % max_num)
#output_directory = './'

input_file_name = sys.argv[1]
# output_file_name = input_file_name + '_top' + max_num
output_file_name = 'top' + str(max_num) + '_'+ input_file_name

input_file = open(input_file_name, 'r')
output_file = open(output_file_name, 'w')

idx = 0;
for line in input_file:

	if idx >= max_num:
		break;
	
	print('%s' % line.replace('\n',''), file=output_file)
	print('%d\n%s' % (idx,line))
	idx += 1;


input_file.close()
output_file.close()



#ret = eng.triarea(1.0,5.0)
#------------------------------------------------------------------------------------------------
# conn = pymongo.MongoClient("localhost", constants.DEFAULT_MONGODB_PORT);

# dbname = constants.DB_NAME;
# db = conn[dbname];

# voca = []
# idx = 0;
# for each in db['vocabulary'].find():
# 	word = each['stem'];
# 	voca.append(word);

# print('Done: loading vocabulary');

# tile_name = 'level11_2013_w52_2572676_mtx'
# tile_mtx_db = db[tile_name];

# tile_mtx = [];
# for each in tile_mtx_db.find():
# 	item = np.array([each['term_idx'], each['doc_idx'], each['freq']], dtype=np.int32);
# 	tile_mtx = np.append(tile_mtx, item, axis=0);
	
# tile_mtx = np.array(tile_mtx, dtype=np.int32).reshape(tile_mtx_db.count(), 3)

# if len(tile_mtx) < constants.MIN_ROW_FOR_TOPIC_MODELING:
# 	print('# of row is too small(%d). --> continue', len(tile_mtx))
# 	exit(1)

# print('Done: Running NMF for %s', tile_name);

# # run topic modeling
# print('Running the Topic Modeling for %s...', tile_name);
# A = matlab.double(tile_mtx.tolist()) # sparse function in function_runme() only support double type.
# [topics_list, w_scores, t_scores] = eng.function_runme(A, voca, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, nargout=3);

# topics = np.asarray(topics_list);
# topics = np.reshape(topics, (constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K));

# word_scores = np.asarray(w_scores);
# word_scores = np.reshape(word_scores, (constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K));

# topic_scores = np.asarray(t_scores);

# print(topics)
# print(word_scores)
# print(topic_scores)


#------------------------------------------------------------------------------------------------
# drop database

# conn = pymongo.MongoClient("localhost", constants.DEFAULT_MONGODB_PORT);

# dbname = constants.DB_NAME;
# db = conn[dbname];

# topics = [];
# for tile_name in db.collection_names():

# 	# find out only the 
# 	if tile_name.find('_2013_') > 0:	
# 		db.drop_collection(tile_name);

# for item in db.counters.find():
# 	name = item['_id']
# 	if name.find('_2013_') > 0:
# 		db.counters.delete_one({'_id':name})

#------------------------------------------------------------------------------------------------
# collection name change

# conn = pymongo.MongoClient("localhost", constants.DEFAULT_MONGODB_PORT);

# dbname = constants.DB_NAME;
# db = conn[dbname];

# topics = [];
# for tile_name in db.collection_names():

# 	if tile_name.startswith('level') == False:
# 		continue;

# 	# find out only the 
# 	if tile_name.endswith('_topics') == True:
# 		db[tile_name].drop();
# 		continue;
# 	elif tile_name.endswith('_raw') == False:
# 		db[tile_name].rename(tile_name + '_raw')

#------------------------------------------------------------------------------------------------
# recalculate the counter

# conn = pymongo.MongoClient("localhost", constants.DEFAULT_MONGODB_PORT);

# dbname = constants.DB_NAME;
# db = conn[dbname];

# for each in db.counters.find():
# 	print(each['_id'])

# 	db.counters.update({'_id': each['_id']}, {'$set': {'_id': each['_id']+'_raw'}})
