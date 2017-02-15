import logging
import pymongo
import constants
import numpy as np
import time


class DBWrapper():

	def __init__(self):

		return;

	def connect(self, ip, port):
		self.conn = pymongo.MongoClient(ip, port);
		self.dbname = constants.DB_NAME;
		self.db = self.conn[self.dbname];

	# The APIs for Topic Modeling Module
	def get_term_doc_matrix(self, id):
		
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

		return tile_mtx;

	def get_term_doc_matrices(self, ids):
		
		tile_mtxs = [];

		for tile_id in ids:
			tile_mtxs.append(self.get_term_doc_matrix(tile_id));

		return tile_mtxs;

	def get_documents_in_tile(self, zoom_level, tile_id):
		# todo
		return "document_list";

	def get_vocabulary(self):
		
		voca = []
		for each in self.db['vocabulary'].find():
			word = {}
			word['stem'] =each['stem']
			word['count'] = each['count'];
			voca.append(word);

		return voca;

	def get_vocabulary_hashmap(self):

		voca_hash= [] 
		for each in self.db['vocabulary_hashmap'].find():
			voca_hash_elemet={}
			voca_hash_elemet['word']=each['word']
			voca_hash_elemet['stem']=each['stem']
			voca_hash_elemet['count']=each['count']
			voca_hash.append(voca_hash_elemet)

		return voca_hash;	
	    	

	def get_raw_data(self, tile_id):

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

		return raw_data;

	def get_precomputed_topics(self, level, x, y ,topic_count, word_count):

		logging.debug('get_precomputed_topics(%d, %d, %d)', level, x, y);

		topics = [];

		start_time=time.time()

		voca_hash = self.get_vocabulary_hashmap()
		voca= self.get_vocabulary();

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

					#start_time_find_info=time.time()

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

					#elaspsed_time_find_info=time.time()-start_time_find_info
					#logging.info("Done find info. Execution time: %.3fms", elaspsed_time_find_info)		



					topic['words'] = words;

					topics.append(topic);

				break;

		elaspsed_time=time.time() - start_time
		logging.info("Done get Pre-computed topics. Execution time: %.3fms", elaspsed_time)	

		return topics;