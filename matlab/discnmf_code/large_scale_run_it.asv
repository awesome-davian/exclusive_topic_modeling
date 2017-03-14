
fp = fopen('voca_131103-131105');
glob_data = textscan(fp,'%s %d');
fclose(fp);
glob_dict = glob_data(:,1);

addpath('./data/mtx_neighbor/131103-131105');

% dic_data_0252 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0252(:,1);
% dic_data_0253 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0253(:,1);
% dic_data_0352 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0252(:,1);
% dic_data_0353 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0253(:,1);
% dic_data_0354 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0254(:,1);
% dic_data_0453 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0253(:,1);
% dic_data_0454 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0254(:,1);
% dic_data_0455 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0255(:,1);
% dic_data_0554 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0254(:,1);
% dic_data_0555 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0255(:,1);
% dic_data_0556 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0256(:,1);
% dic_data_0653 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0253(:,1);
% dic_data_0654 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0254(:,1);
% dic_data_0655 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0255(:,1);
% dic_data_0656 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0256(:,1);
% dic_data_0657 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0257(:,1);
% dic_data_0658 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0258(:,1);
% dic_data_0754 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0254(:,1);
% dic_data_0755 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0255(:,1);
% dic_data_0756 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0256(:,1);
% dic_data_0757 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0257(:,1);
% dic_data_0758 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0258(:,1);
% dic_data_0854 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0254(:,1);
% dic_data_0855 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0255(:,1);
% dic_data_0856 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0256(:,1);
% dic_data_0857 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0257(:,1);
% dic_data_0858 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0258(:,1);
% dic_data_0954 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0254(:,1);
% dic_data_0955 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0255(:,1);
% dic_data_0956 = load('./data/mtx_neighbor/131103-131105/12_voc/308/voca_2013_d308_12_1202_2552'); dict0252 = dic_data_0256(:,1);


M_0252 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1202_2552');
M_0253 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1202_2553');
M_0352 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1203_2552');
M_0353 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1203_2553');
M_0354 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1203_2554');
M_0453 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1204_2553');
M_0454 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1204_2554');
M_0455 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1204_2555');
M_0554 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1205_2554');
M_0555 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1205_2555');
M_0556 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1205_2556');
M_0653 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1206_2553');
M_0654 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1206_2554');
M_0655 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1206_2555');
M_0656 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1206_2556');
M_0657 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1206_2557');
M_0658 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1206_2558');
M_0754 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1207_2554');
M_0755 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1207_2555');
M_0756 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1207_2556');
M_0757 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1207_2557');
M_0758 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1207_2558');
M_0854 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1208_2554');
M_0855 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1208_2555');
M_0856 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1208_2556');
M_0857 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1208_2557');
M_0858 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1208_2558');
M_0954 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1209_2554');
M_0955 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1209_2555');
M_0956 = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1209_2556');


% make them modular. 
function [xcl_value] = get_xclness_neigh(Mat)

    % 1. make them into sparse matrix
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
    
    for i = 1:size(ncols,2)-1
        if ncols(i+1) == 0
            continue
        else
        NB{i} = NB_ALL{i+1};
        N_ON(i) = 1;
        end
    end
    
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
    
    
    
    
    % 2. get the common criterion with the words that are shared by all of the
    %    neighboring matrices. 
    % 3. Get the distribution.  
    % 4. With the given tiles, calculate the exclusiveness using
    %     K-divergence.
    % 5. return exclusiveness
end
