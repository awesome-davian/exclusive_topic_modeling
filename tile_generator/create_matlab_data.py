import os, sys


arglen = len(sys.argv)
if arglen != 3:
	print("Usage: python topic_modeling_module_all.py [vocabulary filename] [term-doc_matrix filename]")
	print("For example, python topic_modeling_module_all.py ./voca/voca_140130 ./mtx/tile_2013_d255_13_2414_5110_19780598_mtx")
	exit(0)

vocabulary_filename = sys.argv[1]
mtx_filename = sys.argv[2]

def readVoca():
	idx = 0
	voca = voca_file.readlines()
	for line in voca:
		v = line.split('\t')
		bag_words[v[0]] = int(v[1])
		word_map[v[0]] = idx
		idx += 1
		list_voca.append(v[0])

	# idx = 0
	# for key, value in bag_words.items():
	# 	if idx > 100:
	# 		break
	# 	print("%s, %d" % (key, int(value)))
	# 	idx += 1

	voca_hash = voca_hash_file.readlines()
	for line in voca_hash:
		v = line.split('\t')
		if v[0] not in stem_bag_words:
			stem_bag_words[v[0]] = collections.OrderedDict()

		stem_bag_words[v[0]][v[1]] = int(v[2])

	# idx = 0
	# for key, value in stem_bag_words.items():
	# 	if idx > 100:
	# 		break

	# 	print("%s, %s, %s" % (key, list(value)[0], value[list(value)[0]]))
	# 	idx += 1

logging.info('loading vocabulary...');
start_time = time.time()

stem_bag_words=collections.OrderedDict()
bag_words = collections.OrderedDict()
word_map = collections.OrderedDict()

list_voca = []

voca_file = open('./'+vocabulary_filename, 'r', encoding='UTF8')
voca_hash_file = open('./'+vocabulary_filename+'_hash', 'r', encoding='UTF8')

readVoca()

voca_file.close()
voca_hash_file.close()

mtx_file = open(mtx_filename, 'r', encoding='UTF8')
lines = mtx_file.readlines()

tile_mtx = [];
for line in lines:
	v = line.split('\t')
	item = np.array([int(v[0]), int(v[1]), int(v[2])], dtype=np.int32)
	tile_mtx = np.append(tile_mtx, item, axis=0)

mtx_file.close()

logging.info("#lines: %s", len(lines))
tile_mtx = np.array(tile_mtx, dtype=np.int32).reshape(len(lines), 3)

A = matlab.double(tile_mtx.tolist()) # sparse function in function_runme() only support double type.
[topics_list, w_scores, t_scores] = eng.function_runme(A, list_voca, constants.DEFAULT_NUM_TOPICS, constants.DEFAULT_NUM_TOP_K, nargout=3);
