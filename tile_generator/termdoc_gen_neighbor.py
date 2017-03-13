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
from os import walk

logging.config.fileConfig('logging.conf')

porter_stemmer=PorterStemmer()

do_stemming = False

conn = pymongo.MongoClient("localhost", 27017)

arglen = len(sys.argv)
if arglen != 3:
	print("Usage: python termdoc_gen_neighbor.py [mtx_dir(IN)] [neighbor_mtx_dir(OUT)]")
	print("For example, python termdoc_gen_neighbor.py ./mtx/130910/ ./mtx_neighbor/130910/")
	exit(0)

module_name = sys.argv[0]
mtx_dir = sys.argv[1]
neighbor_dir = sys.argv[2]

if not os.path.exists(mtx_dir):
	logging.info('The Term-Doc. Matrix Directory(%s) is not exist. Exit %s.', mtx_dir, module_name)
	exit(0)

if os.path.exists(neighbor_dir):
	logging.info('The Neighbor Term-Doc. Matrix Directory(%s) is Already exist. Exit %s.', neighbor_dir, module_name)
	exit(0)	
else:
	os.makedirs(neighbor_dir)



def get_neighbor_mtx(mtx):

	v = mtx.split('_')	# [0]: mtx, [1]: year, [2]: day_of_year, [3]: level, [4]: x, [5]: y

	x = int(v[4])
	y = int(v[5])

	pos = v[4]+'_'+v[5]

	neighbor = []

	temp_name = mtx.replace(pos, '')
	neighbor.append(temp_name+str(x+0)+'_'+str(y+0)) # it's me
	
	neighbor.append(temp_name+str(x+1)+'_'+str(y+1))
	neighbor.append(temp_name+str(x+1)+'_'+str(y+0))
	neighbor.append(temp_name+str(x+1)+'_'+str(y-1))
	neighbor.append(temp_name+str(x+0)+'_'+str(y+1))

	neighbor.append(temp_name+str(x+0)+'_'+str(y-1))
	neighbor.append(temp_name+str(x-1)+'_'+str(y+1))
	neighbor.append(temp_name+str(x-1)+'_'+str(y+0))
	neighbor.append(temp_name+str(x-1)+'_'+str(y-1))

	neighbor_mtx = []

	for idx, each in enumerate(neighbor):
		each_path = mtx_dir + each
		if os.path.exists(each_path) == False:
			continue

		with open(each_path) as each_file:

			for line in each_file:
				line = line.strip()
				v = line.split('\t')
				neighbor_mtx.append([int(v[0]), int(v[1]), int(v[2]), idx])

	return neighbor_mtx

_, _, filenames = next(walk(mtx_dir), (None, None, []))
tile_size = len(filenames)
for idx, mtx in enumerate(filenames):

	logging.info('[%d/%d]Create the Local Term-Doc-Mtx: %s', idx+1, tile_size, mtx)

	# get neighbor mtx
	mtx_neighbor = get_neighbor_mtx(mtx)

	new_bag_words = collections.OrderedDict()
	new_bag_words_doc = collections.OrderedDict()
	new_bag_docs = collections.OrderedDict()

	new_word_map = collections.OrderedDict()
	new_doc_map = collections.OrderedDict()

	new_mtx_me = []
	new_mtx_neighbor = []
	
	# create new bag of words
	for line in mtx_neighbor:

		# logging.debug('%d\t%d\t%d', line[0], line[1], line[2])

		try:
			new_bag_words[line[0]] += line[2]
		except KeyError:
			new_bag_words[line[0]] = line[2]

		try:
			new_bag_words_doc[line[0]] += 1
		except KeyError:
			new_bag_words_doc[line[0]] = 1
			
		new_bag_docs[line[1]] = 1

	# create new voca and word map
	local_voca_file_name = mtx.replace('mtx', 'voca')
	local_voca_file = open(neighbor_dir+local_voca_file_name, 'w', encoding='UTF8')

	idx = 1
	for word_idx_ori in sorted(new_bag_words):

		if new_bag_words_doc[word_idx_ori] < constants.MIN_WORD_FREQUENCY:
			continue

		# logging.debug('word_idx_ori: %s', str(word_idx_ori))
		# logging.debug('new_bag_words[%s]: %s', str(word_idx_ori), str(new_bag_words[word_idx_ori]))
		local_voca_file.write(str(word_idx_ori) + '\t' + str(new_bag_words[word_idx_ori]) + '\n')

		new_word_map[word_idx_ori] = idx
		idx += 1

	local_voca_file.close()

	local_doc_map_name = mtx.replace('mtx', 'docmap')
	local_doc_file = open(neighbor_dir+local_doc_map_name, 'w', encoding='UTF8')
	idx = 1
	for doc_idx_ori in sorted(new_bag_docs):

		local_doc_file.write(str(doc_idx_ori) + '\n')
		new_doc_map[doc_idx_ori] = idx
		idx += 1

	local_doc_file.close()

	# create new term-doc matrix
	# mtx_neighbor_name = mtx.replace('mtx', 'nmtx')
	# mtx_me_file = open(neighbor_dir+mtx, 'w', encoding='UTF8')
	# mtx_neighbor_file = open(neighbor_dir+mtx_neighbor_name, 'w', encoding='UTF8')

	for each in mtx_neighbor:
		try:
			with open(neighbor_dir+mtx, 'a', encoding='UTF8') as f:
				f.write(str(new_word_map[each[0]]) + '\t' + str(new_doc_map[each[1]]) + '\t' + str(each[2]) + '\t' + str(each[3]) + '\n')
		except KeyError:
			continue;

		# if len(each) != 3:
		# 	try:
		# 		new_mtx_me.append([new_word_map[each[0]], new_doc_map[each[1]], each[2]])
		# 		mtx_me_file.write(str(new_word_map[each[0]]) + '\t' + str(new_doc_map[each[1]]) + '\t' + str(each[2]) + '\n')
		# 	except KeyError:
		# 		continue
		# else:
		# 	try:
		# 		new_mtx_neighbor.append([new_word_map[each[0]], new_doc_map[each[1]], each[2]])
		# 		mtx_neighbor_file.write(str(new_word_map[each[0]]) + '\t' + str(new_doc_map[each[1]]) + '\t' + str(each[2]) + '\n')
		# 	except KeyError:
		# 		continue

	# mtx_neighbor_file.close()
	# mtx_me_file.close()