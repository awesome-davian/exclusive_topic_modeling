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

def doPipelinedNMF(pi, task_manager):

	if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF()', pi)

	while(True):
		
		task, is_done = task_manager.get_task(pi)
		if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF() - start task, %s, %s', pi, task.state, is_done)
		if is_done == True:
			break

		if task.state == State.NONE.value:
			time.sleep(0.5)
			continue

		if task.state == State.INIT.value:
			task.run_rank2_nmf(pi)
			#time.sleep(0.1)
			if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF() - INIT, %s, %s', pi, task.state, is_done)
			
		elif task.state == State.STD_COMPLETE.value:
			if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF() - STD_COMPLETE - start, %s, %s', pi, task.state, is_done)
			if task_manager.is_neighbor_ready(pi, task.tile):
				task.run_hier8_neat(pi)
				#time.sleep(0.1)
			else:
				task.put_task(pi, task)
			
		elif task.state == State.EX_COMPLETE.value:
			if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF() - EX_COMPLETE, %s, %s', pi, task.state, is_done)
		
		task_manager.end_task(pi, task)
		
		if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF() - done task, %s, %s', pi, task.state, is_done)
	
	if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF() - All done', pi)

	return


logging.config.fileConfig('logging.conf')

arglen = len(sys.argv)
if arglen != 3:
	print("Usage: python run_nmf_pipelined.py [mtx_dir] [w_dir]")
	print("For example, python run_nmf_pipelined.py ./data/131103-131105/mtx/ ./data/131103-131105/w/")
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
#State = Enum('State', 'INIT_STATE STD_INPROGRESS STD_COMPLETE EX_INPROGRESS EX_COMPLETE')

class Task(object):
	def __init__(self, tile, state):
		self.tile = tile
		self.state = state
		return

	def __eq__(self, other):
		return self.state == other.state

	def __lt__(self, other):
		return self.state < other.state

	def __gt__(self, other):
		return self.state > other.state

	def inc(self):
		self.state += 1
		return self

	def run_rank2_nmf(self, pi):
		
		filepath = dirpath + self.tile
		if print_all == True or pi == 1: logging.debug('filepath: %s', filepath)

		# get mtx
		mtx = []
		line_cnt = 0
		with open(filepath, "r") as f:
			for line in f.readlines():
				v = line.strip().split('\t')

				if line_cnt == 0:
					if print_all == True or pi == 1: logging.debug('[%d] v: %s', pi, v)

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
		w_element = self.tile.replace('mtx_','w_')
		w_element = self.tile.replace('mtx','w')
		#filepath_w = dirpath_w + w_element


		with open(w_element, 'w', encoding='UTF8') as f:
			for line in W:
				str1 = ''.join(str(e)+'\t' for e in line)
				f.write(str1+'\n')
		#logging.debug('done rank2')

		
		if print_all == True or pi == 1: logging.debug('[%d] run_rank2_nmf() - End', pi)

		return

	def run_hier8_neat(self, pi):

		dirpath_w = os.path.abspath(w_dir)
	
		w_element = self.tile.replace('mtx_','w_')
		w_element = self.tile.replace('mtx','w')
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
				if line_cnt == 0:
					if print_all == True or pi == 1: logging.debug('[%d] v: %s', pi, v)
				item = np.array([float(v[0]), float(v[1])], dtype=np.double)
				W = np.append(W, item, axis=0)
				line_cnt += 1
		
		W = np.array(W, dtype=np.double).reshape(line_cnt, 2)
		W_2 = np.array(W, dtype=np.double).reshape(line_cnt, 2)
		W_3 = np.array(W, dtype=np.double).reshape(line_cnt, 2)

		W_tot = np.concatenate((W,W_2,W_3), axis = 1)
		logging.debug(np.shape(W_tot))
		

		k_value = 8

		filepath = dirpath + self.tile
		if print_all == True or pi == 1: logging.debug('filepath: %s', filepath)
		# get mtx

		logging.debug(filepath)

		mtx = []
		line_cnt = 0
		with open(filepath, "r") as f:
			for line in f.readlines():
				v = line.strip().split('\t')

				if line_cnt == 0:
					if print_all == True or pi == 1: logging.debug('v: %s', v)

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


