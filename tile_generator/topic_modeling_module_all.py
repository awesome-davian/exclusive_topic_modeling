import os, sys
sys.path.insert(0, '../')
import constants
import pymongo
import numpy as np
import matlab.engine
import logging, logging.config
import time
import collections
from os import walk

logging.config.fileConfig('logging.conf')
logging.info('Run topic modeling for all tiles using Disc NMF')

arglen = len(sys.argv)
if arglen != 4:
	print("Usage: python topic_modeling_module_all.py [matrix_dir(IN)] [global_voca(IN)] [topic_directory(OUT)]")
	print("For example, python topic_modeling_module_all.py ./mtx/ ./voca/voca_131103-131105 ./topics/131103-131105/")
	exit(0)

module_name = sys.argv[0]
mtx_dir = sys.argv[1]
global_voca_path = sys.argv[2]
topic_dir = sys.argv[3]

if not os.path.exists(mtx_dir):
	logging.info('The Term-Doc. Matrix Directory(%s) is Not exist. Exit %s.', mtx_dir, module_name)
	exit(0)

if not os.path.exists(topic_dir):
    os.makedirs(topic_dir)

xscore_dir = './data/xscore/' + constants.DATA_RANGE + '/'
if not os.path.exists(xscore_dir):
    os.makedirs(xscore_dir)

w_dir = './data/w/' + constants.DATA_RANGE + '/'
if not os.path.exists(w_dir):
    os.makedirs(w_dir)


# Load the Matlab module
start_time = time.time()
eng = matlab.engine.start_matlab();
# eng.cd('../matlab/standard_nmf/');
# eng.cd('../matlab/discnmf_code/');
elapsed_time = time.time() - start_time;
logging.info('matlab loading time: %.3f s', elapsed_time);

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

def read_voca(word_map, bag_words, stem_bag_words):

	voca_file = open(global_voca_path, 'r', encoding='UTF8')
	voca_hash_file = open(global_voca_path+'_hash', 'r', encoding='UTF8')
	logging.debug('voca path: %s', global_voca_path)
	
	idx = 1
	res_voca = collections.OrderedDict()
	for line in voca_file.readlines():
		v = line.split('\t')
		bag_words[v[0]] = int(v[1])
		word_map[v[0]] = idx
		res_voca[idx] = v[0]
		idx += 1

	logging.info('vocabulary size: %d', idx)

	# idx = 0
	# for key, value in bag_words.items():
	# 	if idx > 100:
	# 		break
	# 	print("%s, %d" % (key, int(value)))
	# 	idx += 1

	idx = 1
	for line in voca_hash_file.readlines():
		v = line.split('\t')
		if v[0] not in stem_bag_words:
			stem_bag_words[v[0]] = collections.OrderedDict()

		stem_bag_words[v[0]][v[1]] = int(v[2])
		idx += 1

	logging.info('vocabulary hashfile size: %d', idx)

	# idx = 0
	# for key, value in stem_bag_words.items():
	# 	if idx > 100:
	# 		break

	# 	print("%s, %s, %s" % (key, list(value)[0], value[list(value)[0]]))
	# 	idx += 1

	voca_file.close()
	voca_hash_file.close()

	return res_voca

def read_mtx(mtx):

	v = mtx.split('_')	# [0]: mtx, [1]: year, [2]: day_of_year, [3]: level, [4]: x, [5]: y

	x = int(v[4])
	y = int(v[5])

	pos = v[4]+'_'+v[5]

	neighbor_names = []

	temp_name = mtx.replace(pos, '')
	neighbor_names.append(temp_name+str(x+0)+'_'+str(y+0)) # it's me
	
	neighbor_names.append(temp_name+str(x+1)+'_'+str(y+1))
	neighbor_names.append(temp_name+str(x+1)+'_'+str(y+0))
	neighbor_names.append(temp_name+str(x+1)+'_'+str(y-1))
	neighbor_names.append(temp_name+str(x+0)+'_'+str(y+1))

	neighbor_names.append(temp_name+str(x+0)+'_'+str(y-1))
	neighbor_names.append(temp_name+str(x-1)+'_'+str(y+1))
	neighbor_names.append(temp_name+str(x-1)+'_'+str(y+0))
	neighbor_names.append(temp_name+str(x-1)+'_'+str(y-1))

	nmtx = []

	line_cnt = 0
	center_count = 0
	for idx, each in enumerate(neighbor_names):
		each_path = mtx_dir + each
		if os.path.exists(each_path) == False:
			continue
		
		with open(each_path) as each_file:
			isnt_center = 0 if idx == 0 else 1
			# each_mtx = []
			
			for line in each_file.readlines():
				line = line.strip()
				v = line.split('\t')

				item = np.array([int(v[0]), int(v[1]), int(v[2]), int(isnt_center)], dtype=np.int32)
				# item = np.array([float(v[0]), float(v[1]), float(v[2]), float(isnt_center)], dtype=np.double)
				nmtx = np.append(nmtx, item, axis=0)

				# neighbor_mtx.append([int(v[0]), int(v[1]), int(v[2]), idx])
				line_cnt += 1
				if idx == 0: 
					center_count += 1
			
	nmtx = np.array(nmtx, dtype=np.int32).reshape(line_cnt, 4)
	return nmtx, center_count

