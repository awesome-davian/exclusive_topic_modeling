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
	print("Usage: python topic_modeling_module_all.py [neighbor_matrix_dir(IN)] [global_voca(IN)] [topic_directory(OUT)]")
	print("For example, python topic_modeling_module_all.py ./mtx_neighbor/ ./voca/voca_131103-131105 ./topics/131103-131105/")
	exit(0)

module_name = sys.argv[0]
neighbor_mtx_dir = sys.argv[1]
global_voca_path = sys.argv[2]
topic_dir = sys.argv[3]

if not os.path.exists(neighbor_mtx_dir):
	logging.info('The Neighbor Term-Doc. Matrix Directory(%s) is Not exist. Exit %s.', neighbor_mtx_dir, module_name)
	exit(0)

if not os.path.exists(topic_dir):
    os.makedirs(topic_dir)

# Load the Matlab module
start_time = time.time()
eng = matlab.engine.start_matlab();
#eng.cd('../matlab/standard_nmf/');
eng.cd('../matlab/discnmf_code/');
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

def readVoca(word_map, bag_words, stem_bag_words):

	voca_file = open(global_voca_path, 'r', encoding='UTF8')
	voca_hash_file = open(global_voca_path+'_hash', 'r', encoding='UTF8')

	idx = 1
	list_voca = []
	voca = voca_file.readlines()
	for line in voca:
		v = line.split('\t')
		bag_words[v[0]] = int(v[1])
		word_map[v[0]] = idx
		idx += 1
		list_voca.append(v[0])

	# idx = 0
	# for key, value in bag_words.items():
	# 	if idx > 100:
	# 		break
	# 	print("%s, %d" % (key, int(value)))
	# 	idx += 1

	voca_hash = voca_hash_file.readlines()
	for line in voca_hash:
		v = line.split('\t')
		if v[0] not in stem_bag_words:
			stem_bag_words[v[0]] = collections.OrderedDict()

		stem_bag_words[v[0]][v[1]] = int(v[2])

	# idx = 0
	# for key, value in stem_bag_words.items():
	# 	if idx > 100:
	# 		break

	# 	print("%s, %s, %s" % (key, list(value)[0], value[list(value)[0]]))
	# 	idx += 1

	voca_file.close()
	voca_hash_file.close()

	return list_voca

def readLocalVoca(word_map, bag_words):

	voca_file_name = tile_name.replace('mtx_', 'voca_')
	local_voca_file = open(neighbor_mtx_dir+voca_file_name, 'r', encoding='UTF8')

	idx = 1
	list_voca = []
	voca = local_voca_file.readlines()
	for line in voca:
		v = line.split('\t')
		bag_words[v[0]] = int(v[1])
		word_map[v[0]] = idx
		idx += 1
		list_voca.append(v[0])

	local_voca_file.close()

	return list_voca

def readLocalDoc():
	doc_file_name = tile_name.replace('mtx_', 'docmap_')
	local_doc_file = open(neighbor_mtx_dir+doc_file_name, 'r', encoding='UTF8')

	list_doc = []
	docs = local_doc_file.readlines()
	for doc in docs:
		list_doc.append(doc)

	local_doc_file.close()

	return list_doc

# def readTermDocMtx(need_neighbor_mtx):

# 	if need_neighbor_mtx == True:
# 		mtx_file = open(neighbor_mtx_dir + tile_name, 'r', encoding='UTF8')
# 	else:
# 		mtx_file = open(neighbor_mtx_dir + tile_name.replace('mtx_', 'nmtx_'), 'r', encoding='UTF8')
	
# 	lines = mtx_file.readlines()

# 	tile_mtx = [];
# 	for line in lines:
# 		v = line.split('\t')
# 		item = np.array([v[0], v[1], v[2]], dtype=np.int32)
# 		tile_mtx = np.append(tile_mtx, item, axis=0)

# 	mtx_file.close()

# 	logging.info("#lines: %s", len(lines))
# 	tile_mtx = np.array(tile_mtx, dtype=np.int32).reshape(len(lines), 3)

# 	return tile_mtx

def readTermDocMtx(mtx, nmtx):

	mtx_file = open(neighbor_mtx_dir + tile_name, 'r', encoding='UTF8')

	lines = mtx_file.readlines()

	tile_mtxs = [];

	mtx_dict = collections.OrderedDict()
	for nid in range(0, 9):
		mtx_dict[nid] = []

	for line in lines:
		v = line.split('\t')
		mtx_dict[int(v[3])].append(line)

	for nid in range(0, 9):

		temp_mtx = []
		for each in mtx_dict[nid]:
			v = each.split('\t')
			item = np.array([float(v[0]), float(v[1]), float(v[2])], dtype=np.double)
			temp_mtx = np.append(temp_mtx, item, axis=0)
		temp_mtx = np.array(temp_mtx, dtype=np.double).reshape(len(mtx_dict[nid]), 3)

		if nid == 0:
			mtx = temp_mtx
		else:
			nmtx.append(temp_mtx)

	mtx_file.close()

	logging.info("#lines: %s", len(lines))

	return mtx, nmtx

