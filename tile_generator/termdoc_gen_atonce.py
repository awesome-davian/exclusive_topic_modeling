# -*- coding: utf-8 -*-
import io, sys, os
sys.path.insert(0, '../')
import constants
import collections
import operator
import pymongo
import time
from nltk import PorterStemmer
import logging, logging.config
import math
from datetime import datetime 

logging.config.fileConfig('logging.conf')

porter_stemmer=PorterStemmer()

do_stemming = False

conn = pymongo.MongoClient("localhost", 27017)

arglen = len(sys.argv)
if arglen != 5:
	print("Usage: python termdoc_gen_atonce.py [vocabulary_filename] [rawdata_db_name] [rawdata_db_collection_name] [mtx_dir]")
	print("For example, python termdoc_gen_atonce.py voca_140130 test_rawdata_140130 SALT_DB_140130 ./mtx/")
	exit(0)

module_name = sys.argv[0]
vocabulary_filename = sys.argv[1]
rawdata_db_name = sys.argv[2]
rawdata_col_name = sys.argv[3]
mtx_dir = sys.argv[4]

rawdata_db = conn[rawdata_db_name]
rawdata_col = rawdata_db[rawdata_col_name]

if not os.path.exists(mtx_dir):
    os.makedirs(mtx_dir)
else:
	logging.info('The Term-Doc. Matrix Directory(%s) is already exist. Exit %s.', mtx_dir, module_name)
	exit(1)

def truncate_word(word):
	start = 0
	while start < len(word) and word[start].isalpha() == False:
		start += 1
	end = len(word)
	while end > start and word[end-1].isalpha() == False:
		end -= 1
	truncated = word[start:end].lower()
	for letter in truncated:
		if letter.isalpha():
			break
	else:
		return ''
	if truncated.find('http://') == 0:
		return ''
	if do_stemming == True:
		if len(truncated) == 0:
			return ''
	else:
		return truncated

def tokenization(text):
	if len(text) == 0:
		return
	start_pos = 0
	while start_pos < len(text):
		while start_pos < len(text):
			if text[start_pos].isalpha():
				break
			else:
				start_pos += 1
		end_pos = start_pos
		while end_pos < len(text):
			if text[end_pos].isalpha():
				end_pos += 1
			else:
				break
		word = text[start_pos:end_pos].lower()
		if word.find('urgent') == -1:
			yield text[start_pos:end_pos]
		start_pos = end_pos

def read_txt(text):
	bag_words = collections.OrderedDict()
	for word in tokenization(text):
		truncated = truncate_word(word)
		if truncated != '':
			try:
				bag_words[truncated] += 1
			except KeyError:
				bag_words[truncated] = 1
	return bag_words

def stem_read_txt(text):
	bag_words = collections.OrderedDict()
	for word in tokenization(text):
		truncated = truncate_word(word)
		truncated = porter_stemmer.stem(truncated)

		if truncated != '':
			try:
				bag_words[truncated] += 1
			except KeyError:
				bag_words[truncated] = 1
	return bag_words

def getTwitterDate(date):
	date_format = ''
	if len(date) == 30:
		# date_format = "EEE MMM dd HH:mm:ss ZZZZZ yyyy";
		date_format = "%a %b %d %H:%M:%S %z %Y"
		
	else:
		# date_format = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'";
		date_format = "%Y-%m-%dT%H:%M:%S.000Z"

	return datetime.strptime(date, date_format)

def getMercatorPoint(lon, lat, level):
	latR = math.radians(lat)

	pow2 = 1 << level;
	x = (lon+180.0)/360.0 * pow2;
	y = (1 - math.log(math.tan(latR) + 1 / math.cos(latR)) / math.pi) / 2 * pow2;
	
	return math.floor(x), math.floor(pow2-y);

def readVoca():
	idx = 1
	voca = voca_file.readlines()
	for line in voca:
		v = line.split('\t')
		bag_words[v[0]] = int(v[1])

		word_map[v[0]] = idx

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

stem_bag_words=collections.OrderedDict()
bag_words = collections.OrderedDict()
word_map = collections.OrderedDict()

voca_file = open(vocabulary_filename, 'r', encoding='UTF8')
voca_hash_file = open(vocabulary_filename+'_hash', 'r', encoding='UTF8')

readVoca()

voca_file.close()
voca_hash_file.close()

# creating term-document frequency matrix
start_time = time.time()
logging.info('Creating the term-document matrix...')
idx = 0

time_make_bag_words = 0;
time_find = 0;
time_insert = 0;

mtx_file = open(mtx_dir + 'total_mtx', 'w', encoding='UTF8')
col_size = rawdata_col.count()
for idx, doc in enumerate(rawdata_col.find()):
	text = doc['text']

	s_time_bag_words = time.time()
	bag_words_one = stem_read_txt(text)
	time_make_bag_words += time.time() - s_time_bag_words;

	doc_time = getTwitterDate(doc['created_at'])
	year = doc_time.timetuple().tm_year
	day_of_year = doc_time.timetuple().tm_yday
	
	lon = doc['coordinates']['coordinates'][0]
	lat = doc['coordinates']['coordinates'][1]

	for word in sorted(bag_words_one):
		
		s_time_find = time.time()
		try:
			word_idx = word_map[word]
			time_find += time.time() - s_time_find;

			s_time_insert = time.time()
			mtx_file.write(str(word_idx) + '\t' + str(doc['_id']) + '\t' + str(bag_words_one[word]) + '\n')
			time_insert += time.time() - s_time_insert;

			for level in range(9, 14):

				[x, y] = getMercatorPoint(lon, lat, level)
				tilename = 'mtx_' + str(year) + '_d' + str(day_of_year) + '_' + str(level) + '_' + str(x) + '_' + str(y)

				mtx_tile_file = open(mtx_dir+tilename, 'a', encoding='UTF8')
				mtx_tile_file.write(str(word_idx) + '\t' + str(doc['_id']) + '\t' + str(bag_words_one[word]) + '\n')
				mtx_tile_file.close()

		except KeyError:
			continue

	if ((idx+1) % 10000) == 0:
		logging.info('Creating the term-document matrix... (%d/%d)', idx+1, col_size)

mtx_file.close()

elapsed_time = time.time() - start_time

logging.info('Time to create Term-Doc-Frequency Matrix: %.3fs, Time to find: %.3fs, Time to insert: %.3fs', time_make_bag_words, time_find, time_insert)
logging.info('Done: Creating the total term-document frequency matrix. Execution time: %.3fs', elapsed_time)


