from Log import Log
import database_wrapper as DBWrapper
import nmf_core as NMFCore

class TileGenerator():

	def __init__(self, DB):
		Log.d("TileGenerator.__init__")
		self.db = DB

	def load_raw_data(self):
		return "";

	def store_raw_data(self):
		return "";

	def make_dictionary(self):
		return "";

	def store_dictionary(self):
		return "";

	def make_term_doc_matrix(self):
		return "";

	def store_term_doc_matrix(self):
		return "";

	def make_tile(self):
		return "";
		
	def store_tiles(self):
		return "";

	def make_default_tiles(self):

		Log.d("make_default_tiles() - IN")

		self.load_raw_data()

		self.store_raw_data()

		self.make_dictionary()

		self.store_dictionary()

		self.make_term_doc_matrix()

		self.store_term_doc_matrix()

		self.make_tile()

		self.store_tiles()

		return;

	def run_topic_modeling(self, topic_modeling_module, num_clusters, num_keywords, exclusiveness):

		Log.d("run_topic_modeling() - IN")

		# for every zoom level
		for level in range(7, 13):

			# every tile in this zoom level
			for tile in range(1, 20):

				# calculate topic modeling on the fly
				nmf_result = topic_modeling_module.get_topics(level, tile, topic_modeling_module.MAX_NUM_CLUSTERS, topic_modeling_module.MAX_NUM_KEYWORDS, "", "", 0, "", 1)
				self.db.set_topic_modeling_result(level, tile, nmf_result)

		return;