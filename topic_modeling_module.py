
class TopicModelingModule():

	def __init__(self, DB):
		
		import nmf_core

		self.nmf = nmf_core
		self.MAX_NUM_CLUSTERS = 10
		self.MAX_NUM_KEYWORDS = 10
		self.db = DB

	def make_sub_term_doc_matrix(self, term_doc_mtx, doc_ids, include_word_list, exclude_word_list, time_range):

		return "sub_term_doc_mtx";

	def get_topics(self, zoom_level, tile_id, num_clusters, num_keywords, include_word_list, exclude_word_list, exclusiveness, time_range, need_remake):

		#if include_word_list == "" && exclude_word_list == "" && exclusiveness == 0 && time_range.start == "" && time_range.end == "":
		if include_word_list == "" and exclude_word_list == "" and exclusiveness == 0 and need_remake == 0:
			# get precomputed topic modeling
			nmf_result = self.db.get_topic_modeling_result(zoom_level, tile_id)
		else:
			# calculate topic modeling on the fly
			term_doc_mtx = self.db.get_term_doc_matrix()

			doc_ids = self.db.get_documents_in_tile(zoom_level, tile_id)

			sub_term_doc_mtx = self.make_sub_term_doc_matrix(term_doc_mtx, doc_ids, include_word_list, exclude_word_list, time_range)

			nmf_result = self.nmf.runNMF(sub_term_doc_mtx, num_clusters, num_keywords, exclusiveness)

		return nmf_result;

	def get_word_ref_count(self, zoom_level, tile_id, word):
		return 0;

	def get_word_info(self, zoom_level, tile_id, word):
		return "word_info";