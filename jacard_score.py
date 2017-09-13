import logging, logging.config
import constants
import os
import collections 
import time

logging.config.fileConfig('logging.conf')



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
	x = 1208
	y = 2555

	neighbor_names = []

	topic_file_name = 'topics_' + str(year) + '_' + str(yday) + '_' + str(level) + '_' + str(x) + '_' + str(y)

	logging.info(topic_file_name)

	# temp_name = 'topics_' + str(2013) + '_' + str(307) + '_' + str(12) + '_' 

	# neighbor_names.append(temp_name+str(x+1)+'_'+str(y+0))
	# neighbor_names.append(temp_name+str(x+0)+'_'+str(y+1))
	# neighbor_names.append(temp_name+str(x+0)+'_'+str(y-1))
	# neighbor_names.append(temp_name+str(x-1)+'_'+str(y+0))

	for i in range(1,6):
		temp_name = 'topics_' + str(year) + '_' + str(yday - i) + '_' +str(level) + '_' + str(x) + '_' + str(y)
		neighbor_names.append(temp_name)

	topic_self = [] 
	topic_neighbor = []

	try: 
		with open(mypath + topic_file_name, 'r', encoding = 'ISO-8859-1') as file:
			lines = file.readlines()
			if len(lines) > 0:
				is_first = True
				for line in lines: 
					v = line.split('\t')

					if is_first == True:
						is_first =False
						continue
					for i in range(0,len(v) - 1):
						topic_self.append(v[i].strip())

	except KeyError as fe:
		logging.error(fe)
		pass

	for each in neighbor_names:
		logging.debug('path: %s', each)

	for idx, each in enumerate(neighbor_names):
		each_path = datapath + each 

		if os.path.exists(each_path) == False:
			continue

		try:
			with open(each_path, 'r', encoding = 'ISO-8859-1') as each_file: 

				lines = each_file.readlines()

				if len(lines) > 0 :	

					is_first = True
					for line in lines:

						v = line.split('\t')

						if is_first == True:
							is_first = False
							continue

						for i in range(0, len(v)-1):
							topic_neighbor.append(v[i].strip())

		except FileNotFoundError as fe:
			logging.error(fe)
			pass




	print(topic_self)
	print(topic_neighbor)




	query_self = []
	query_neighbor = []
	for element in topic_self:
		try:
			query_idx = map_word_to_idx[element]
			query_self.append(query_idx)

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
	print(len(set_neighbor))
	print(len(set_self))

	print(len(set_neighbor.intersection(set_self)))
	print(len(set_neighbor.union(set_self)))
	jacard_score = len(set_neighbor.intersection(set_self)) / len(set_neighbor.union(set_self))

	print(jacard_score)



def get_tfidf_values(word):

	datapath = constants.TFIDF_DIR
	tfidf_values = [] 

	tileid = '2013_d307_11_602_1276'
	tilename = 'tfidf_eightdays_' + tileid


	try: 
		query_idx = map_word_to_idx[word]
		print(query_idx)

		try: 
			with open(datapath + tilename, 'r', encoding = 'UTF8') as f: 
				print('a')
				lines = f.readlines()
				for line in lines: 
					v = line.split('\t')
					temp_word_idx = v[0]
					if int(temp_word_idx) == int(query_idx): 
						print(temp_word_idx)
						for i in range(2,9):
							tfidf_values.append(float(v[i]))
						break 
		except FileNotFoundError as fe: 
			tfidf_values = [] 
			print('not found')
	except KeyError as ke: 
		tfidf_values = [] 

	return tfidf_values


temp = get_tfidf_values('ytma')
print(temp)

#compute_jacard_score(12, 1208, 2555, 2013, 307, 4)
#temp = read_all_file()
#print(temp)

