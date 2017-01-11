class DBWrapper():

	def __init__(self):
		return;
		
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

	def get_topic_modeling_result(self, zoom_level, tile_id):
		return "topic_modeling_result";

	def db_to_file(self, ):
		# raw_data;
		# time_stamp;
		# x,y;
		return "";

