function [topics, topic_score] = main_runme(tile_mtx,neighbor_mtx,exclusiveness,voca,k,kd)

    % 0. addpath needed 
%     addpath(./library);
%     addpath(./library/nmf);
%     addpath(./library/ramkis);
%     addpath(./library/topictoolbox);
    
    % 1. sparsing the matrices from term_doc
    AC = sparse( tile_mtx(:,1),tile_mtx(:,2),tile_mtx(:,3),max(tile_mtx(:,1)),max(tile_mtx(:,2)));
    n = size(neighbor_mtx_2);
    AN = cell(n,1);
    
    for c1 = 1:n
    AN{c1} = sparse( neighbor_mtx{c1}(:,1),neighbor_mtx{c1}(:,2),neighbor_mtx{c1}(:,3),max(neighbor_mtx{c1}(:,1)),max(neighbor_mtx{c1}(:,2)));
    end
    % sparsing finished
    
    % 2. normalisation
    AC_norm = bsxfun(@rdivide,AC,sqrt(sum(A.^2)));
    AN_norm = bsxfun(@rdivide,AN,sqrt(sum(A.^2)));
    
    % 3. initialisation
   
    rp=1; % regularisation parameter
    xcl = exclusiveness; AL = ones(8,1); BE = ones(8,1); AL = (rp*(1-xcl)).*AL; BE = (rp*xcl).*BE;
    % 4. the NMF process 
    [WC,WN,HC,HN] = xcl_nmf(AC_norm,AN_norm,k,kd,20,AL,BE);  
    
    % 5. displaying top keywords
    topk = 5;
    Wtopk = {}; Htopk = {}; DocTopk = {}; Wtopk_idx = {};
    [Wtopk,Htopk;DocTopk;Wtopk_idx] = parsenmf(WC,HC,voca,topk);
    topics = Wtopk(:)';
    
    Wtopk_idx
    
    %6 topic score algorithm. 
    topic_score =0;
    
end
