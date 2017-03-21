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
	print("For example, python termdoc_gen_neighbor.py ./mtx/130910/ ./data/131103-131105/nmtx/")
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

spatial_ndir = neighbor_dir+'spatial/'
if not os.path.exists(spatial_ndir):
    os.makedirs(spatial_ndir)
temporal_ndir = neighbor_dir+'temporal/'
if not os.path.exists(temporal_ndir):
    os.makedirs(temporal_ndir)

def get_spatial_neighbor_mtx(mtx):

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

def get_temporal_neighbor_mtx(mtx):

	v = mtx.split('_')	# [0]: mtx, [1]: year, [2]: day_of_year, [3]: level, [4]: x, [5]: y

	yday = int(v[2].replace('d',''))

	neighbor_names = []
	for idx in range(0, constants.TEMPORAL_DATE_RANGE):
		neighbor_names.append(v[0]+'_'+v[1]+'_d'+str(yday-idx)+'_'+v[3]+'_'+v[4]+'_'+v[5])
	
	neighbor_mtx = []

	line_cnt = 0
	center_count = 0
	for idx, each in enumerate(neighbor_names):
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

	logging.info('[%d/%d]Create the Neighbor Term-Doc-Mtx: %s', idx+1, tile_size, mtx)

	if mtx.startswith('mtx_') == False:
		continue

	# get neighbor mtx
	mtx_neighbor = get_spatial_neighbor_mtx(mtx)

	for each in mtx_neighbor:
		try:
			with open(spatial_ndir+mtx, 'a', encoding='UTF8') as f:
				f.write(str(each[0]) + '\t' + str(each[1]) + '\t' + str(each[2]) + '\t' + str(each[3]) + '\n')
		except KeyError:
			continue;

	mtx_neighbor = get_temporal_neighbor_mtx(mtx)

	for each in mtx_neighbor:
		try:
			with open(temporal_ndir+mtx, 'a', encoding='UTF8') as f:
				f.write(str(each[0]) + '\t' + str(each[1]) + '\t' + str(each[2]) + '\t' + str(each[3]) + '\n')
		except KeyError:
			continue;	





















