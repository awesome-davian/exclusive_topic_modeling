function [W,H] = hals_stan_nmf_salt(A,k,iter)

    params = inputParser;
    params.addParamValue('k'          ,0,@(x) isscalar(x) & x>=0);
    params.addParamValue('kd'          ,0,@(x) isscalar(x) & x>=0);
    params.addParamValue('m'          ,0,@(x) isscalar(x) & x>=0);

    epsilon = 1e-16;
    
    par = params.Results;
    par.k = k;
    [par.m, par.n] = size(A);
    % 1. Initialization

    
    s=rng;
    rng(s); H = rand(par.k,par.n);
    rng(s); W = rand(par.m,par.k);
    H = bsxfun(@rdivide,H,sqrt(sum(H.^2)));
    
    for repeat = 1:5
        WtA = W'*A; WtW = W'*W; 
        WtW_reg = applyReg(WtW,par,[0 1]);
        for i = 1:par.k
            H(i,:) = max( H(i,:) + WtA(i,:) - WtW_reg(i,:)*H, epsilon);
        end
        
        AHt = A*H';
        HHt_reg = applyReg(H*H',par,[1 0]);
        for i = 1:par.k
            W(:,i) = max(W(:,i) * HHt_reg(i,i) + AHt(:,i) - W * HHt_reg(:,i),epsilon);
            if sum(W(:,i))>0
                W(:,i) = W(:,i)/norm(W(:,i));
            end
        end 
    end
    disp('NMF-0. initializing W,H done');
    
    for c3 = 1:iter      
        [H,W,par] = stan_nmf_itersolver(A,H,W,par);
        disp('NMF-1-i. NMF iteration going on');
    end
    
    disp('NMF-1. NMF iteration completed');
    
end
function [H,W,par] = stan_nmf_itersolver(A,H,W,par)

    epsilon = 1e-16;
    WtA = W'*A;
	WtW = W'*W;
    WtW_reg = applyReg(WtW,par,[0 1]);
    HHt = H*H';
    
	for i = 1:par.k 	
        H(i,:) = max( H(i,:) + ( WtA(i,:) - WtW_reg(i,:)*H/WtW_reg(i,i)),epsilon);
    end   
    
    AHt = A*H';
    HHt = H*H';
 
    HHt_reg = applyReg(HHt,par,[1 0]); 

	for i = 1:par.k   
        W(:,i) = max( W(:,i) + ( AHt(:,i) - W * HHt_reg(:,i) )/(HHt_reg(i,i)), epsilon); 
        if sum(W(:,i))>0
            W(:,i) = W(:,i)/norm(W(:,i));
        end
    end
end

function AtA = applyReg(AtA,par,reg)
    % Frobenius norm regularization
    if reg(1) > 0
        AtA = AtA + 2 * reg(1) * eye(par.k);
    end
    % L1-norm regularization
    if reg(2) > 0
        AtA = AtA + 2 * reg(2) * ones(par.k,par.k);
    end
end