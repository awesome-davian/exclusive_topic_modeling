# -*- coding: utf-8 -*-
import io, sys, os
sys.path.insert(0, '../')
import constants
import collections
import operator
import time
from nltk import PorterStemmer
import logging, logging.config
import math
from datetime import datetime 
import concurrent.futures
import math

def doParWork(pi, l):

	logging.debug('[%d] doParWord(%d, %d)', pi, len(l), num_thread)

	# do nmf
	
	return

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

time_make_bag_words = 0

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

		sl[idx%mx] = each

	return sl

def main():

	# creating term-document frequency matrix
	start_time = time.time()
	logging.info('Run NMF...')


	
	with concurrent.futures.ProcessPoolExecutor(max_workers = num_thread) as exe:
		logging.info('fs - 1')

		l = get_files_in_dir(w_dir, os.path.getsize, True)

		sl = divide_list(l, num_thread)

		fs = {exe.submit(doParWork, idx, sl[idx]) for idx in range(0, num_thread)}

		logging.info('fs - 2')
		done, _ = concurrent.futures.wait(fs)
		logging.info('fs - 3')


	elapsed_time = time.time() - start_time

	logging.info('Done: Creating the total term-document frequency matrix. Execution time: %.3fs', elapsed_time)

if __name__ == '__main__':
    main()
