import matlab.engine
import logging
import math
import constants
import numpy as np
import pymongo
import sys
sys.path.insert(0, '../')
conn = pymongo.MongoClient("localhost", constants.DEFAULT_MONGODB_PORT);

dbname = constants.DB_NAME;
db = conn[dbname];

class TopicModelingModule():

	def __init__(self, DB):
		
		import nmf_core

		logging.debug('init');

		self.nmf = nmf_core
		self.db = DB

		logging.info("loading Matlab module...");
		self.eng = matlab.engine.start_matlab();
		self.eng.cd('./matlab/discnmf_code/');
		logging.info("Done: loading Matlab module");

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


	def get_doc_idx_include_word(self, term_doc_mtx, word_list):

		doc_lists=[]

		for word in word_list:

	        #find stemmed word form voca-hashmap
			voca_hash= self.db.get_vocabulary_hashmap();
			for each in voca_hash:
				if word==each['word']:
					stem_word=each['stem']
					break;
			#logging.info(stem_word)

			#get stemmed word id from voca 
			voca= self.db.get_vocabulary();
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

		return doc_lists;
    
    


    #todo: JinHo 
	def make_sub_term_doc_matrix(self, term_doc_mtx, include_word_list, exclude_word_list, time_range):

		exclude_doc_list=self.get_doc_idx_include_word(term_doc_mtx, exclude_word_list)
		include_doc_list=self.get_doc_idx_include_word(term_doc_mtx, include_word_list)

		new_tile_mtx=[]

		if(len(include_word_list)>0):
			for each in term_doc_mtx:
				for in_word in include_doc_list:
					for idx in in_word:
						if(each[1]==idx):
							item = np.array([each[0], each[1], each[2]], dtype=np.double);
							logging.info(item)
							new_tile_mtx = np.append(new_tile_mtx, item, axis=0)

		new_tile_mtx = np.array(new_tile_mtx, dtype=np.double).reshape(int(np.size(new_tile_mtx)/3), 3)


		logging.debug(new_tile_mtx)					
			# for idx, each in enumerate(new_tile_mtx):
			# 	for ex_word in exclude_doc_list:
			# 		if(each[1]==ex_word):
			# 			new_tile_mtx = np.delete(new_tile_mtx, idx, axis=0)

		# else: 
		# 	for idx, each in enumerate(term_doc_mtx):
		# 	    for ex_word in exclude_doc_list:
		# 	        if(each[1] == ex_word):
		# 	            continue;
		# 	        else:
		# 	        	item = np.array([each[0], each[1], each[2]], dtype=np.double);
		# 	        	new_tile_mtx = np.append(til_mtx, item,item, dtype=np.double);


		# loggging.debug(new_tile_mtx);	            



		return new_tile_mtx;
    


	def run_topic_modeling(self, level, x, y, exclusiveness, num_clusters, num_keywords):
		
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

		# for each in B:
		# 	print(type(each));

		# print(type(neighbor_mtx));
		# print(type(tile_mtx.tolist()));

		voca = self.db.get_vocabulary();

        #[topics_list] = self.eng.function_run_extm(A, B, exclusiveness, voca, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, nargout=3);
		[topics_list, w_scores, t_scores] = self.eng.function_run_extm(A, B, exclusiveness, voca, num_clusters, num_keywords, nargout=3);
		topics = np.asarray(topics_list);
		topics = np.reshape(topics, (num_clusters, num_keywords));

		word_scores = np.asarray(w_scores);
		word_scores = np.reshape(word_scores, (num_clusters, num_keywords));

		topic_scores = np.asarray(t_scores);

		# find original word and replace
		temp_word = "";
		for topic in topics:
			for word in topic:
				s_count=0
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
						word['score'] = word_scores[i,i1]
						words.append(word)

					# topic['words'] = words;
			tpc['words'] = words;

			rettopics.append(tpc);


		# end. 

		return rettopics;

	def get_topics(self, level, x, y, topic_count, word_count, include_words, exclude_words, exclusiveness, time_from, time_to):

		logging.debug('get_topics(%s, %s, %s)', level, x, y)
		
		tile_id = self.get_tile_id(level, x, y);
		
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
		if exclusiveness == 0 :  

			# get precomputed tile data
<<<<<<< HEAD
			topics = self.db.get_precomputed_topics(level, x, y,num_clusters,num_keywords);
			
			tile_mtx = self.db.get_term_doc_matrix(tile_id);
			self.make_sub_term_doc_matrix(tile_mtx,include_word_list,exclude_word_list,time_range)
=======
			topics = self.db.get_precomputed_topics(level, x, y, topic_count, word_count);
>>>>>>> 1d72da48a45c5ea87109a5681182e7dec1b28074

		else :

			topics = self.run_topic_modeling(level, x, y, exclusiveness, topic_count, word_count);



		result['topic'] = topics;

		#print(result);

		return result;


	def get_releated_docs(self, level, x, y, word):

		logging.debug('get_releated_docs(%s, %s, %s, %s)', level, x, y, word)

		tile_id = self.get_tile_id(level, x, y);

		result = {};
		tile = {};
		tile['x'] = x;
		tile['y'] = y; 
		tile['level'] = level;

		result['tile'] = tile;
		documents = [];

        #find stemmed word form voca-hashmap
		stem_word = "";
		voca_hash= self.db.get_vocabulary_hashmap();
		for each in voca_hash:
			if word==each['word']:
				stem_word=each['stem']
				break;
		logging.info(stem_word)

		#get stemmed word id from voca 
		word_id = "";
		voca= self.db.get_vocabulary();
		for idx, each in enumerate(voca):
		 	if stem_word==each['stem']:
		 		word_id=idx+1 
		 		break;

		logging.info(word_id);

        #get doc list for tem_doc.mtx
		tile_mtx = self.db.get_term_doc_matrix(tile_id);
		doc_list=[]
		for each in tile_mtx:
			if each[0]==word_id:
				doc_list.append(each[1])

		logging.info(doc_list)		

		#get raw_documents from raw_data 
		raw_data=self.db.get_raw_data(tile_id)
		for idx, each in enumerate(raw_data):
			for doc_num in doc_list:
				if ((idx==doc_num-1) and (each['text'].find(word)!=0)):
					raw_documents={}
					raw_documents['text']=each['text']
					raw_documents['created_at']=each['created_at']
					documents.append(raw_documents)

		result['documents'] = documents;

		return result;

	def get_word_info(self, level, x, y, word):
		# TBD
		return "word_info";





