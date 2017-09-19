import logging, logging.config
import constants
import os
import collections 
import time
from nltk import PorterStemmer
from datetime import datetime
import math
import json


logging.config.fileConfig('logging.conf')


def getTwitterDate(date):
	date_format = ''
	if len(date) == 30:
		# date_format = "EEE MMM dd HH:mm:ss ZZZZZ yyyy";
		date_format = "%a %b %d %H:%M:%S %z %Y"

	else:
		# date_format = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'";
		date_format = "%Y-%m-%dT%H:%M:%S.000Z"


	return datetime.strptime(date, date_format)

def getTwitterHour(date):
	date_format = ''
	if len(date) == 30:
		# date_format = "EEE MMM dd HH:mm:ss ZZZZZ yyyy";
		date_format = "%a %b %d %H:%M:%S %z %Y"

	else:
		# date_format = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'";
		date_format = "%Y-%m-%dT%H:%M:%S.000Z"


	return datetime.strptime(date, date_format).timetuple().tm_hour, datetime.strptime(date, date_format).timetuple().tm_min

porter_stemmer=PorterStemmer()


start_time = time.time()

stem_bag_words = collections.OrderedDict()
bag_words = collections.OrderedDict()
map_word_to_idx = collections.OrderedDict()

voca_file = open(constants.GLOBAL_VOCA_FILE_PATH, 'r', encoding='UTF8')
voca_hash_file = open(constants.GLOBAL_VOCA_FILE_PATH+'_hash', 'r', encoding='UTF8')

idx = 1
map_idx_to_word = collections.OrderedDict()
voca = voca_file.readlines()
for line in voca:
	v = line.split('\t')

	bag_words[v[0]] = int(v[1])
	map_word_to_idx[v[0]] = idx
	map_idx_to_word[idx] = v[0]
	idx += 1

# idx = 0
# for key, value in bag_words.items():
# 	if idx > 100:
# 		break
# 	print("%s, %d" % (key, int(value)))
# 	idx += 1

voca_hash = voca_hash_file.readlines()
for line in voca_hash:
	v = line.split('\t')
	if v[0] not in stem_bag_words:
		stem_bag_words[v[0]] = collections.OrderedDict()

	stem_bag_words[v[0]][v[1]] = int(v[2])

# idx = 0
# for key, value in stem_bag_words.items():
# 	if idx > 100:
# 		break

# 	print("%s, %s, %s" % (key, list(value)[0], value[list(value)[0]]))
# 	idx += 1

voca_file.close()
voca_hash_file.close()

elapsed_time = time.time() - start_time
logging.info('read_voca(). Elapsed time: %.3fms', elapsed_time)


# start_time = time.time()

# docs_file = open(constants.GLOBAL_DOC_FILE_PATH, 'r', encoding='UTF8')

# map_idx_to_doc = collections.OrderedDict()
# docs = docs_file.readlines()

# for idx, doc in enumerate(docs):

# 	v = doc.split('\t')

# 	# v[0]: index
# 	# v[1]: date
# 	# v[2]: lon
# 	# v[3]: lat
# 	# v[4]: author
# 	# v[5]: text

# 	# doc_time = getTwitterDate(v[1])
# 	# #year = doc_time.timetuple().tm_year
# 	# day_of_year = doc_time.timetuple().tm_yday

# 	map_idx_to_doc[idx+1] = collections.OrderedDict()
# 	map_idx_to_doc[idx+1] = [v[1], v[2], v[3], v[4], v[5]]

# 	# map_idx_to_doc[0]: date
# 	# map_idx_to_doc[1]: lon
# 	# map_idx_to_doc[2]: lat
# 	# map_idx_to_doc[3]: author
# 	# map_idx_to_doc[4]: text

# 	# try:
# 	# 	if len(map_idx_to_doc[idx][day_of_year]) == 0:
# 	# 		map_idx_to_doc[idx][day_of_year] = []
# 	# except KeyError:
# 	# 	map_idx_to_doc[idx][day_of_year] = []

