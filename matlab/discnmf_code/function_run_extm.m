function [Topics, wtopk_score, Topic_score, xcl_score, Freq_words] = function_run_extm(Tdm, exclusiveness,Stop_words, voca, k, topk)

    Topics = {}; wtopk_score = []; Topic_score = {}; xcl_score = 0; Freq_words = cell(1,2);

    % dict = voca{1};
    dict = voca;
    xcl = exclusiveness;

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
    Tdm_s = cell(1,2);
    Tdm_s{1} = Tdm(1:end_center,1:3);
    Tdm_s{2} = Tdm(end_center:end,1:3);
    
    if( end_center <50)
        return
    end
    
    if  size(Tdm,1)-end_center < 50
        return
    end
    
    
    Spar_Mtx = cell(2,1);
    
    Spar_Mtx{1} = sparse(Tdm_s{1}(:,1),Tdm_s{1}(:,2),Tdm_s{1}(:,3),size(dict,1),max(Tdm_s{1}(:,2)));
    Spar_Mtx{2} = sparse(Tdm_s{2}(:,1),Tdm_s{2}(:,2),Tdm_s{2}(:,3),size(dict,1),max(Tdm_s{2}(:,2)));
    
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
    dict = dict(nz_voc_idx,:);
    size(nz_voc_idx);
