                %the operation 
                % chooses one matrix,
                % which calls for max 8 neighboring matrices
                % and does the operation.
function [topics, topic_score] = main_runme(tile_mtx,neighbor_mtx,exclusiveness,voca,k,kd)

    
    % 1. sparsing the matrices from term_doc
    AC = sparse( tile_mtx(:,1),tile_mtx(:,2),tile_mtx(:,3),max(tile_mtx(:,1)),max(tile_mtx(:,2)));
    n = size(neighbor_mtx_2);
    AN = cell(n,1);
    
    for c2 = 1:n
    AN{c1} = sparse( neighbor_mtx{c1}(:,1),neighbor_mtx{c1}(:,2),neighbor_mtx{c1}(:,3),max(neighbor_mtx{c1}(:,1)),max(neighbor_mtx{c1}(:,2)));
    end
    % sparsing finished
    
    % 2. normalisation
    AC_norm = bsxfun(@rdivide,AC,sqrt(sum(A.^2)));
    AN_norm = bsxfun(@rdivide,AN,sqrt(sum(A.^2)));
    
    % 3. initialisation
   
    xcl = exclusiveness; AL = ones(8,1); BE = zeros(8,1); AL = xcl.*AL;
    % 4. the NMF process 
    [WC,WN,HC,HN] = xcl_nmf(AC_norm,AN_norm,k,kd,AL,BE,20);  
    
    % 5. displaying top keywords
    [Wtopk,Htopk;DocTopk;Wtopk_idx] = parsenmf(WC,HC,dict,topk);
    topics = Wtopk(:)';
    
    Wtopk_idx
    
    %6 topic score algorithm. 
    topic_score =0;
    
end

   