# -*- coding: utf-8 -*-
import collections
import time

# for parallel processing
import concurrent.futures

LEVEL = 0
DAY = 1
X = 2
Y = 3

MAX_CAL = 9

tile = collections.OrderedDict()

# set sample data. [level, day, x, y]
ids = [ [9, 1, 1, 1], [9, 1, 1, 2], [9, 1, 1, 3], [9, 1, 2, 1], [9, 1, 2, 2], [9, 1, 2, 3], [9, 1, 3, 1], [9, 1, 3, 2], [9, 1, 3, 3],
		[9, 2, 1, 1], [9, 2, 1, 2], [9, 2, 1, 3], [9, 2, 2, 1], [9, 2, 2, 2], [9, 2, 2, 3], [9, 2, 3, 1], [9, 2, 3, 2], [9, 2, 3, 3],
		[9, 3, 1, 1], [9, 3, 1, 2], [9, 3, 1, 3], [9, 3, 2, 1], [9, 3, 2, 2], [9, 3, 2, 3], [9, 3, 3, 1], [9, 3, 3, 2], [9, 3, 3, 3],
		[10, 1, 1, 1], [10, 1, 1, 2], [10, 1, 1, 3], [10, 1, 2, 1], [10, 1, 2, 2], [10, 1, 2, 3], [10, 1, 3, 1], [10, 1, 3, 2], [10, 1, 3, 3],
		[10, 2, 1, 1], [10, 2, 1, 2], [10, 2, 1, 3], [10, 2, 2, 1], [10, 2, 2, 2], [10, 2, 2, 3], [10, 2, 3, 1], [10, 2, 3, 2], [10, 2, 3, 3],
		[10, 3, 1, 1], [10, 3, 1, 2], [10, 3, 1, 3], [10, 3, 2, 1], [10, 3, 2, 2], [10, 3, 2, 3], [10, 3, 3, 1], [10, 3, 3, 2], [10, 3, 3, 3],
		[11, 1, 1, 1], [11, 1, 1, 2], [11, 1, 1, 3], [11, 1, 2, 1], [11, 1, 2, 2], [11, 1, 2, 3], [11, 1, 3, 1], [11, 1, 3, 2], [11, 1, 3, 3],
		[11, 2, 1, 1], [11, 2, 1, 2], [11, 2, 1, 3], [11, 2, 2, 1], [11, 2, 2, 2], [11, 2, 2, 3], [11, 2, 3, 1], [11, 2, 3, 2], [11, 2, 3, 3],
		[11, 3, 1, 1], [11, 3, 1, 2], [11, 3, 1, 3], [11, 3, 2, 1], [11, 3, 2, 2], [11, 3, 2, 3], [11, 3, 3, 1], [11, 3, 3, 2], [11, 3, 3, 3] ]


def doWork(level, day, x, y):
	time.sleep(.001)
	tile[level][day][x][y] += 1
	return

def doParWork(idx):

	t = ids[idx]

	level = t[LEVEL]
	day = t[DAY]
	x = t[X]
	y = t[Y]

	while(True):
		if tile[level][day][x][y] > MAX_CAL:
			break
		else:
			time.sleep(.001)
			tile[level][day][x][y] += 1

	print("%s: %d" % (ids[idx], tile[level][day][x][y]))

	return

def init():
	
	# 모든 파일 ID 를 Scan 해서 저장
	for tid in ids:
		
		lv = tid[LEVEL]
		if lv not in tile:
		 	tile[lv] = collections.OrderedDict()

		day = tid[DAY]
		if day not in tile[lv]:
			tile[lv][day] = collections.OrderedDict()

		x = tid[X]
		if x not in tile[lv][day]:
			tile[lv][day][x] = collections.OrderedDict()

		y = tid[Y]
		if y not in tile[lv][day][x]:
			tile[lv][day][x][y] = collections.OrderedDict()

		tile[lv][day][x][y] = 0

	# for tid in ids:
	# 	print("%s: %d" % (tid, tile[tid[LEVEL]][tid[DAY]][tid[X]][tid[Y]]))

def seqDo():

	# baseline(sequantial algorithm)
	for tid in ids:
		while(True):
			if tile[tid[LEVEL]][tid[DAY]][tid[X]][tid[Y]] > MAX_CAL:
				break
			else:
				doWork(tid[LEVEL],tid[DAY],tid[X],tid[Y])
		print("%s: %d" % (tid, tile[tid[LEVEL]][tid[DAY]][tid[X]][tid[Y]]))

def parDo():

	# apply parallel algorithm
	
	with concurrent.futures.ProcessPoolExecutor() as exe:
		fs = {exe.submit(doParWork, idx) for idx in range(0, len(ids))}
		done, _ = concurrent.futures.wait(fs)

	return

def main():
	
	init()
	
	s_time = time.time()
	seqDo()
	e_time = time.time() - s_time
	print("seq elapsed time: %.3f" % (e_time))

	init()

	s_time = time.time()
	parDo()
	e_time = time.time() - s_time
	print("par elapsed time: %.3f" % (e_time))



if __name__ == "__main__":
	main()