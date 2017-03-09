# -*- coding: utf-8 -*-
import io, sys, os
sys.path.insert(0, '../')
import operator
import constants
import collections
import operator
import pymongo
import time
from nltk import PorterStemmer
import logging, logging.config

logging.config.fileConfig('logging.conf')

porter_stemmer=PorterStemmer()

do_stemming = False

conn = pymongo.MongoClient("localhost", 27017)

arglen = len(sys.argv)
if arglen != 4:
	print("Usage: python create_voca.py [rawdata_db_name] [collection_name] [vocabulary_file]")
	print("For example, python create_voca.py test_rawdata_140130 SALT_DB_140130 ./voca/voca_140130")
	exit(0)

logging.info('Run create_voca.py %s %s %s', sys.argv[1], sys.argv[2], sys.argv[3])

module_name = sys.argv[0]
rawdata_db_name = sys.argv[1]
collection_name = sys.argv[2]
vocabulary_filename = sys.argv[3]

if not os.path.exists('./voca/'):
    os.makedirs('./voca/')

if os.path.exists(vocabulary_filename) is True:
	logging.info('The Vocabulary file(%s) is already exist. Exit %s.', vocabulary_filename, module_name)
	exit(1)

rawdata_db = conn[rawdata_db_name]
rawdata_col = rawdata_db[collection_name]

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

stop_list = set()
f_stop = io.open('english.stop')
for line in f_stop:
	stop_list.add(line[0:-1])
f_stop.close()

f_slang_stop=io.open('slangword', encoding='utf-8')
for line in f_slang_stop:
	stop_list.add(line[0:-1])
f_slang_stop.close()

stemmed_words_one=collections.OrderedDict()
stem_bag_words=collections.OrderedDict()
bag_words = collections.OrderedDict()

# stemming
start_time = time.time()
logging.info('Stemming...')


for doc in rawdata_col.find():
	text = doc['text']
	bag_words_one = read_txt(text)
	stemmed_words_one = stem_read_txt(text)

	for s_word in stemmed_words_one:

		if s_word in stop_list:
			continue

		if s_word not in stem_bag_words:
			stem_bag_words[s_word]=collections.OrderedDict()

	for word in bag_words_one:

		s_word = porter_stemmer.stem(word)
		
		if s_word in stop_list:
			continue

		if word in stop_list:
			continue

		if word not in stem_bag_words[s_word]:
			stem_bag_words[s_word][word] = bag_words_one[word]
		else:
			stem_bag_words[s_word][word] += bag_words_one[word]

		try:
			bag_words[s_word] += bag_words_one[word]
		except KeyError:
			bag_words[s_word] = bag_words_one[word]

elapsed_time = time.time() - start_time
logging.info('Done: Stemming. Execution time: %.3fs', elapsed_time)

voca_file = open(vocabulary_filename, 'w', encoding='UTF8')
voca_hash_file = open(vocabulary_filename+'_hash', 'w', encoding='UTF8')

for word in sorted(bag_words):

	if bag_words[word] < constants.MIN_WORD_FREQUENCY:
		continue

	voca_file.write(word + '\t' + str(bag_words[word]) + '\n')
	
	for each in sorted(stem_bag_words[word], key=stem_bag_words[word].get, reverse=True):
		voca_hash_file.write(word + '\t' + each + '\t' + str(stem_bag_words[word][each]) + '\n')

voca_file.close()
voca_hash_file.close()