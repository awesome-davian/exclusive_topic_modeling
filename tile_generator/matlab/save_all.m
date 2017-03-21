function [ output_args ] = save_data( dir, source_name, xcl_value, k, topk, topic, topic_score, word_score, xcl_score, word_freq, opmode)
    
    res = 0;
    
    % save topics ---------------------------------------------------------
    if opmode == 0
        file_dir = strcat(dir, 'topics/spatial/');
    elseif opmode == 1
        file_dir = strcat(dir, 'topics/temporal/');
    end
    file_name = strrep(source_name, 'mtx_', 'topics_');
    
    xcl_value_int = round(xcl_value * 5);
    file_path = strcat( file_dir, file_name, '_',  num2str(xcl_value_int));
    fid =  fopen(file_path, 'w');
    
    for i = 1:k
        nbytes = fprintf(fid, '%s\n', num2str(topic_score{i}(:)));
        for j = 1:topk
            idx = (i-1)*k + j;
            topic{idx}(:)';
            nbytes = fprintf(fid, '%s\t%s\t%s\n', topic{idx}(:)', num2str(word_freq{1,2}(idx)), num2str(word_score{idx}(:)));
        end
    end
    fclose(fid);
    
    % save xcl_score ------------------------------------------------------
    if opmode == 0
        file_dir = strcat(dir, 'xscore/spatial/');
    elseif opmode == 1
        file_dir = strcat(dir, 'xscore/temporal/');
    end
    
    file_name = strrep(source_name, 'mtx_', 'xscore_');
    
    file_path = strcat( file_dir, file_name );
    fid =  fopen(file_path, 'w');
    
    nbytes = fprintf(fid, '%s\n', num2str(xcl_score(:)));
    fclose(fid);
    
    % save w --------------------------------------------------------------
    
    res = 1;
end

