import logging
import pymongo
import constants
import numpy as np
import time
from datetime import datetime 
import collections
import random


def getTwitterDate(date):
	date_format = ''
	if len(date) == 30:
		# date_format = "EEE MMM dd HH:mm:ss ZZZZZ yyyy";
		date_format = "%a %b %d %H:%M:%S %z %Y"
		
	else:
		# date_format = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'";
		date_format = "%Y-%m-%dT%H:%M:%S.000Z"


	return datetime.strptime(date, date_format)

class DBWrapper():

	def __init__(self):
		
		self.map_idx_to_word, self.map_word_to_idx, self.bag_words, self.stem_bag_words = self.read_voca()
		self.map_idx_to_doc = self.read_docs()
		self.map_related_docs = self.read_related_docs()

		return;

	def get_global_docs_map_idx_to_doc(self):
		return self.map_idx_to_doc

	def get_global_voca_map_idx_to_word(self):
		return self.map_idx_to_word

	def get_global_voca_map_word_to_idx(self):
		return self.map_word_to_idx

	def get_related_docs_map(self):
		return self.map_related_docs

	def read_docs(self):

		start_time = time.time()

		docs_file = open(constants.GLOBAL_DOC_FILE_PATH, 'r', encoding='UTF8')

		map_idx_to_doc = collections.OrderedDict()
		docs = docs_file.readlines()
		
		for idx, doc in enumerate(docs):

			v = doc.split('\t')

			# doc_time = getTwitterDate(v[1])
			# #year = doc_time.timetuple().tm_year
			# day_of_year = doc_time.timetuple().tm_yday

			map_idx_to_doc[idx+1] = collections.OrderedDict()
			map_idx_to_doc[idx+1] = [v[1], v[2], v[3], v[4], v[5]]

			# try:
			# 	if len(map_idx_to_doc[idx][day_of_year]) == 0:
			# 		map_idx_to_doc[idx][day_of_year] = []
			# except KeyError:
			# 	map_idx_to_doc[idx][day_of_year] = []

			# 	map_idx_to_doc[idx][day_of_year].append([v[2], v[3], v[4], v[5]])

		docs_file.close()

		elapsed_time= time.time() - start_time
		logging.info('read_docs(). Elapsed time: %.3fms', elapsed_time)	

		return map_idx_to_doc

	def read_voca(self):

		start_time = time.time()

		stem_bag_words =collections.OrderedDict()
		bag_words = collections.OrderedDict()
		map_word_to_idx = collections.OrderedDict()

		voca_file = open(constants.GLOBAL_VOCA_FILE_PATH, 'r', encoding='UTF8')
		voca_hash_file = open(constants.GLOBAL_VOCA_FILE_PATH+'_hash', 'r', encoding='UTF8')

		idx = 1
		map_idx_to_word = collections.OrderedDict()
		voca = voca_file.readlines()
		for line in voca:
			v = line.split('\t')
			bag_words[v[0]] = int(v[1])
			map_word_to_idx[v[0]] = idx
			map_idx_to_word[idx]=v[0]
			idx += 1

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

		elapsed_time= time.time() - start_time
		logging.info('read_voca(). Elapsed time: %.3fms', elapsed_time)	

		return map_idx_to_word, map_word_to_idx, bag_words, stem_bag_words

	def read_related_docs(self):
		start_time=time.time()

		rel_docs = collections.OrderedDict()
		with open(constants.MTX_DIR + 'total_mtx', 'r', encoding='UTF8') as f:
			lines = f.readlines()
			for line in lines:
				v = line.split('\t')

				word_idx = int(v[0])
				doc_idx = int(v[1])

				doc_time = getTwitterDate(self.map_idx_to_doc[doc_idx][0])
				date = doc_time.timetuple().tm_yday
				unixtime = time.mktime(doc_time.timetuple())
				username = str(self.map_idx_to_doc[doc_idx][3])
				text = str(self.map_idx_to_doc[doc_idx][4])

				if word_idx in rel_docs:
					pass
				else:
					rel_docs[word_idx] = collections.OrderedDict()

				if date in rel_docs[word_idx]:
					pass
				else:
					rel_docs[word_idx][date] = []

				rel_docs[word_idx][date].append([username, unixtime, text])

				# try:
				# 	rel_docs[word_idx][date].append(text)
				# except KeyError:
				# 	rel_docs[word_idx] = collections.OrderedDict()
				# 	rel_docs[word_idx][date] = []
				# 	rel_docs[word_idx][date].append(text)

				# if word_idx == 5318:
				# 	word = self.get_global_voca_map_idx_to_word()[word_idx]

				# 	logging.info('word: %s, doc: %s', word, text)

				# 	doc_list = rel_docs[word_idx][date]
				# 	for doc in doc_list:
				# 		logging.info(doc)
				# 	exit(0)

		elapsed_time= time.time() - start_time
		logging.info('get_related_docs_map(). Elapsed time: %.3fms', elapsed_time)	

		return rel_docs

	def get_xscore(self, level, x, y, year, yday):

		xscore_dir = constants.SPATIAL_XSCORE_DIR
		file_name = topic_file_name = 'xscore_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)

		score = 0.0
		try:
			with open(xscore_dir + file_name, 'r', encoding='UTF8') as f:
				score = float(f.readline())
		except FileNotFoundError:
			logging.debug('FileNotFoundError: %s', (xscore_dir + file_name))
			#score = -1.0
			#score = random.uniform(0, 1)
			score = 0.0

		return score

	def get_W(self, level, x, y, year, yday):

		W_dir = constants.W_PATH
		file_name = W_file_name = 'w_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)

		try:
			with open(W_dir + file_name, 'r', encoding='UTF8') as f:
				logging.info('get W')
		except FileNotFoundError:
			logging.info('not found')
		
		return W 

	def connect(self, ip, port):
		# self.conn = pymongo.MongoClient(ip, port);
		# self.dbname = constants.DB_NAME;
		# self.db = self.conn[self.dbname];
		return

	# The APIs for Topic Modeling Module
	def get_term_doc_matrix(self, id):
		
		start_time=time.time()

		logging.debug('id: %s', id)
		tile_mtx = [];
		for tile_name in self.db.collection_names():

			if tile_name.endswith('_mtx') == False:
				continue;

			if tile_name.find(str(id)) < 0:
				continue;

			logging.info(tile_name);

			tile_mtx_db = self.db[tile_name];
			
			for each in tile_mtx_db.find():
				item = np.array([each['term_idx'], each['doc_idx'], each['freq']], dtype=np.double);
				tile_mtx = np.append(tile_mtx, item, axis=0);
				
			tile_mtx = np.array(tile_mtx, dtype=np.double).reshape(tile_mtx_db.count(), 3)

			break;

		logging.debug(tile_mtx)

		elapsed_time=time.time() - start_time
		logging.info('get term_doc_matrix Execution time : %.3fms' , elapsed_time)


		return tile_mtx;	

	def get_term_doc_matrices(self, ids):
		
		start_time_get_mtx=time.time()

		tile_mtxs = [];

		for tile_id in ids:
			tile_mtxs.append(self.get_term_doc_matrix(tile_id));


		elapsed_time_get_mtx= time.time() - start_time_get_mtx
		logging.info('get_topics -get tile_mtx Execution time: %.3fms', elapsed_time_get_mtx)

		return tile_mtxs;

	def get_documents_in_tile(self, zoom_level, tile_id):
		# todo
		return "document_list";

	def get_vocabulary(self):

		start_time=time.time()

		voca = []
		for each in self.db['vocabulary'].find():
			word = {}
			word['stem'] =each['stem']
			word['count'] = each['count'];
			voca.append(word);

		elapsed_time=time.time() - start_time
		logging.info('get voca Execution time : %.3fms' , elapsed_time)

		return voca;

	def get_vocabulary_hashmap(self):

		start_time=time.time()

		voca_hash= [] 
		for each in self.db['vocabulary_hashmap'].find():
			voca_hash_elemet={}
			voca_hash_elemet['word']=each['word']
			voca_hash_elemet['stem']=each['stem']
			voca_hash_elemet['count']=each['count']
			voca_hash.append(voca_hash_elemet)


		elapsed_time=time.time() - start_time
		logging.info('get voca_hash Execution time : %.3fms' , elapsed_time)
		return voca_hash;	
	    	

	def get_raw_data(self, tile_id):

		start_time = time.time()

		logging.debug('tile_id: %s', tile_id)

		raw_data= []

		for tile_name in self.db.collection_names():

			if tile_name.endswith('_raw') == False:
				continue;
			
			if tile_name.find(str(tile_id)) < 0:
				continue;
		
			logging.info(tile_name);

			current_raw_db=self.db[tile_name];

			for each in current_raw_db.find():
				raw_text= {}
				raw_text['text']=each['text']
				raw_text['created_at']=each['created_at']
				raw_data.append(raw_text)

			break;

		elapsed_time=time.time() - start_time
		logging.info('get_raw_data Execution time : %.3fms' , elapsed_time)

		return raw_data;

	def get_fake_topics(self):

		topics = []
		for idx in range(0, constants.DEFAULT_NUM_TOPICS+1):
			topic = {}

			topic['score'] = 0.12

			words = []
			for each in range(0, constants.DEFAULT_NUM_TOP_K+1):
				word = {}
				word['word'] = 'word_example_'+str(idx)
				word['count'] = idx+1
				word['score'] = random.uniform(0, 1)
				words.append(word)

			topic['words'] = words
			topic['exclusiveness'] = random.uniform(0, 1)

			topics.append(topic)

		return topics

	def get_most_freq_word(self, stemmed_word):
		
		stemmed_list = list(self.stem_bag_words[stemmed_word].items())

		try:
			word = stemmed_list[0][0]
		except KeyError:
			word = ''

		return word
	
	def get_key(self,item):
		return float(item['score'])

	def get_topics(self, level, x, y, year, yday, topic_count, word_count, exclusiveness):
		
		logging.debug('get_topics(%d, %d, %d, %d, %d, %d, %d, %d)', level, x, y, year, yday, topic_count, word_count, exclusiveness);

		# date_format = "%Y-%m-%d"
		# date = datetime.strptime(date, date_format)

		exclusiveness = int(exclusiveness)

		datapath = constants.SPATIAL_TOPIC_PATH
		topic_file_name = 'topics_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y) + '_' + str(exclusiveness)

		topics = []
		
		try: 
			with open(datapath+topic_file_name, 'r') as f:
				
				lines = f.readlines()

				if len(lines) > 0:

					num_topics = 0
					for line in lines:
						logging.debug(line)

						v = line.split('\t')

						if len(v) == 1:
							
							if num_topics > 0:
								topic['words'] = words
								topic['exclusiveness']=exclusiveness
								topics.append(topic)

							num_topics += 1

							topic = {}
							words = []
							append_cnt = 0

							topic['score'] = float(v[0])
						else:

							if append_cnt < word_count:

								freq_word = self.get_most_freq_word(str(v[0]))

								word = {}
								word['word'] = freq_word
								word['count'] = int(v[1])
								word['score'] = float(v[2])

								words.append(word)
								append_cnt += 1
					
					topic['words'] = words
					topic['exclusiveness']=exclusiveness
					topics.append(topic)				
						
		except FileNotFoundError:
			logging.debug('%s is not exist.', (datapath+topic_file_name))
			# set fake data
			#topics = self.get_fake_topics()

		topics = sorted(topics, key=self.get_key, reverse=True)

		return topics[:topic_count]

	def get_all_topics(self, level, x, y, year, yday_from, yday_to):

		return

	def read_spatial_mtx(self, directory, mtx):

		v = mtx.split('_')

		res, center_cnt = self.read_spatial_mtx(directory, int(v[1]), int(v[2]), int(v[3]), int(v[4]), int(v[5]))

		return res, center_cnt

	def read_spatial_mtx(self, directory, year, yday, level, x, y):

		pos = str(x)+'_'+str(y)

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
			each_path = directory + each
			if os.path.exists(each_path) == False:
				continue
			
			with open(each_path) as each_file:
				isnt_center = 0 if idx == 0 else 1
				# each_mtx = []
				
				for line in each_file.readlines():
					
					v = line.split('\t')

					item = [int(v[0]), int(v[1]), int(v[2]), int(isnt_center)]
					# item = np.array([float(v[0]), float(v[1]), float(v[2]), float(isnt_center)], dtype=np.double)
					nmtx.append(item)

					# neighbor_mtx.append([int(v[0]), int(v[1]), int(v[2]), idx])
					line_cnt += 1
					if idx == 0: 
						center_count += 1

		return