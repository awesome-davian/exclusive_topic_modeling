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

logging.config.fileConfig('logging.conf')

porter_stemmer=PorterStemmer();

do_stemming = False

conn = pymongo.MongoClient("localhost", 27017)

#dbname = sys.argv[1]
dbname = constants.DB_NAME;
db = conn[dbname]

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

def get_next_sequence_value(sequence_name):

	db.counters.find_and_modify(
		{'_id':sequence_name}, 
		{'$inc':{'seq':1}}, upsert=True, new=True
	);

	return db.counters.find_one({'_id':sequence_name})['seq']

def clean_up_data():
	if 'vocabulary' in db.collection_names():
		db.drop_collection('vocabulary')
	if 'vocabulary_hashmap' in db.collection_names():
		db.drop_collection('vocabulary_hashmap')

	for col in db.collection_names():
		if col.endswith('_mtx') == True:
			db.drop_collection(col)

	for item in db.counters.find():
		name = item['_id']
		if name.endswith('_mtx') == True:
			db.counters.delete_one({'_id':name})
		if name.startswith('vocabulary') == True:
			db.counters.delete_one({'_id':name})
		if name.startswith('vocabulary_hashmap') == True:
			db.counters.delete_one({'_id':name})

stop_list = set()
f_stop = io.open('english.stop')
for line in f_stop:
	stop_list.add(line[0:-1])
f_stop.close()

f_slang_stop=io.open('slangword')
for line in f_slang_stop:
	stop_list.add(line[0:-1])
f_slang_stop.close()



stemmed_word_one=collections.OrderedDict()
stem_bag_words=collections.OrderedDict()

# clean up stored data
clean_up_data()

col_voca = db['vocabulary']
col_voca_hash = db['vocabulary_hashmap']

for each in col_voca_hash.find():
	stem = each['stem']
	word = each['word']
	count = each['count']

	if stem not in stem_bag_words:
		stem_bag_words[stem] = collections.OrderedDict()
	stem_bag_words[stem][word] = int(count)

# stemming
start_time = time.time()
logging.info('Stemming...')

total_col_size = len(db.collection_names());
idx = 0
for tile_name in db.collection_names():
	idx += 1;
	if tile_name.endswith('_raw') == False:
		logging.info('%s(%d/%d), skip.', tile_name, idx, total_col_size)
		continue;

	start_time_detail = time.time()
	tile = db[tile_name]
	doc_count=0
	for doc in tile.find():
		text = doc['text']
		bag_words_one=read_txt(text)
		stemmed_word_one=stem_read_txt(text)
		for s_word in stemmed_word_one:
			if s_word not in stem_bag_words:
				stem_bag_words[s_word]=collections.OrderedDict()
			for word in bag_words_one:
				if word not in stem_bag_words[s_word]:
					stem_bag_words[s_word][word]=0
				if s_word==porter_stemmer.stem(word):
				    stem_bag_words[s_word][word]+=bag_words_one[word]
		doc_count+=1
	elapsed_time_detail = time.time() - start_time_detail
	logging.info('%s(%d/%d), doc_count: %d, stemming complete. elapsed: %.3fms', tile_name, idx, total_col_size, tile.count(), elapsed_time_detail)

elapsed_time = time.time() - start_time
logging.info('Done: Stemming. Execution time: %.3fms', elapsed_time)

# create the vocabulary collection
start_time = time.time()
logging.info('Creating the vocabulary collection...')
word_map =collections.OrderedDict()
count=0
for stem in stem_bag_words:
	if stem in stop_list:
		continue
	tot_num=0
	for word in stem_bag_words[stem]:
		if stem==porter_stemmer.stem(word):
			tot_num+=stem_bag_words[stem][word]
			col_voca_hash.insert({'_id': get_next_sequence_value('vocabulary_hashmap'), 'stem':stem, 'word':word, 'count':stem_bag_words[stem][word]});
	col_voca.insert({'_id': get_next_sequence_value('vocabulary'), 'stem':stem, 'count':tot_num})
	word_map[stem]=count
	count +=1
elapsed_time = time.time() - start_time
logging.info('Done: Creating the vocabulary collections. Execution time: %.3fms', elapsed_time)

# creating term-document frequency matrix
start_time = time.time()
logging.info('Creating the term-document matrix...')
idx = 0
for tile_name in db.collection_names():

	idx += 1;
	if tile_name.endswith('_raw') == False:
		logging.info('%s(%d/%d), skip', tile_name, idx, total_col_size)
		continue

	tile = db[tile_name]

	tile_mtx_name = tile_name.replace('_raw', '')+'_mtx'
	tile_mtx = db[tile_mtx_name]

	word_map_tot_len = len(word_map)

	start_time_detail = time.time()
	for doc in tile.find({},no_cursor_timeout=True):
		text = doc['text']
		bag_words_one = read_txt(text)
		for word in bag_words_one:
			s_word=porter_stemmer.stem(word)
			w = col_voca.find_one({'stem':s_word})
			if w != None:
				word_idx = w['_id']
				tile_mtx.insert({'_id': get_next_sequence_value(tile_mtx_name), 'term_idx': word_idx, 'doc_idx': doc['_id'], 'freq': bag_words_one[word]})

	elapsed_time_detail = time.time() - start_time_detail
	logging.info('%s(%d/%d), creating the term-document matrix complete. elapsed: %.3fms', tile_name, idx, total_col_size, elapsed_time_detail)		
elapsed_time = time.time() - start_time
logging.info('Done: Creating the term-document frequency matrix. Execution time: %.3fms', elapsed_time)



