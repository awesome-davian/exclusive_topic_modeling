import logging

class TopicModelingModule():

	def __init__(self, DB):
		
		import nmf_core

		self.nmf = nmf_core
		self.MAX_NUM_CLUSTERS = 10
		self.MAX_NUM_KEYWORDS = 10
		self.db = DB

	def getTileId(self, x, y):

		tile_id = x + y;

		return tile_id;

	def make_sub_term_doc_matrix(self, term_doc_mtx, doc_ids, include_word_list, exclude_word_list, time_range):

		return "sub_term_doc_mtx";

	def get_topics(self, zoom_level, x, y, num_clusters, num_keywords, include_word_list, exclude_word_list, exclusiveness, time_range):

		logging.debug('get_topics(%s, %s, %s)', zoom_level, x, y)

		topic = {};
		if x == 5 and y == 4:
			topic = {
				"tile": {"x": 5, "y": 4, "level": 12},
				"topic": [{
					"score": 4.315,
					"words": [
						{"score": 1.23, "word": "food"},
						{"score": 0.9855, "word": "burger"},
						{"score": 0.72735, "word": "fries"},
						{"score": 0.71, "word": "drinks"}
					] }]
				};

		elif x == 5 and y == 6:
			topic = {
				"tile": {"x": 5, "y": 6, "level": 12},
				"topic": [{
					"score": 5.385,
					"words": [
						{"score": 1.47, "word": "yankees"}, 
						{"score": 0.2347, "word": "baseball"}, 
						{"score": 0.742, "word": "beer"}, 
						{"score": 0.92, "word": "pizza"}
					] }]
				};

		return topic;

		# tile_id = self.getTileId(x, y);

		# #if include_word_list == "" && exclude_word_list == "" && exclusiveness == 0 && time_range.start == "" && time_range.end == "":
		# if include_word_list == "" and exclude_word_list == "" and exclusiveness == 0:
		# 	# get precomputed topic modeling
		# 	nmf_result = self.db.get_topic_modeling_result(zoom_level, tile_id)
		# else:
		# 	# calculate topic modeling on the fly
		# 	term_doc_mtx = self.db.get_term_doc_matrix()

		# 	doc_ids = self.db.get_documents_in_tile(zoom_level, tile_id)

		# 	sub_term_doc_mtx = self.make_sub_term_doc_matrix(term_doc_mtx, doc_ids, include_word_list, exclude_word_list, time_range)

		# 	nmf_result = self.nmf.runNMF(sub_term_doc_mtx, num_clusters, num_keywords, exclusiveness)

		# return nmf_result;

	def get_word_ref_count(self, zoom_level, x, y, word):
		return 0;

	def get_word_info(self, zoom_level, x, y, word):
		return "word_info";