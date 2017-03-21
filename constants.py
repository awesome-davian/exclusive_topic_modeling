# v0.1.x.x : Local test
# v0.2.x.x : Protocol test in progress
# v0.3.x.x : GET_RELATED_TOPIC protocol added
# v0.5.x.x : Protocol test complete
VERSION = 'v0.5.0.1_Mar21'	# get related docs complete

MATLAB_DIR = './matlab/standard_nmf/'
#MATLAB_DIR = './matlab/'
DEFAULT_MONGODB_PORT = 27017

# DB_NAME_TILE = 'tweets_tiles' + DB_NAME_POSTFIX
# DB_NAME_MTX = 'SALT_DB_mtx' + DB_NAME_POSTFIX
# DB_NAME_TOPICS = 'SALT_DB_topics' + DB_NAME_POSTFIX

DATA_RANGE = '131103-131105'

GLOBAL_VOCA_FILE_PATH = './tile_generator/data/'+DATA_RANGE+'/voca/voca'
GLOBAL_DOC_FILE_PATH = './tile_generator/data/'+DATA_RANGE+'/rawdata/raw_tweets'
NEIGHBOR_MTX_DIR = './tile_generator/data/'+DATA_RANGE+'/mtx_neighbor/'
MTX_DIR = './tile_generator/data/'+DATA_RANGE+'/mtx/'
SPATIAL_XSCORE_DIR = './tile_generator/data/'+DATA_RANGE+'/xscore/spatial/'
TEMPORAL_XSCORE_DIR = './tile_generator/data/'+DATA_RANGE+'/xscore/temporal/'
SPATIAL_TOPIC_PATH = './tile_generator/data/'+DATA_RANGE+'/topics/spatial/'
TEMPORAL_TOPIC_PATH = './tile_generator/data/'+DATA_RANGE+'/topics/temporal/'
W_PATH = './tile_generator/data/'+DATA_RANGE+'/w/'

OPMODE_SPATIAL_MTX = 0
OPMODE_TEMPORAL_MTX = 0

DEFAULT_NUM_TOPICS = 5
DEFAULT_NUM_TOP_K = 5
DEFAULT_EXCLUSIVENESS = 0
TEMPORAL_DATE_RANGE = 5
EXCLUSIVE_RANGE = 6

MIN_ROW_FOR_TOPIC_MODELING = 30
MIN_WORD_FREQUENCY = 10

MAX_RELATED_DOCS = 1000

TOPIC_ID_MARGIN_FOR_SCORE = 10000

POS_TILE = 0
POS_YEAR = 1
POS_WEEK = 2
POS_LEVEL = 3
POS_X = 4
POS_Y = 5
POS_TILEID = 6
POS_COL_TYPE = 7