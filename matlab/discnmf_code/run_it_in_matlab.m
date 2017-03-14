% clear work space
clear;
clear all;

% topk and k;
topk=10;
k=5;
% choose exclusiveness
exclusiveness = 0.5;

% add path to the libradata folder

addpath('./data/voca');
addpath('./data/mtx_neighbor/131103-131105');

% the global dictionary
fp = fopen('voca_131103-131105');
glob_data = textscan(fp,'%s %d');
fclose(fp);
glob_dict = glob_data(:,1);
%glob_data = load('voca_131103-131105');
%local_data
loc_data = load('./data/mtx_neighbor/131103-131105/12_voc/voca_2013_d308_12_1202_2552');
dict = loc_data(:,1);
% choose neighboring_matrix
NEIGH_tdm = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1202_2552');
NEIGH_tdm;



NB = cell(1,8);
Ntdms = cell(1,9);
ATDMs = cell(9,1);
N_ON = zeros(8,1);
neigh_size = size(NEIGH_tdm,1);
% decomposition into cells

% 1. getting information on the neighboring matrix

kk =1;
 j = NEIGH_tdm(1,4);
 NM_num(1) = j;
   for i = 1:neigh_size
     if( NEIGH_tdm(i,4) ~= j )
         Nei_Length(kk) = i-1; 
         j = NEIGH_tdm(i,4);
         kk = kk+1;
         NM_num(kk) = j;
     end
   end
   Nei_Length = [Nei_Length neigh_size];
   NM_num;
   size(NM_num,2);
   
% 2. Decomposing them

s =1;
NEIGH_tdm(1:Nei_Length(1),1:3);
for i = 1:(size(NM_num,2))
    Ntdms{NM_num(i)+1} = NEIGH_tdm(s:Nei_Length(i),1:3);
    s = Nei_Length(i)+1;
end


[nrows, ncols] = cellfun(@size, Ntdms);

    freq=0;
    NB_ALL = cell(9,1);

    for i = 1:9
        NB_ALL{i} = [];
        if ncols(i) == 0
            continue
        else
        freq=freq+1;
        Tdm_cell = Ntdms{1, i};
        %Mtx = cell2mat( cellfun( @(x) cell2mat(x), Tdm_cell, 'UniformOutput', 0 ) );
        Mtx = Ntdms{1,i};
        num_tdm(i) = max(Mtx(:,2));
        % max(Mtx(:,2))
        NB_ALL{i} = sparse(Mtx(:,1),Mtx(:,2),Mtx(:,3),size(dict,1),max(Mtx(:,2)));
       % NB_ALL{i} = sparse(Mtx(:,1),Mtx(:,2),Mtx(:,3),size(dict,1), max(Mtx(:,2)) );
       % NB_ALL{i}(isnan(NB_ALL{i}))=1e-16;

        % end of sparsing. The end 
        end
    end


    AC = NB_ALL{1};

    N_size=num_tdm./size(AC,2);     
    
    for i = 1:size(ncols,2)-1
        if ncols(i+1) == 0
            continue
        else
        NB{i} = NB_ALL{i+1};
        N_ON(i) = 1;
        end
    end
    
    
    N_ON;
    clear tdm;

    % 3. Normalisation (why?)
    
    disp('1');
    NB_norm = cell(8,1);
    AC_norm = bsxfun(@rdivide,AC,sqrt(sum(AC.^2))); %NaN Value going in. 
    AC_norm(isnan(AC_norm))=1e-16;
    disp('2');
    for c = 1:8
        if (N_ON(c) == 0)
            continue
        else
            disp('3');
            NB_norm{c}=bsxfun(@rdivide,NB{c},sqrt(sum(NB{c}.^2)));
            NB_norm{c}(isnan(NB_norm{c}))=1e-16;
        end
    end

    
    Euclid_dist_mat = [1.414; 1; 1.414; 1; 1; 1.414 ;1; 1.414];
    N_ON = N_ON .* Euclid_dist_mat;
    
    % 4. NMF
    
    %   i) initialising
    % scaling
    
    xcl = exclusiveness; 
    
    % AL = ones(1,8)./(N_size+1e-16);
    % AL(isnan(AL))=1e-16;
    % AL = 20 + 80 * bsxfun(@rdivide,AL',sum(AL'));
    % BE = ones(1,8)./(N_size+1e-16);
    % BE(isnan(BE))=1e-16;
    % BE = 20 + 80 * bsxfun(@rdivide,BE',sum(BE'));
    % AL = bsxfun(@rdivide,AL',sum(AL'))
    % BE = bsxfun(@rdivide,BE',sum(BE'))

    % Scaling
    % N_size
    AL = ones(8,1);
    BE = ones(8,1);
    
    for i = 1:8
        if N_ON(i) == 0
            AL(i) = 0;
            BE(i) = 0;
        
        else
            AL(i) = AL(i)/N_size(i+1);
            BE(i) = BE(i)/N_size(i+1);
        end

    end
    AL = AL./sum(AL);
    BE = BE./sum(BE);
    
    for i = 1:8
        if N_ON(i) == 0
            continue
        else
            AL(i) = 30 + 70*AL(i);
            BE(i) = 30 + 70*BE(i);
        end
    end

    AL = (1-xcl) * AL/(10*sum(AL));
    BE = xcl * BE/(10*sum(BE));

    disp('4');
    [WC,WN,HC,HN] = xcl_nmf(AC_norm,NB_norm,k*2,k,30,AL,BE,freq,N_ON); %NB coming in cell format. 
    %[WC,WN,HC,HN] = xcl_nmf(AC,NB,k*2,k,30,AL,BE);
    % 5. Displaying the key words (parsing)
    disp('12')
    Wtopk = {}; Htopk = {}; DocTopk = {}; Wtopk_idx = {}; %Wtopk_score={}; Topic_score={};
    [ Wtopk,Htopk,DocTopk,Wtopk_idx,Wtopk_score,Topic_score] = parsenmf(WC,HC,dict,glob_dict,topk);
    disp('13')
    WCsort1 = sort(WC(:,1),'descend');
    WCsort2 = sort(WC(:,2),'descend');
    WCsort3 = sort(WC(:,3),'descend');
    WCsort4 = sort(WC(:,4),'descend');
    WCsort5 = sort(WC(:,5),'descend');
    WCsort6 = sort(WC(:,6),'descend');
    WCsort7 = sort(WC(:,7),'descend');
    WCsort8 = sort(WC(:,8),'descend');
    WCsort9 = sort(WC(:,9),'descend');
    WCsort10 = sort(WC(:,10),'descend');
    [ WCsort1(1:10) WCsort2(1:10) WCsort3(1:10) WCsort4(1:10) WCsort5(1:10) ] 
    [ WCsort6(1:10) WCsort7(1:10) WCsort8(1:10)  WCsort9(1:10) WCsort10(1:10) ]
    
    ttopk = Wtopk(:);
    Topics = ttopk(1:k*topk)';
    
    

    tWtopk_score = Wtopk_score(:);
    wtopk_score = tWtopk_score(1:k*topk)';
    
    tTopic_score = Topic_score;
    topic_score = tTopic_score(1:k)'

    Topic_score
    sum(Topic_score)
    A = sum(sum(WC(:,1:5)))
    B = sum(sum(WC(:,5:10)))
    excl_score = A / B
% clean up variables
clear nrows;
clear ncols;
clear ntdms;