logging.info('loading vocabulary...');
s_time_voca = time.time()

stem_bag_words_g =collections.OrderedDict()
bag_words_g = collections.OrderedDict()
word_map_g = collections.OrderedDict()

list_voca_g = readVoca(word_map_g, bag_words_g, stem_bag_words_g)

elapsed_time = time.time() - s_time_voca;
logging.info('Done: loading vocabulary: %.3f s', elapsed_time);

_, _, filenames = next(walk(neighbor_mtx_dir), (None, None, []))

logging.info('Run NMF for all tiles...');
mtx_tile_list = (mtx_tile for mtx_tile in filenames if mtx_tile.startswith('mtx_') == True)

# logging.info('The number of matrices: %d', sum(1 for x in mtx_tile_list))

passed_cnt = 0
for tile_name in mtx_tile_list:

	v = tile_name.split('_')
	if int(v[3]) < 13:
		continue;

	logging.info('Load vocabulary for %s', tile_name);
	start_time_detail = time.time()

	# read local voca
	bag_words_l = collections.OrderedDict()
	word_map_l = collections.OrderedDict()
	# doc_map_l = collections.OrderedDict()

	list_voca_l = readLocalVoca(word_map_l, bag_words_l)

	logging.info('Vocabulary size: %d', len(list_voca_l))

	elapsed_time = time.time() - start_time_detail;
	logging.info('Done: loading vocabulary: %.3f s', elapsed_time);

	logging.info('Load document for %s', tile_name);
	start_time_detail = time.time()

	list_doc_l = readLocalDoc()

	logging.info('Doc size: %d', len(list_doc_l))
	
	logging.info('Loading document for %s...', tile_name);
	elapse_time = time.time() - start_time_detail;	

	logging.info('Loading Term-Doc. Matrices for %s...', tile_name);
	start_time_detail = time.time()

	tile_mtx = []
	tile_nmtx = []

	# read single term-doc matrix
	[tile_mtx, tile_nmtx] = readTermDocMtx(tile_mtx, tile_nmtx)

	# tile_mtx = readTermDocMtx(False)

	if len(tile_mtx) < constants.MIN_ROW_FOR_TOPIC_MODELING:
		logging.debug('# of row is too small(%d). --> continue', len(tile_mtx))
		passed_cnt += 1
		continue

	# tile_nmtx = readTermDocMtx(True)

	elapsed_time_detail = time.time() - start_time_detail
	logging.info('Done: Loading Term-Doc. Matrices for %s, elapse: %.3fms', tile_name, elapsed_time_detail);	

	logging.info('Running the Topic Modeling for %s...', tile_name);
	start_time_detail = time.time()
	A = matlab.double(tile_mtx.tolist()) # sparse function in function_runme() only support double type.
	# N = matlab.double(tile_nmtx.tolist()) # sparse function in function_run_extm().
	N = []
	for each in tile_nmtx:
		if each == []:
			N.append(each)
		else:
			N.append(each.tolist())

	for exclusiveness in range(0, 6):

		# [topics_list, w_scores, t_scores] = eng.function_runme(A, list_voca_l, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, nargout=3);
		[topics_list, w_scores, t_scores] = eng.function_run_extm(A, N, exclusiveness/5, list_voca_l, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, nargout=3);

		topics = np.asarray(topics_list);
		topics = np.reshape(topics, (constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K));

		word_scores = np.asarray(w_scores);
		word_scores = np.reshape(word_scores, (constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K));

		topic_scores = np.asarray(t_scores);

		# store topics in DB		

		# logging.debug(word_scores)
		# logging.debug(topic_scores)

		topic_name = tile_name.replace('mtx_','topics_')
		logging.info('file_name: %s', topic_dir+topic_name)
		topic_file = open(topic_dir+topic_name+'_'+str(exclusiveness), 'a', encoding='UTF8')
		# topic_file = open(topic_dir+topic_name, 'a', encoding='UTF8')

		topic_id = 0;
		for topic in topics:
			
			topic_file.write(str(topic_scores[topic_id,0]) + '\n')

			for rank, word in enumerate(topic): 

				word_score = word_scores[topic_id, rank];				
				
				temp_count=0;
				temp_word="";
				s_count=0

				g_word = list_voca_g[int(word)]

				res_word = ''
				for key, value in stem_bag_words_g[g_word].items():
					res_word = key
					break

				word_cnt = bag_words_l[word]

				topic_file.write(str(res_word) + '\t' + str(word_cnt) + '\t' + str(word_score) + '\n')
				#logging.info(str(rank) + '\t' + str(res_word) + '\t' + str(word_score) + '\n')

			topic_id += 1;
	  
		topic_file.close()	

	elapsed_time_detail = time.time() - start_time_detail
	logging.info('Done: Running the Topic Modeling for %s, elapse: %.3fms', tile_name, elapsed_time_detail);

elapsed_time = time.time() - start_time;
logging.info('Done: NMF, elapsed: %.3fms', elapsed_time);
logging.debug('passed_cnt: %d', passed_cnt)
