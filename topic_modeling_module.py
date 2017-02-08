import matlab.engine
import logging
import math
import constants
import numpy as np
import pymongo
import sys
sys.path.insert(0, '../')

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

		# logging.debug('x: %d, y: %d', x, y)

		# x = self.lon_to_x(level, lon);
		# y = self.lat_to_y(level, lat);

		# x = math.floor(x);
		# y = math.floor(y);

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

		# logging.debug('%f, %f, %f, %f', lat, level, latR, pow2);
		# logging.debug('%f, %f', math.tan(latR), 1/math.cos(latR))
		# logging.debug('%f', math.log(math.tan(latR) + 1/math.cos(latR)))

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


    #todo: JinHo 
	def make_sub_term_doc_matrix(self, term_doc_mtx, doc_ids, include_word_list, exclude_word_list, time_range):

		return "sub_term_doc_mtx";
    


	def run_topic_modeling(self, level, x, y, exclusiveness):
		
		logging.debug('run_topic_modeling(%d, %d, %d, %.2f)', level, x, y, exclusiveness);

		tile_id = self.get_tile_id(level, x, y);
		neighbor_ids = self.get_neighbor_ids(level, x, y);

		logging.debug(neighbor_ids)

		tile_mtx = self.db.get_term_doc_matrix(tile_id);
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
				print("found it, idx: " + str(idxa));
				B.append(each);
			else:
				B.append(each.tolist());

			idxa += 1;

		# for each in B:
		# 	print(type(each));

		# print(type(neighbor_mtx));
		# print(type(tile_mtx.tolist()));

		voca = self.db.get_vocabulary();

		topics = self.eng.function_run_extm(A, B, exclusiveness, voca, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, nargout=3);

		return topics;

	def get_topics(self, level, x, y, num_clusters, num_keywords, include_word_list, exclude_word_list, exclusiveness, time_range):

		logging.debug('get_topics(%s, %s, %s)', level, x, y)
		
		# todo here.
		tile_id = self.get_tile_id(level, x, y);
		#tile_id = 2570625;
		#zoom_level = 11;
		exclusiveness = 50;

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
			topics = self.db.get_precomputed_topics(level, x, y);

		else :

			# get neighbor tiles
			
			# neighbor_ids = []
			# neighbor_ids.append(642238)
			# neighbor_ids.append(642240)
			# neighbor_ids.append(642241)
			# neighbor_ids.append(642242)
			# neighbor_ids.append(642243)
			# neighbor_ids.append(643264)
			# neighbor_ids.append(643265)
			# neighbor_ids.append(643266)

			topics = self.run_topic_modeling(level, x, y, exclusiveness);

			#A = matlab.double(tile_mtx.tolist()) # sparse function in function_runme() only support double type.
			#topics_list = eng.function_runme(A, voca, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, nargout=1);

		result['topic'] = topics;

		print(result);

		#else
			# calculte on the fly.
		

		# return topics


		# topics = eng.function_runme(A, V, nargout=0);

		# topic = {};
		# if x == 5 and y == 4:
		# 	topic = {
		# 		"tile": {"x": 5, "y": 4, "level": 12},
		# 		"topic": [{
		# 			"score": 4.315,
		# 			"words": [
		# 				{"score": 1.23, "word": "food"},
		# 				{"score": 0.9855, "word": "burger"},
		# 				{"score": 0.72735, "word": "fries"},
		# 				{"score": 0.71, "word": "drinks"}
		# 			] }]
		# 		};

		# elif x == 5 and y == 6:
		# 	topic = {
		# 		"tile": {"x": 5, "y": 6, "level": 12},
		# 		"topic": [{
		# 			"score": 5.385,
		# 			"words": [
		# 				{"score": 1.47, "word": "yankees"}, 
		# 				{"score": 0.2347, "word": "baseball"}, 
		# 				{"score": 0.742, "word": "beer"}, 
		# 				{"score": 0.92, "word": "pizza"}
		# 			] }]
		# 		};

		return result;

	def get_word_ref_count(self, level, x, y, word):
		return 0;

	def get_word_info(self, level, x, y, word):
		return "word_info";