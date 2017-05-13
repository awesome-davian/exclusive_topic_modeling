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

# for creating the term-doc matrix
from nltk import PorterStemmer
import pymongo

import queue
from enum import Enum


print_all = False

def run_rank2_nmf(tileid, k):
	filepath = dirpath + tileid
	if print_all == True or pi == 1: logging.debug('filepath: %s', filepath)

	# get mtx
	mtx = []
	line_cnt = 0
	with open(filepath, "r") as f:
		 for line in f.readlines():
		 	v = line.split('\t')

		 	item = np.array([float(v[0]), float(v[1]), float(v[2])], dtype=np.double)
			mtx = np.append(mtx, item, axis=0)
			line_cnt += 1

	mtx = np.array(mtx, dtype=np.double).reshape(line_cnt, 3)

	# do nmf here


def doPipelinedNMF(pi, task_manager):

	if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF()', pi)

	while(True):
		
		task, is_done = task_manager.get_task()
		if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF() - start task, %s, %s', pi, task.state, is_done)
		if is_done == True:
			break

		if task.state == State.NONE.value:
			time.sleep(0.5)
			continue

		if task.state == State.INIT.value:
			# TODO: Add the rank 2 nmf code here
			run_rank2_nmf(task.tile, 2)
			if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF() - INIT, %s, %s', pi, task.state, is_done)
			time.sleep(0.1)
			
		elif task.state == State.STD.value:
			#TODO: Add the hier 8 nmf code here
			if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF() - STD, %s, %s', pi, task.state, is_done)
			time.sleep(0.1)
			
		elif task.state == State.EX.value:
			#TODO: do nothing
			if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF() - EX, %s, %s', pi, task.state, is_done)
			time.sleep(0.1)
		
		task_manager.end_task(task)
		
		if print_all == True or pi == 1: logging.debug('[%d] doPipelinedNMF() - done task, %s, %s', pi, task.state, is_done)
	
	return


logging.config.fileConfig('logging.conf')

porter_stemmer=PorterStemmer()
do_stemming = False

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

State = Enum('State', 'INIT STD EX NONE')
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

class TaskManager:

	def __init__(self, num_thread, tiles):
		
		self.tile_ids = collections.OrderedDict()
		self.work_queue = queue.PriorityQueue()
		self.num_tiles = len(tiles)
		self.num_std_done = 0
		self.is_done = False
		self.idx = 0

		with mutex:
			for each in tiles:
				task = Task(each, State.INIT.value)
				self.work_queue.put(task)
			
		return

	def get_task(self):
		
		with mutex:
			if not self.work_queue.empty():
				self.idx += 1
				logging.debug('get_task, idx: %d', self.idx)
				return self.work_queue.get(), False
			else:
				if self.is_done == True:
					return Task('', State.NONE.value), True
				else:
					return Task('', State.NONE.value), False

	def end_task(self, task):

		new_task = task.inc()
		# logging.debug('new_task.state: %d', new_task.state)
		if new_task.state <= State.EX.value:
			if new_task.state == State.STD.value:
				self.num_std_done += 1
			with mutex:
				# logging.debug('before size: %d', self.work_queue.qsize())
				self.work_queue.put(new_task)
				#logging.debug('after size: %d', self.work_queue.qsize())

		if self.num_std_done == self.num_tiles:
			self.is_done = True

		return


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
