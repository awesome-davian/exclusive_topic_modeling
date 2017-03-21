function [Topics, wtopk_score, topic_score, xcl_score,Freq_words] = func_run_stanNMF_hals(Tdm,Stop_words, voca, k, topk)

    dict = voca;

    disp('1. initializing dictionary done'); 
    
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
    Tdm_s = Tdm(1:end_center,1:3);
    Spar_Mtx = sparse(Tdm_s(:,1),Tdm_s(:,2),Tdm_s(:,3),size(dict{1},1),max(Tdm_s(:,2)));
    nz_doc_idx = sum(Spar_Mtx,1) ~= 0;
    NS_Mtx = Spar_Mtx(:,nz_doc_idx);
    nz_voc_idx = sum(NS_Mtx,2) ~= 0;
    NS_Mtx = NS_Mtx(nz_voc_idx,:);
    dict{1} = dict{1}(nz_voc_idx,:);
    clear Tdm
    disp('2-1. sparse matrix making done');
    
    %--------- Stop Word Gathering ------------
    stop_words_index = [];    
    exist_sw = zeros(size(Stop_words,2),1);
    
    for i = 1: size(Stop_words,2)
        for j = 1:size(dict{1},1)
            if strcmp(Stop_words{i},dict{1}(j)) > 0
                stop_words_index(i) = j ;
                exist_sw(i) = exist_sw(i) + 1;
            else
                exist_sw(i) = exist_sw(i) + 0;
            end
        end
    end

    % stop words index gathered. Then. so what?
    stop_wds_idx = ones(size(dict{1},1),1);
    for i=1:size(Stop_words,2)
        if(exist_sw(i) >= 1)
            stop_wds_idx(stop_words_index(i)) = 0;
        end
    end

    stop_wds_idx = stop_wds_idx ~= 0;
    dict{1} = dict{1}(stop_wds_idx,:);
    NS_Mtx = NS_Mtx(stop_wds_idx,:);

    disp('2-2. Stop Word Controlling done');
    

    % [AL BE] = [ (1-xcl)/Num_tdm(1) xcl/Num_tdm(2) ];
    % ------------------------ 3. NMF operation  ----------------------
    
    [W,H] = hals_stan_nmf_salt(NS_Mtx,k*2,20);
    
    disp('3. disc_nmf operation done');
    
    % ----------------------- 4. Parsing Procedure ---------------------
    Wtopk = {}; Htopk = {}; DocTopk = {}; Wtopk_idx = {}; Wtopk_score={}; Topic_score={};    
    [ Wtopk,Htopk,DocTopk,Wtopk_idx,Wtopk_score,Topic_score,Wtopk_num] = parsenmf(W,H,dict{1},topk);
    
    disp('4. parsing operation done');
    %------------------------ 5. making exclusive score ---------------
    
    topk_num = Wtopk_num' ; topk_score = Wtopk_score'; ttopk = Wtopk(:);
    numt=1; List_of_topics = {}; num_of_topics =[]; Score_of_topics ={};
    cnumt=1; List_of_ctopics = {}; num_of_ctopics = []; Score_of_ctopics ={};
    Disc_topics = []; Com_topics = [];
    NS_Mtx_YD=cell(1,1) ; YD = {}; NS_Mtx_YC=cell(1,1); YC={};
    Count_YD = cell(1,1); Count_YC =cell(1,1); count_y = []; count_yc = [];
    
    Wsort = cell(10,1);
    for i=1:10
        Wsort{i} =  sort(W(:,i),'descend');
    end
    
    for j=1:5  
        for i=1:topk
            if(Wsort{j}(i) > 1e-5)
                List_of_topics(numt) = ttopk((j-1)*10 + i);
                num_of_topics(numt) = topk_num(j,i);
                Score_of_topics{numt} = topk_score{j,i};
                numt = numt+1;
            end
        end
    end
    
    for j=6:10  
        for i=1:topk
            if(Wsort{j}(i) > 1e-5)
                List_of_ctopics(cnumt) = ttopk((j-1)*10 + i);
                num_of_ctopics(cnumt) = topk_num(j,i);
                Score_of_ctopics{cnumt} = topk_score{j,i};
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
    
    for i=1:10
        YD{i} = Disc_topics{i,2};
        YC{i} = Com_topics{i,2};
    end
    

    for j = 1:10
        NS_Mtx_YD{1} = [ NS_Mtx_YD{1}; NS_Mtx(YD{j},:) ];
        NS_Mtx_YC{1} = [ NS_Mtx_YC{1}; NS_Mtx(YC{j},:) ];
    end


    Count_YD{1} = NS_Mtx_YD{1}~=0,2;
    Count_YC{1} = NS_Mtx_YC{1}~=0,2;
    count_yc(1) = sum(sum(Count_YC{1},2));
    count_yd(1) = sum(sum(Count_YD{1},2));

    
    disc_pro = count_yd(1);
    comm_pro = count_yc(1);
    
    disp('5-2. getting exclusiveness score done');

   %---------- Making the Outputs
   wtopk_score = {}; topic_score = {};
   Topics = {}; Topic_num = [];
   for i = 1:k
       for j = 1:topk
           if  ( topk_score{i,j} > 1e-6 )
               Topics{(i-1)*5+j} = ttopk{ (i-1)*10 +j };
               wtopk_score{(i-1)*5+j} = topk_score{i,j};
               Topics_num((i-1)*5+j) = topk_num(i,j);
           else
               Topics{(i-1)*10+j} = '';
               wtopk_score{(i-1)*5+j} = 0;
           end
       end
   end
   
   NS_Mtx_FR = cell(1,1);
   Freq_words = cell(1,1);
   for i = 1:k
       for j = 1:topk
           NS_Mtx_FR{1} = [ NS_Mtx_FR{1}; NS_Mtx(topk_num(i,j),:) ];
       end
   end
   
    Freq_words{1} = sum(NS_Mtx_FR{1},2);
   
   for i=1:k
    topic_score{i} = Topic_score(i);
   end

   xcl_score = (disc_pro)/(disc_pro+comm_pro)

    
   disp('6. making outputs done');
   disp('------------- Complete ------------- ');
    
end
