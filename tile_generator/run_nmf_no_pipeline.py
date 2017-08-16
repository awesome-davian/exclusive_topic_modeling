# -*- coding: utf-8 -*-
import io, sys, os
sys.path.insert(0, '../')
import constants
import collections
import operator
import time
import logging, logging.config
from datetime import datetime 
import concurrent.futures
from multiprocessing import Lock
import multiprocessing.managers as m
import math
import shutil
import numpy as np

import queue
from enum import Enum
from hier8_net import Hier8_net
from scipy import sparse


print_all = False

logging.config.fileConfig('logging.conf')

arglen = len(sys.argv)
if arglen != 3:
	print("Usage: python run_nmf_pipelined.py [mtx_dir] [w_dir]")
	print("For example, python run_nmf_no_pipeline.py ./data_test/131103-131105/mtx/ ./data_test/131103-131105/w/")
	exit(0)

module_name = sys.argv[0]
mtx_dir = sys.argv[1]
w_dir = sys.argv[2]

if not os.path.exists(w_dir):
    os.makedirs(w_dir)
else:
	# logging.info('The W Matrix Directory(%s) is already exist. Do you want to continue? The W matrix will be replaced. (Yes/No)', w_dir)
	user_input = input('The W Matrix Directory is already exist. Do you want to continue? The W matrix will be replaced. (Yes/no): ')
	if user_input.strip().lower() == 'no' or user_input.strip().lower() == 'n':
		exit(1)
	else:
		shutil.rmtree(w_dir)
		os.makedirs(w_dir)
		pass

dirpath = ""
num_thread = 40

mutex = Lock()

State = Enum('State', 'INIT STD_COMPLETE EX_COMPLETE NONE')

#State = Enum('State', 'INIT_STATE STD_INPROGRESS STD_COMPLETE EX

