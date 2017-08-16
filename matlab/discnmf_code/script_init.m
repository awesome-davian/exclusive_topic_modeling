clear all;

range = '131020-131110'
%range = '130701-130731'
spatial_nmtx_dir = sprintf('/scratch/salt/exclusive_topic_modeling/tile_generator/data/%s/nmtx/spatial/', range)

dir_data = dir(spatial_nmtx_dir);
dir_idx = [dir_data.isdir];
file_list = {dir_data(~dir_idx).name}';

spatial_nmtx_map = containers.Map;

[list_len,~] = size(file_list);
list_len;

for idx=1:size(file_list)
	
	file_name = file_list{idx};
 
	if strncmp(file_name, 'mtx_', 4) == 1

		file_path = strcat(spatial_nmtx_dir, file_name);
		mtx = load(file_path);
		spatial_nmtx_map(file_name) = mtx;

	end

	if mod(idx, 100) == 0
		temp_str = sprintf('loading mtx... %d/%d', idx, list_len);
		disp(temp_str);
	end

end

% temp_mtx = values(spatial_nmtx_map, {'mtx_2013_d309_13_2418_5112'})

% spatial_nmtx_map

temp_str = sprintf('loading mtx complete. total number of mtx: %d', list_len);
disp(temp_str);
