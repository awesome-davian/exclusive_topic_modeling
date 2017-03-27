
clear all;
% 
% fp = fopen('data/voca/voca_131103-131105');
% glob_data = textscan(fp,'%s %d');
% fclose(fp);
% glob_dict = glob_data(:,1);
tic
k = 5;
topk = 5;

date_range = '160414-160421';

spatial_nmtx_dir = sprintf('./data/%s/nmtx/spatial/', date_range);
temporal_nmtx_dir = sprintf('./data/%s/nmtx/temporal/', date_range) ;
mtx_dir = sprintf('./data/%s/mtx/', date_range);
basic_address_voc = sprintf('./data/%s/voca/voca', date_range);
save_dir= sprintf('./data/%s/', date_range);

fp = fopen(basic_address_voc');
voc_temp = textscan(fp,'%s %d');
fclose(fp);
dict = voc_temp(:,1);

do_spatial = 0
do_temporal = 1
do_w = 0

min_row = 50


% Stop Words
Stop_words = {'http','gt','ye','wa','thi','ny','lt','im','ll','ya','rt','ha','lol','ybgac','ve','destexx','ur','mta','john','kennedi','st','wat','atl',' '...
    ,'dinahjanefollowspre','nj ','york','nk','ili','bx','idk','doe','rn', '  ','pg','dimezthebulli','wu','crack','suck','lmaoo','lmfaoo','kt','ku','kw','ky','kx','kz','la','ac','acc','ae','af','ag','ahh','ah','ahaha','ahhh','ahhhh','aj','ak','al'...
    ,'itskimmiehey','guh','njcl','tho','de','mia','yow','alla','vamo','meg','charli','charl','anthoni','justjo','sucker','sexfactsoflif','woohoo','byeee','tmm','manddddddd','aw','rb','le','el','fsu'};

% 'ain', 



%--------------------------------------------------------------------------
% NMF using spatial neighbor

dir_data = dir(spatial_nmtx_dir);
dir_idx = [dir_data.isdir];
file_list = {dir_data(~dir_idx).name}';

[list_len,~] = size(file_list);
list_len;

if do_spatial == 1
    opmode = 0;
    for idx = 1:size(file_list)
        
%         if idx ~= 234
%             continue
%         end

        file_name = file_list{idx};
        
        str_disp = sprintf('[%s]NMF using spatial neighbor for %s in progress...[%d/%d]', date_range, file_name, idx, list_len);
        disp(str_disp);
        
%         if strncmp(file_name, 'mtx_2013_d314_13_2408_5110', length(file_name)) ~= 1
%             continue
%         end

        

        if strncmp(file_name, 'mtx_', 4) == 1
            v = strsplit(file_name, '_');
            type = v{1};
            year = v{2};
            day = sscanf(v{3}, 'd%d');
            level = v{4};
            x = v{5};
            y = v{6};
            
            file_path = strcat(spatial_nmtx_dir, file_name);
            nmtx = load(file_path);
            
            A = nmtx(:,4) ~= 0;
            [row, col] = size(A)
            size_nv = sum(A(:,1));
            size_ct = row - size_nv;
            
            if size_ct < min_row
                str_disp = sprintf('center %s does not have more than %d words. size: %d [%d/%d]', file_name, min_row, size_ct, idx, list_len);
                disp(str_disp);
                continue
            end
            
            if size_nv < min_row
                str_disp = sprintf('neighbor %s does not have more than %d words. size: %d [%d/%d]', file_name, min_row, size_nv, idx, list_len);
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

                [Topics,word_score,topic_score,xcl_score,Freq_words] = function_run_extm(nmtx, xcl_value, Stop_words, dict, k, topk);

                save_all(save_dir, file_name, xcl_value, k, topk, Topics, topic_score, word_score, xcl_score, Freq_words, opmode);
            end

            clear nmtx
        end

        str_disp = sprintf('[%s]NMF using spatial neighbor for %s complete.[%d/%d]', date_range, file_name, idx, list_len);
        disp(str_disp);
    end
end



%--------------------------------------------------------------------------
% NMF using temporal neighbor

dir_data = dir(temporal_nmtx_dir);
dir_idx = [dir_data.isdir];
file_list = {dir_data(~dir_idx).name}';

[list_len,~] = size(file_list);
list_len;
size(file_list)
if do_temporal == 1
    opmode = 1;
    for idx = 1:size(file_list)
        
                
        if idx < 39978
            continue
        end

        file_name = file_list{idx};
        
%         if strncmp(file_name, 'mtx_2013_d314_13_2408_5110', length(file_name)) ~= 1
%             continue
%         end

        

        str_disp = sprintf('[%s]NMF using temporal neighbor for %s in progress...[%d/%d]', date_range, file_name, idx, list_len);
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

            nmtx = load(file_path);
            
            C = unique(nmtx(nmtx(:,4)~=1,1));
            N = unique(nmtx(nmtx(:,4)~=0,1));
            
            [size_ct, a] = size(C);
            [size_nv, a] = size(N);
            

%             A = nmtx(:,4) ~= 0;
%             [row, col] = size(A);
%             size_nv = sum(A(:,1));
%             size_ct = row - size_nv;
            
            if size_ct < min_row
                str_disp = sprintf('center %s does not have more than %d words. size: %d [%d/%d]', file_name, min_row, size_ct, idx, list_len);
                disp(str_disp);
                continue
            end
            
            if size_nv < min_row
                str_disp = sprintf('neighbor %s does not have more than %d words. size: %d [%d/%d]', file_name, min_row, size_nv, idx, list_len);
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

                [Topics,word_score,topic_score,xcl_score,Freq_words] = function_run_extm(nmtx, xcl_value, Stop_words, dict, k, topk);

                save_all(save_dir, file_name, xcl_value, k, topk, Topics, topic_score, word_score, xcl_score, Freq_words, opmode);
            end

            clear nmtx
        end

        str_disp = sprintf('[%s]NMF using temporal neighbor for %s complete.[%d/%d]', date_range, file_name, idx, list_len);
        disp(str_disp);
    end
end
    
    
%--------------------------------------------------------------------------
% Save W for Warm Start

% dir_data = dir(spatial_nmtx_dir);
% dir_idx = [dir_data.isdir];
% file_list = {dir_data(~dir_idx).name}';
% 
% [list_len,~] = size(file_list);
% list_len;
% 
% if do_w == 1
%     for idx = 1:size(file_list)
% 
%         file_name = file_list{idx};
% 
%         if strncmp(file_name, 'mtx_', 4) == 1
%             v = strsplit(file_name, '_');
%             type = v{1};
%             year = v{2};
%             day = sscanf(v{3}, 'd%d');
%             level = v{4};
%             x = v{5};
%             y = v{6};
% 
%             file_path = strcat(spatial_nmtx_dir, file_name);
% 
%             nmtx = load(file_path);
% 
%             [WC] = func_warm_start_W(nmtx, dict, k, topk);
% 
%             save_w(save_dir, file_name, WC);
% 
%             clear nmtx
%         end
% 
%         str_disp = sprintf('Createing W for %s complete.[%d/%d]', file_name, idx, list_len);
%         disp(str_disp);
%     end
% end


elapsed_time = toc