# 	# 	map_idx_to_doc[idx][day_of_year].append([v[2], v[3], v[4], v[5]])

# docs_file.close()

# elapsed_time = time.time() - start_time
# logging.info('read_docs(). Elapsed time: %.3fms', elapsed_time)




def read_all_file():

	all_file = collections.OrderedDict()
	path = constants.TOPIC_DIR + 'alpha_0.'
	i= 0 
	for i in range (6,8):

		datapath = path + str(i) +'/'
		all_file[i] = collections.OrderedDict()

		for root, dictionries, files in os.walk(datapath):			
			for filename in files:
				if 'just' in filename:
					continue

				print(filename)
				v = filename.split('_')
				year = int(v[1])
				yday = int(v[2])
				level = int(v[3])
				x = int(v[4])
				y = int(v[5])

				print(year)
				print(yday)
				print(level)
				print(x)
				print(y)


				i += 1 
				if i > 10:
					break 



				#jacard_score = compute_jacard_score(level, x, y, year, yday, datapath)

				#all_file[i][filename].append(jacard_score)

	return 




def compute_jacard_score(level, x, y, year, yday , datapath):
	mypath = constants.TOPIC_DIR + 'alpha_0.0/'
	# x = 1208
	# y = 2555

	neighbor_names = []

	topic_file_name = 'topics_' + str(year) + '_' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)

	#logging.info(topic_file_name)
	temp_name = 'topics_' + str(year) + '_' + str(yday) + '_' + str(level) + '_' 



	for i in range(0,3):
		temp_name1 = 'topics_' + str(year) + '_' + str(yday - i) + '_' +str(level) + '_' + str(x) + '_' + str(y)
		neighbor_names.append(temp_name1)

	# neighbor_names.append(temp_name+str(x+1)+'_'+str(y+0))
	# neighbor_names.append(temp_name+str(x+0)+'_'+str(y+1))
	# neighbor_names.append(temp_name+str(x+0)+'_'+str(y-1))
	# neighbor_names.append(temp_name+str(x-1)+'_'+str(y+0))

	topic_self = [] 
	topic_neighbor = []
	topic_yesterday = []
	num_topics = 0
	topic_count = 5

	try: 
		with open(datapath + topic_file_name, 'r', encoding = 'ISO-8859-1') as file:
			lines = file.readlines()
			if len(lines) > 0:

				topic_cnt = 0 
				is_first = True
				for line in lines: 
					v = line.split('\t')

					if is_first == True:
						num_topics = int(v[0])
						is_first =False
						continue

					topic_cnt += 1 
					if topic_cnt > topic_count:
						break

					for i in range(0,len(v) - 1):
						topic_self.append(porter_stemmer.stem(v[i].strip()))

	except KeyError as fe:
		logging.error(fe)
		pass

   

	# for each in neighbor_names:
	# 	logging.debug('path: %s', each)

	for idx, each in enumerate(neighbor_names):

		each_path = mypath + each 

		if os.path.exists(each_path) == False:
			#logging.debug(each_path)
			continue

		try:
			with open(each_path, 'r', encoding = 'ISO-8859-1') as each_file: 

				lines = each_file.readlines()

				if len(lines) > 0 :	

					is_first = True
					topic_cnt = 0 
					for line in lines:

						v = line.split('\t')

						if is_first == True:
							num_topics = int(v[0])
							is_first = False
							continue
						topic_cnt += 1 
						if topic_cnt > topic_count:
							break

						for i in range(0, len(v)-1):
							if idx == 0 :
								topic_yesterday.append(porter_stemmer.stem(v[i].strip()))
							else:
							    topic_neighbor.append(porter_stemmer.stem(v[i].strip()))

		except FileNotFoundError as fe:
			logging.error(fe)
			pass




	#print(topic_self)
	#print(topic_neighbor)




	query_self = []
	query_neighbor = []
	query_yesterday = []
	for element in topic_self:
		try:
			query_idx = map_word_to_idx[element]
			query_self.append(query_idx)

		except KeyError as ke:
			continue

	for element in topic_yesterday:
		try: 
			query_idx = map_word_to_idx[element]
			query_yesterday.append(query_idx)
		except KeyError as ke:
			continue

	for element in topic_neighbor:
		try:
			query_idx = map_word_to_idx[element]
			query_neighbor.append(query_idx)
		except KeyError as ke:
			continue

	set_neighbor = set(query_neighbor)
	set_self = set(query_self)
	set_yesterday = set(query_yesterday)

	diff_set_with_neighbor = list(set_self.difference(set_neighbor))
	diff_set_with_yesterday = list(set_self.difference(set_yesterday))
	# print(len(set_neighbor))
	# print(len(set_self))
	#print(len(set_yesterday))

	# print((diff_set_with_neighbor))
	# print((diff_set_with_yesterday))

	tot_freq_neighbor = 0
	tot_freq_yesterday = 0

	for i in range(len(diff_set_with_neighbor)):
		temp = map_idx_to_word[diff_set_with_neighbor[i]]
		temp_word_freq, _  = get_word_frequency(temp, level, x, y, year, yday)
		tot_freq_neighbor += temp_word_freq

	for i in range(len(diff_set_with_yesterday)):
		temp = map_idx_to_word[diff_set_with_yesterday[i]]
		temp_word_freq, _ = get_word_frequency(temp, level, x, y, year, yday)
		tot_freq_yesterday += temp_word_freq

	if int(num_topics) == 0:
		tot_freq_yesterday = 0
		tot_freq_neighbor = 0
	else: 
		tot_freq_neighbor = tot_freq_neighbor / int(num_topics)
		tot_freq_yesterday = tot_freq_yesterday / int(num_topics)



	if len(set_neighbor) == 0 or len(set_yesterday) ==0:
		jacard_score = 0.0
		jacard_score_yesterday = 0.0

	else : 
		#jacard_score = len(set_neighbor.intersection(set_self)) / len(set_neighbor.union(set_self))
		#jacard_score_yesterday = len(set_yesterday.intersection(set_self)) / len(set_yesterday.union(set_self))
		jacard_score = len(set_self.difference(set_neighbor)) / len((set_self)) 
		jacard_score_yesterday = len(set_self.difference(set_yesterday)) / len((set_self))
	
	#print(jacard_score)
	#print(jacard_score_yesterday)
	# print('---------------------------------------------')
	# print('freq')
	# print(tot_freq_neighbor)
	# print('len')
	# print(len(diff_set_with_neighbor))
	#print(math.log(tot_freq_neighbor,2.7) * len(diff_set_with_neighbor) / num_topics)
	#print(math.log(tot_freq_yesterday,2.7) * len(diff_set_with_yesterday) / num_topics)
	print(tot_freq_yesterday)
	print(tot_freq_neighbor)


	return jacard_score, jacard_score_yesterday



