function [WC] = func_warm_start_W(Tdm, voca, k, topk)

    dict = voca';
    xcl = 0.5;

    disp('1. initializing variables done'); % the term format will be given in text form so you need to divide them. 
    
    
    % 2. Separating the term doc cells. 


  
    [tdm_row, tdm_cols] = size(Tdm);
    
    
    M_num = []; M_end = [];
    num_term = 1;
    
    a2 = Tdm(1,4);
    M_num(1) = a2;
    
    for i = 1:tdm_row
        if( Tdm(i,4) ~= a2)
            end_center =  i-1;
            break;
        end
    end
    Tdm_s = cell(2,1);
    Tdm_s{1} = Tdm(1:end_center,1:3);
    Tdm_s{2} = Tdm(end_center:end,1:3);
    
    Spar_Mtx = cell(2,1);
    Spar_Mtx{1} = sparse(Tdm_s{1}(:,1),Tdm_s{1}(:,2),Tdm_s{1}(:,3),size(dict{1},1),max(Tdm_s{1}(:,2)));
    Spar_Mtx{2} = sparse(Tdm_s{2}(:,1),Tdm_s{2}(:,2),Tdm_s{2}(:,3),size(dict{1},1),max(Tdm_s{2}(:,2)));
    
    nz_doc_idx = cell(2,1);
    NS_Mtx = cell(2,1);
    for i = 1:2
        nz_doc_idx{i} = sum(Spar_Mtx{i},1) ~= 0;
        NS_Mtx{i} = Spar_Mtx{i}(:,nz_doc_idx{i});
    end
    nz_voc_idx = ( sum(NS_Mtx{1},2) + sum(NS_Mtx{2},2) ) ~= 0;
    for i= 1:2
        NS_Mtx{i} = NS_Mtx{i}(nz_voc_idx,:);
    end
    
    disp('2. sparse matrix making done');
    
    Num_tdm = [ 1 size(NS_Mtx{2},2)/size(NS_Mtx{1},2) ];
    AL = (1-xcl)/Num_tdm(1);
    BE =  xcl/Num_tdm(2);
    % [AL BE] = [ (1-xcl)/Num_tdm(1) xcl/Num_tdm(2) ];
    % ------------------------ 3. NMF operation  ----------------------
    
    [WC,WN,HC,HN] = xcl_nmf_updated0316(NS_Mtx{1},NS_Mtx{2},k*2,k,20,AL,BE);
    disp('3. discNMF done');
    disp('------------- Complete ------------- ');
    
end
