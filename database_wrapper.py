import logging
import pymongo
import constants
import numpy as np

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
			word = each['stem'];
			voca.append(word);

		return voca;

	def get_raw_data(self, doc_id):
		# todo
		return "raw_data";

	def get_precomputed_topics(self, level, x, y):

		logging.debug('get_precomputed_topics(%d, %d, %d)', level, x, y);

		topics = [];
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
				for i in range(1,11):

					topic = {};
					topic['score'] = tile.find_one({'topic_id':constants.TOPIC_ID_MARGIN_FOR_SCORE+i})['topic_score'];

					words = [];
					
					for each in tile.find({'topic_id': i}).sort('rank',pymongo.ASCENDING):
						# topic.append(each['word']);
						
						word = {};
						word['word'] = each['word']
						word['score'] = each['score']
						word['count']=each['count']  # add count element 
						words.append(word)

					topic['words'] = words;

					topics.append(topic);

				break;

		return topics;