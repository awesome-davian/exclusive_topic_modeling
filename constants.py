# v0.1.x.x : Local test
# v0.2.x.x : Protocol test in progress
# v0.3.x.x : Protocol test complete
VERSION = 'v0.1.0.3_Jan20'

MATLAB_DIR = './matlab/standard_nmf/'
#MATLAB_DIR = './matlab/'
DEFAULT_MONGODB_PORT = 27017
#DB_NAME = 'tweets_tiles'
DB_NAME = 'tweets_tiles131225'

DEFAULT_NUM_TOPICS = 10
DEFAULT_NUM_TOP_K = 10
DEFAULT_EXCLUSIVENESS = 0

MIN_ROW_FOR_TOPIC_MODELING = 30

TOPIC_ID_MARGIN_FOR_SCORE = 10000

POS_TILE = 0
POS_YEAR = 1
POS_WEEK = 2
POS_LEVEL = 3
POS_X = 4
POS_Y = 5
POS_TILEID = 6
POS_COL_TYPE = 7
