function [topics, wtopk_score, topic_score] = function_run_extm(tdm, ntdms, exclusiveness, voca, k, topk)

% addpath('./library/nmf');     
% addpath('./library/ramkis');
% addpath('./library/peripheral');
% addpath('./library/discnmf');

dict = voca;

A = sparse(tdm(:,1),tdm(:,2),tdm(:,3),max(tdm(:,1)),max(tdm(:,2)));
clear tdm;

% ncols --> The actual length of each neighbor tile
[nrows, ncols] = cellfun(@size, ntdms);

for i = 1:8

	if ncols(i) == 0
		continue
	end

	tdm_cell = ntdms{1, i};
	mtx = cell2mat( cellfun( @(x) cell2mat(x), tdm_cell, 'UniformOutput', 0 ) );
	ntdm = reshape(mtx, 3, [])';

	B = sparse(ntdm(:,1),ntdm(:,2),ntdm(:,3),max(ntdm(:,1)),max(ntdm(:,2)));

	% do NMF using B. Bs are the neighbor term-doc matrices.

end

% return values
topics = ''
wtopk_score = ''
topic_score = ''

% clean up variables
clear nrows;
clear ncols;
clear ntdms;

end