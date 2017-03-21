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

	def get_docs_including_word(self, level, x, y, year, yday, word_list):

		doc_lists=collections.OrderedDict()

		map_idx_to_word, map_word_to_idx, bag_words, stem_bag_words = self.db.read_voca()

		termdoc_dir = constants.MTX_DIR + constants.DATA_RANGE + '/'
		file_name  = 'mtx_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)

		word_idxs = []
		for w in word_list:
			stemmed = porter_stemmer.stem(w)
			word_idxs.append(map_word_to_idx[stemmed])


		with open(termdoc_dir + file_name, 'r', encoding='UTF8') as f:
			lines=f.readlines()
			for line in lines:
				v = line.split('\t')
				word_idx = int(v[0])
				doc_idx = int(v[1])
				for w in word_idxs:
					if doc_idx == w:
						doc_lists[doc_idx] = 1
						# doc_lists.append(doc_idx)
						break;


			# # duplicate date can be appended so i changed the algorithm like above.
			# for word in word_list:
			# 	stem_word=porter_stemmer.stem(word)

			# 	for line in lines:
			# 		v = line.split('\t')
			# 		word_idx = int(v[0])
			# 		doc_idx = int(v[1])
			# 		if(map_word_to_idx[stem_word]==word_idx):
			# 			doc_lists.append(doc_idx)

		# logging.info(doc_lists)

		return doc_lists

	def make_sub_term_doc_matrix(self, level, x, y, year, yday, date, include_word_list, exclude_word_list):

		map_idx_to_word, map_word_to_idx, bag_words, stem_bag_words = self.db.read_voca()

		include_docs = self.get_docs_including_word(level, x, y, year, yday, include_word_list)
		exclude_docs = self.get_docs_including_word(level, x, y, year, yday, exclude_word_list)
		# term_doc_mtx = self.getTermDocMtx(level, x, y, date)
		mtx = self.db.read_spatial_mtx(constants.MTX_DIR+constants.DATA_RANGE + '/', year, yday, level, x, y)

		new_tile_mtx=[]
		word_idx=0;

		for each in mtx:
			flag = True
			if len(include_docs) > 0 && (each[1] in include_docs):
				flag = True
			if len(exclude_docs) > 0 && (each[1] in exclude_docs):
				flag = False

			if flag == True:
				new_tile_mtx.append([int(each[0]), int(each[1]), int(each[2]), int(each[3])])

		new_tile_mtx = np.array(new_tile_mtx, dtype=np.int32).reshape(int(np.size(new_tile_mtx)/4), 4)

		return new_tile_mtx;

		
	def run_topic_modeling(self, mtx, level, x, y, xcls_value, num_clusters, num_keywords, voca):
		
		start_time = time.time()

		logging.debug('run_topic_modeling(%d, %d, %d, %d)', level, x, y, xcls_value);

		start_time_makeab = time.time()

		A = matlab.double(tile_mtx.tolist());

		elapsed_time_makeab= time.time() - start_time_makeab
		logging.info('run_topic_modeling -make ab Execution time: %.3fms', elapsed_time_makeab)


		start_time_function_run = time.time()

		map_idx_to_word, map_word_to_idx, bag_words, stem_bag_words = self.db.read_voca()
		voca = []
		for key, value in map_idx_to_word.items():
			temp = [key,value]
			voca.append(temp)

        #[topics_list] = self.eng.function_run_extm(A, B, xcls_value, voca, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, nargout=3);
		[topics_list, w_scores, t_scores, xscore] = self.eng.function_run_extm(A, xcls_value, voca, num_clusters, num_keywords, nargout=4);
		topics = np.asarray(topics_list);
		topics = np.reshape(topics, (num_clusters, num_keywords));

		word_scores = np.asarray(w_scores);
		word_scores = np.reshape(word_scores, (num_clusters, num_keywords));

		topic_scores = np.asarray(t_scores);

		elapsed_time_function_run = time.time() - start_time_function_run
		logging.info('run_topic_modeling -function_run_extm Execution time: %.3fms', elapsed_time_function_run)


		start_time_replace = time.time()
		# find original word and replace

		ret_topics = []
		topic_id = 0;
		for topic in topics:

			ret_topic = {}
			ret_topic['score'] = topic_scores[topic_id, 0]
			ret_words = []
			for rank, word in enumerate(topic):

				word_score = word_scores[topic_id, rank]

				temp_count = 0
				temp_word = ''
				s_count = 0

				res_word = ''
				for key, value in stem_bag_words[word].items():
					res_word = key
					break

				word_cnt = bag_words[word]

				ret_word = {}
				ret_word['word'] = res_word
				ret_word['score'] = word_score
				ret_word['count'] = word_cnt
				ret_words.append(ret_word)

			ret_topic['words'] = ret_words
			ret_topics.append(ret_topic)
			topic_id += 1


		elapsed_time_replace= time.time() - start_time_replace
		logging.info('run_topic_modeling -replace Execution time: %.3fms', elapsed_time_replace)

		return ret_topics

	def get_ondemand_topics(self, level, x, y, year, yday, topic_count, word_count, exclusiveness, include_words, exclude_words):

		ondemand_topics=[]

		sub_mtx = make_sub_term_doc_matrix(level, x, y, year, yday, include_words, exclude_words)
		ondemand_topics = run_topic_modeling(sub_mtx, level, x, y, exclusiveness, topic_count, word_count)

		return ondemand_topics;


	def get_topics(self, level, x, y, topic_count, word_count, include_words, exclude_words, exclusiveness, date):

		start_time=time.time()
		
		logging.debug('get_topics(%s, %s, %s)', level, x, y)
		tile_id = self.get_tile_id(level, x, y);

		# voca_hash= self.db.get_vocabulary_hashmap();
		# voca= self.db.get_vocabulary();
		
		# for testing
		#exclusiveness = 50;

		exclusiveness_local = exclusiveness / 5;
		logging.debug('exclusiveness: %f', exclusiveness_local);

		result = {};
		tile = {};
		tile['x'] = x;
		tile['y'] = y;
		tile['level'] = level;

		result['tile'] = tile;

		# result['exclusiveness'] = exclusiveness

		date = datetime.fromtimestamp(int(int(date)/1000))
		year = date.timetuple().tm_year
		yday = date.timetuple().tm_yday

		# result['exclusiveness_score'] = self.db.get_xscore(level, x, y, year, yday)

		topics = []
		
		# if include or exclude exist 
		if len(include_words)==0 and len(exclude_words) ==0:
			
			topics = self.db.get_topics(level, x, y, year, yday, topic_count, word_count, exclusiveness);
			logging.info('done get_topics')

		else:

			topics = self.get_ondemand_topics(level, x, y, year, yday, topic_count, word_count, exclusiveness, include_words, exclude_words)
			logging.info('done ondemand_topics')


		# topics = self.db.get_topics(level, x, y, year, yday, topic_count, word_count, exclusiveness);

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
		#neighbor_tile_name = 'docmap_' + str(year) + '_d' + str(day_of_year) + '_' + str(level) + '_' + str(x) + '_' + str(y)

		
		mtx_file = open(constants.MTX_DIR + tile_name, 'r', encoding='UTF8')
		
		#mtx_file = open(constants.MTX_DIR + neighbor_tile_name, 'r', en)

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

	def get_tile_detail_info(self, level, x, y, time_from, time_to):

		logging.debug('get_tile_detail_info(%s, %s, %s, %s, %s)', level, x, y, time_from, time_to)

		# convert the unixtime to ydate
		date_from = datetime.fromtimestamp(int(int(date_from)/1000))
		date_to = datetime.fromtimestamp(int(int(date_to)/1000))

		year = date_from.timetuple().tm_year
		mon = date_from.timetuple().tm_mon
		mday = date_from.timetuple().tm_mday

		yday_from = date_from.timetuple().tm_yday
		yday_to = date_to.timetuple().tm_yday

		result = {};
		tile = {};
		tile['x'] = x;
		tile['y'] = y; 
		tile['level'] = level;

		result['tile'] = tile;

		time_graph = []
		all_topics = []
		for ydate in range(yday_from, yday_to+1):
			item = []
			exclusiveness_score = self.get_xscore(level, x, y, year, ydate)
			item['score'] = exclusiveness_score
			item['date'] = datetime(year=year, month=mon, day=mday).strftime("%d-%m-%Y")
			time_graph.append(item)

			item = []
			item['date'] = datetime(year=year, month=mon, day=mday).strftime("%d-%m-%Y")
			topics = []
			for xvalue in range(0, 6):
				topic = {}
				topic['exclusiveness'] = xvalue
				topic['topic'] = self.db.get_topics(level, x, y, ydate, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, xvalue)
				topics.append(topic)

			item['topics'] = topics
			all_topics.append(item)

		result['time_grath'] = time_graph
		result['all_topics'] = all_topics

		return result;

	def get_heatmaps(self, level, x, y, date_from, date_to):

		logging.debug('get_heatmaps(%d, %d, %d, %d, %d)', level, x, y, date_from, date_to)

		# convert the unixtime to ydate
		date_from = datetime.fromtimestamp(int(int(date_from)/1000))
		date_to = datetime.fromtimestamp(int(int(date_to)/1000))

		year = date_from.timetuple().tm_year
		mon = date_from.timetuple().tm_mon
		mday = date_from.timetuple().tm_mday

		yday_from = date_from.timetuple().tm_yday
		yday_to = date_to.timetuple().tm_yday

		result = []

		for ydate in range(yday_from, yday_to+1):

			# get heatmap list from db
			exclusiveness_score = self.db.get_xscore(level, x, y, year, ydate)

			xcls_scores = {}

			tile = {}
			tile['x'] = x
			tile['y'] = y
			tile['level'] = level
			xcls_scores['tile'] = tile

			xcls_scores['exclusiveness'] = []
			xcls_score = {}
			xcls_score['value'] = exclusiveness_score

			date = datetime(year=year, month=mon, day=mday)
			date_str = date.strftime("%d-%m-%Y")
			logging.debug('date_str: %s', date_str)
			xcls_score['date'] = date_str

			xcls_scores['exclusiveness'].append(xcls_score)

			result.append(xcls_scores)

		return result


	def get_word_info(self, level, x, y, word):
		# TBD
		return "word_info";