class TaskManager:

	def __init__(self, num_thread, tiles):
		
		self.tiles = collections.OrderedDict()
		self.work_queue = queue.PriorityQueue()
		self.num_tiles = len(tiles)
		self.num_std_done = 0
		self.is_done = False
		self.idx = 0

		with mutex:
			for tile in tiles:
				tile_id = tile.strip().split('/')[-1]
				self.tiles[tile_id] = collections.OrderedDict()
				self.tiles[tile_id]['LEFT'] = 0
				self.tiles[tile_id]['RIGHT'] = 0
				self.tiles[tile_id]['UP'] = 0
				self.tiles[tile_id]['DOWN'] = 0
				self.tiles[tile_id]['STATE'] = State.INIT.value

				task = Task(tile, State.INIT.value)
				self.work_queue.put(task)

		self.set_neighbor()
			
		return

	def get_task(self, pi):
		
		with mutex:
			if not self.work_queue.empty():
				self.idx += 1
				# logging.debug('get_task, idx: %d', self.idx)
				return self.work_queue.get(), False
			else:
				if self.is_done == True:
					return Task('', State.NONE.value), True
				else:
					return Task('', State.NONE.value), False

	def put_task(self, pi, task):
		with mutex:	
			self.work_queue.put(task)

	def end_task(self, pi, task):

		if print_all == True or pi == 1: logging.debug('[%d] end_task() - IN, %s', pi, task.state)

		new_task = task.inc()
		
		tile_id = task.tile.strip().split('/')[-1]

		with mutex:
			self.tiles[tile_id]['STATE'] = new_task.state

		# Put new task in the workerqueue
		# logging.debug('new_task.state: %d', new_task.state)
		if new_task.state <= State.EX_COMPLETE.value:
			if new_task.state == State.STD_COMPLETE.value:
				self.num_std_done += 1
			with mutex:
				# logging.debug('before size: %d', self.work_queue.qsize())
				self.work_queue.put(new_task)
				#logging.debug('after size: %d', self.work_queue.qsize())

		if self.num_std_done == self.num_tiles:
			self.is_done = True

		if print_all == True or pi == 1: logging.debug('[%d] end_task() - 2, %s', pi, task.state)

		return

	def set_neighbor(self):

		with mutex:
			for tile, value in self.tiles.items():

				neighbor = 0

				t = tile.split('_')

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
				
				if left in self.tiles:
					self.tiles[tile]['LEFT'] = 1
				if right in self.tiles:
					self.tiles[tile]['RIGHT'] = 1
				if up in self.tiles:
					self.tiles[tile]['UP'] = 1
				if down in self.tiles:
					self.tiles[tile]['DOWN'] = 1
		return

	def is_neighbor_ready(self, pi, tile):

		if print_all == True or pi == 1: logging.debug('[%d] is_neighbor_ready() - IN, %s', pi, tile)

		tile_id = tile.strip().split('/')[-1]
		if print_all == True or pi == 1: logging.debug('[%d] tile id: %s', pi, tile_id)
		t = tile_id.strip().split('_')
		if print_all == True or pi == 1: logging.debug('[%d] t: %s', pi, t)

		pre = t[0]
		year = t[1]
		yday = t[2]
		lv = t[3]
		x = int(t[4])
		y = int(t[5])

		left  = str(pre) + '_' + str(year) + '_' + str(yday) + '_' + str(lv) + '_' + str(x-1) + '_' + str(y)
		right = str(pre) + '_' + str(year) + '_' + str(yday) + '_' + str(lv) + '_' + str(x+1) + '_' + str(y)
		up   = str(pre) + '_' + str(year) + '_' + str(yday) + '_' + str(lv) + '_' + str(x) + '_' + str(y-1)
		down  = str(pre) + '_' + str(year) + '_' + str(yday) + '_' + str(lv) + '_' + str(x) + '_' + str(y+1)
		
		if left in self.tiles and self.tiles[left]['STATE'] < State.STD_COMPLETE.value:
			return False
		if right in self.tiles and self.tiles[right]['STATE'] < State.STD_COMPLETE.value:
			return False
		if up in self.tiles and self.tiles[up]['STATE'] < State.STD_COMPLETE.value:
			return False
		if down in self.tiles and self.tiles[down]['STATE'] < State.STD_COMPLETE.value:
			return False

		return True

class MultiProcessingManager(m.BaseManager):
	pass

def main():

	# creating term-document frequency matrix
	start_time = time.time()
	logging.info('Run NMF...')

	# make a generator for all file paths within dirpath
	dirpath = os.path.abspath(mtx_dir)

	all_files = ( os.path.join(basedir, filename) for basedir, dirs, files in os.walk(dirpath) for filename in files   )
	tiles = sorted(all_files, key=os.path.getsize, reverse=True)	

	logging.debug('# of tiles: %d', len(tiles))

	MultiProcessingManager.register("TaskManager", TaskManager)

	manager = MultiProcessingManager()
	manager.start()

	tm = manager.TaskManager(num_thread, tiles)

	with concurrent.futures.ProcessPoolExecutor(max_workers = num_thread) as exe:
		logging.info('pipelined_topic_modeling - parallel operation is ready')

		fs = {exe.submit(doPipelinedNMF, idx, tm) for idx in range(0, num_thread)}

		logging.info('pipelined_topic_modeling - start parallel operation')
		done, _ = concurrent.futures.wait(fs)
		logging.info('pipelined_topic_modeling - parallel operation finished')


	elapsed_time = time.time() - start_time

	logging.info('Done: Creating the total term-document frequency matrix. Execution time: %.3fs', elapsed_time)

if __name__ == '__main__':
    main()
