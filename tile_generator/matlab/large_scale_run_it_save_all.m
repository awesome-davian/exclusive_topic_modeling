
clear all;
% 
% fp = fopen('data/voca/voca_131103-131105');
% glob_data = textscan(fp,'%s %d');
% fclose(fp);
% glob_dict = glob_data(:,1);
tic
k = 5;
topk = 5;

fp = fopen('data/131103-131105/voca/voca');
voc_temp = textscan(fp,'%s %d');
fclose(fp);
dict = voc_temp(:,1);

spatial_nmtx_dir = './data/131103-131105/nmtx/spatial/';
temporal_nmtx_dir = './data/131103-131105/nmtx/temporal/';
original_mtx_dir = './data/131103-131105/mtx/';
basic_address_voc = './data/131103-131105/voca/voca';

% Stop Words
Stop_words = {'http','gt','ye','wa','thi','ny','lt','im','ll','ya','rt','ha','lol','ybgac','ve','destexx','ur','mta','john','kennedi','st','wat','atl',' '...
    'dinahjanefollowspre','nj ','york','nk','ili','bx','idk','doe','rn', '  ','pg','dimezthebulli','wu'};

save_dir='./data/131103-131105/';

%--------------------------------------------------------------------------
% NMF using spatial neighbor

dir_data = dir(spatial_nmtx_dir);
dir_idx = [dir_data.isdir];
file_list = {dir_data(~dir_idx).name}';

[list_len,~] = size(file_list);
list_len;


% opmode = 0;
% for idx = 1:size(file_list)
%     
%     file_name = file_list{idx};
%     
%     if strncmp(file_name, 'mtx_', 4) == 1
%         v = strsplit(file_name, '_');
%         type = v{1};
%         year = v{2};
%         day = sscanf(v{3}, 'd%d');
%         level = v{4};
%         x = v{5};
%         y = v{6};
%         
%         file_path = strcat(spatial_nmtx_dir, file_name);
%         
%         mtx = load(file_path);
%         xcl_value = 0;
%         for xcl = 1:6
%             
%             xcl_value = (xcl - 1) / 5;
%             if xcl_value == 0
%                 xcl_value = 0.01;
%             end
%             if xcl_value == 1
%                 xcl_value = 0.99;
%             end
%           
%             [Topics,word_score,topic_score,xcl_score,Freq_words] = function_run_extm_updated0316(mtx, xcl_value, Stop_words, dict, k, topk);
%         
%             save_all(save_dir, file_name, xcl_value, k, topk, Topics, topic_score, word_score, xcl_score, Freq_words, opmode);
%         end
%         
%         clear mtx
%     end
%     
%     str_disp = sprintf('NMF using spatial neighbor for %s complete.[%d/%d]', file_name, idx, list_len);
%     disp(str_disp);
% end



%--------------------------------------------------------------------------
% NMF using temporal neighbor

dir_data = dir(temporal_nmtx_dir);
dir_idx = [dir_data.isdir];
file_list = {dir_data(~dir_idx).name}';

[list_len,~] = size(file_list);
list_len;

opmode = 1;
for idx = 1:size(file_list)
    
    file_name = file_list{idx};
    
    str_disp = sprintf('NMF using temporal neighbor for %s in progress...[%d/%d]', file_name, idx, list_len);
    disp(str_disp);
    
    if strncmp(file_name, 'mtx_', 4) == 1
        v = strsplit(file_name, '_');
        type = v{1};
        year = v{2};
        day = sscanf(v{3}, 'd%d');
        int_day = str2double(day);
        level = v{4};
        x = v{5};
        y = v{6};
        
        file_path = strcat(temporal_nmtx_dir, file_name);
        
        mtx = load(file_path);
        
        % check if the center tile has any neighbor
        sum_nvr = sum(mtx(:,4));
        if sum_nvr <= 0
            [row, col] = size(mtx);
            str_disp = sprintf('%s does not have any neighbor tiles. Mtx Size: (%d, %d) [%d/%d]', file_name, row, col, idx, list_len);
            disp(str_disp);
            continue
        end
        
        xcl_value = 0;
        for xcl = 1:6
            
            xcl_value = (xcl - 1) / 5;
            if xcl_value == 0
                xcl_value = 0.01;
            end
            if xcl_value == 1
                xcl_value = 0.99;
            end
          
            [Topics,word_score,topic_score,xcl_score,Freq_words] = function_run_extm_updated0316(mtx, xcl_value, Stop_words, dict, k, topk);
        
            save_all(save_dir, file_name, xcl_value, k, topk, Topics, topic_score, word_score, xcl_score, Freq_words, opmode);
        end
        
        clear mtx
    end
    
    str_disp = sprintf('NMF using temporal neighbor for %s complete.[%d/%d]', file_name, idx, list_len);
    disp(str_disp);
end

%--------------------------------------------------------------------------
% Save W for Warm Start

dir_data = dir(spatial_nmtx_dir);
dir_idx = [dir_data.isdir];
file_list = {dir_data(~dir_idx).name}';

[list_len,~] = size(file_list);
list_len;

for idx = 1:size(file_list)
    
    file_name = file_list{idx};
    
    if strncmp(file_name, 'mtx_', 4) == 1
        v = strsplit(file_name, '_');
        type = v{1};
        year = v{2};
        day = sscanf(v{3}, 'd%d');
        level = v{4};
        x = v{5};
        y = v{6};
        
        file_path = strcat(spatial_nmtx_dir, file_name);
        
        mtx = load(file_path);
        
        [WC] = func_warm_start_W(mtx, dict, k, topk);
        
        save_w(save_dir, file_name, WC);
        
        clear mtx
    end
    
    str_disp = sprintf('Createing W for %s complete.[%d/%d]', file_name, idx, list_len);
    disp(str_disp);
end


elapsed_time = toc
