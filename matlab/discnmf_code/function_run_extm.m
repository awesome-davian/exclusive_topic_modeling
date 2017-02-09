function [Topics, wtopk_score, topic_score] = function_run_extm(Tdm, Ntdms, exclusiveness, Voca, k, topk)
    % 0. the term definitions:
    %   - k: how many clusters (the columns in W) shall be used?
    %   - topk: how many topics will be taken in each clusters. 
    %   - so the frequency of output words has to be k*topk in total. 
    %   - topics has to be in k*topk matrix form, anbd So the Topic_score has to
    %   - be also in k*topk matrix form. 

    % 1. Addpath needed
    % addpath('./library/nmf');     
    % addpath('./library/ramkis');
    % addpath('./library/peripheral');
    % addpath('./library/discnmf');

    % 2. Sparsing
    dict = Voca;
    ATDMs = cell(9,1);
%    ATDMs{1} = Tdm;
    [nrows, ncols] = cellfun(@size, Ntdms);


    % ncols --> The actual length of each neighbor tile
    ATDMs{1} = Tdm;
    max_tdm_m = max(Tdm(:,1));
    max_tdm_n = max(Tdm(:,2));
     for i = 1:8

            if ncols(i) == 0
                continue
            else

            Tdm_cell = Ntdms{1, i};
            Mtx = cell2mat( cellfun( @(x) cell2mat(x), Tdm_cell, 'UniformOutput', 0 ) );
            Ntdm = reshape(Mtx, 3, [])';
            num_tdm_m = max(Ntdm(:,1));
            num_tdm_n = max(Ntdm(:,2));
          %  num_tdm(i) = max(Ntdm(:,2));
            max_tdm_m = max(max_tdm_m,num_tdm_m);
          %  max_tdm_n = max(max_tdm_n,num_tdm_n);
            end
    end
    %num_tdm
    freq=0;
    NB = cell(8,1);
    for i = 1:8
        NB{i} = [];
        if ncols(i) == 0
            continue
        else
        freq=freq+1;
        Tdm_cell = Ntdms{1, i};
        Mtx = cell2mat( cellfun( @(x) cell2mat(x), Tdm_cell, 'UniformOutput', 0 ) );
        Ntdm = reshape(Mtx, 3, [])';
        num_tdm(i) = max(Ntdm(:,2));
        NB{i} = sparse(Ntdm(:,1),Ntdm(:,2),Ntdm(:,3),max_tdm_m, max(Ntdm(:,2)) );
        NB{i}(isnan(NB{i}))=1e-16;

        % end of sparsing. The end 
        end
    end

    N_size=num_tdm./max_tdm_n;    
    AC = sparse(Tdm(:,1),Tdm(:,2),Tdm(:,3),max_tdm_m, max(Tdm(:,2)) );
    AC(isnan(AC))=1e-16;
 
    clear tdm;

    
    % 3. Normalisation (why?)
    NB_norm = cell(8,1);
    AC_norm = bsxfun(@rdivide,AC,sqrt(sum(AC.^2))); %NaN Value going in. 
    AC_norm(isnan(AC_norm))=1e-16;
    for c = 1:8
        if (ncols(c) == 0)
            continue
        else
            NB_norm{c} = bsxfun(@rdivide,NB{c},sqrt(sum(NB{c}.^2)));
            NB_norm{c}(isnan(NB_norm{c}))=1e-16;
        end
    end
    
    % 4. NMF
    %   i) initialising
    % scaling
    xcl = exclusiveness; 
    AL = ones(1,8)./N_size;
    AL = 20+ 80 * bsxfun(@rdivide,AL',sum(AL'));
    BE = ones(1,8)./N_size;
    BE = 20+ 80 * bsxfun(@rdivide,BE',sum(BE'));
    AL = bsxfun(@rdivide,AL',sum(AL'));
    BE = bsxfun(@rdivide,BE',sum(BE'));


    AL = (1-xcl)*AL; BE = xcl*BE;
    
    %   ii) doing the initialisation
       [WC,WN,HC,HN] = xcl_nmf(AC_norm,NB_norm,k*2,k,20,AL,BE,freq); %NB coming in cell format. 
    %[WC,WN,HC,HN] = xcl_nmf(AC,NB,k*2,k,30,AL,BE);
    % 5. Displaying the key words (parsing)
    Wtopk = {}; Htopk = {}; DocTopk = {}; Wtopk_idx = {}; %Wtopk_score={}; Topic_score={};
    [ Wtopk,Htopk,DocTopk,Wtopk_idx,Wtopk_score,Topic_score] = parsenmf(WC,HC,dict,topk);
    % WCsort1 = sort(WC(:,1),'descend');
    % WCsort2 = sort(WC(:,2),'descend');
    % WCsort3 = sort(WC(:,3),'descend');
    % WCsort4 = sort(WC(:,4),'descend');
    % WCsort5 = sort(WC(:,5),'descend');
    % WCsort6 = sort(WC(:,6),'descend');
    % WCsort7 = sort(WC(:,7),'descend');
    % WCsort8 = sort(WC(:,8),'descend');
    % WCsort9 = sort(WC(:,9),'descend');
    % WCsort10 = sort(WC(:,10),'descend');
    % WCsort1(1:5)
    % WCsort2(1:5)
    % WCsort3(1:5)
    % WCsort4(1:5)
    % WCsort5(1:5)
    % WCsort6(1:6);
    % WCsort7(1:7);
    % WCsort8(1:8);
    % WCsort9(1:9);
    % WCsort10(1:10);
    ttopk = Wtopk(:);
    Topics = ttopk(1:k*topk)';

    tWtopk_score = Wtopk_score(:);
    wtopk_score = tWtopk_score(1:k*topk)';
    
    tTopic_score = Topic_score;
    topic_score = tTopic_score(1:k)'; 

    Topic_score;
    Wtopk(:,:);

    
% clean up variables
clear nrows;
clear ncols;
clear ntdms;

end

% return values
% topics = ''
% wtopk_score = ''
% topic_score = ''
% 
