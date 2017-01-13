function topics, topic_score = function_runme(tdm, voca, k, topk)

% clear all;
% close all;

addpath('./library/nmf');     
addpath('./library/ramkis');
addpath('./library/peripheral');
addpath('./library/discnmf');

dict = voca;

A = sparse(tdm(:,1),tdm(:,2),tdm(:,3),max(tdm(: ,1)),max(tdm(:,2)));
clear tdm;

% normalization
A_norm = bsxfun(@rdivide,A,sqrt(sum(A.^2)));  

% choosing one among different preprocessings
target_A = A;     % replaced by below code (9/10) <- original
% target_A = A_norm;
% target_A = A_idf;

[W,H]=nmf(target_A, k); % nmf() is matrix decomposition on A to get W,H (i.e. A=W*H); num of topic = k ; =

% displaying top keywords for each topic
[Wtopk,Htopk,DocTopk,Wtopk_idx] = parsenmf(W,H,dict,topk);

topics = Wtopk(:)';

Wtopk_idx

end