%     disp('dict')
%     size(dict,1)
    disp('2-1. sparse matrix making done');
    
    %--------- Stop Word Gathering ------------
    stop_words_index = [];    
    exist_sw = zeros(size(Stop_words,2),1);
    
    for i = 1: size(Stop_words,2)
        for j = 1:size(dict,1)
            if strcmp(Stop_words{i},dict(j)) > 0
                stop_words_index(i) = j ;
                exist_sw(i) = exist_sw(i) + 1;
            else
                exist_sw(i) = exist_sw(i) + 0;
            end
        end
    end
    stop_words_index;
    exist_sw;
    % stop words index gathered. Then. so what?
    stop_wds_idx = ones(size(dict,1),1);
    for i=1:size(Stop_words,2)
        if(exist_sw(i) >= 1)
            stop_wds_idx(stop_words_index(i)) = 0;
        end
    end

    stop_wds_idx = stop_wds_idx ~= 0;
    
    
    dict = dict(stop_wds_idx,:);
    for i=1:2
        NS_Mtx{i} = NS_Mtx{i}(stop_wds_idx,:);
    end
    
    
    disp('2-2. Stop Word Controlling done');
    
    
    
    disp('2-3. Search for words done');
    
    
    Num_tdm = [ 1 size(NS_Mtx{2},2)/size(NS_Mtx{1},2) ];
    
    regularization_param  = 2;
    
    AL = regularization_param*(1-xcl)/Num_tdm(1);
    BE =  regularization_param*xcl/Num_tdm(2);
    % [AL BE] = [ (1-xcl)/Num_tdm(1) xcl/Num_tdm(2) ];
    % ------------------------ 3. NMF operation  ----------------------
    
    [WC,WN,HC,HN] = xcl_nmf_perceptual(NS_Mtx{1},NS_Mtx{2},k*2,k,50,AL,BE);
    
    disp('3. disc_nmf operation done');
    
    % ----------------------- 4. Parsing Procedure ---------------------
    Wtopk = {}; Htopk = {}; DocTopk = {}; Wtopk_idx = {}; Wtopk_score={}; 
    [ Wtopk,Htopk,DocTopk,Wtopk_idx,Wtopk_score,Topic_score,Wtopk_num] = parsenmf(WC,HC,dict,topk);
    Wtopk_score
    
    disp('4. parsing operation done');
    
    %------------------------ 5. making exclusive score ---------------
    topk_num = Wtopk_num' ; topk_score = Wtopk_score'; ttopk = Wtopk(:);
    numt=1; List_of_topics = {}; num_of_topics =[]; Score_of_topics =[];
    cnumt=1; List_of_ctopics = {}; num_of_ctopics = []; Score_of_ctopics =[];
    Disc_topics = []; Com_topics = [];
    NS_Mtx_YD = cell(2,1); YD = {}; NS_Mtx_YC=cell(2,1); YC={};
    Count_Y = cell(9,1); Count_YC =cell(9,1); count_y = []; count_yc = [];
    
    WCsort = cell(k*2,1);
    for i=1:k*2
        WCsort{i} =  sort(WC(:,i),'descend');
    end
    
    for j=1:k  
        for i=1:min([size(WC,1) topk])
            if(WCsort{j}(i) > 1e-5)
                List_of_topics(numt) = ttopk((j-1)*(topk*2) + i);
                num_of_topics(numt) = topk_num(j,i);
                % Score_of_topics{numt} = topk_score{j,i};
                Score_of_topics(numt) = topk_score(j,i);
                numt = numt+1;
            end
        end
    end
    
    for j= (k+1):k*2  
        for i=1:min([size(WC,1) topk])
            if(WCsort{j}(i) > 1e-5)
                List_of_ctopics(cnumt) = ttopk((j-1)*(topk*2) + i);
                num_of_ctopics(cnumt) = topk_num(j,i);
                % Score_of_ctopics{cnumt} = topk_score{j,i};
                Score_of_ctopics(cnumt) = topk_score(j,i);
                cnumt = cnumt+1;
            end
        end
    end
    
    for i=1:numt-1
        Disc_topics = [ Disc_topics; List_of_topics(i) num_of_topics(i) Score_of_topics(i) ];
    end
    for i=1:cnumt-1
        Com_topics = [ Com_topics; List_of_ctopics(i) num_of_ctopics(i) Score_of_ctopics(i) ];
    end

    Disc_topics = sortrows(Disc_topics,-3);
    Com_topics = sortrows(Com_topics,-3);
    
    disp('5-1. end of choosing row vectors');
    
    for i=1:min(10, min(numt-1, cnumt-1))
        YD{i} = Disc_topics{i,2};
        YC{i} = Com_topics{i,2};
    end
    
    for i=1:2
        for j = 1:min(10, min(numt-1, cnumt-1))
            NS_Mtx_YD{i} = [ NS_Mtx_YD{i}; NS_Mtx{i}(YD{j},:) ];
            NS_Mtx_YC{i} = [ NS_Mtx_YC{i}; NS_Mtx{i}(YC{j},:) ];
        end
    end
    
    for i=1:2
        Count_YD{i} = NS_Mtx_YD{i}~=0,2;
        Count_YC{i} = NS_Mtx_YC{i}~=0,2;
        count_yc(i) = sum(sum(Count_YC{i},2));
        count_yd(i) = sum(sum(Count_YD{i},2));
    end
    
    disc_pro = count_yd(1)/sum(count_yd(1:2));
    comm_pro = count_yc(1)/sum(count_yc(1:2));
    
    disp('5-2. getting exclusiveness score done');

   %---------- Making the Outputs
   Topic_num = [];
   Tem_wtopk_score = []; Tem_topic_score = {};
   Tem_Topics = {}; Tem_Topic_num = [];
      
   % for i=1:k
   %  topic_score{i} = Topic_score(i);
   % end
   
   Valid_k = zeros(k,1);
   for i = 1:k
       a=0;
       if Topic_score(i) > 1e-6
           a = a+1;
           for j = 1:topk
               if  ( topk_score(i,j) > 1e-4 )
                   Valid_k(a)=i;
                   Tem_Topics{(i-1)*topk+j} = ttopk{ (i-1)*(topk*2) +j };
                   Tem_wtopk_score((i-1)*topk+j) = topk_score(i,j);
               else
                   Tem_Topics{(i-1)*(topk*2)+j} = ' ';
                   Tem_wtopk_score((i-1)*topk+j) = 0.0;
               end
           end
       else
           Tem_Topics{(i-1)*(topk*2)+j} = ' ';
           Tem_wtopk_score((i-1)*topk+j) = 0.0;
       end
   end
   
   for i =1:k
       if Valid_k(i) ~= 0
           for j = 1:topk 
               Topics{(i-1)*topk+j} = Tem_Topics{(Valid_k(i)-1)*topk+j};
               wtopk_score((i-1)*topk+j) = Tem_wtopk_score((Valid_k(i)-1)*topk+j);
           end
       else
           for j = 1:topk 
               Topics{(i-1)*topk+j} = Tem_Topics{(i-1)*topk+j};
               wtopk_score((i-1)*topk+j) = Tem_wtopk_score((i-1)*topk+j);
           end
       end
   end
   
   
   NS_Mtx_FR = cell(1,2);
   
   for T = 1:2
       for i = 1:k
           for j = 1:topk
               NS_Mtx_FR{T} = [ NS_Mtx_FR{T}; NS_Mtx{T}(topk_num(i,j),:) ];
           end
       end
   end
   
   for i=1:2
       Freq_words{i} = sum(NS_Mtx_FR{i},2);
   end


   xcl_score = (disc_pro)/(disc_pro+comm_pro)

    
   disp('6. making outputs done');
   disp('------------- Complete ------------- ');
    
end
