function [WC,WN,HC,HN,par] =...
    xcl_nmf(AC,AN,k,kd,iter,ALPHA,BETA,freq) 

    params = inputParser;
    params.addParamValue('k'          ,0,@(x) isscalar(x) & x>=0);
    params.addParamValue('kd'          ,0,@(x) isscalar(x) & x>=0);
    params.addParamValue('n'              ,0          ,@(x) isscalar(x) & x>=0 & x<=8);
    params.addParamValue('ALPHA'          ,[ 0 0 0 0 0 0 0 0 ],@(x) isvector(x) & x==8);
    params.addParamValue('BETA'          ,[ 0 0 0 0 0 0 0 0 ],@(x) isvector(x) & x==8);
 %   params.addParamValue('reg'           , 0,@(x) isscalar(x) & x>=0);
    
% params.addParamValue('N'             ,[ 0 0 0 0 0 0 0 0 ],@(x) isvector(x) & x==8);

    par = params.Results;
    
    par.k = k;
    par.kd = kd;
    par.ALPHA = ALPHA;
    par.BETA = BETA;
    par.n = freq;
    Wm = size(AC,1);  
   
    WN = rand(Wm,par.k,par.n);
    for c1=1:par.n
        WN(:,:,c1) = bsxfun(@rdivide,WN(:,:,c1),sqrt(sum(WN(:,:,c1).^2)));
    end
    
    if(1<par.n+1)
        t = size(AC,2);
        THC = rand(t,par.k);
        THC = bsxfun(@rdivide,THC,sqrt(sum(THC.^2)));
        HC = THC';
        WC = rand(Wm,par.k);
        WC = bsxfun(@rdivide,WC,sqrt(sum(WC.^2)));
    end
 
    for c2 = 1:par.n
        clear THC;
        t = size(AN{c2},2);
        THC = rand(t,par.k);
        THC = bsxfun(@rdivide,THC,sqrt(sum(THC.^2)));
        HN{c2} = THC';
        HN{c2} = bsxfun(@rdivide,HN{c2},sqrt(sum(HN{c2}.^2)));
    end
    
    %s  INITIALISING W,H Terminated (for the moment)    
    
    %s the iteration process to go.
    
%    iter = 20; %initial iteration = 20;


    for c3 = 1:iter
        for c4 = 1:par.n
        [WN(:,:,c4),HN{c4},par] = xcl_n_itersolver(AN{c4},HN{c4},WC,WN(:,:,c4),ALPHA(c4),BETA(c4),par);
        end  
        [HC,WC,par] = xcl_c_itersolver(AC,HC,WC,WN,Wm,par);     
    end
end

function[HC,WC,par] = xcl_c_itersolver(AC,HC,WC,WN,Wm,par)

    epsilon = 1e-16;
    WCtAC = WC'*AC;
	WCtWC = WC'*WC;
    WCtAC(isnan(WCtAC))=epsilon;
    WCtWC(isnan(WCtWC))=epsilon;
    WCtWC_reg = applyReg(WCtWC,par,[0 1]);
    HCHCt = HC*HC';
        HCHCt(isnan(HCHCt))=epsilon;

    
	for i = 1:par.k 
		
      %  HC(i,:) = max(HC(i,:) + ( WCtAC(i,:) - WCtWC(i,:)*HC )/HCHCt(i,i),epsilon);
        HC(i,:) = max( HC(i,:) + ( WCtAC(i,:) - WCtWC_reg(i,:)*HC/WCtWC_reg(i,i)),epsilon);
    end   
    
    ACHCt = AC*HC';
    HCHCt = HC*HC';
    ACHCt(isnan(ACHCt))=epsilon;
    
    T1 = zeros(Wm,1); 
    HCHCt_reg = applyReg(HCHCt,par,[1 0]);
	for i = 1:par.kd   
        for i_i = 1:par.n
            T1 = T1 + (par.BETA(i_i)/2) * sum(WN(:,1:par.kd,i_i),2);
        end
		WC(:,i) = max( WC(:,i) + ( ACHCt(:,i) - WC * HCHCt_reg(:,i)- T1 )/(HCHCt_reg(i,i)),...
            epsilon); 
		if sum(WC(:,i))>0
			WC(:,i) = WC(:,i)/norm(WC(:,i));
		end
    end
    
    T2 = 0; T3=zeros(Wm,1);
    for i = par.kd+1:par.k 
        
        for i_i = 1:par.n
            T2 = T2 + par.ALPHA(i_i);
            T3 = T3 + par.ALPHA(i_i)*WN(:,i,i_i);
        end
        
		WC(:,i) = max(WC(:,i) * HCHCt_reg(i,i)/( HCHCt_reg(i,i)+T2 )...
                  + ( ACHCt(:,i)-WC*HCHCt_reg(:,i)+T3 )/( HCHCt_reg(i,i)+ T2 ),...
                  epsilon); 

        if sum(WC(:,i))>0
			WC(:,i) = WC(:,i)/norm(WC(:,i));
        end
 
    end    
    HC(isnan(HC))=epsilon;
    WC(isnan(WC))=epsilon;
    
end

function[Wj,Hj,par] = xcl_n_itersolver(Aj,Hj,WC,WNi,alpha,beta,par) 


    epsilon = 1e-16;
    Wj = WNi;
    WjtAj = Wj'*Aj;
    WjtWj = Wj'*Wj;
    HjHjt = Hj *Hj';
    HjHjt(isnan(HjHjt))=epsilon;
    WjtWj_reg = applyReg(WjtWj,par,[0 1]);

	for i = 1:par.k
		Hj(i,:) = max(Hj(i,:) + ( WjtAj(i,:) - WjtWj_reg(i,:)*Hj)/WjtWj_reg(i,i),epsilon);
      %  HC(i,:) = max(HC(i,:) + ( WCtAC(i,:) - WCtWC_reg(i,:)*HC/WCtWC_reg(i,i)),epsilon);
    end    
    
    AjHjt = Aj*Hj';
    HjHjt_reg = applyReg(HjHjt,par,[1 0]);
	for i = 1:par.kd  
		Wj(:,i) = max(Wj(:,i) + ...
            ( AjHjt(:,i) - Wj * HjHjt_reg(:,i)-(beta/2)*sum(Wj(:,1:par.kd),2) )/HjHjt_reg(i,i),epsilon);
		if sum(Wj(:,i))>0
			Wj(:,i) = Wj(:,i)/norm(Wj(:,i));
            
		end
        
    end
    
    for i = par.kd+1:par.k
		Wj(:,i) = max(Wj(:,i) * HjHjt_reg(i,i)/(HjHjt_reg(i,i)+alpha) + ...
            (AjHjt(:,i)+alpha*WC(:,i)-Wj*HjHjt_reg(:,i)) / (HjHjt_reg(i,i)+alpha),epsilon);
		if sum(Wj(:,i))>0
			Wj(:,i) = Wj(:,i)/norm(Wj(:,i));
		end

    end


    Wj(isnan(Wj))=epsilon;
    Hj(isnan(Hj))=epsilon;

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
