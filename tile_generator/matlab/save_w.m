function [ output_args ] = save_w( dir, source_name, w)
    
    % save w --------------------------------------------------------------
    
    file_dir = strcat(dir, 'w/');
    file_name = strrep(source_name, 'mtx_', 'w_');
    
    file_path = strcat( file_dir, file_name );
    
    save(file_path, 'w')
    
%     fid =  fopen(file_path, 'w');
%     
%     nbytes = fprintf(fid, '%s\n', num2str(w));
%     fclose(fid);
    
    res = 1;
end

