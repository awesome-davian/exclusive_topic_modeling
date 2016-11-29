import operator
import sys
import os
import collections

do_stemming = False
input_file = sys.argv[1]
output_file = sys.argv[1]

def truncate_word(word):
	start = 0
	while start < len(word) and word[start].isalpha() == False:
		start += 1
	end = len(word)
	while end > start and word[end-1].isalpha() == False:
		end -= 1
	truncated = word[start:end].lower()
	for letter in truncated:
		if letter.isalpha():
			break
	else:
		return ''
	if truncated.find('http://') == 0:
		return ''
	if do_stemming == True:
		if len(truncated) == 0:
			return ''
	else:
		return truncated

def tokenization(text):
	if len(text) == 0:
		return
	start_pos = 0
	while start_pos < len(text):
		while start_pos < len(text):
			if text[start_pos].isalpha():
				break
			else:
				start_pos += 1
		end_pos = start_pos
		while end_pos < len(text):
			if text[end_pos].isalpha():
				end_pos += 1
			else:
				break
		word = text[start_pos:end_pos].lower()
		if word.find('urgent') == -1:
			yield text[start_pos:end_pos]
		start_pos = end_pos

def read_txt(text):
	bag_words = collections.OrderedDict()
	for word in tokenization(text):
		truncated = truncate_word(word)
		if truncated != '':
			try:
				bag_words[truncated] += 1
			except KeyError:
				bag_words[truncated] = 1
	return bag_words


stop_list = set()
f_stop = open('english.stop')
for line in f_stop:
	stop_list.add(line[0:-1])
f_stop.close()

new_voc= open('tmp2/vocabulary.txt', 'r', encoding='UTF8')
nv_bag_words=collections.OrderedDict()
for line in new_voc:
	text=line[0:-1].split()[0]
	frec=line[0:-1].split()[1]
	nv_bag_words[text]=int(frec)
new_voc.close()



if os.path.isdir(input_file):
	list_count=0
	file_list=[]
	for root, dirs, files in os.walk(input_file):
		for file in files:
			file_list.append(os.path.join(root,file))
	for fname in file_list:
		f_each=open(fname,'r',encoding='UTF8')
		doc_count=0
		for line in f_each:
			text=line[0:-1]
			bag_words_one=read_txt(text)
			for word in bag_words_one:
				try:
					nv_bag_words[word]+=bag_words_one[word]
				except:
				    nv_bag_words[word]=bag_words_one[word]
			doc_count+=1
		print(doc_count)
		f_each.close();
	print(list_count)   	


voc_file = open('tmp2/vocabulary.txt', 'w', encoding='UTF8')
word_map =collections.OrderedDict()
count = 0
for word in nv_bag_words:
	if word in stop_list:
		continue	
	voc_file.write(word + '\t' + str(nv_bag_words[word]) + '\n')
	word_map[word] = count
	count += 1
voc_file.close()



mtxs=[]


for root, dirs, files in os.walk(input_file):
	for file in files:
		mtxs.append(os.path.join(root,file))

for tiles in mtxs:
	f_name=tiles.split('\\')[2]
	f_mtx=open(os.path.join('tmp2',f_name+'.mtx'),'w',encoding='UTF8')
	f_mtx.write('%%MatrixMarket matrix coordinate real general\n')
	word_map_tot_len = len(word_map)
	doc_count = 0
	line_count = 0

	f_tweets = open(tiles, encoding='UTF8')
	for line in f_tweets:
		text = line[0:-1]
		bag_words_one = read_txt(text)
		for word in bag_words_one:
			try:
				word_idx = word_map[word]
				#print(word + '\t' + str(word_idx+1) + ' '+str(doc_count+1)+'\n')
				f_mtx.write(str(word_idx+1) + ' ' + str(doc_count+1) + ' ' + str(bag_words_one[word]) + '\n')
				line_count +=1
			except KeyError:
				continue
		doc_count += 1
	print(tiles)	
	f_tweets.close()
	f_mtx.close()
