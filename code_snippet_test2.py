import numpy as np
import collections

#########################################################################
# freq = 0

# tdm = np.array([[1, 2, 3], 
# 				[1, 3, 4], 
# 				[2, 3, 4]])

# tdm = tdm[:,1]
# setTdm = set(tdm)
# freq = len(setTdm)

# print(freq)
#########################################################################


# freq = 0
# word_idx = [1,3]

# tdm = np.array([[1, 2, 3], 
# 				[2, 3, 4], 
# 				[3, 3, 4]])

# # tdm = tdm[np.logical_or.reduce([tdm[:,0] == w for w in word_idx])]

# # tdm = tdm[:,2]
# tdm = tdm[tdm[:,0]==2]

# s = tdm.sum(axis=1)

# print(tdm)
# print(s[0])

#########################################################################

# freq = 0
# word_idx = [1,3]

# tdm = np.array([[1, 2, 3], 
# 				[2, 3, 4],
# 				[2, 4, 5],
# 				[3, 3, 4]])

# # tdm = tdm[np.logical_or.reduce([tdm[:,0] == w for w in word_idx])]

# # tdm = tdm[:,2]
# tdm = tdm[tdm[:,0]==2]

# s = tdm.sum(axis=0)

# print(tdm)
# print(s[2])

#########################################################################

# a = collections.OrderedDict()

# a['a'] = 1
# a['b'] = 2
# a['c'] = 3

# for key, value in a.items():
# 	print(key)
# 	print(value)

#########################################################################

# name = 'freq_2013_d208_9_13_124'

# m = name[name.find('_')+1:]

# print(m)

#########################################################################

# t = '103_0.104_0.0_0.1_0.2_0.3_0.4_0.5_0.6'

# v = t.split('_')

# r = []
# for i in range(2, 9):
# 	r.append(float(v[i]))

# print(r)

#########################################################################

topics = []

with open('temp', 'r', encoding='UTF8') as f:
	lines = f.readlines()
	is_firstline = True
	k = 0
	for line in lines:
		v = line.split('\t')
		if is_firstline == True:
			k = int(v[0])
			is_firstline = False
			continue
		
		topic = []
		for i in range(0, k):
			topic.append(v[i].strip())

		topics.append(topic)

topics = [[topics[j][i] for j in range(len(topics))] for i in range(len(topics[0]))]

for i in range(k):
	words = topics[i]
	for word in words:
		print(word)





































































