def get_tfidf_values(word):

	datapath = constants.TFIDF_DIR
	tfidf_values = [] 

	tileid = '2013_d307_11_602_1276'
	tilename = 'tfidf_eightdays_' + tileid


	try: 
		query_idx = map_word_to_idx[word]
		#print(query_idx)

		try: 
			with open(datapath + tilename, 'r', encoding = 'UTF8') as f: 
				print('a')
				lines = f.readlines()
				for line in lines: 
					v = line.split('\t')
					temp_word_idx = v[0]
					if int(temp_word_idx) == int(query_idx): 
						#print(temp_word_idx)
						for i in range(2,9):
							tfidf_values.append(float(v[i]))
						break 
		except FileNotFoundError as fe: 
			tfidf_values = [] 
			print('not found')
	except KeyError as ke: 
		tfidf_values = [] 

	return tfidf_values

def get_tfidf_value(word):

	datapath = constants.TFIDF_DIR
	tfidf_values = 0.0 

	tileid = '2013_d307_11_603_1278'
	tilename = 'tfidf_eightdays_' + tileid


	try: 
		query_idx = map_word_to_idx[word]
		#print(query_idx)

		try: 
			with open(datapath + tilename, 'r', encoding = 'UTF8') as f: 
				print('a')
				lines = f.readlines()
				for line in lines: 
					v = line.split('\t')
					temp_word_idx = v[0]
					if int(temp_word_idx) == int(query_idx): 
						#print(temp_word_idx)
						tfidf_values = float(v[1])
						break 
		except FileNotFoundError as fe: 
			tfidf_values = 0.0 
			print('not found')
	except KeyError as ke: 
		tfidf_values = 0.0

	return tfidf_values

