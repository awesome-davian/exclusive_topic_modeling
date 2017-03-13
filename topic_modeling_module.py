import matlab.engine
import logging
import math
import constants
import numpy as np
import pymongo
import sys
from nltk import PorterStemmer
import time
from datetime import datetime


porter_stemmer=PorterStemmer();

sys.path.insert(0, '../')
conn = pymongo.MongoClient("localhost", constants.DEFAULT_MONGODB_PORT);

# dbname = constants.DB_NAME;
# db = conn[dbname];

class TopicModelingModule():

	def __init__(self, DB):
		
		import nmf_core

		logging.debug('init');

		self.nmf = nmf_core
		self.db = DB

		# logging.info("loading Matlab module...");
		# self.eng = matlab.engine.start_matlab();
		# self.eng.cd('./matlab/discnmf_code/');
		# logging.info("Done: loading Matlab module");

	def get_tile_id(self, level, x, y):

		pow2 = 1 << level;
		tile_id = x * pow2 + y;

		return round(tile_id);

	def lon_to_x(self, level, lon):

		pow2 = 1 << level;
		x = (lon + 180.0)/360.0 * pow2;
		return x;

	def lat_to_y(self, level, lat):

		latR = math.radians(lat);
		pow2 = 1 << level;

		y = (1 - math.log(math.tan(latR) + 1 / math.cos(latR)) / math.pi) / 2 * pow2;
		y = pow2 - y;
		return y;

	def x_to_lon(self, level, x):

		pow2 = 1 << level;
		lon = (x / pow2 * 360.0) - 180.0;
		return lon;

	def y_to_lat(self, level, y):

		pow2 = 1 << level;
		n = -math.pi + (2.0*math.pi*y)/pow2;
		lat = math.degrees(math.atan(math.sinh(n)))

		return lat;

	def get_neighbor_ids(self, level, x, y):

		neighbor = [];
		neighbor.append(self.get_tile_id(level, x+1, y+1));
		neighbor.append(self.get_tile_id(level, x+1, y+0));
		neighbor.append(self.get_tile_id(level, x+1, y-1));
		neighbor.append(self.get_tile_id(level, x+0, y+1));
		#neighbor.append(self.get_tile_id(level, x+0, y+0)); --> it's me.
		neighbor.append(self.get_tile_id(level, x+0, y-1));
		neighbor.append(self.get_tile_id(level, x-1, y+1));
		neighbor.append(self.get_tile_id(level, x-1, y+0));
		neighbor.append(self.get_tile_id(level, x-1, y-1));

		return neighbor;


	def get_doc_idx_include_word(self, term_doc_mtx, word_list, voca_hash, voca):

		doc_lists=[]


		for word in word_list:

			stem_word ="";
			word_id=0;

	        #find stemmed word form voca-hashmap
			for each in voca_hash:
				if word==each['word']:
					stem_word=each['stem']
					break;
			#logging.info(stem_word)

			#get stemmed word id from voca 			
			for idx, each in enumerate(voca):
			 	if stem_word==each['stem']:
			 		word_id=idx+1 
			 		break;
			#logging.info(word_id);

	        #get doc list for tem_doc.mtx
			doc_list=[]
			for each in term_doc_mtx:
				if each[0]==word_id:
					doc_list.append(each[1])

			#logging.info(doc_list)	
			doc_lists.append(doc_list)

		logging.info(doc_lists)	

		return doc_lists;
  

	def make_sub_term_doc_matrix(self, term_doc_mtx, include_word_list, exclude_word_list, voca_hash, voca):

		start_time_make_sub=time.time()


		exclude_doc_list=self.get_doc_idx_include_word(term_doc_mtx, exclude_word_list, voca_hash, voca)
		include_doc_list=self.get_doc_idx_include_word(term_doc_mtx, include_word_list, voca_hash, voca)

		new_tile_mtx=[]
		word_idx=0;

		if(len(include_word_list)>0):
			for each in term_doc_mtx:
				for in_word in include_doc_list:
					for idx in in_word:
						if(each[1]==idx):
							item = np.array([each[0], each[1], each[2]], dtype=np.double);
							#logging.info(item)
							new_tile_mtx = np.append(new_tile_mtx, item, axis=0)

			new_tile_mtx = np.array(new_tile_mtx, dtype=np.double).reshape(int(np.size(new_tile_mtx)/3), 3)				
			
			#logging.info(new_tile_mtx)

			if(len(exclude_word_list)>0):
				for ex_word in exclude_word_list:
					#logging.info(ex_word)
					for idx, element in enumerate(voca):
						if(element['stem']==porter_stemmer.stem(ex_word)):
							word_idx=idx+1
							break;	
					#logging.info(word_idx)								
					for each in new_tile_mtx:
						if(each[0]==word_idx):
						 	new_tile_mtx=np.delete(new_tile_mtx, word_idx-1, axis=0)

		else:
			for ex_word in exclude_doc_list:
				for element in ex_word:
					for each in term_doc_mtx:
						if(each[1] == element):
							logging.info(element)
							continue;
						item=np.array([each[0], each[1], each[2]], dtype=np.double);
						new_tile_mtx = np.append(new_tile_mtx, item, axis=0)

	

		new_tile_mtx = np.array(new_tile_mtx, dtype=np.double).reshape(int(np.size(new_tile_mtx)/3), 3)				 	

		elapsed_time_make_sub= time.time() - start_time_make_sub
		logging.info('get_topics -make sub term_doc_mtx Execution time: %.3fms', elapsed_time_make_sub)
	
		logging.debug(new_tile_mtx)

		return new_tile_mtx;
    


	def run_topic_modeling(self, level, x, y, exclusiveness, num_clusters, num_keywords, voca):
		
		start_time = time.time()

		logging.debug('run_topic_modeling(%d, %d, %d, %.2f)', level, x, y, exclusiveness);

		tile_id = self.get_tile_id(level, x, y);
		neighbor_ids = self.get_neighbor_ids(level, x, y);

		logging.debug(neighbor_ids)

		tile_mtx = self.db.get_term_doc_matrix(tile_id);
		if tile_mtx == []:
			return [];

		neighbor_mtx = self.db.get_term_doc_matrices(neighbor_ids);

		# print(type(neighbor_mtx));
		# print(type(neighbor_mtx[0]));
		# print(type(neighbor_mtx[3]));
		# print(type(tile_mtx.tolist()));
		
		# logging.debug(neighbor_mtx);
		# logging.debug(tile_mtx);

		start_time_makeab = time.time()

		A = matlab.double(tile_mtx.tolist());

		B = [];
		idxa = 0;
		for each in neighbor_mtx:
			if each == []: 
				#logging.debug("found it, idx: " + str(idxa));
				B.append(each);
			else:
				B.append(each.tolist());

			idxa += 1;


		elapsed_time_makeab= time.time() - start_time_makeab
		logging.info('run_topic_modeling -make ab Execution time: %.3fms', elapsed_time_makeab)


		start_time_function_run = time.time()

		# for each in B:
		# 	print(type(each));

		# print(type(neighbor_mtx));
		# print(type(tile_mtx.tolist()));


        #[topics_list] = self.eng.function_run_extm(A, B, exclusiveness, voca, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, nargout=3);


		[topics_list, w_scores, t_scores] = self.eng.function_run_extm(A, B, exclusiveness, voca, num_clusters, num_keywords, nargout=3);
		topics = np.asarray(topics_list);
		topics = np.reshape(topics, (num_clusters, num_keywords));

		word_scores = np.asarray(w_scores);
		word_scores = np.reshape(word_scores, (num_clusters, num_keywords));

		topic_scores = np.asarray(t_scores);

		elapsed_time_function_run = time.time() - start_time_function_run
		logging.info('run_topic_modeling -function_run_extm Execution time: %.3fms', elapsed_time_function_run)


		start_time_replace = time.time()
		# find original word and replace
		
		for topic in topics:
			for word in topic:
				
				s_count=0
				temp_word = "";
				temp_count=0;

				for each in db['vocabulary_hashmap'].find():
					if((word==each['stem']) and (s_count==0)):
						temp_word=each['word']
						temp_count=each['count']
						#logging.info('the word is :  %s  %s...', temp_word, each['stem'])
					#if(word==each['stem']):
					if((word==each['stem']) and (s_count!=0)):
						if(each['count']>temp_count):
							temp_count=each['count']
							temp_word=each['word']
					s_count+=1	
				#logging.debug('the result is %s   %s', word, temp_word)		
				word=temp_word
		elapsed_time_replace= time.time() - start_time_replace
		logging.info('run_topic_modeling -replace Execution time: %.3fms', elapsed_time_replace)
		# update at 8th February, 2017 - the formation starts here.

	#	tile = self.db[tile_name]
		rettopics = []
		for i in range(0,num_clusters):

			tpc = {}
			# topic['score'] = tile.find_one({'topic_id':constants.TOPIC_ID_MARGIN_FOR_SCORE+i})['topic_score'];
			tpc['score'] = topic_scores[i,0]
			# 1. starting from topic_scores
			
			# 2. 
			words = [];
			for i1 in range(0,num_keywords):
				# topic.append(each['word']);
						word = {};
						word['word'] = topics[i,i1]
						word['scoret'] = word_scores[i,i1]
						words.append(word)

					# topic['words'] = words;
			tpc['words'] = words;

			rettopics.append(tpc);


		# end. 

		elapsed_time= time.time() - start_time
		logging.info('run_topic_modeling  Execution time: %.3fms', elapsed_time)
	

		return rettopics;

	def get_topics(self, level, x, y, topic_count, word_count, include_words, exclude_words, exclusiveness, date):

		start_time=time.time()
		
		logging.debug('get_topics(%s, %s, %s)', level, x, y)
		tile_id = self.get_tile_id(level, x, y);

		# voca_hash= self.db.get_vocabulary_hashmap();
		# voca= self.db.get_vocabulary();
		
		# for testing
		#exclusiveness = 50;

		exclusiveness /= 100;
		logging.debug('exclusiveness: %f', exclusiveness);

		result = {};
		tile = {};
		tile['x'] = x;
		tile['y'] = y;
		tile['level'] = level;

		result['tile'] = tile;

		topics = []
		# check if it needs a precomputed tile data.
		# if exclusiveness == 0 :  
		# 	# get precomputed tile data       			
		# 	tile_mtx = self.db.get_term_doc_matrix(tile_id);
		# 	self.make_sub_term_doc_matrix(tile_mtx,include_words,exclude_words, voca_hash, voca)
			
		# 	topics = self.db.get_precomputed_topics(level, x, y, topic_count, word_count, voca_hash, voca);
						
		# else :

		# 	topics = self.run_topic_modeling(level, x, y, exclusiveness, topic_count, word_count, voca);

		topics = self.db.get_topics(level, x, y, date, topic_count, word_count);

		result['topic'] = topics;

		end_time=time.time() - start_time
		logging.info('end of get_topics Execution time: %.3fms' , end_time)

		print(result);

		return result;

	def get_related_docs(self, level, x, y, word, date):

		start_time = time.time()

		# get docs including the word 
		date = datetime.fromtimestamp(int(int(date)/1000))
		year = date.timetuple().tm_year
		day_of_year = date.timetuple().tm_yday

		logging.debug('get_releated_docs(%s, %s, %s, %s, %d)', level, x, y, word, day_of_year)

		s_word = porter_stemmer.stem(word)
		word_idx = self.db.get_global_voca_map_word_to_idx()[s_word]

		logging.info('word: %s, s_word: %s, word_idx: %d', word, s_word, word_idx)

		map_related_docs = self.db.get_related_docs_map()[word_idx]

		logging.info('stemmed word: %s, idx: %d', s_word, word_idx)

		d = str(constants.DATA_RANGE).split('-')

		d[0] = '20'+d[0][0:2] + '-' + d[0][2:4] + '-' + d[0][4:6]
		d[1] = '20'+d[1][0:2] + '-' + d[1][2:4] + '-' + d[1][4:6]

		logging.debug(d[0])
		logging.debug(d[1])

		date_format = "%Y-%m-%d"
		start_date = datetime.strptime(d[0], date_format).timetuple().tm_yday
		end_date = datetime.strptime(d[1], date_format).timetuple().tm_yday if len(d) > 1 else start_date

		# start_date = int(d[0])
		# end_date = int(d[1]) if len(d) > 1 else int(d[0])

		max_compare = max([end_date - day_of_year, day_of_year - start_date])

		logging.debug('start date: %d', start_date)
		logging.debug('end date: %d', end_date)
		logging.debug('max_compare: %d', max_compare)

		total_docs = []

		# size = 0
		# f_size = 0
		# docs = self.db.get_related_docs_map()
		# for each in docs.items():
		
		# 	try: 
		# 		size += len(each[1][day_of_year])
		# 		for txt in each[1][day_of_year]:
		# 			f_size += txt.count('love')
		# 			if txt.count('love') > 0:
		# 				logging.debug('Found! [%d]: %s', each[0], str(txt).encode('utf-8'))

		# 	except KeyError:
		# 		pass
			
		# logging.debug('size of %d : %d, f_size: %d', day_of_year, size, f_size)

		logging.debug('case: %s', day_of_year)

		try: 
			doc_list = map_related_docs[day_of_year]
			for doc in doc_list:
				d = {}
				d['username'] = str(doc[0])
				d['created_at'] = int(doc[1])
				d['text'] = str(doc[2])
				total_docs.append(d)
		except KeyError:
			pass

		logging.debug('len: %s', len(total_docs))

		if len(total_docs) < constants.MAX_RELATED_DOCS:

			for each in range(1, max_compare+1):	
				
				date_cursor = day_of_year - each
				if date_cursor < start_date:
					continue
				else:
					logging.debug('case: %s', date_cursor)

					try: 
						doc_list = map_related_docs[date_cursor]
						for doc in doc_list:
							d = {}
							d['username'] = str(doc[0])
							d['created_at'] = int(doc[1])
							d['text'] = str(doc[2])
							total_docs.append(d)
					except KeyError:
						pass

				logging.debug('len: %s', len(total_docs))

				if len(total_docs) > constants.MAX_RELATED_DOCS:
					break

				date_cursor = day_of_year + each
				if date_cursor > end_date:
					continue
				else:
					logging.debug('case: %s', date_cursor)

					try: 
						doc_list = map_related_docs[date_cursor]
						for doc in doc_list:
							d = {}
							d['username'] = str(doc[0])
							d['created_at'] = int(doc[1])
							d['text'] = str(doc[2])
							total_docs.append(d)
					except KeyError:
						pass

				logging.debug('len: %s', len(total_docs))

				if len(total_docs) > constants.MAX_RELATED_DOCS:
					break

		result = {}
		tile = {}
		tile['x'] = x
		tile['y'] = y
		tile['level'] = level

		result['tile'] = tile

		result['documents'] = total_docs[:constants.MAX_RELATED_DOCS]

		elapsed_time=time.time()-start_time
		logging.info('get_releated_docs elapsed: %.3fms' , elapsed_time)

		return result

	def getTermDocMtx(self, level, x, y, date):

		date = datetime.fromtimestamp(int(int(date)/1000))
		year = date.timetuple().tm_year
		day_of_year = date.timetuple().tm_yday

		tile_name = 'mtx_' + str(year) + '_d' + str(day_of_year) + '_' + str(level) + '_' + str(x) + '_' + str(y)

		mtx_file = open(constants.MTX_DIR + tile_name, 'r', encoding='UTF8')

		lines = mtx_file.readlines()

		tile_mtxs = [];
		for line in lines:
			v = line.split('\t')
			item = [float(v[0]), float(v[1]), float(v[2])]
			temp_mtx = np.append(temp_mtx, item, axis=0)

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

	def get_tile_detail_info(level, x, y, time_from, time_to):

		logging.debug('get_tile_detail_info(%s, %s, %s, %s, %s)', level, x, y, time_from, time_to)

		tile_id = self.get_tile_id(level, x, y)

		result = {};
		tile = {};
		tile['x'] = x;
		tile['y'] = y; 
		tile['level'] = level;

		result['tile'] = tile;

		#todo: get all_topics / get time_graph
		time_graph = self.get_time_graph();
		topics = self.get_all_topics();

		result['time_graph'] = time_graph
		result['all_topics'] = topics

		return result;

	def get_himap(time_from, time_to):

		logging.debug('get_himap(%s, %s)', time_from, time_to)

		return result


	def get_word_info(self, level, x, y, word):
		# TBD
		return "word_info";





