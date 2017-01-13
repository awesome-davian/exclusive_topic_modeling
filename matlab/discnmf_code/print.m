function topics = print(W,U,par)
    k = par.k; dic = par.dic;
    [val,IX] = sort([W U],'descend'); topw = IX(1:10,:);
    topics = [];
    if iscell(dic)
        num = par.num1; num2 = par.num2;
        for i = 1:k
            topics = [topics [num2cell(num(topw(:,i),:)) dic(topw(:,i),:);num2cell(1) '----'; num2cell(num2(topw(:,i+k),:)) dic(topw(:,i+k),:)]];
        end
    else
        digit = floor(log10(max([par.num1;par.num2])))+1;
        num = num2str(par.num1,['%0' num2str(digit) 'd']); num2 = num2str(par.num2,['%0' num2str(digit) 'd']); 
        len = (size(dic,2)+1+size(num,2));
        for i = 1:k
            topics = [topics [num(topw(:,i),:),repmat(' ',10,1),dic(topw(:,i),:); repmat('-',1,len); num2(topw(:,i+k),:),repmat(' ',10,1),dic(topw(:,i+k),:)]];
        end
    end
    topics
    disp('pairwise topic similarity (or inner product) matrix')
    disp(W'*U)
end