def get_word_frequency(word, level, x, y, year, yday):

	datapath = constants.FREQ_DIR

	word_freq = 0
	doc_freq = 0

	tileid = str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)
	tileid = 'wfreq_' + tileid
	
	try:
		query_idx = map_word_to_idx[word]
		#logging.info('word: %s, query_idx: %d', word, query_idx)

		try: 
			with open(datapath+tileid, 'r', encoding='UTF8') as f:

				lines = f.readlines()
				is_firstline = True
				for line in lines:

					# pass the first line
					if is_firstline == True:	
						is_firstline = False
						continue

					v = line.split('\t')
					
					temp_word_idx = int(v[0])

					if temp_word_idx == query_idx:
						word_freq = int(v[1])
						doc_freq = int(v[2])
						break


		except FileNotFoundError as fe:
			print(fe)
			word_freq = 0
			doc_freq = 0

	except KeyError as ke:
		print(ke)
		word_freq = 0
		doc_freq = 0

	return word_freq, doc_freq


def get_week_freq(word, level, x, y, year, yday):

	word_freq = 0.0
	tf_word_percent = []

	try:
		for i in range(0,7):
			# get term-doc matrix
			word_freq, _ = get_word_frequency(word, level, x, y, year, str(yday - i))
			tot_freq = 0
			for i in range(0,7):
				temp_word_freq, _ = get_word_frequency(word, level, x, y, year, str(yday - i))
				tot_freq += temp_word_freq
				logging.debug(tot_freq)

			#logging.debug(tot_freq)

			if(tot_freq >0):
				tf_word_percent.append(word_freq / tot_freq)

			# max_freq = self.map_max_word_freq[yday][level]
			# word_score = word_freq / max_freq


	except KeyError as e:
		logging.debug('KeyError: %s', e)
		word_freq = 0
		tf_word_percent.append(0)


	#print(tf_word_percent)


	return tf_word_percent

def get_day_related_docs(level, x, y, year, yday, word):

	s_word = porter_stemmer.stem(word)
	#print(word)
	word_idx = map_word_to_idx[s_word]

	#print(word_idx)

	rel_docs = []
	doc_list = []  

	if os.path.exists(constants.MTX_DIR + 'mtx_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)) == True:
		try:
			with open(constants.MTX_DIR + 'mtx_' + str(year) + '_d'
			 + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y), 'r', encoding = 'UTF8') as f:
			    lines = f.readlines()
			    for line in lines: 
			    	v= line.split('\t')

			    	temp_word_idx = int(v[0])
			    	doc_idx = int(v[1])

			    	if int(word_idx) == temp_word_idx:

				    	doc_time = getTwitterDate(map_idx_to_doc[doc_idx][0])
				    	date = doc_time.timetuple().tm_yday
				    	unixtime = time.mktime(doc_time.timetuple())
				    	username = str(map_idx_to_doc[doc_idx][3])
				    	text = str(map_idx_to_doc[doc_idx][4])

				    	local_hours, local_minutes = getTwitterHour(map_idx_to_doc[doc_idx][0])


				    	d = {}
				    	d['username'] = username
				    	d['created_at'] = unixtime
				    	d['text'] = text
				    	doc_list.append(d)

				    	rel_docs.append(local_hours)


			arr = [] 
			for i in range(0,24): 
				isexist = rel_docs.count(i)
				arr.append(isexist)
	
		except FileNotFoundError as fe :
			rel_docs = []
			doc_list = []
			pass 


	return rel_docs, doc_list




