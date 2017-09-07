import os
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
		self.map_tdm = self.read_term_doc_matrices()
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

	def get_docs(self, word, x, y, level, year, yday):

		docs = []

		try:
			# word to idx
			word_idx = self.map_word_to_idx[word]

			# get term-doc matrix
			tileid = 'mtx_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)		
		
			tdm = self.map_tdm[tileid]
			
			tdm = tdm[tdm[:,0]==word_idx]

			# get docs including the word_idx
			for item in tdm:
				doc_idx = item[1]
				doc = self.map_idx_to_doc[doc_idx]
				docs.append(doc)
		except KeyError as e:
			logging.debug('KeyError: %s', e)


		return docs

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

	def get_tileglyph(self, level, x, y, year, yday, exclusiveness):
		logging.debug('get_tileglyph(%d, %d, %d, %d, %d, %d)', level, x, y, year, yday, exclusiveness);

		# TODO: to be modified.
		datapath = constants.SPATIAL_TOPIC_PATH
		topic_file_name = 'topics_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y) + '_' + str(exclusiveness)

		glyph = {}
		try: 
			with open(datapath+topic_file_name, 'r', encoding='UTF8') as f:
				
				lines = f.readlines()

				if len(lines) > 0:	
					for line in lines:
						v = line.split('\t')
						glyph['spatial_score'] = 0.5391	# float(v[1])
						glyph['temporal_score'] = 0.4327 # float(v[2])
						break

		except FileNotFoundError:
			glyph['spatial_score'] = 0.0
			glyph['temporal_score'] = 0.0
			pass

		return glyph

	def get_word_info(self, word, level, x, y, year, yday):
		logging.debug('get_word_info(%s, %d, %d, %d, %d, %d)', word, level, x, y, year, yday)

		# TODO: to be modified

		# calculate the frequency
		freq = 0
		try:
			# word to idx
			word_idx = self.map_word_to_idx[word]

			# get term-doc matrix
			tileid = 'mtx_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)		
		
			# tdm = self.get_tdm(tileid)
			tdm = self.map_tdm[tileid]
			
			tdm = tdm[tdm[:,0]==word_idx]

			# get docs including the word_idx
			
			for item in tdm:
				freq += int(item[2])
				
		except KeyError as e:
			logging.debug('KeyError: %s', e)


		# get tfidf

		# get temporal novelty score

		return freq, 0, [0,1,2,3,4,5,6]


	def get_topics(self, level, x, y, year, yday, topic_count, word_count, exclusiveness):
		
		logging.debug('get_topics(%d, %d, %d, %d, %d, %d, %d, %d)', level, x, y, year, yday, topic_count, word_count, exclusiveness);

		# date_format = "%Y-%m-%d"
		# date = datetime.strptime(date, date_format)

		exclusiveness = int(exclusiveness)

		datapath = constants.SPATIAL_TOPIC_PATH
		topic_file_name = 'topics_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y) + '_' + str(exclusiveness)

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
								#freq_word = str(v[0])

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
			#logging.debug('%s is not exist.', (datapath+topic_file_name))
			pass
			# set fake data
			#topics = self.get_fake_topics()

		topics = sorted(topics, key=self.get_key, reverse=True)

		return topics[:topic_count]

	def get_all_topics(self, level, x, y, year, yday_from, yday_to):

		return

	def read_spatial_mtx(self, directory, mtx):

		v = mtx.split('_')

		# remove d from v[2]
		year = int(v[1])
		yday = int(v[2][1:])
		level = int(v[3])
		x = int(v[4])
		y = int(v[5])

		res = self.read_spatial_mtx(directory, year, yday, level, x, y)

		return res

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