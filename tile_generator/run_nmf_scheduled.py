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
import multiprocessing.managers as m
import math

import queue

def doStandardNMF(pi, tile_instance):

	# logging.debug('[%d] doParWord(%d, %d): %s', pi, len(l[idx]), num_thread, l[idx][0])
	#logging.debug('[%d] doParWord(%d)', pi, num_thread)

	# tile = tile_instance.get_tile(pi)

	# logging.debug('[%d] tile: %s', pi, tile)

	while(True):
		tile = tile_instance.get_tile()
		
		if tile == None:
			break

		logging.debug('[%d]tile: %s', pi, tile)
		time.sleep(0.1)
	

	# do nmf
	
	return

def doExNMF(pi, tile_instance):

	while(True):
		tile = tile_instance.get_tile()
		
		if tile == None:
			break

		logging.debug('[%d]tile: %s', pi, tile)
		time.sleep(0.1)

	return

def get_files_in_dir(dirname, sort_key, reverse):

	# usage: get_files_in_dir('.', os.path.getsize')
	
	dirpath = os.path.abspath(dirname)

	# make a generator for all file paths within dirpath
	all_files = ( os.path.join(basedir, filename) for basedir, dirs, files in os.walk(dirpath) for filename in files   )

	sorted_files = sorted(all_files, key=sort_key, reverse=reverse)

	# make a generator for tuples of file path and size: ('/Path/to/the.file', 1024)
	# files_and_sizes = ( (path, os.path.getsize(path)) for path in all_files )
	# sorted_files_with_size = sorted( files_and_sizes, key = operator.itemgetter(1) )

	return sorted_files


def divide_list(l, mx):
	
	sl = []
	for i in range(0, mx):
		sl.append([])

	for idx, each in enumerate(l):
		# logging.debug('%s --> %d', each, idx%mx)
		sl[idx%mx].append(each)

	return sl

logging.config.fileConfig('logging.conf')

arglen = len(sys.argv)
if arglen != 3:
	print("Usage: python run_nmf.py [mtx_dir] [w_dir]")
	print("For example, python run_nmf.py ./data/131103-131105/mtx/ ./data/131103-131105/w/")
	exit(0)

module_name = sys.argv[0]
mtx_dir = sys.argv[1]
w_dir = sys.argv[2]

if not os.path.exists(w_dir):
    os.makedirs(w_dir)
else:
	logging.info('The W Matrix Directory(%s) is already exist. Exit %s.', w_dir, module_name)
	exit(1)

num_thread = 40

l = get_files_in_dir(mtx_dir, os.path.getsize, True)
sl = divide_list(l, num_thread)

class TileManager:
	def __init__(self, num_thread):
		self.text = 'helloworld'
		self.tiles = queue.Queue()
		self.num_thread = num_thread

		return

	def add_tile(self, tilename):
		# self.tiles.append(tilename)
		self.tiles.put(tilename)

	def get_tile(self):
		# return self.tiles[pid]

		# possible to occur the timing issue...
		if self.tiles.empty():
			return None
		else:
			return self.tiles.get()


class MultiProcessingManager(m.BaseManager):
	pass


def main():

	# creating term-document frequency matrix
	start_time = time.time()
	logging.info('Run NMF...')

	MultiProcessingManager.register("TileManager", TileManager)

	manager = MultiProcessingManager()
	manager.start()

	t = manager.TileManager(num_thread)

	# make a generator for all file paths within dirpath
	dirpath = os.path.abspath(mtx_dir)
	all_files = ( os.path.join(basedir, filename) for basedir, dirs, files in os.walk(dirpath) for filename in files   )
	sorted_files = sorted(all_files, key=os.path.getsize, reverse=True)

	for each in sorted_files:
		t.add_tile(each)

	with concurrent.futures.ProcessPoolExecutor(max_workers = num_thread) as exe:
		logging.info('standard_nmf - 1')

		fs = {exe.submit(doStandardNMF, idx, t) for idx in range(0, num_thread)}

		logging.info('standard_nmf - 2')
		done, _ = concurrent.futures.wait(fs)
		logging.info('standard_nmf - 3')

	for each in sorted_files:
		t.add_tile(each)

	with concurrent.futures.ProcessPoolExecutor(max_workers = num_thread) as exe:
		logging.info('ex_nmf - 1')

		fs = {exe.submit(doExNMF, idx, t) for idx in range(0, num_thread)}

		logging.info('ex_nmf - 2')
		done, _ = concurrent.futures.wait(fs)
		logging.info('ex_nmf - 3')


	elapsed_time = time.time() - start_time

	logging.info('Done: Creating the total term-document frequency matrix. Execution time: %.3fs', elapsed_time)

if __name__ == '__main__':
    main()