def get_related_docs(level, x, y, word, date):

	start_time = time.time()

	# get docs including the word 
	date = datetime.fromtimestamp(int(int(date)/1000))
	year = date.timetuple().tm_year
	day_of_year = date.timetuple().tm_yday

	logging.debug('get_releated_docs(%s, %s, %s, %s, %d)', level, x, y, word, day_of_year)

	s_word = porter_stemmer.stem(word)
	word_idx = map_word_to_idx[s_word]

	logging.info('word: %s, s_word: %s, word_idx: %d', word, s_word, word_idx)


	total_docs = []
	time_arr = {}

	_,  temp_doc_list = get_day_related_docs(level, x, y, year, day_of_year, word)

	for element in temp_doc_list:
		d = {}
		d['username'] = element.get('username')
		d['created_at'] = element.get('created_at')
		d['text'] = element.get('text')
		total_docs.append(d)


	for i in range(day_of_year, day_of_year + 30):

		_, doc_freq = get_word_frequency(s_word, level, x, y, year, i)
		time_arr[str(i)] = doc_freq	


	result = {}
	tile = {}
	tile['x'] = x
	tile['y'] = y
	tile['level'] = level

	result['tile'] = tile

	result['documents'] = total_docs
	result['timeGraph'] = time_arr;

	elapsed_time=time.time()-start_time
	logging.info('get_releated_docs elapsed: %.3fms' , elapsed_time)

	print(time_arr)


	return result



def get_day_geo_docs( level, x, y, year, yday, word):

	s_word = porter_stemmer.stem(word)
	word_idx =map_word_to_idx[s_word]

	points = []



	if os.path.exists(constants.MTX_DIR + 'mtx_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)) == True:
		try:
			with open(constants.MTX_DIR + 'mtx_' + str(year) + '_d' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y), 'r', encoding = 'UTF8') as f:
			    lines = f.readlines()
			    for line in lines: 
			    	v= line.split('\t')

			    	temp_word_idx = int(v[0])
			    	doc_idx = int(v[1])

			    	if int(word_idx) == temp_word_idx:

				    	lon = str(map_idx_to_doc[doc_idx][1])
				    	lat = str(map_idx_to_doc[doc_idx][2])

				    	point = {}
				    	point['xbin'] = lon
				    	point['ybin'] = lat
				    	points.append(point)    	


		except FileNotFoundError as fe:
			logging.debug('FileNotFoundError: %s', fe);
			points = []
			pass 

	#print(points)

	return points

datapath = constants.TOPIC_DIR + 'alpha_0.8/'

# points = get_day_geo_docs(11, 603, 1277, 2013, 307, 'marathon')

# geo_points = []

# for element in points:
# 	point = {}
# 	point['xbin'] = float(element.get('xbin'))
# 	point['ybin'] = float(element.get('ybin'))

# 	geo_points.append(point)


# print(geo_points)



#temp = get_related_docs(11, 603, 1277, 'marathon', 1383485320000)
#json.dumps(temp)
# temp= porter_stemmer.stem('someones')
# print(map_word_to_idx[temp])
#temp = get_tfidf_value('nycmarathon')
#print(temp)
#compute_jacard_score(12, 1206, 2554, 2013, 307, datapath)

