import logging
import pymongo
import constants
import numpy as np
import time
from datetime import datetime 
import collections


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
		with open(constants.MTX_DIR + constants.DATA_RANGE + '/total_mtx', 'r', encoding='UTF8') as f:
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

	def get_xscore(self, level, x, y, year, ydate):

		xscore_dir = constants.XSCORE_DIR + constants.DATA_RANGE + '/'
		file_name = topic_file_name = 'xscore_' + str(year) + '_d' + str(ydate) + '_' + str(level) + '_' + str(x) + '_' + str(y)

		score = 0.0
		try:
			with open(xscore_dir + file_name, 'r', encoding='UTF8') as f:
				score = float(f.readline())
		except FileNotFoundError:
			score = -1.0

		return score

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


	def get_topics(self, level, x, y, date, topic_count, word_count, exclusiveness):
		
		logging.debug('get_topics(%d, %d, %d, %s, %d, %d, %d)', level, x, y, date, topic_count, word_count, exclusiveness);

		# date_format = "%Y-%m-%d"
		# date = datetime.strptime(date, date_format)

		logging.info(date)
		print(int(int(date)/1000))

		date = datetime.fromtimestamp(int(int(date)/1000))
		year = date.timetuple().tm_year
		day_of_year = date.timetuple().tm_yday

		datapath = './tile_generator/topics/'+constants.DATA_RANGE+'/'
		topic_file_name = 'topics_' + str(year) + '_d' + str(day_of_year) + '_' + str(level) + '_' + str(x) + '_' + str(y) + '_' + str(exclusiveness)

		topics = []
		
		try: 
			with open(datapath+topic_file_name, 'r') as f:
				
				topic = {}
				words = []

				lines = f.readlines()
				idx = 0
				for line in lines:
					line = line.strip()
					if idx == 0:
						topic['score'] = float(line)
						idx += 1
					else:
						
						v = line.split('\t')
						word = {}
						word['word'] = str(v[0])
						word['count'] = int(v[1])
						word['score'] = float(v[2])

						words.append(word)

						idx += 1
						if idx > 10:
							idx = 0
							
							topic['words'] = words
							topics.append(topic)

							topic = {}
							words = []
		except FileNotFoundError:
			logging.debug('%s is not exist.', topic_file_name)

		return topics

	def get_all_topics(self, level, x, y, year, yday_from, yday_to):



		return

	def get_precomputed_topics(self, level, x, y ,topic_count, word_count, voca_hash, voca):

		logging.debug('get_precomputed_topics(%d, %d, %d)', level, x, y);

		topics = [];

		start_time=time.time()

		for tile_name in self.db.collection_names():

			if tile_name.endswith('_topics') == False:
				continue;

			#logging.debug(tile_name)

			tile_info = tile_name.split('_');

			tile_x = tile_info[constants.POS_X];
			tile_y = tile_info[constants.POS_Y];
			tile_level = tile_info[constants.POS_LEVEL];


			# if tile_name.find(str(tile_id)) > 0:
			if int(tile_x) == x and int(tile_y) == y and int(tile_level) == level:
				logging.debug('found, %s', tile_name);

				tile = self.db[tile_name]
				for i in range(0,topic_count):

					topic = {};
					topic['score'] = tile.find_one({'topic_id':constants.TOPIC_ID_MARGIN_FOR_SCORE+i+1})['topic_score'];

					words = [];

					start_time_find_info=time.time()

					for idx, each in enumerate(tile.find({'topic_id': i+1}).sort('rank',pymongo.ASCENDING)):
						word={}
						word['word'] = each['word']
						word['score'] = each['score']
						
						#start_time_find_count=time.time()

					    #find stemmed word form voca-hashmap
						for each in voca_hash:
							if word['word']==each['word']:
								stem_word=each['stem']
								break;
						#logging.info(stem_word)

						#get stemmed word count  from voca 				
						for each in voca:
						 	if stem_word==each['stem']:	
						 		word['count']=each['count']
						 		break;


						# #find count from voca-hash						
						# for each in voca_hash:
						# 	if(word['word']==each['word']):
						# 		word['count']=each['count']
						# 		break;

						words.append(word)

						#elaspsed_time_find_couunt=time.time()-start_time_find_count
						#logging.info("Done get count. Execution time: %.3fms", elaspsed_time_find_couunt)


						if(idx>=word_count-1):
							break;

					elaspsed_time_find_info=time.time()-start_time_find_info
					logging.info("get_precomputed_topics -  find info. Execution time: %.3fms", elaspsed_time_find_info)		



					topic['words'] = words;

					topics.append(topic);

				break;

		elaspsed_time=time.time() - start_time
		logging.info("Done get Pre-computed topics. Execution time: %.3fms", elaspsed_time)	

		return topics;