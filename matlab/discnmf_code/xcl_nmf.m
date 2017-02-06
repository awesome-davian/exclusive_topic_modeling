function [WC,WN,HC,HN,par] =...
    xcl_nmf(AC,AN,k,kd,iter,ALPHA,BETA) 
  
    params = inputParser;
    params.addParamValue('k'          ,0,@(x) isscalar(x) & x>=0);
    params.addParamValue('kd'          ,0,@(x) isscalar(x) & x>=0);
    params.addParamValue('n'              ,0          ,@(x) isscalar(x) & x>=0 & x<=8);
    params.addParamValue('ALPHA'          ,[ 0 0 0 0 0 0 0 0 ],@(x) isvector(x) & x==8);
    params.addParamValue('BETA'          ,[ 0 0 0 0 0 0 0 0 ],@(x) isvector(x) & x==8);
    
% params.addParamValue('N'             ,[ 0 0 0 0 0 0 0 0 ],@(x) isvector(x) & x==8);

    

    par = params.Results;
    
    par.k = k;
    par.kd = kd;
    par.ALPHA = ALPHA;
    par.BETA = BETA;
    par.n = size(AN,2);
    
    Wm = size(AC,1);  
   
    for c1=1:par.n
        WN = rand(Wm,par.k,par.n);
    end
    
    if(1<par.n+1)
        par.N(1) = size(AC,2);
        HC = rand(par.k,par.N(1));
        WC = rand(Wm,par.k);
    end
 
    for c2 = 1:par.n
        par.N(c2) = size(AN{c2},2);
        HN{c2} = rand(par.k,par.N(c2));
    end
    
    %s  INITIALISING W,H Terminated (for the moment)    
    
    %s the iteration process to go.
    
%    iter = 20; %initial iteration = 20;
    
    for c3 = 1:iter
        [HC,WC,par] = xcl_c_itersolver(AC,HC,WC,WN,Wm,par);
        for c4 = 1:par.n
        [W(:,:,c4),HN{c4},par] = xcl_n_itersolver(AN{c4},HN{c4},WC,WN(:,:,c4),ALPHA(c4),BETA(c4),par);
        end       
    end
end

function[HC,WC,par] = xcl_c_itersolver(AC,HC,WC,WN,Wm,par)

    epsilon = 1e-16;
    WCtAC = WC'*AC;
	WCtWC = WC'*WC;
    
	for i = 1:par.k 
		HC(i,:) = max(HC(i,:) + ( WCtAC(i,:)-WCtWC(i,:)*HC )/WCtWC(i,i),epsilon);
    end   
    
    ACHCt = AC*HC';
    HCHCt = HC*HC';
    T1 = zeros(Wm,1); 
    
	for i = 1:par.kd   
        for i_i = 1:par.n
            T1 = T1 + (par.BETA(i_i)/2) * sum(WN(:,1:par.kd,i_i),2);
        end
		WC(:,i) = max(WC(:,i) + (ACHCt(:,i) - WC * HCHCt(:,i)- T1)/HCHCt(i,i),...
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
        
		WC(:,i) = max(WC(:,i) * HCHCt(i,i)/( HCHCt(i,i)+T2 )...
                  + ( ACHCt(:,i)-WC*HCHCt(:,i)+T3 )/( HCHCt(i,i)+ T2 ),...
                  epsilon); 

        if sum(WC(:,i))>0
			WC(:,i) = WC(:,i)/norm(WC(:,i));
        end
 
    end    
    
end

function[Wj,Hj,par] = xcl_n_itersolver(Aj,Hj,WC,WNi,alpha,beta,par) 
    
    epsilon = 1e-16;
    Wj = WNi;
    WjtAj = Wj'*Aj;


	WjtWj = Wj'*Wj;
    HjHjt = Hj *Hj';
    
	for i = 1:par.k
		Hj(i,:) = max(Hj(i,:) + (WjtAj(i,:) - WjtWj(i,:) * Hj)/WjtWj(i,i),epsilon);
    end    
    
    AjHjt = Aj*Hj';
	for i = 1:par.kd  
		Wj(:,i) = max(Wj(:,i) + ...
            (AjHjt(:,i) - Wj * HjHjt(:,i)-beta/2*sum(Wj(:,1:par.kd),2))/HjHjt(i,i),epsilon);
		if sum(Wj(:,i))>0
			Wj(:,i) = Wj(:,i)/norm(Wj(:,i));
		end
    end
    
    for i = par.kd+1:par.k
		Wj(:,i) = max(Wj(:,i) * HjHjt(i,i)/(HjHjt(i,i)+alpha) + ...
            (AjHjt(:,i)+alpha*WC(:,i)-Wj*HjHjt(:,i)) / (HjHjt(i,i)+alpha),epsilon);
		if sum(Wj(:,i))>0
			Wj(:,i) = Wj(:,i)/norm(Wj(:,i));
		end
    end
    
end

