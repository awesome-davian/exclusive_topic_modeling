import pymongo
import constants


#import constants
# import matlab.engine
# eng = matlab.engine.start_matlab()
# eng.cd(constants.MATLAB_DIR)

#ret = eng.triarea(1.0,5.0)
#------------------------------------------------------------------------------------------------
conn = pymongo.MongoClient("localhost", constants.DEFAULT_MONGODB_PORT);

dbname = constants.DB_NAME;
db = conn[dbname];

tile_id = 642237
print(str(tile_id))

topics = [];
for tile_name in db.collection_names():

	# find out only the 
	if tile_name.endswith('_topics') == True:
		print(tile_name)

		if tile_name.find(str(tile_id)) > 0:
			print('found')

			tile = db[tile_name]
			for i in range(1,11):

				topic = {};
				topic["score"] = tile.find_one({'topic_id':999})['topic_score'];

				words = [];
				
				for each in tile.find({'topic_id': i}).sort('rank',pymongo.ASCENDING):
					# topic.append(each['word']);
					
					word = {};
					word["word"] = each['word']
					words.append(word)
					

				topic["words"] = words;

				topics.append(topic);

			break;

print(topics);

#------------------------------------------------------------------------------------------------
# drop database

# conn = pymongo.MongoClient("localhost", constants.DEFAULT_MONGODB_PORT);

# dbname = constants.DB_NAME;
# db = conn[dbname];

# topics = [];
# for tile_name in db.collection_names():

# 	# find out only the 
# 	if tile_name.find('_2013_') > 0:	
# 		db.drop_collection(tile_name);

# for item in db.counters.find():
# 	name = item['_id']
# 	if name.find('_2013_') > 0:
# 		db.counters.delete_one({'_id':name})
