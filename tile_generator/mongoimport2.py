import sys, os
import errno
from os import listdir
from os.path import isfile, join
import pymongo, json
import logging, logging.config
import time

module_start_time = time.time();

logging.config.fileConfig('logging.conf')

conn = pymongo.MongoClient("localhost", 27017)

#mongoimport --db salt_rawdata_131231 --collection tweets --file 2013_12_31

def check_input_args(argv):
	print('argv[0]: %s' % (argv[0]))
	print('argv[1]: %s -> DB Name' % (argv[1]))
	print('argv[2]: %s -> Collection Name' % (argv[2]))
	print('argv[3]: %s -> Source' % (argv[3]))
	print("")

def get_next_sequence_value(sequence_name):

	# print("test: " % (db.counters.find_one({'_id':sequence_name})['seq']))

	db.counters.find_and_modify(
		{'_id':sequence_name}, 
		{'$inc':{'seq':1}}, upsert=True, new=True
	)

	# print("test: " % (db.counters.find_one({'_id':sequence_name})['seq']))

	#exit(0)

	return db.counters.find_one({'_id':sequence_name})['seq']

def import_file(input_file):

	print("Importing file(%s)... " % input_file)
	function_start_time = time.time();

	key_err = 0
	lang_err = 0
	dup_err = 0
	if os.path.isfile(input_file):
		
		with open(input_file, 'r', encoding='UTF8') as file:

			idx = 0;
			start_time = time.time()
			for line in file:

				line = line.strip()
				
				idx += 1;

				if idx % 10000 == 0:
					elapsed_time = time.time() - start_time
					print("%d items imported. Elapsed time: %.5fs" % (idx, elapsed_time));
					start_time = time.time()

				v = line.split(',')

				if len(v) < 7:
					continue

				# for each in v:
				# 	logging.debug(each)

				# 6부터 끝까지
				text = ''
				for i, each in enumerate(v):
					if i < 6:
						continue
					else:
						# if each.startswith('http://') == True or each.startswith('https://') == True:
						# 	continue
						text = text + ' ' + each.strip()

				# logging.debug(text)

				# print(line_json["id"])
				# print(line_json["text"].encode('utf-8'))
				# print(line_json["coordinates"])
				# print(line_json["created_at"])
				# print(line_json["user"]["id"])
				# print(line_json["user"]["name"].encode('utf-8'))
				# print(line_json["favorite_count"])
				# print(line_json["retweet_count"])
				# print('')

				try:

					tweet_lang = "en"
					tweet_id = int(v[0].strip())
					tweet_date = v[1].strip()
					tweet_time = v[2].strip()
					tweet_coordinates = {}
					tweet_coordinates["coordinates"] = []
					tweet_coordinates["coordinates"].append(float(v[4].strip()))
					tweet_coordinates["coordinates"].append(float(v[3].strip()))
					tweet_user_name = v[5].strip()
					tweet_text = text
					
				except ValueError:
					continue

				tweet_created_at = tweet_date + ' ' + tweet_time

				col.insert({"_id": get_next_sequence_value(col_name), "id": tweet_id,
					"text": tweet_text,
					"coordinates": tweet_coordinates,
					"created_at": tweet_created_at,
					"user":{
						"name": tweet_user_name
						}
					});
				

				
	else:
		print("%s is not a file." % input_file)

	function_elapsed_time = time.time() - function_start_time;
	print("Complete. Elapsed time: %.3fs" % (function_elapsed_time))

	if key_err != 0:
		print("[Err]# of Key Errors: %d" % (key_err))
	# elif lang_err != 0:
	# 	print("[Err]# of not the US language: %d" % (lang_err))
	elif dup_err != 0:
		print("[Err]# of duplicated: %d" % (dup_err))


arglen = len(sys.argv)
if arglen != 4:
	print("Usage: python mongoimport.py [db_name] [col_name] [source file or directory]")
	print("For example, python mongoimport.py test_rawdata_131225_final SALT_DB_131225 ../2013_12_25")
	exit(0)

check_input_args(sys.argv)

db_name = sys.argv[1]
col_name = sys.argv[2]
input_file = sys.argv[3]

db = conn[db_name]
col = db[col_name]

# TODO: Comment out this line when you contribute this module.
#db.drop_collection(col_name);

# with open(input_file, 'r', encoding='UTF8') as file:
# 	filedata = file.read()
# 	filedata = filedata.replace('\nTemp', 'Temp')

# with open(input_file, 'w', encoding='UTF8') as file:
# 	file.write(filedata)

# exit(0)

# check if the input value is file or directory
if os.path.isdir(input_file) == True:
	#print("%s is a directory." % input_file);

	for root, directories, files in os.walk(input_file):
		for filename in files:
			import_file(os.path.join(root, filename));

	# onlyfiles = [f for f in listdir(input_file) if isfile(join(input_file, f))]
	# for file in onlyfiles:
	# 	import_file(file);
else :
	#print("%s is a file." % input_file);
	import_file(input_file);

module_elapsed_time = time.time() - module_start_time;
print("All done. Total Elapsed Time: %.3fs" % (module_elapsed_time));