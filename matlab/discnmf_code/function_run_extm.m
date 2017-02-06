function [Topics, Wtopk_score, Topic_score] = function_run_extm(Tdm, Ntdms, exclusiveness, Voca, k, topk)
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
            max_tdm_m = max(max_tdm_m,num_tdm_m);
            max_tdm_n = max(max_tdm_n,num_tdm_n);
        end
    end


    
    NB = cell(8,1);
    for i = 1:8

        if ncols(i) == 0
            continue
        else

        Tdm_cell = Ntdms{1, i};
      %  Mtx = cell2mat( cellfun( @(x) cell2mat(x), Tdm_cell, 'UniformOutput', 0 ) );
      %  Ntdm = reshape(Mtx, 3, [])';
        NB{i} = sparse(Ntdm(:,1),Ntdm(:,2),Ntdm(:,3),max_tdm_m,max(Ntdm(:,2)) );
        NB{i}(isnan(NB{i}))=0;

        % end of sparsing. The end 
        end
    end

   AC = sparse(Tdm(:,1),Tdm(:,2),Tdm(:,3),max_tdm_m,max(Tdm(:,2)) );
   AC(isnan(AC))=0;
 
    clear tdm;

    
    % 3. Normalisation (why?)
    NB_norm = cell(8,1);
    AC_norm = bsxfun(@rdivide,AC,sqrt(sum(AC.^2))); %NaN Value going in. 
    AC_norm(isnan(AC_norm))=0;
    for c = 1:8
        if (ncols(c) == 0)
            continue
        else
            NB_norm{c} = bsxfun(@rdivide,NB{i},sqrt(sum(NB{i}.^2)));
            NB_norm{c}(isnan(NB_norm{c}))=0;
        end
    end
    
    % 4. NMF
    %   i) initialising
    rp = 7; %regularisation parameter
    xcl = exclusiveness; AL = ones(8,1); BE = ones(8,1);
    AL = (rp*(1-xcl))*AL; BE = (rp*xcl)*BE;
    
    %   ii) doing the initialisation
    [WC,WN,HC,HN] = xcl_nmf(AC_norm,NB_norm,k*2,k,30,AL,BE); %NB coming in cell format. 
    
    % 5. Displaying the key words (parsing)
    Wtopk = {}; Htopk = {}; DocTopk = {}; Wtopk_idx = {};
    [ Wtopk,Htopk,DocTopk,Wtopk_idx,Wtopk_score,Topic_score] = parsenmf(WC,HC,dict,topk);
    Topics = Wtopk
  
    
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
