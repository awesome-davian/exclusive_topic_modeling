import logging, logging.config
import constants
import os
import datetime 
import time 
import collections
import numpy as np 

logging.config.fileConfig('logging.conf')

def parse_UB_log():

	datapath = constants.LOG_DIR + '/'
	clicked_by_zoom = collections.OrderedDict()
	last = ''
	tot_onshow_time = [] 
	tot_clicked_time = [] 
	tot_zoom_arr = []

	for root, directories, files in os.walk(datapath):

		for filename in files: 
			zoom_time = [] 
			onShowTopics_time = [] 
			clicked_time = []
			zoom_levels = []

			with open(datapath + filename, 'r', encoding = 'UTF-8') as f:
				lines = f.readlines()	
				zoom_level = '10'	
				zoom_levels.append(zoom_level)

				for line in lines: 
					if line.find("[UB]") > 0:

						v = line[:-1].split(' ')

						if line.find("onShowTopics()") > 0:
							onShowTopics_time.append(v[0])

						elif line.find("Zoom")	> 0:
							zoom_level = v[6]
							zoom_time.append(v[0])
							zoom_levels.append(zoom_level)


						elif line.find("A word clicked") > 0:
							clicked_time.append(v[0])
							if zoom_level not in clicked_by_zoom:
								clicked_by_zoom[zoom_level] =0
							clicked_by_zoom[zoom_level] +=1 

						last = v[0]

			tot_onshow_time.extend(compute_time_consumed(onShowTopics_time, last))
			tot_clicked_time.extend(compute_time_consumed(clicked_time, last))
			tot_zoom_arr.extend(compute_zoom_time(zoom_time, last, onShowTopics_time[0], zoom_levels))

	onshow_time = np.array(tot_onshow_time)
	clicked_time = np.array(tot_clicked_time)

	print('onshow time mean : '+ str(np.mean(onshow_time)) + ' variance: ' + str(np.var(onshow_time)))
	print('clicked time mean : '+ str(np.mean(clicked_time)) + ' variance: ' + str(np.var(clicked_time)))
	print(clicked_by_zoom)
	print(time_by_zoom(tot_zoom_arr))

			#print(zoom_arr)
			#print(compute_time_consumed(clicked_time, last))

			#print(clicked_by_zoom)




			# for i in range(0,len(onShowTopics_time)):
			# 	time_consumed  = 0
			# 	time_1 = convert_time_to_second(onShowTopics_time[i])

			# 	if i == len(onShowTopics_time) - 1 :
			# 		last_time = convert_time_to_second(last)
			# 		time_consumed = last_time - time_1
			# 	else :
			# 		time_2 = convert_time_to_second(onShowTopics_time[i+1])
			# 		time_consumed = time_2 - time_1

			# 	if()

				# x = time.strptime(onShowTopics_time[i].split(',')[0],'%H:%M:%S')
				# print(datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds())




def convert_time_to_second(time_str):
	time, ms = time_str.split('.')
	h, m, s = time.split(':')
	return int(h) * 3600 + int(m)*60 + int(s)

def compute_time_consumed(arr, last):

	time_arr = []

	for i in range(0, len(arr)):
		time_consumed  = 0
		time_1 = convert_time_to_second(arr[i])

		if i == len(arr) - 1 :
			last_time = convert_time_to_second(last)
			time_consumed = last_time - time_1
		else :
			time_2 = convert_time_to_second(arr[i+1])
			time_consumed = time_2 - time_1

		if time_consumed < 300 and time_consumed > 0:
			time_arr.append(time_consumed)


	return time_arr

def compute_zoom_time(arr, last, start, zoom):

	time_arr = []
	zoom_arr = []

	for i in range(0, len(arr)):
		time_consumed = 0 
		time_1 = convert_time_to_second(arr[i])

		if i == 0 :
			start_time = convert_time_to_second(start)
			time_consumed = time_1 - start_time
		elif i == len(arr) - 1 :
			last_time = convert_time_to_second(last)
			time_consumed = last_time - time_1
		else: 
			time_2 = convert_time_to_second(arr[i+1])
			time_consumed = time_2 - time_1 

		# print(time_consumed)
		time = {}
		time['time_consumed'] = time_consumed
		time['zoom'] = zoom[i]

		time_arr.append(time)


	return time_arr				

def time_by_zoom(dictionary):

	tot = []

	for i in range(9,14):
		temp_arr = []
		for element in dictionary:
			if element.get("zoom") == str(i):
				temp_arr.append(element.get("time_consumed"))

		temp_np = np.array(temp_arr)
		temp_mean = np.mean(temp_np)
		temp_var = np.var(temp_np)

		temp = {}
		temp['zoom'] = i
		temp['mean'] = temp_mean
		temp['var'] = temp_var

		tot.append(temp)

	return tot





def Parse_log_info(filename):

	datapath = constants.LOG_DIR + '/'

	onShowTopic_time = []
	Zoom_time = []
	word_clicked  =[]

	with open(datapath + filename, 'r', encoding = 'UTF-8') as f:
		lines = f.readlines()
		for line in lines:
			if line.find("[UB]") > 0:
				v = line.split(' ')
				if line.find("onShowTopics()") > 0:
					#print(v[0])
					onShowTopic_time.append(v[0])
				elif line.find("Zoom")	> 0:
					zoom = {}
					zoom['level'] = v[6]
					zoom['time'] = v[0]
					Zoom_time.append(zoom)
				elif line.find("A word clicked") > 0:
					print(v)
					print(v[0])
					word_clicked.append(v[0])




				




parse_UB_log()
#Parse_log_info('163.152.20.64-1505456434529_sujong')