#get_week_freq('nycmarathon', 11, 603, 1278, 2013, 307)
# compute_jacard_score(12, 1207, 2556, 2013, 307, datapath)f
compute_jacard_score(11, 601, 1276, 2013, 306, datapath)
compute_jacard_score(11, 602, 1276, 2013, 306, datapath)
compute_jacard_score(11, 602, 1277, 2013, 306, datapath)
compute_jacard_score(11, 603, 1277, 2013, 306, datapath)
compute_jacard_score(11, 603, 1278, 2013, 306, datapath)
compute_jacard_score(11, 603, 1279, 2013, 306, datapath)
compute_jacard_score(11, 604, 1277, 2013, 306, datapath)
compute_jacard_score(11, 604, 1278, 2013, 306, datapath)

# compute_jacard_score(12, 1203, 2553, 2013, 307, datapath)
# compute_jacard_score(12, 1204, 2553, 2013, 307, datapath)
# compute_jacard_score(12, 1205, 2554, 2013, 307, datapath)
# compute_jacard_score(12, 1205, 2556, 2013, 307, datapath)
# compute_jacard_score(12, 1206, 2554, 2013, 307, datapath)
# compute_jacard_score(12, 1206, 2555, 2013, 307, datapath)
# compute_jacard_score(12, 1206, 2556, 2013, 307, datapath)
# compute_jacard_score(12, 1207, 2555, 2013, 307, datapath)
# compute_jacard_score(12, 1207, 2556, 2013, 307, datapath)
# compute_jacard_score(12, 1208, 2554, 2013, 307, datapath)
# compute_jacard_score(12, 1208, 2555, 2013, 307, datapath)
# compute_jacard_score(12, 1208, 2556, 2013, 307, datapath)

# get_day_related_docs(11,603,1278, 2013, 307, 'start')
#get_day_related_docs(12, 1207, 2556, 2013, 307, 'start')
# get_day_related_docs(11, 601, 1276, 2013, 307, 'start')
# get_day_related_docs(11, 602, 1276, 2013, 307, 'start')
#get_day_related_docs(12, 1206, 2556, 2013, 307, 'finish')
# get_day_related_docs(11, 603, 1277, 2013, 307, 'start')
# get_day_related_docs(11, 603, 1278, 2013, 307, 'nycmarathon')
# get_day_related_docs(11, 603, 1279, 2013, 307, 'nycmarathon')
# get_day_related_docs(11, 604, 1277, 2013, 307, 'nycmarathon')
# get_day_related_docs(11, 604, 1278, 2013, 307, 'nycmarathon')

# get_day_related_docs(12, 1203, 2553, 2013, 307, 'nycmarathon')
# get_day_related_docs(12, 1204, 2553, 2013, 307, 'nycmarathon')
# get_day_related_docs(12, 1205, 2554, 2013, 307, 'nycmarathon')
# get_day_related_docs(12, 1205, 2556, 2013, 307, 'nycmarathon')
# get_day_related_docs(12, 1206, 2554, 2013, 307, 'nycmarathon')
# get_day_related_docs(12, 1206, 2555, 2013, 307, 'nycmarathon')
# get_day_related_docs(12, 1206, 2556, 2013, 307, 'nycmarathon')
# get_day_related_docs(12, 1207, 2555, 2013, 307, 'nycmarathon')
# get_day_related_docs(12, 1207, 2556, 2013, 307, 'nycmarathon')
# get_day_related_docs(12, 1208, 2554, 2013, 307, 'nycmarathon')
# get_day_related_docs(12, 1208, 2555, 2013, 307, 'nycmarathon')
# get_day_related_docs(12, 1208, 2556, 2013, 307, 'nycmarathon')


# arr = [] 
# for i in range(0,1440): 
# 	isexist = temp.count(i)
# 	if isexist > 0:
# 		arr.append(1)
# 	else: 
# 		arr.append(0)

# print(arr)
# arr = [] 
# for i in range(0,7):
# 	day = 307  
# 	temp = compute_jacard_score(12, 1208, 2555, 2013, 307 - i, datapath)
# 	arr.append(temp)

# print(arr)
#temp = read_all_file()
#print(temp)

