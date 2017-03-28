function a = function_test(mtx_name)

	a = 1

	nmtx_map = evalin('base','spatial_nmtx_map')

	A = values(nmtx_map, {'mtx_2013_d309_13_2418_5112'})
	A = cell2mat(A)

	% A = [0 1 4; 1 1 1; 2 1 2; 3 2 4; 2 2 1; 5 3 2; 6 3 4; 2 3 1; 3 3 2; 7 4 3; 8 4 1; 3 5 2; 1 5 2]
	% in_words = [3, 5]
	in_words = [4908, 3581]
	% found_word_idx = find(A(:,1)==in_words)
	found_word_idx = find(ismember(A(:,1),in_words));
	Docs = A(:,2);
	DocIdx = Docs(found_word_idx);

	Af = A(ismember(Docs, DocIdx),:)

	ex_words = [5];
	found_word_idx = find(ismember(Af(:,1),ex_words));
	Docs = Af(:,2);
	DocIdx = Docs(found_word_idx);

	Afinal = Af(~ismember(Docs, DocIdx),:);

end