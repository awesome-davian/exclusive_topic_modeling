function [ Wtopk,Htopk,DocTopk,Wtopk_idx,Wtopk_score,TopicScore,Wtopk_num ] = parsenmf(W,H,vocab,topk)
    %W is of size mxk
    %H is of size kxn
    Wtopk_num = [];
    k = size(W,2);      % k <- num of topics
    Wtopk=cell(min([size(W,1) topk*2]),k); % create empty matrix of size, topk x k, for storing
    Wtopk_idx = zeros(min([size(W,1) topk*2]),k);
    Wtopk_score = cell(min([size(W,1) topk*2]),k);
    
    n = size(H,2);      % n <- num of documents
    Htopk=zeros(min([topk size(W,2)]),n); % zeroes of k x 512

    sum_w=zeros(k);

    %generate topk words based on W
    for i=1:k
        [sorted_w,idx]=sort(W(:,i),'descend');
        sum_w(i) = sum(W(:,i));
        for j=1:topk*2
            Wtopk{j,i}=vocab{ idx(j) };
            Wtopk_num(j,i) = idx(j);
            Wtopk_idx(j,i) = idx(j);
            Wtopk_score{j,i} = sorted_w(j)/sum_w(i);
        end
    end

    sum_A=zeros(k:1);
    TopicScore=zeros(k:1);
    
    for i=1:k
        sum_A(i) = sum(H(i,:))*sum_w(i);
    end

    sum_topic = sum(sum_A(:));
    
    for i=1:k
        TopicScore(i) = sum_A(i)/sum_topic;
    end

    %find top k topics for every document/tweet based on H
    for j=1:n
        [~,idx]=sort(H(:,j),'descend');
        Htopk(:,j)=idx(1:min([topk size(W,2)]));
    end

    DocTopk = zeros(min([topk size(H,2)]),k);

    for j=1:k
        [~,idx]=sort(H(j,:),'descend');
        DocTopk(:,j) = idx(1:min([topk size(H,2)]));
    end
end

