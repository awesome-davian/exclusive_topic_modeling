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

import queue

def doPipelinedNMF(pi, tile_manager):

	if pi == 1: logging.debug('[%d] doPipelinedNMF()', pi)

	is_std_done = False

	while(True):

		if is_std_done == False:
			
			tile = tile_manager.get_std_tile()
		
			if tile == None:
				is_std_done = True
				continue

			# logging.debug('[%d]tile: %s', pi, tile)
			time.sleep(0.1)

			tile_id = tile.split('/')[-1]

			tile_manager.set_std_done(tile_id)

		else:

			# if pi == 1: logging.debug('[%d] exnmf', pi)

			tile_id, neighbors = tile_manager.get_ex_tile(pi)

			if tile_id == None:
				break

			# if pi == 1: logging.debug('[%d] exnmf end: %s, n: %d', pi, tile_id, neighbors)
			time.sleep(0.1)

			tile_manager.set_ex_done(tile_id)

	# do nmf
	
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

INIT_STATE = 0
STD_INPROGRESS = 1
STD_COMPLETE = 2
EX_INPROGRESS = 3
EX_COMPLETE = 4

l = get_files_in_dir(mtx_dir, os.path.getsize, True)
sl = divide_list(l, num_thread)

mutex = Lock()

class TileManager:
	def __init__(self, num_thread):
		self.tile_ids = collections.OrderedDict()
		self.tiles = queue.Queue()
		self.num_thread = num_thread
		
		return

	def add_tile(self, tilename):
		
		with mutex:
			self.tiles.put(tilename)
		
		tile_id = tilename.split('/')[-1]
		# logging.debug('%s', tile_id)

		with mutex:
			self.tile_ids[tile_id] = INIT_STATE

		# t2 = t1.split('_')
		# year = t2[1]
		# yday = t2[2]
		# level = t2[3]
		# x = t2[4]
		# y = t2[5]

	def get_std_tile(self):

		with mutex:

			if self.tiles.empty():
				return None
			else:
				tile = self.tiles.get()
				tile_id = tile.split('/')[-1]

				# logging.debug('tile_id: %s', tile_id)
				
				self.tile_ids[tile_id] = STD_INPROGRESS

				return tile

	def get_ex_tile(self, pi):

		found = False

		res_tile = ""
		idx = 0

		with mutex:

			for tilename, value in self.tile_ids.items():

				idx += 1

				if value > STD_COMPLETE:
					continue

				# if pi == 1: logging.debug('[%d] idx: %d, tilename: %s, value(status): %s', pi, idx, tilename, value)

				found = False

				t = tilename.split('_')
				pre = t[0]
				year = t[1]
				yday = t[2]
				level = t[3]
				x = int(t[4])
				y = int(t[5])

				neighbors = 0

				# check left
				temp = pre + '_' + year + '_' + yday + '_' + level + '_' + str(x-1) + '_' + str(y)
				if temp in self.tile_ids:
					neighbors = neighbors | 1
					if self.tile_ids[temp] < STD_COMPLETE:
						if pi == 1: logging.debug('[%d]1 %s, n: %d --> continue: %d', pi, temp, neighbors, self.tile_ids[temp])		
						continue

				# check right
				temp = pre + '_' + year + '_' + yday + '_' + level + '_' + str(x+1) + '_' + str(y)
				if temp in self.tile_ids:
					neighbors = neighbors | (1 << 1)
					if self.tile_ids[temp] < STD_COMPLETE:
						if pi == 1: logging.debug('[%d]2 %s, n: %d --> continue: %d', pi, temp, neighbors, self.tile_ids[temp])		
						continue
				
				# check up
				temp = pre + '_' + year + '_' + yday + '_' + level + '_' + str(x) + '_' + str(y-1)
				if temp in self.tile_ids:
					neighbors = neighbors | (1 << 2)
					if self.tile_ids[temp] < STD_COMPLETE:
						if pi == 1: logging.debug('[%d]3 %s, n: %d --> continue: %d', pi, temp, neighbors, self.tile_ids[temp])		
						continue
				
				# check down
				temp = pre + '_' + year + '_' + yday + '_' + level + '_' + str(x) + '_' + str(y+1)
				if temp in self.tile_ids:
					neighbors = neighbors | (1 << 3)
					if self.tile_ids[temp] < STD_COMPLETE:
						if pi == 1: logging.debug('[%d]4 %s, n: %d --> continue: %d', pi, temp, neighbors, self.tile_ids[temp])		
						continue
			
				res_tile = tilename
				found = True
				break

		if found == True:
			self.tile_ids[res_tile] = EX_INPROGRESS
		else:
			res_tile = None

		if pi == 1: logging.debug('[%d] res_tile: %s, idx: %d, neighbor: %d', pi, res_tile, idx, neighbors)		

		return res_tile, neighbors

	def set_std_done(self, tile_id):
		
		with mutex:
			if tile_id in self.tile_ids:
				# logging.debug('set_std_done: %s --> %d', tile_id, STD_COMPLETE)
				self.tile_ids[tile_id] = STD_COMPLETE

	def set_ex_done(self, tile_id):
		with mutex:
			if tile_id in self.tile_ids:
				self.tile_ids[tile_id] = EX_COMPLETE			


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
		logging.info('pipelined_topic_modeling - parallel operation is ready')

		fs = {exe.submit(doPipelinedNMF, idx, t) for idx in range(0, num_thread)}

		logging.info('pipelined_topic_modeling - start parallel operation')
		done, _ = concurrent.futures.wait(fs)
		logging.info('pipelined_topic_modeling - parallel operation finished')


	elapsed_time = time.time() - start_time

	logging.info('Done: Creating the total term-document frequency matrix. Execution time: %.3fs', elapsed_time)

if __name__ == '__main__':
    main()
