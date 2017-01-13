import logging
import pymongo
import constants

class DBWrapper():

	def __init__(self):

		return;

	def connect(self, ip, port):
		self.conn = pymongo.MongoClient(ip, port);
		self.dbname = constants.DB_NAME;
		self.db = self.conn[self.dbname];
		
	# The APIs for TileGenerator
	def set_raw_data(self, doc):
		return;

	def set_dictionary(self, obj):
		return;

	def set_term_doc_matrix(self, obj):
		return;

	def insert_doc_id_in_tile(self, tile_id, doc_id):
		return;

	def set_topic_modeling_result(self, zoom_level, tile_id, topics):
		return;

	# The APIs for Topic Modeling Module
	def get_term_doc_matrix(self):
		return "term_doc_matrix";

	def get_documents_in_tile(self, zoom_level, tile_id):
		return "document_list";

	def get_word(self, term_id):
		return "word";

	def get_raw_data(self, doc_id):
		return "raw_data";

	def get_topics(self, zoom_level, tile_id):

		logging.debug('get_topics(%d, %d)', zoom_level, tile_id);

		topics = [];
		for tile_name in self.db.collection_names():

			# find out only the 
			if tile_name.endswith('_topics') == True:
				print(tile_name)

				if tile_name.find(str(tile_id)) > 0:
					print('found')

					tile = self.db[tile_name]
					for i in range(1,11):

						topic = {};
						topic["score"] = tile.find_one({'topic_id':999})['topic_score'];

						words = [];
						
						for each in tile.find({'topic_id': i}).sort('rank',pymongo.ASCENDING):
							# topic.append(each['word']);
							
							word = {};
							word["word"] = each['word']
							words.append(word)
							

						topic["words"] = words;

						topics.append(topic);

					break;

		return topics;

	def db_to_file(self, ):
		# raw_data;
		# time_stamp;
		# x,y;
		return "";

