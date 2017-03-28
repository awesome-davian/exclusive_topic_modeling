function [WC,WN,HC,HN] =...
    xcl_nmf_perceptual(AC,AN,k,kd,iter,ALPHA,BETA)
    params = inputParser;
    params.addParamValue('k'          ,0,@(x) isscalar(x) & x>=0);
    params.addParamValue('kd'          ,0,@(x) isscalar(x) & x>=0);
    params.addParamValue('al'          ,0,@(x) isscalar(x) & x>=0);
    params.addParamValue('be'          ,0,@(x) isscalar(x) & x>=0);


    epsilon = 1e-16;

    par = params.Results;
    par.k = k;
    par.kd = kd;
    par.al = ALPHA;
    par.be = BETA;
    
    Wm = size(AC,1);  
    
    % AC and AN will come as sparse matrices.
    % a better way of initialization? 
    
%     THC = rand(par.k,size(AC,2));
%     HC = bsxfun(@rdivide,THC,sqrt(sum(THC.^2)));
%     TWC = rand(Wm,par.k);
%     WC = bsxfun(@rdivide,TWC,sqrt(sum(TWC.^2)));
%     THN = rand(par.k,size(AN,2);
%     HN = bsxfun(@rdivide,THN,sqrt(sum(THN.^2)));
%     TWN = rand(Wm,par.k);
%     WN = bsxfun(@rdivide,TWN,sqrt(sum(TWN.^2)));
    s=rng;
    
    rng(s); HC = rand(par.k,size(AC,2));
    rng(s); WC = rand(Wm,par.k);
    rng(s); HN = rand(par.k,size(AN,2));
    rng(s); WN = rand(Wm,par.k);
    HC = bsxfun(@rdivide,HC,sqrt(sum(HC.^2)));
    HN = bsxfun(@rdivide,HN,sqrt(sum(HN.^2)));
  
    % initialization 
  
        WCtAC = WC'*AC; WCtWC = WC'*WC; 
        WCtWC_reg = applyReg(WCtWC,par,[0 1]);
        WNtAN = WN'*AN; WNtWN = WN'*WN; 
        WNtWN_reg = applyReg(WNtWN,par,[0 1]);
        HNHNt = HN*HN'; HCHCt = HC*HC';
        HNHNt_reg = applyReg(HNHNt,par,[1 0]);
        HCHCt_reg = applyReg(HCHCt,par,[1 0]);
        HCACt = HC*AC'; HNANt = HN*AN';      
        HC = max (WCtWC_reg \ WCtAC, epsilon);
        WC = max (HCHCt_reg \ HCACt, epsilon)';
        HN = max (WNtWN_reg \ WNtAN, epsilon);
        WN = max (HNHNt_reg \ HNANt, epsilon)';
        WCsort=cell(k,1); WCsortbef = cell(k,1);
        WCidx = cell(k,1); WCbefidx = cell(k,1);
    disp('NMF-0. initializing done');
        iterator = 1;
            for i=1:k
                [~, WCbefidx{i}] = sort(WC(:,i),'descend');  
            end
            
        count = 1;    
        while(iterator)
            [WN,HN,par] = xcl_n_itersolver(AN,HN,WC,WN,par);
            [HC,WC,par] = xcl_c_itersolver(AC,HC,WC,WN,Wm,par);
            for i = 1:k
                [~,WCidx{i}] = sort(WC(:,i),'descend');
            end
            
            det = 1;
            for i = 1:k
                for j = 1:10
                    if ( WCidx{i}(j) == WCbefidx{i}(j) )
                        det = det*1;
                    else
                        det = 0;
                    end
                end
            end
            
           WCbefidx = WCidx;
           
           count = count +1;
           if det == 1
               iterator = 0;
           end
           if count == 25
               iterator = 0;
           end
           
          end
    
    disp('NMF-2-Final. NMF process done');

end



function[HC,WC,par] = xcl_c_itersolver(AC,HC,WC,WN,Wm,par)

    epsilon = 1e-16;
    WCtAC = WC'*AC;
	WCtWC = WC'*WC;
    WCtWC_reg = applyReg(WCtWC,par,[0 1]);
    HCHCt = HC*HC';
    
	for i = 1:par.k 	
        HC(i,:) = max( HC(i,:) + ( WCtAC(i,:) - WCtWC_reg(i,:)*HC/WCtWC_reg(i,i)),epsilon);
    end   
    
    ACHCt = AC*HC';
    HCHCt = HC*HC';
    
    T1 = zeros(Wm,1); 
    HCHCt_reg = applyReg(HCHCt,par,[1 0]); 

	for i = 1:par.kd   
        T1 = T1 + (par.be/2) * sum(WN(:,1:par.kd),2);
        WC(:,i) = max( WC(:,i) + ( ACHCt(:,i) - WC * HCHCt_reg(:,i) - (T1) )/(HCHCt_reg(i,i)),...
        epsilon); 

        if sum(WC(:,i))>0
            WC(:,i) = WC(:,i)/norm(WC(:,i));
        end
    end
    
    for i = par.kd+1:par.k 
        WC(:,i) = max(WC(:,i) * HCHCt_reg(i,i)/( HCHCt_reg(i,i)+par.al )...
                    + ( ACHCt(:,i)-WC*HCHCt_reg(:,i)+par.al*WN(:,i) )/( HCHCt_reg(i,i)+ par.al ),...
                    epsilon); 

        if sum(WC(:,i))>0
            WC(:,i) = WC(:,i)/norm(WC(:,i));
        end
    end  
    
end


function[Wj,Hj,par] = xcl_n_itersolver(Aj,Hj,WC,WN,par) 

    epsilon = 1e-16;
    Wj = WN;

    WjtAj = Wj'*Aj;
    WjtWj = Wj'*Wj;
    HjHjt = Hj *Hj';
    WjtWj_reg = applyReg(WjtWj,par,[0 1]);

	for i = 1:par.k
		Hj(i,:) = max(Hj(i,:) + ( WjtAj(i,:) - WjtWj_reg(i,:)*Hj)/WjtWj_reg(i,i),epsilon);
    end    
    
    AjHjt = Aj*Hj';
    HjHjt_reg = applyReg(HjHjt,par,[1 0]);
    
	for i = 1:par.kd  
		Wj(:,i) = max(Wj(:,i) + ...
                  ( AjHjt(:,i) - Wj * HjHjt_reg(:,i) - (par.be/2) * sum(Wj(:,1:par.kd),2) )/HjHjt_reg(i,i),epsilon);
		if sum(Wj(:,i))>0
			Wj(:,i) = Wj(:,i)/norm(Wj(:,i));   
        end
    end
    
    for i = par.kd+1:par.k
		Wj(:,i) = max( Wj(:,i) * HjHjt_reg(i,i) / ( HjHjt_reg(i,i) + par.al) + ...
                  ( AjHjt(:,i) + par.al * WC(:,i) - Wj*HjHjt_reg(:,i)) / (HjHjt_reg(i,i) + par.al ) , epsilon);
		if sum(Wj(:,i))>0
			Wj(:,i) = Wj(:,i)/norm(Wj(:,i));
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
