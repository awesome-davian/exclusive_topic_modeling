import os
import logging
import constants
import numpy as np
import time
from datetime import datetime
import collections
import random
from nltk import PorterStemmer

porter_stemmer=PorterStemmer();

def getTwitterDate(date):
	date_format = ''
	if len(date) == 30:
		# date_format = "EEE MMM dd HH:mm:ss ZZZZZ yyyy";
		date_format = "%a %b %d %H:%M:%S %z %Y"

	else:
		# date_format = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'";
		date_format = "%Y-%m-%dT%H:%M:%S.000Z"


	return datetime.strptime(date, date_format)

def getTwitterHour(date):
	date_format = ''
	if len(date) == 30:
		# date_format = "EEE MMM dd HH:mm:ss ZZZZZ yyyy";
		date_format = "%a %b %d %H:%M:%S %z %Y"

	else:
		# date_format = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'";
		date_format = "%Y-%m-%dT%H:%M:%S.000Z"


	return datetime.strptime(date, date_format).timetuple().tm_hour, datetime.strptime(date, date_format).timetuple().tm_min

class DBWrapper():

	def __init__(self):

		self.map_idx_to_word, self.map_word_to_idx, self.bag_words, self.stem_bag_words = self.read_voca()
		self.map_idx_to_doc = self.read_docs()
		self.map_related_docs = self.read_related_docs()
		# self.map_max_word_freq = self.get_max_word_freq()
		# self.map_tdm = self.read_term_doc_matrices()
		# self.map_max_doc_freq = self.read_max_doc_frequency()
		# self.map_tdm = {}

		return

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

			# v[0]: index
			# v[1]: date
			# v[2]: lon
			# v[3]: lat
			# v[4]: author
			# v[5]: text

			# doc_time = getTwitterDate(v[1])
			# #year = doc_time.timetuple().tm_year
			# day_of_year = doc_time.timetuple().tm_yday

			map_idx_to_doc[idx+1] = collections.OrderedDict()
			map_idx_to_doc[idx+1] = [v[1], v[2], v[3], v[4], v[5]]

			# map_idx_to_doc[0]: date
			# map_idx_to_doc[1]: lon
			# map_idx_to_doc[2]: lat
			# map_idx_to_doc[3]: author
			# map_idx_to_doc[4]: text

			# try:
			# 	if len(map_idx_to_doc[idx][day_of_year]) == 0:
			# 		map_idx_to_doc[idx][day_of_year] = []
			# except KeyError:
			# 	map_idx_to_doc[idx][day_of_year] = []

			# 	map_idx_to_doc[idx][day_of_year].append([v[2], v[3], v[4], v[5]])

		docs_file.close()

		elapsed_time = time.time() - start_time
		logging.info('read_docs(). Elapsed time: %.3fms', elapsed_time)

		return map_idx_to_doc

	def read_voca(self):

		start_time = time.time()

		stem_bag_words = collections.OrderedDict()
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
			map_idx_to_word[idx] = v[0]
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

		elapsed_time = time.time() - start_time
		logging.info('read_voca(). Elapsed time: %.3fms', elapsed_time)

		return map_idx_to_word, map_word_to_idx, bag_words, stem_bag_words

	def read_related_docs(self):
		start_time = time.time()

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

		elapsed_time = time.time() - start_time
		logging.info('read_related_docs(). Elapsed time: %.3fms', elapsed_time)

		return rel_docs

	def get_xscore(self, level, x, y, year, yday):

		xscore_dir = constants.SPATIAL_XSCORE_DIR
		file_name = topic_file_name = 'xscore_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)

		east = 0.0
		west = 0.0
		south = 0.0
		north = 0.0
		
		try:
			with open(xscore_dir + file_name, 'r', encoding='UTF8') as f:
				east = float(f.readline())
				west = random.uniform(0, 1)
				south = random.uniform(0, 1)
				north = random.uniform(0, 1)
				# TODO: need to be modified to get 4 direction heatmap
		except FileNotFoundError:
			logging.debug('FileNotFoundError: %s', (xscore_dir + file_name))
			#score = -1.0
			#score = random.uniform(0, 1)
			east = 0.0
			west = 0.0
			south = 0.0
			north = 0.0

		#logging.info(east)
		#logging.info(west)
		return east, west, south, north

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

		start_time = time.time()

		logging.debug('get_term_dic_matrix(), id: %s', id)
		tile_mtx = []
		for tile_name in self.db.collection_names():

			if tile_name.endswith('_mtx') == False:
				continue

			if tile_name.find(str(id)) < 0:
				continue

			logging.info(tile_name)

			tile_mtx_db = self.db[tile_name]

			for each in tile_mtx_db.find():
				item = np.array([each['term_idx'], each['doc_idx'], each['freq']], dtype=np.double)
				tile_mtx = np.append(tile_mtx, item, axis=0)

			tile_mtx = np.array(tile_mtx, dtype=np.double).reshape(tile_mtx_db.count(), 3)

			break

		logging.debug(tile_mtx)

		elapsed_time = time.time() - start_time
		logging.info('get term_doc_matrix Execution time : %.3fms', elapsed_time)

		return tile_mtx

	def get_term_doc_matrices(self, ids):

		start_time_get_mtx = time.time()

		tile_mtxs = []

		for tile_id in ids:
			tile_mtxs.append(self.get_term_doc_matrix(tile_id))

		elapsed_time_get_mtx = time.time() - start_time_get_mtx
		logging.info('get_term_doc_matrices(), Execution time: %.3fms', elapsed_time_get_mtx)

		return tile_mtxs

	# def get_tdm(self, tileid):

	# 	tdm = []
	# 	try:
	# 		tdm = self.map_tdm[tileid]
	# 	except KeyError as e:
	# 		tdm = []

	# 	return tdm

	def get_frequency_in_tile(self, tileid):

		datapath = constants.FREQ_DIR

		word_freq = 0
		doc_freq = 0

		tileid = 'wfreq_' + tileid

		try: 

			with open(datapath+tileid, 'r', encoding='UTF8') as f:	

				try:
					lines = f.readlines()
					line = lines[0]
					v = line.split('\t')
					word_freq = int(v[0])
					doc_freq = int(v[1])
				except KeyError as ke:
					word_freq = 0
					doc_freq = 0	

			# tdm = self.map_tdm[tileid]
			# tdm = self.read_tem_doc_matrix(tileid)
			# if tdm.size > 0 :
			# 	tdm = tdm[tdm[:,0]==word_idx]

			# 	# for item in tdm:
			# 	# 	freq += int(item[2])
			# 	freq = tdm.sum(axis=0)
			# 	# logging.info('freq: %d', freq)
			# 	try:
			# 		freq = int(freq[2])
			# 	except IndexError as ie:
			# 		freq = 0
		
		except FileNotFoundError as fe:
			print(fe)
			word_freq = 0
			doc_freq = 0

		return word_freq, doc_freq

	def get_tfidf_variation(self, word, tileid):

		datapath = constants.TFIDF_DIR		
		tfidf_var = 0.0

		tilename = 'tfidf_' + tileid

		try:
			query_idx = self.map_word_to_idx[word]

			try: 
				with open(datapath+tilename, 'r', encoding='UTF8') as f:

					lines = f.readlines()
					for line in lines:
						v = line.split('\t')

						temp_word_idx = v[0]

						if temp_word_idx == query_idx:
							tfidf_var = v[1]
							break

			except FileNotFoundError as fe:
				tfidf_var = 0.0

		except KeyError as ke:
			tfidf_var = 0.0
			

		return tfidf_var

	def get_tfidf_values(self, word, tileid):
		
		datapath = constants.TFIDF_DIR		
		tfidf_values = 0.0

		tilename = 'tfidf_eightdays_' + tileid

		try:
			query_idx = self.map_word_to_idx[word]

			try: 
				with open(datapath+tilename, 'r', encoding='UTF8') as f:

					lines = f.readlines()
					for line in lines:
						v = line.split('\t')

						temp_word_idx = v[0]

						if int(temp_word_idx) == int(query_idx):
							tfidf_values = float(v[1])
							break

			except FileNotFoundError as fe:
				tfidf_values = 0.0

		except KeyError as ke:
			tfidf_values = 0.0

		return tfidf_values

	def get_tfidf_values2(self, word, tileid):
		
		datapath = constants.TFIDF_DIR		
		tfidf_values = 0.0

		tilename = 'tfidf_eightdays_' + tileid

		try:
			query_idx = self.map_word_to_idx[word]

			try: 
				with open(datapath+tilename, 'r', encoding='UTF8') as f:

					lines = f.readlines()
					for line in lines:
						v = line.split('\t')

						temp_word_idx = v[0]

						if int(temp_word_idx) == int(query_idx):
							tfidf_values = float(v[1])
							break

			except FileNotFoundError as fe:
				tfidf_values = 0.0

		except KeyError as ke:
			tfidf_values = 0.0

		return tfidf_values

	def get_word_frequency(self, word, level, x, y, year, yday):

		datapath = constants.FREQ_DIR

		word_freq = 0
		doc_freq = 0

		tileid = str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)
		tileid = 'wfreq_' + tileid
		
		try:
			query_idx = self.map_word_to_idx[word]
			#logging.info('word: %s, query_idx: %d', word, query_idx)

			try: 
				with open(datapath+tileid, 'r', encoding='UTF8') as f:

					lines = f.readlines()
					is_firstline = True
					for line in lines:

						# pass the first line
						if is_firstline == True:	
							is_firstline = False
							continue

						v = line.split('\t')
						
						temp_word_idx = int(v[0])

						if temp_word_idx == query_idx:
							word_freq = int(v[1])
							doc_freq = int(v[2])
							break

				# tdm = self.map_tdm[tileid]
				# tdm = self.read_tem_doc_matrix(tileid)
				# if tdm.size > 0 :
				# 	tdm = tdm[tdm[:,0]==word_idx]

				# 	# for item in tdm:
				# 	# 	freq += int(item[2])
				# 	freq = tdm.sum(axis=0)
				# 	# logging.info('freq: %d', freq)
				# 	try:
				# 		freq = int(freq[2])
				# 	except IndexError as ie:
				# 		freq = 0
			
			except FileNotFoundError as fe:
				print(fe)
				word_freq = 0
				doc_freq = 0

		except KeyError as ke:
			print(ke)
			word_freq = 0
			doc_freq = 0

		return word_freq, doc_freq

	def get_docs(self, word, x, y, level, year, yday):

		docs = []

		try:
			# word to idx
			word_idx = self.map_word_to_idx[word]

			# get term-doc matrix
			tileid = str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)		
		
			# tdm = self.map_tdm[tileid]
			tdm = self.read_tem_doc_matrix(tileid)
			if tdm.size > 0 :			
				tdm = tdm[tdm[:,0]==word_idx]

				# get docs including the word_idx
				for item in tdm:
					doc_idx = item[1]
					doc = self.map_idx_to_doc[doc_idx]
					docs.append(doc)
		except KeyError as e:
			logging.debug('KeyError: %s', e)


		return docs

	# get_docs2: not by word, but by word list.
	# def get_docs2(self, words, x, y, level, year, yday):

	# 	docs = []
		
	# 	word_idx = []
	# 	for word in words:
	# 		try:
	# 			word_idx.append(self.map_word_to_idx[word])
	# 		except KeyError as e:
	# 			logging.debug('KeyError: %s', e)

	# 	try:
	# 		# get term-doc matrix
	# 		tileid = 'mtx_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)				
	# 		tdm = self.map_tdm[tileid]
	# 		tdm = tdm[np.logical_or.reduce([tdm[:,0] == w for w in word_idx])]

	# 		tdm = tdm[:,1]
	# 		setTdm = set(tdm)

	# 		for doc_idx in setTdm:
	# 			doc = self.map_idx_to_doc[doc_idx]
	# 			docs.append(doc)

	# 	except KeyError as e:
	# 		logging.debug('KeyError: %s', e)

	# 	return docs

	def read_tem_doc_matrix(self, tileid):
		
		datapath = constants.MTX_DIR

		mtx = np.array([])
		tileid = 'mtx_' + tileid

		try:
			
			with open(datapath+tileid, 'r', encoding='UTF8') as f:
				lines = f.readlines()
				for line in lines:
					v = line.split('\t')
					word_idx = v[0]
					doc_idx = v[1]
					word_freq = v[2]

					item = np.array([v[0], v[1], v[2]], dtype=np.int32)
					mtx = np.append(mtx, item, axis=0)

				mtx = np.array(mtx, dtype=np.int32).reshape(len(lines), 3)		

		except FileNotFoundError as fe:
			logging.debug('FileNotFoundError: %s', fe);
			pass

		return mtx

	def get_max_word_freq(self):

		datapath = constants.FREQ_DIR

		max_all = collections.OrdderedDict()

		for root, directories, files in os.walk(datapath):

			for filename in files:
									
				if filename.startswith('freq_') == True:
					
					tileid = filename[filename.find('_')+1:]
					freq, _ = self.get_frequency_in_tile(tileid)

					v = filename.split('_')
					level = v[2]
					day = str(v[1][1:])
			
					if day not in max_all:
						max_all[day] = collections.OrderedDict()

					if level not in max_all[day]:
						max_all[day][level] = 0

					if freq > max_all[day][level]:
						max_all[day][level] = freq

		return max_all

	def read_term_doc_matrices(self):

		start_time = time.time()

		datapath = constants.MTX_DIR

		mtx_all = collections.OrderedDict()

		try: 

			for root, directories, files in os.walk(datapath):

				idx = 0
				for filename in files:
										
					if filename.startswith('mtx_') == True:

						logging.debug('read term-doc matrix(%s)... %d/%d', filename, idx, len(files))

						mtx = np.array([])
						with open(datapath+filename, 'r', encoding='UTF8') as f:
							lines = f.readlines()
							for line in lines:
								v = line.split('\t')
								word_idx = v[0]
								doc_idx = v[1]
								word_freq = v[2]

								item = np.array([v[0], v[1], v[2]], dtype=np.double)
								mtx = np.append(mtx, item, axis=0)

							mtx = np.array(mtx, dtype=np.double).reshape(len(lines), 3)
							mtx_all[filename] = mtx
					else:
						logging.debug('read term-doc matrix(%s)... %d/%d --> Passed. Not a valid term-doc matrix', filename, idx, len(files))
					idx += 1

		except FileNotFoundError:
			logging.debug('FileNotFoundError!');
			pass

		#logging.debug(mtx_all)

		elapsed_time = time.time() - start_time
		logging.info('read_term_doc_matrices Execution time : %.3fms', elapsed_time)

		return mtx_all

	# This function does not working properly.
	# def read_max_doc_frequency(self):

	# 	freq = collections.OrderedDict()

	# 	for key, value in self.map_tdm.items():
	# 		logging.info('key: %s, value: %s', key, value)
	# 		v = key.split('_')

	# 		level = v[3]
	# 		freq = self.get_doc_frequency_in_tile(key)

	# 		day = str(v[2][1:])
	
	# 		if day not in freq:
	# 			freq[day] = collections.OrderedDict()

	# 		if level not in freq[day]:
	# 			freq[day][level] = 0

	# 		if freq > freq[day][level]:
	# 			freq[day][level] = freq

	# 	print(freq)

	# 	return freq


	def get_documents_in_tile(self, zoom_level, tile_id):
		# todo
		return "document_list"

	def get_vocabulary(self):

		start_time = time.time()

		voca = []
		for each in self.db['vocabulary'].find():
			word = {}
			word['stem'] = each['stem']
			word['count'] = each['count']
			voca.append(word)

		elapsed_time = time.time() - start_time
		logging.info('get voca Execution time : %.3fms', elapsed_time)

		return voca

	def get_vocabulary_hashmap(self):

		start_time = time.time()

		voca_hash = [] 
		for each in self.db['vocabulary_hashmap'].find():
			voca_hash_elemet = {}
			voca_hash_elemet['word'] = each['word']
			voca_hash_elemet['stem'] = each['stem']
			voca_hash_elemet['count'] = each['count']
			voca_hash.append(voca_hash_elemet)


		elapsed_time = time.time() - start_time
		logging.info('get voca_hash Execution time : %.3fms', elapsed_time)
		return voca_hash

	def get_raw_data(self, tile_id):

		start_time = time.time()

		logging.debug('tile_id: %s', tile_id)

		raw_data = []

		for tile_name in self.db.collection_names():

			if tile_name.endswith('_raw') == False:
				continue

			if tile_name.find(str(tile_id)) < 0:
				continue

			logging.info(tile_name)

			current_raw_db = self.db[tile_name]

			for each in current_raw_db.find():
				raw_text = {}
				raw_text['text'] = each['text']
				raw_text['created_at'] = each['created_at']
				raw_data.append(raw_text)

			break

		elapsed_time = time.time() - start_time
		logging.info('get_raw_data Execution time : %.3fms', elapsed_time)

		return raw_data

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

		try:
			stemmed_list = list(self.stem_bag_words[stemmed_word].items())
			word = stemmed_list[0][0]
		except KeyError:
			word = ''

		return word
	
	def get_key(self,item):
		return float(item['score'])

	def get_jacard_score(self, datapath, level, x, y, year, yday, exclusiveness):
		
		topic_file_name = 'topics_' + str(year) + '_' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)
		mypath = constants.TOPIC_DIR + 'alpha_0.0/'
		neighbor_names = []
		topic_self = [] 
		topic_neighbor = []
		topic_yesterday = []
		jacard_score = 0.0
		jacard_score_yesterday = 0.0
		topic_count = 10
		


		for i in range(1,4):
			temp_name = 'topics_' + str(year) + '_' + str(yday - i) + '_' +str(level) + '_' + str(x) + '_' + str(y)
			neighbor_names.append(temp_name)
	  

		for each in neighbor_names:
			logging.debug('path: %s', each)

		for idx, each in enumerate(neighbor_names):
			each_path = mypath + each 

			if os.path.exists(each_path) == False:
				logging.debug('no file %s', each_path)
				continue

			try:
				with open(each_path, 'r', encoding = 'ISO-8859-1') as each_file: 

					lines = each_file.readlines()

					if len(lines) > 0 :	
									
						is_first = True
						topic_cnt = 0
						for line in lines:

							v = line.split('\t')

							if is_first == True:
								is_first = False
								continue

							topic_cnt += 1 
							if topic_cnt > topic_count:
								break

							for i in range(0, len(v) - 1):
								if idx == 0 :
								    topic_yesterday.append(v[i].strip()) 
								topic_neighbor.append(v[i].strip())
			
			except FileNotFoundError as fe:
				logging.debug(fe)
				pass 

		#get topic_self 
		if os.path.exists(datapath + topic_file_name) == True:		
			try: 
				with open(datapath + topic_file_name, 'r', encoding = 'ISO-8859-1') as file:
					lines = file.readlines()
					if len(lines) > 0:

						topic_cnt = 0
						is_first = True
						for line in lines: 
							v = line.split('\t')

							if is_first == True:
								is_first =False
								continue

							topic_cnt += 1 
							if topic_cnt > topic_count:
								break

							for i in range(0,len(v) - 1):
								topic_self.append(v[i].strip())

			except KeyError as fe:
				logging.error(fe)
				pass

		query_self = []
		query_neighbor = []
		query_yesterday = []

		for element in topic_self:
			try:
				query_idx = self.map_word_to_idx[element]
				query_self.append(query_idx)

			except KeyError as ke:
				continue

		for element in topic_neighbor:
			try:
				query_idx = self.map_word_to_idx[element]
				query_neighbor.append(query_idx)
			except KeyError as ke:
				continue

		for element in topic_yesterday:
			try: 
				query_idx = self.map_word_to_idx[element]
				query_yesterday.append(query_idx)
			except KeyError as ke:
				continue

		set_neighbor = set(query_neighbor)
		set_self = set(query_self)
		set_yesterday = set(query_yesterday)

		diff_set_with_neighbor = list(set_self.difference(set_neighbor))
		diff_set_with_yesterday = list(set_self.difference(set_yesterday))

		tot_freq_neighbor = 0
		tot_freq_yesterday = 0

		for i in range(len(diff_set_with_neighbor)):
			temp = self.map_idx_to_word[diff_set_with_neighbor[i]]
			temp_word_freq, _  = self.get_word_frequency(temp, level, x, y, year, yday)
			tot_freq_neighbor += temp_word_freq

		for i in range(len(diff_set_with_yesterday)):
			temp = self.map_idx_to_word[diff_set_with_yesterday[i]]
			temp_word_freq, _ = self.get_word_frequency(temp, level, x, y, year, yday)
			tot_freq_yesterday += temp_word_freq


		# if len(set_self) == 0 :
		# 	jacard_score = 0.0
		# 	jacard_score_yesterday = 0.0

		# else : 
		# 	#jacard_score = len(set_neighbor.intersection(set_self)) / len(set_neighbor.union(set_self))
		# 	#jacard_score_yesterday = len(set_yesterday.intersection(set_self)) / len(set_yesterday.union(set_self))
		# 	jacard_score = len(set_self.difference(set_neighbor)) / len((set_self))
		# 	jacard_score_yesterday = len(set_self.difference(set_yesterday)) / len((set_self))
	
		return tot_freq_neighbor, tot_freq_yesterday

	def get_tileglyph(self, level, x, y, year, yday, exclusiveness):
		logging.debug('get_tileglyph(%d, %d, %d, %d, %d, %d)', level, x, y, year, yday, exclusiveness);

		# datapath = constants.SPATIAL_TOPIC_PATH
		if exclusiveness == 1:
			datapath = constants.TOPIC_DIR + 'alpha_0.0/'
		elif exclusiveness == 2:
			datapath = constants.TOPIC_DIR + 'alpha_0.6/'
		elif exclusiveness == 3:
			datapath = constants.TOPIC_DIR + 'alpha_0.7/'
		elif exclusiveness == 4:
			datapath = constants.TOPIC_DIR + 'alpha_0.8/'
		elif exclusiveness == 5:
			datapath = constants.TOPIC_DIR + 'alpha_0.9/'
		else:
			datapath = constants.TOPIC_DIR + 'alpha_0.7/'

		topic_file_name = 'topics_' + str(year) + '_' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)
		tileid = str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)		

		tile_boarder, tile_glyph_arc = self.get_jacard_score(datapath, level, x, y, year, yday, exclusiveness)


		glyph = {}
		try: 
			with open(datapath+topic_file_name, 'r', encoding='ISO-8859-1') as f:
				
				lines = f.readlines()

				if len(lines) > 0:
					for line in lines:
						v = line.split('\t')
						#glyph['spatial_score'] = float(v[1]) / 100.0
						#glyph['temporal_score'] = float(v[2]) / 100.0
						_, frequency = self.get_frequency_in_tile(tileid)
						glyph['frequency'] = frequency
						break

					glyph['spatial_score'] = tile_boarder
					glyph['temporal_score'] = tile_glyph_arc

		except FileNotFoundError as fe:
			print(fe)
			glyph['spatial_score'] = 0.0
			glyph['temporal_score'] = 0.0
			glyph['frequency'] = 0.0
			pass

		return glyph

	def get_day_related_docs(self, level, x, y, year, yday, word):

		s_word = porter_stemmer.stem(word)
		word_idx = self.map_word_to_idx[s_word]

		rel_docs = [] 
		time_arr = [] 

		if os.path.exists(constants.MTX_DIR + 'mtx_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)) == True:
			try:
				with open(constants.MTX_DIR + 'mtx_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y), 'r', encoding = 'UTF8') as f:
				    lines = f.readlines()
				    for line in lines: 
				    	v= line.split('\t')

				    	temp_word_idx = int(v[0])
				    	doc_idx = int(v[1])

				    	if int(word_idx) == temp_word_idx:

					    	# doc_time = getTwitterDate(self.map_idx_to_doc[doc_idx][0])
					    	# date = doc_time.timetuple().tm_yday
					    	# unixtime = time.mktime(doc_time.timetuple())
					    	# username = str(self.map_idx_to_doc[doc_idx][3])
					    	# text = str(self.map_idx_to_doc[doc_idx][4])

					    	local_hours, local_minutes = getTwitterHour(self.map_idx_to_doc[doc_idx][0])
					    	rel_docs.append(local_hours)


					    	#d = {}
					    	#d['username'] = username
					    	#d['created_at'] = unixtime
					    	#d['text'] = text
					        #rel_docs.append(local_hours*60 + local_minutes)

				for i in range(0,24): 
					isexist = rel_docs.count(i)
					time_arr.append(isexist)


			except FileNotFoundError as fe:
				logging.debug('FileNotFoundError: %s', fe);
				time_arr = [] 
				pass 

		return time_arr

	def get_word_info(self, word, level, x, y, year, yday):
		logging.debug('get_word_info(%s, %d, %d, %d, %d, %d)', word, level, x, y, year, yday)

		# calculate the frequency
		word_freq = 0.0
		tfidf_var = 0.0
		tf_word_percent = [] 
		time_arr = []
		today_freq = 0.0

		try:
			# get term-doc matrix
			tileid = str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)		
			word_freq, _ = self.get_word_frequency(word, level, x, y, year, yday)
			for i in range(0,7):
				tot_freq = 0
				today_freq, _ = self.get_word_frequency(word,level, x, y, year, str(yday - i))
				for i in range(0,7):
					temp_word_freq, _ = self.get_word_frequency(word, level, x, y, year, str(yday - i))
					tot_freq += temp_word_freq
					#logging.debug(tot_freq)

				#logging.debug(tot_freq)

				if(tot_freq >0):
					tf_word_percent.append(today_freq / tot_freq)

				# max_freq = self.map_max_word_freq[yday][level]
				# word_score = word_freq / max_freq


		except KeyError as e:
			logging.debug('KeyError: %s', e)
			word_freq = 0
			tf_word_percent.append(0)

		# get tfidf variation
		#tfidf_var = self.get_tfidf_variation(word, tileid)
		#tfidf_value = self.get_tfidf_values(word, tileid)
		time_arr = self.get_day_related_docs(level, x, y, year, yday, word)

		# get temporal novelty score
		return word_freq, time_arr, tf_word_percent

	def get_topics_new(self, level, x, y, year, yday, topic_count, word_count, exclusiveness):
		
		logging.debug('get_topics_new(%d, %d, %d, %d, %d, %d, %d, %d)', level, x, y, year, yday, topic_count, word_count, exclusiveness);

		# date_format = "%Y-%m-%d"
		# date = datetime.strptime(date, date_format)

		# exclusiveness = int(exclusiveness)

		
		if exclusiveness == 1:
			datapath = constants.TOPIC_DIR + 'alpha_0.0/'
		elif exclusiveness == 2:
			datapath = constants.TOPIC_DIR + 'alpha_0.6/'
		elif exclusiveness == 3:
			datapath = constants.TOPIC_DIR + 'alpha_0.7/'
		elif exclusiveness == 4:
			datapath = constants.TOPIC_DIR + 'alpha_0.8/'
		elif exclusiveness == 5:
			datapath = constants.TOPIC_DIR + 'alpha_0.9/'
		else:
			datapath = constants.TOPIC_DIR + 'alpha_0.7/'
		
		tileid = str(year) + '_' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)
		topic_file_name = 'topics_' + tileid
		# topic_file_name = 'topics_' + tileid + '_' + str(exclusiveness)

		tileid2 = str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)
		total_word_freq, _ = self.get_frequency_in_tile(tileid2)
		
		topic_word_freq = 0
		topics = []
		num_topics = 0
		
		try: 
			with open(datapath+topic_file_name, 'r', encoding='ISO-8859-1') as f:
				
				lines = f.readlines()

				if len(lines) > 0:

					topic_cnt = 0
					is_first = True
					for line in lines:
						#logging.debug(line)

						v = line.split('\t')

						if is_first == True:
							num_topics = int(v[0])
							is_first = False
							continue

						topic_cnt += 1

						if topic_cnt > topic_count:
							break

						topic = []
						for i in range(0, num_topics):
							topic.append(v[i].strip())

						topics.append(topic)

		except FileNotFoundError as fe:
			print(fe)
			pass

		print(topics)

		if len(topics) == 0:
			return topics

		topics = [[topics[j][i] for j in range(len(topics))] for i in range(len(topics[0]))]
		
		res = []
		for i in range(num_topics):

			words = topics[i]
			new_words = []
			topic_word_freq = 0
			for word in words:
				word_freq, _ = self.get_word_frequency(word, level, x, y, year, yday)
				freq_word = self.get_most_freq_word(word)
				topic_word_freq += word_freq

				w = {}
				w['word'] = freq_word
				w['count'] = word_freq
				w['score'] = 0

				new_words.append(w)



			topic = {}
			topic['words'] = new_words
			# topic['count'] = topic_word_freq
			logging.info('topic_word_freq: %d, total_word_freq: %d', topic_word_freq, total_word_freq)
			topic['score'] = (topic_word_freq/total_word_freq) if total_word_freq != 0 else 0.0

			res.append(topic)

		res = sorted(res, key=self.get_key, reverse=True)

		# return topics[:num_topics]
		return res


	def get_topics(self, level, x, y, year, yday, topic_count, word_count, exclusiveness):
		
		logging.debug('get_topics(%d, %d, %d, %d, %d, %d, %d, %d)', level, x, y, year, yday, topic_count, word_count, exclusiveness);

		# date_format = "%Y-%m-%d"
		# date = datetime.strptime(date, date_format)

		# exclusiveness = int(exclusiveness)

		datapath = constants.SPATIAL_TOPIC_PATH
	
		tileid = str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)		
		topic_file_name = 'topics_' + tileid + '_' + str(exclusiveness)

		total_word_freq, _ = self.get_frequency_in_tile(tileid)
		
		topic_word_freq = 0
		
		topics = []
		
		try: 
			with open(datapath+topic_file_name, 'r', encoding='UTF8') as f:
				
				lines = f.readlines()

				if len(lines) > 0:

					num_topics = 0

					# TODO: pass the first line
					# is_first = True
					for line in lines:
						#logging.debug(line)

						v = line.split('\t')

						# if is_first == True:
						# 	is_first = False
						# 	continue

						if len(v) == 1:
							
							if num_topics > 0:

								# if num_topics < 2:
								topic['words'] = words
								topic['score'] = (topic_word_freq/total_word_freq) if total_word_freq != 0 else 0
								topics.append(topic)

							num_topics += 1

							topic = {}
							words = []
							append_cnt = 0
							topic_word_freq = 0

							topic['score'] = float(v[0])
						else:

							if append_cnt < word_count:

								freq_word = self.get_most_freq_word(str(v[0]))
								#freq_word = str(v[0])

								word = {}
								word['word'] = freq_word
								word['count'] = int(v[1])
								word['score'] = float(v[2])
								words.append(word)

								topic_word_freq += int(v[1])
								append_cnt += 1
					
					topic['words'] = words
					topic['score'] = (topic_word_freq / total_word_freq) if total_word_freq != 0 else 0
					
					topics.append(topic)				
						
		except FileNotFoundError:
			#logging.debug('%s is not exist.', (datapath+topic_file_name))
			pass
			# set fake data
			#topics = self.get_fake_topics()

		topics = sorted(topics, key=self.get_key, reverse=True)

		return topics[:topic_count]

	def get_all_topics(self, level, x, y, year, yday_from, yday_to):

		return

	# def read_spatial_mtx(self, directory, mtx):

	# 	v = mtx.split('_')

	# 	# remove d from v[2]
	# 	year = int(v[1])
	# 	yday = int(v[2][1:])
	# 	level = int(v[3])
	# 	x = int(v[4])
	# 	y = int(v[5])

	# 	res = self.read_spatial_mtx(directory, year, yday, level, x, y)

	# 	return res

	def read_spatial_mtx(self, directory, year, yday, level, x, y):

		neighbor_names = []

		temp_name = 'mtx_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_'

		neighbor_names.append(temp_name+str(x+0)+'_'+str(y+0)) # it's me
		
		neighbor_names.append(temp_name+str(x+1)+'_'+str(y+1))
		neighbor_names.append(temp_name+str(x+1)+'_'+str(y+0))
		neighbor_names.append(temp_name+str(x+1)+'_'+str(y-1))
		neighbor_names.append(temp_name+str(x+0)+'_'+str(y+1))

		neighbor_names.append(temp_name+str(x+0)+'_'+str(y-1))
		neighbor_names.append(temp_name+str(x-1)+'_'+str(y+1))
		neighbor_names.append(temp_name+str(x-1)+'_'+str(y+0))
		neighbor_names.append(temp_name+str(x-1)+'_'+str(y-1))

		for each in neighbor_names:
			logging.debug('path: %s', each)

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

					# item = [int(v[0]), int(v[1]), int(v[2]), int(isnt_center)]
					# nmtx.append(item)
					item = np.array([float(v[0]), float(v[1]), float(v[2]), float(isnt_center)], dtype=np.double)
					nmtx = np.append(nmtx, item, axis=0)

					# neighbor_mtx.append([int(v[0]), int(v[1]), int(v[2]), idx])
					line_cnt += 1
					if idx == 0: 
						center_count += 1

		nmtx = np.array(nmtx, dtype=np.double).reshape(line_cnt, 4)

		return nmtx