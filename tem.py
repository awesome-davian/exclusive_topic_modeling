    #todo: JinHo 
	def make_sub_term_doc_matrix(self, term_doc_mtx, include_word_list, exclude_word_list, time_range):

		exclude_doc_list=self.get_doc_idx_include_word(term_doc_mtx, exclude_word_list)
		include_doc_list=self.get_doc_idx_include_word(term_doc_mtx, include_word_list)

		new_tile_mtx=[]

		if(len(include_word_list)>0):
			for each in term_doc_mtx:
				for in_word in include_doc_list:
					for idx in in_word:
						if(each[1]==idx):
							item = np.array([each[0], each[1], each[2]], dtype=np.double);
							logging.info(item)
							new_tile_mtx = np.append(new_tile_mtx, item, axis=0)
				for ex_word in exclude_doc_list:
				    for element in ex_word:
				        if(each[1]==element):
				            new_tile_mtx = np.delete(new_tile_mtx, element, axis=0)	

				    
		else: 
		    for each in term_doc_mtx:
		        for ex_word in exclude_doc_list:
		            for indx in ex_word:
		                if(each[1] == ex_word):
		                    continue;
		                else:
		                    item=np.array([each[0], each[1], each[2]], dtype=np.double)
		                    new_tile_mtx = np.append(til_mtx, item,item, dtype=np.double



		new_tile_mtx = np.array(new_tile_mtx, dtype=np.double).reshape(int(np.size(new_tile_mtx)/3), 3)


		logging.debug(new_tile_mtx)

	    
		# loggging.debug(new_tile_mtx);	            



		return new_tile_mtx;