function [Topics, wtopk_score, topic_score,xcl_score] = function_run_extm(Tdm, exclusiveness, voca, k, topk)

    dict = voca;
    xcl = exclusiveness;

    disp('1. initializing variables done'); % the term format will be given in text form so you need to divide them. 
    
    
    % 2. Separating the term doc cells. 
    
    [tdm_row, tdm_cols] = cellfun(@size, Tdm);
    
    
    M_num = []; M_end = [];
    num_term = 1;
    
    a2 = Tdm(1,4)
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
    Spar_Mtx{1} = sparse(Tdm_s{1}(:,1),Tdm_s{1}(:,2),Tdm_s{1}(:,3),size(dict,1),max(Tdm_s{1}(:,2)));
    Spar_Mtx{2} = sparse(Tdm_s{2}(:,1),Tdm_s{2}(:,2),Tdm_s{2}(:,3),size(dict,1),max(Tdm_s{2}(:,2)));
    
    NS_Mtx = cell(2,1);
    for i = 1:2
        nz_doc_idx(i) = sum(Spar_Mtx{i},1) ~= 0;
        NS_Mtx{i} = Spar_Mtx{i}(:,nz_doc_idx);
    end
    nz_voc_idx(i) = ( sum(NS_Mtx{1},2) + sum(NS_Mtx{2},2) ) ~= 0;
    for i= 1:2
        NS_Mtx{i} = NS_Mtx{i}(nz_voc_idx,:);
    end
    
    disp('2. sparse matrix making done');
    
    Num_tdm = [ 1 size(NS_Mtx{2},2)/size(NS_Mtx{1},2) ];
    [AL BE] = [ (1-xcl)/Num_tdm(1) xcl/Num_tdm(2) ];
    % ------------------------ 3. NMF operation  ----------------------
    
    [WC,WN,HC,HN] = xcl_nmf(NS_Mtx{1},NS_Mtx{2},k*2,k,20,AL,BE);
    
    disp('3. disc_nmf operation done');
    
    % ----------------------- 4. Parsing Procedure ---------------------
    Wtopk = {}; Htopk = {}; DocTopk = {}; Wtopk_idx = {}; %Wtopk_score={}; Topic_score={};    
    [ Wtopk,Htopk,DocTopk,Wtopk_idx,Wtopk_score,Topic_score,Wtopk_num] = parsenmf(WC,HC,dict,voca,topk);
    
    disp('4. parsing operation done');
    
    %------------------------ 5. making exclusive score ---------------
    topk_num = Wtopc_num'; topk_score = Wtopk_score'; ttopk = Wtopk(:);
    numt=1; List_of_topics = {}; num_of_topics =[]; Score_of_topics =[];
    cnumt=1; List_of_ctopics = {}; num_of_ctopics = []; Score_of_ctopics =[];
    Disc_topics = []; Com_topics = [];
    NS_Mtx_YD = cell(2,1); YD = []; NS_Mtx_YC=cell(2,1); YC={};
    Count_Y = cell(9,1); Count_YC =cell(9,1); count_y = []; count_yc = [];
    
    WCsort = cell(10,1);
    for i=1:10
        WCsort{i} =  sort(WC(:,i),'descend');
    end
    
    for j=1:5  
        for i=1:topk
            if(WCsort{j}(i) > 1e-5)
                List_of_topics(numt) = ttopk((j-1)*10 + i);
                num_of_topics(numt) = topk_num(j,i);
                Score_of_topics(numt) = topk_score(j,i);
                numt = numt+1;
            end
        end
    end
    
    for j=6:10  
        for i=1:topk
            if(WCsort{j}(i) > 1e-5)
                List_of_ctopics(numt) = ttopk((j-1)*10 + i);
                num_of_ctopics(numt) = topk_num(j,i);
                Score_of_ctopics(numt) = topk_score(j,i);
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
        YD(i) = Disc_topics{i,2};
        YC(i) = Com_topics{i,2};
    end
    
    for i=1:2
        for j = 1:10
            NS_Mtx_YD{i} = [ NS_Mtx_YD{i}; NS_Mtx{i}(YD(j),:) ];
            NS_Mtx_YC{i} = [ NS_Mtx_YC{i}; NS_Mtx{i}(YC(j),:) ];
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
   Topics = {};
   for i = 1:k
       for j = 1:topk
           if  ( wtopk_score{i,j} > 1e-6 )
               Topics{(i-1)*10+j} = ttopk{ (i-1)*10 +j };
               wtopk_score{i,j} = topk_score{i,j};
           else
               Topics{(i-1)*10+j} = '';
               wtopk_score{i,j} = 0;
           end
       end
   end
    topic_score = tTopic_score(1:k)';
    xcl_score = (disc_pro)/(disc_pro+comm_pro);
    
    disp('6. making outputs done');
    
end
