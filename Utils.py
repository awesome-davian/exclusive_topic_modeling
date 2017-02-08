import logging

class Util():
		
    def __init__(self, Do_stemming):
    	self.Do_stemming=False;


	def truncate_wrod(word):
		start=0
		return word; 


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
