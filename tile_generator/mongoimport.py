import sys
import pymongo, json
import logging, logging.config


logging.config.fileConfig('logging.conf')

conn = pymongo.MongoClient("localhost", 27017)

#mongoimport --db salt_rawdata_131231 --collection tweets --file 2013_12_31

#dbname = sys.argv[1]
# dbname = constants.DB_NAME;
# db = conn[dbname]


arglen = len(sys.argv)
for item in range(0, arglen):
	print('argv[%d]: %s' % (item, sys.argv[item]))

db_name = sys.argv[1]
col_name = sys.argv[2]
input_file_name = sys.argv[3]

input_file = open(input_file_name, 'r')
db = conn[db_name]
col = db[col_name]

# only for test
db.drop_collection(col_name);

for line in input_file:
	line_json = json.loads(line)
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
		if line_json["lang"] != "en":
			continue;
	except KeyError as e:
		continue;

	col.insert({"id": line_json["id"], 
		"text": line_json["text"], 
		"coordinates": line_json["coordinates"],
		"created_at": line_json["created_at"],
		"user":{
			"id": line_json["user"]["id"],
			"name": line_json["user"]["name"]
		},
		"favorite_count": line_json["favorite_count"],
		"retweet_count": line_json["retweet_count"]
		});



input_file.close()