def create_w(mtx, v, num_topics, num_words):

	eng.cd('../matlab/standard_nmf/')
	w = eng.function_runme(mtx, v, num_topics, num_words, nargout=1)

	# print (W)
	# 	W_array =np.asarray(W)
	# 	for each in W_array:
	# 		print(each)

	w_name = tile_name.repace('mtx_', 'w_')
	with open(w_dir+w_name, 'w', encoding='UTF8') as f:
		f.write(str(w)+'\n')

def create_topics(mtx, xcls_value, v, num_topics, num_words, opmode):

	eng.cd('../matlab/discnmf_code/')
	[topics_list, w_scores, t_scores, x_score] = eng.function_run_extm(mtx, xcls_value, v, num_topics, num_words, nargout=4)

	topics = np.asarray(topics_list)
	topics = np.reshape(topics, (num_topics, num_words))

	word_scores = np.asarray(w_scores);
	word_scores = np.reshape(word_scores, (num_topics, num_words))

	topic_scores = np.asarray(t_scores)
	# xls_scores = np.asarry(x_scores)

	prefix = 'stopics_' if opmode == constants.OPMODE_SPATIAL_MTX else 'ttopics_'
	topic_name = tile_name.replace('mtx_', prefix)
	logging.info('file_name: %s', topic_dir+topic_name)
	topic_file = open(topic_dir+topic_name+'_'+str(exclusiveness), 'a', encoding='UTF8')

	topic_id = 0;
	for topic in topics:
		
		topic_file.write(str(topic_scores[topic_id,0]) + '\n')

		for rank, word in enumerate(topic): 

			word_score = word_scores[topic_id, rank];				
			
			temp_count=0;
			temp_word="";
			s_count=0

			g_word = g_voca[word]

			res_word = ''
			for key, value in stem_bag_words[g_word].items():
				res_word = key
				break

			word_cnt = bag_words[word]

			topic_file.write(str(res_word) + '\t' + str(word_cnt) + '\t' + str(word_score) + '\n')
			#logging.info(str(rank) + '\t' + str(res_word) + '\t' + str(word_score) + '\n')

		topic_id += 1;
  
	topic_file.close()

	prefix = 'sxscore_' if opmode == constants.OPMODE_SPATIAL_MTX else 'txscore_'
	x_score_name = tile_name.replace('mtx_', prefix)
	logging.info('file_name: %s', xscore_dir+x_score_name)
	with open(xscore_dir+x_score_name, 'w', encoding='UTF8') as f:
		f.write(str(xls_score) + '\n')	

	return 

logging.info('loading vocabulary...');
s_time_voca = time.time()

stem_bag_words = collections.OrderedDict()
bag_words = collections.OrderedDict()
word_map = collections.OrderedDict()

g_voca = read_voca(word_map, bag_words, stem_bag_words)

elapsed_time = time.time() - s_time_voca;
logging.info('Done: loading vocabulary: %.3f s', elapsed_time);

_, _, filenames = next(walk(mtx_dir), (None, None, []))

logging.info('Run NMF for all tiles...');
mtx_tile_list = (mtx_tile for mtx_tile in filenames if mtx_tile.startswith('mtx_') == True)

passed_cnt = 0
for tile_name in mtx_tile_list:

	print(tile_name)

	v = tile_name.split('_')
	if int(v[3]) != 13:
		continue;

	logging.info('Loading Term-Doc. Matrices for %s...', tile_name);
	start_time_detail = time.time()

	# read term-doc matrices including neighbor tiles
	tile_mtx, center_cnt = read_mtx(tile_name)

	if center_cnt < constants.MIN_ROW_FOR_TOPIC_MODELING:
		logging.debug('# of row is too small(%d). --> continue', center_cnt)
		passed_cnt += 1
		continue

	elapsed_time_detail = time.time() - start_time_detail
	logging.info('Done: Loading Term-Doc. Matrices for %s, elapse: %.3fms', tile_name, elapsed_time_detail);	

	logging.info('Running the Topic Modeling for %s...', tile_name);
	start_time_detail = time.time()
	# A = matlab.double(tile_mtx.tolist()) # sparse function in function_runme() only support double type.
	# A = []
	# A.append(matlab.int32(tile_mtx.tolist()))
	A = tile_mtx.tolist()

	#change vocabulary type from dict to list 
	voca = []
	for key, value in g_voca.items():
		temp = [key,value]
		voca.append(temp)

	x_score = 0

	# create_w(A, voca, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K)

	# store topics in DB	

	for exclusiveness in range(0, 6):

		create_topics(A, exclusiveness/5, voca, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, constants.OPMODE_SPATIAL_MTX)
		create_topics(A, exclusiveness/5, voca, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, constants.OPMODE_TEMPORAL_MTX)

	elapsed_time_detail = time.time() - start_time_detail
	logging.info('Done: Running the Topic Modeling for %s, elapse: %.3fms', tile_name, elapsed_time_detail);

elapsed_time = time.time() - start_time;
logging.info('Done: NMF, elapsed: %.3fms', elapsed_time);
logging.debug('passed_cnt: %d', passed_cnt)
