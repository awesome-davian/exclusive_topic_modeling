function [cos,euc] = pwdist(X,w)
    X = normc(X);
    w = reshape(w,[1,length(w)]);
    
%     distfun = @(XI,XJ) abs(1-XJ*diag(w)*XI');
%     cos = squareform(pdist(X',distfun));
%     distfun = @(XI,XJ) sum(repmat(w,size(XJ,1),1).*bsxfun(@minus,XJ,XI).^2,2);
%     euc = squareform(pdist(X',distfun));
    
    X = bsxfun(@times,X,sqrt(w)');
%     cos = 1-X'*X;
%     cos(1:size(cos,1)+1:end) = 0;
cos = [];
    XX = sum(X.*X); XtX = X'*X;
    euc = (repmat(XX',[1 size(XX,2)]) + repmat(XX,[size(XX,2) 1]) - 2*XtX);
    euc(1:size(euc,1)+1:end) = 0;
end

