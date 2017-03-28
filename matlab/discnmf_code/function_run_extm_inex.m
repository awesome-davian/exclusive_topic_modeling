function [topics, word_score, topic_score] = function_run_extm_inex(mtx_name, xcl_value, stop_words,...    
                                                                          in_words_str, ex_words_str, voca, k, topk)

    topics = {}; word_score = []; topic_score = []; xcl_score = 0;

    min_row = 50;
    
    dict = voca';

    size(dict);

    nmtx_map = evalin('base','spatial_nmtx_map');
    mtx_name
    if isKey(nmtx_map, {mtx_name}) == 0
      return
    end
    nmtx = values(nmtx_map, {mtx_name});
    nmtx = cell2mat(nmtx);

    in_words_idx = find(ismember(dict, in_words_str))
    ex_words_idx = find(ismember(dict, ex_words_str))

    in_mtx_idx = find(ismember(nmtx(:,1), in_words_idx));
    docs = nmtx(:,2);
    doc_idx = docs(in_mtx_idx);
    nmtx_in = nmtx(ismember(docs, doc_idx),:);

    ex_mtx_idx = find(ismember(nmtx_in(:,1), ex_words_idx));
    docs = nmtx_in(:,2);
    doc_idx = docs(ex_mtx_idx);
    nmtx_ex = nmtx_in(~ismember(docs, doc_idx),:);

    sub_nmtx = nmtx_ex;
    
    A = sub_nmtx(:,4) ~= 0;
    [row, col] = size(A)
    size_nv = sum(A(:,1));
    size_ct = row - size_nv;
    
    if size_ct < min_row
        str_disp = sprintf('center tile does not have more than %d words. size: %d', min_row, size_ct);
        disp(str_disp);
        return
    end
    
    if size_nv < min_row
        str_disp = sprintf('neighbor tile does not have more than %d words. size: %d', min_row, size_nv);
        disp(str_disp);
        return
    end

    if xcl_value == 0
      xcl_value = 0.01;
    elseif xcl_value == 1
      xcl_value = 0.99;
    end

    [topics, word_score, topic_score, xcl_score, freq_words] = function_run_extm(sub_nmtx, xcl_value, stop_words, dict, k, topk);

    topics
    word_score
    topic_score
    xcl_score
    
end