class Process():
	def __init__(self):
		return

	def run_rank2_nmf(tile):
		
		filepath = tile
		#if print_all == True or pi == 1: logging.debug('filepath: %s', filepath)

		# get mtx
		logging.debug(filepath)
		mtx = []
		line_cnt = 0
		with open(filepath, "r") as f:
			for line in f.readlines():
				v = line.strip().split('\t')

				# if line_cnt == 0:
				# 	if print_all == True or pi == 1: logging.debug('[%d] v: %s', pi, v)

				item = np.array([float(v[0]), float(v[1]), float(v[2])], dtype=np.double)
				mtx = np.append(mtx, item, axis=0)
				line_cnt += 1

				# This is just for quick test.
				# break

		mtx = np.array(mtx, dtype=np.double).reshape(line_cnt, 3)


		# do nmf here
		A = sparse.csr_matrix((mtx[:,2], (mtx[:,0], mtx[:,1])), shape=(int(mtx[:,0].max(0)+1), int(mtx[:,1].max(0)+1)))
		m = np.shape(A)[0]
		n = np.shape(A)[1]

		W_org = np.random.rand(m,2)
		H_org = np.random.rand(n,2)

		#logging.debug(np.shape(A))
		#logging.debug(filepath)
		# logging.debug(np.shape(W))
		# logging.debug(np.shape(H))

		W, H = Hier8_net().nmfsh_comb_rank2(A, W_org, H_org,100)
		
		W = np.array(W)

		logging.debug(np.shape(W))

		#dirpath_w = os.path.abspath(w_dir)
		w_element =tile.replace('mtx_','w_')
		w_element =tile.replace('mtx','w')
		#filepath_w = dirpath_w + w_element


		with open(w_element, 'w', encoding='UTF8') as f:
			for line in W:
				str1 = ''.join(str(e)+'\t' for e in line)
				f.write(str1+'\n')
		#logging.debug('done rank2')

		
		#if print_all == True or pi == 1: logging.debug('[%d] run_rank2_nmf() - End', pi)

		return

	def run_hier8_neat( tile):

		dirpath_w = os.path.abspath(w_dir)
	
		w_element = tile.replace('mtx_','w_')
		w_element = tile.replace('mtx','w')
		logging.debug('start next process')

		tile_idx = w_element.split('/')[10]
		#logging.debug(tile_idx)
		t = tile_idx.split('_')

		pre = t[0]
		year = t[1]
		yday = t[2]
		lv = t[3]
		x = int(t[4])
		y = int(t[5])

		# left:right:top:bottom neighbor
		left  = str(pre) + '_' + str(year) + '_' + str(yday) + '_' + str(lv) + '_' + str(x-1) + '_' + str(y)
		right  = str(pre) + '_' + str(year) + '_' + str(yday) + '_' + str(lv) + '_' + str(x+1) + '_' + str(y)
		up  = str(pre) + '_' + str(year) + '_' + str(yday) + '_' + str(lv) + '_' + str(x) + '_' + str(y-1)
		down  = str(pre) + '_' + str(year) + '_' + str(yday) + '_' + str(lv) + '_' + str(x) + '_' + str(y+1)

		w_element_left = dirpath_w + str('/')+str(left)
		w_element_right = dirpath_w+ str('/')+str(right)
		w_element_up = dirpath_w + str('/')+str(up)
		w_element_down = dirpath_w + str('/')+str(down)


		W = []
		line_cnt = 0
		with open(w_element, "r") as f:
			for line in f.readlines():
				v = line.strip().split('\t')
				# if line_cnt == 0:
				# 	if print_all == True or pi == 1: logging.debug('[%d] v: %s', pi, v)
				item = np.array([float(v[0]), float(v[1])], dtype=np.double)
				W = np.append(W, item, axis=0)
				line_cnt += 1
		
		W = np.array(W, dtype=np.double).reshape(line_cnt, 2)
		W_2 = np.array(W, dtype=np.double).reshape(line_cnt, 2)
		W_3 = np.array(W, dtype=np.double).reshape(line_cnt, 2)

		W_tot = np.concatenate((W,W_2,W_3), axis = 1)
		logging.debug(np.shape(W_tot))
		

		k_value = 8

		filepath = tile
		#if print_all == True or pi == 1: logging.debug('filepath: %s', filepath)
		# get mtx

		logging.debug(filepath)

		mtx = []
		line_cnt = 0
		with open(filepath, "r") as f:
			for line in f.readlines():
				v = line.strip().split('\t')

				# if line_cnt == 0:
				# 	if print_all == True or pi == 1: logging.debug('v: %s', v)

				item = np.array([float(v[0]), float(v[1]), float(v[2])], dtype=np.double)
				mtx = np.append(mtx, item, axis=0)
				line_cnt += 1

		mtx = np.array(mtx, dtype=np.double).reshape(line_cnt, 3)
		logging.debug(np.shape(mtx))

		A = sparse.csr_matrix((mtx[:,2], (mtx[:,0], mtx[:,1])), shape=(int(mtx[:,0].max(0)+1), int(mtx[:,1].max(0)+1)))
		#logging.debug(np.shape(A))
		#At = A * 0.8

		W_final = Hier8_net().hier8_net(A, 4, 100)
		logging.debug(np.shape(W_final))

		return


def main():

	# creating term-document frequency matrix
	start_time = time.time()
	logging.info('Run NMF...')

	# make a generator for all file paths within dirpath
	dirpath = os.path.abspath(mtx_dir)

	all_files = ( os.path.join(basedir, filename) for basedir, dirs, files in os.walk(dirpath) for filename in files   )
	tiles = sorted(all_files, key=os.path.getsize, reverse=True)	

	logging.debug('# of tiles: %d', len(tiles))

	for tile in tiles: 
		Process.run_rank2_nmf(tile)

	for tile in tiles: 
		Process.run_hier8_neat(tile)






	elapsed_time = time.time() - start_time

	logging.info('Done: Creating the total term-document frequency matrix. Execution time: %.3fs', elapsed_time)

if __name__ == '__main__':
    main()
