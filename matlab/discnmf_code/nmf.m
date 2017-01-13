% Nonnegative Matrix Factorization : Algorithms Toolbox
%
% Written by Jingu Kim (jingu.kim@gmail.com)
%            School of Computational Science and Engineering,
%            Georgia Institute of Technology
%
% Please send bug reports, comments, or questions to Jingu Kim.
% This code comes with no guarantee or warranty of any kind.
%
% Reference:
%		 Jingu Kim and Haesun Park,
%		 Fast Nonnegative Matrix Factorization: An Active-set-like Method And Comparisons,
%		 SIAM Journal on Scientific Computing (SISC), 33(6), pp. 3261-3281, 2011.
%
% Last modified on 02/22/2012
%
% <Inputs>
%        A : Input data matrix (m x n)
%        k : Target low-rank
%
%        (Below are optional arguments: can be set by providing name-value pairs)
%
%        METHOD : Algorithm for solving NMF. One of the following values:
%				  'anls_bpp' 'hals' 'anls_asgroup' 'anls_asgivens' 'anls_pgrad' 'anls_pqn' 'als' 'mu'
%				  See above paper (and references therein) for the details of these algorithms.
%				  Default is 'anls_bpp'.
%        TOL : Stopping tolerance. Default is 1e-3. 
%              If you want to obtain a more accurate solution, decrease TOL and increase MAX_ITER at the same time.
%        MAX_ITER : Maximum number of iterations. Default is 500.
%        MIN_ITER : Minimum number of iterations. Default is 20.
%        MAX_TIME : Maximum amount of time in seconds. Default is 1,000,000.
%		 INIT : A struct containing initial values. INIT.W and INIT.H should contain initial values of
%               W and H of size (m x k) and (k x n), respectively.
%        VERBOSE : 0 (default) - No debugging information is collected.
%                  1 (debugging/experimental purpose) - History of computation is returned. See 'REC' variable.
%                  2 (debugging/experimental purpose) - History of computation is additionally printed on screen.
%		 REG_W, REG_H : Regularization parameters for W and H.
%                       Both REG_W and REG_H should be vector of two nonnegative numbers.
%                       The first component is a parameter with Frobenius norm regularization, and
%                       the second component is a parameter with L1-norm regularization.
%                       For example, to promote sparsity in H, one might set REG_W = [alpha 0] and REG_H = [0 beta]
%                       where alpha and beta are positive numbers. See above paper for more details.
%                       Defaut is [0 0] for both REG_W and REG_H, which means no regularization.
% <Outputs>
%        W : Obtained basis matrix (m x k)
%        H : Obtained coefficient matrix (k x n)
%        iter : Number of iterations
%        HIS : (debugging/experimental purpose) Auxiliary information about the execution
% <Usage Examples>
%        nmf(A,10)
%        nmf(A,20,'verbose',2)
%        nmf(A,20,'verbose',1,'method','anls_bpp')
%        nmf(A,20,'verbose',1,'method','hals')
%        nmf(A,20,'verbose',1,'method','comp','n1',,'n2',,'k1',,'k2',,'ks',,'kd1',,'kd2',,'alpha',,'beta',)
%        nmf(A,20,'verbose',1,'reg_w',[0.1 0],'reg_h',[0 0.5])


function [W,H,res,iter,REC]=nmf(A,k,varargin)
%s varargin --> variable, argument, input?
	% parse parameters
	params = inputParser;
%	params.addParamValue('method'        ,'anls_bpp',@(x) ischar(x) );
%	params.addParamValue('method'        ,'hals',@(x) ischar(x) );
    params.addParamValue('method'       ,'exclusive_nmf',@(x) ischar(x) );
	params.addParamValue('tol'           ,1e-2      ,@(x) isscalar(x) & x > 0);
	params.addParamValue('min_iter'      ,20        ,@(x) isscalar(x) & x > 0);
	params.addParamValue('max_iter'      ,100      ,@(x) isscalar(x) & x > 0);
	params.addParamValue('max_time'      ,1e6       ,@(x) isscalar(x) & x > 0);
	params.addParamValue('init'          ,struct([]),@(x) isstruct(x));
	params.addParamValue('verbose'       ,1         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('reg_w'         ,[0 0]     ,@(x) isvector(x) & length(x) == 2);
	params.addParamValue('reg_h'         ,[0 0]     ,@(x) isvector(x) & length(x) == 2);
	% The following options are reserved for debugging/experimental purposes. 
	% Make sure to understand them before making changes
	params.addParamValue('subparams'     ,struct([]),@(x) isstruct(x) );
	params.addParamValue('track_grad'    ,1         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('track_prev'    ,1         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('stop_criterion',2         ,@(x) isscalar(x) & x >= 0);
    params.addParamValue('n1'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('n2'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('k1'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('k2'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('ks'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('kd1'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('kd2'    ,0         ,@(x) isscalar(x) & x >= 0);
    %-- New alpha, beta variables created to control the weights
    % distancewise
	params.addParamValue('alpha1'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('beta1'    ,0         ,@(x) isscalar(x) & x >= 0);
    params.addParamValue('alpha2'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('beta2'    ,0         ,@(x) isscalar(x) & x >= 0);
    params.addParamValue('alpha3'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('beta3'    ,0         ,@(x) isscalar(x) & x >= 0);
    params.addParamValue('alpha4'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('beta4'    ,0         ,@(x) isscalar(x) & x >= 0);
    params.addParamValue('alpha5'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('beta5'    ,0         ,@(x) isscalar(x) & x >= 0);
    params.addParamValue('alpha6'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('beta6'    ,0         ,@(x) isscalar(x) & x >= 0);
    params.addParamValue('alpha7'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('beta7'    ,0         ,@(x) isscalar(x) & x >= 0);
    params.addParamValue('alpha8'    ,0         ,@(x) isscalar(x) & x >= 0);
	params.addParamValue('beta8'    ,0         ,@(x) isscalar(x) & x >= 0);

	params.parse(varargin{:});

%     % joyfull
%     save tmp_data;

    if size(A,2)==3
        A=full(sparse(A(:,1),A(:,2),A(:,3)));
        size(A)
    %     X=X(:,data_ind);
    %     X=X((sum(abs(X),2)~=0)',:);
    %     size(X)
    end
    % X=X-repmat(mean(X,2),1,size(X,2));
%     params

	% copy from params object
	[m,n] = size(A);
	par = params.Results;
	par.m = m;
	par.n = n;
	par.k = k;
    par.iter = 0;

	% Stopping criteria are based on the gradient information.
	% Hence, 'track_grad' option needs to be turned on to use a criterion.
	if par.stop_criterion > 0
		par.track_grad = 1;
	end

	% initialize
	if isempty(par.init)
    	W = rand(m,k); H = rand(k,n);
%        W = WW; H = HH;
	else
		W = par.init.W; 
        H = par.init.H;
	end

	% This variable is for analysis/debugging, so it does not affect the output (W,H) of this program
    REC = struct([]);

    if par.verbose          % Collect initial information for analysis/debugging
		clear('init');
		init.norm_A      = norm(A,'fro'); 
		init.norm_W		 = norm(W,'fro');
		init.norm_H		 = norm(H,'fro');
		init.baseObj	 = getObj((init.norm_A)^2,W,H,par);
		if par.track_grad
        	[gradW,gradH] 	 = getGradient(A,W,H,par);
			init.normGr_W    = norm(gradW,'fro');
			init.normGr_H    = norm(gradH,'fro');
			init.SC_NM_PGRAD = getInitCriterion(1,A,W,H,par,gradW,gradH);
			init.SC_PGRAD    = getInitCriterion(2,A,W,H,par,gradW,gradH);
			init.SC_DELTA    = getInitCriterion(3,A,W,H,par,gradW,gradH);
		else
        	gradW = 0; gradH = 0;
		end

		if par.track_prev 
			prev_W = W; prev_H = H;
		else
			prev_W = 0; prev_H = 0;
		end
			
		ver = prepareHIS(A,W,H,prev_W,prev_H,init,par,0,0,gradW,gradH);
		REC(1).init = init;
		REC.HIS = ver;

        if par.verbose == 2
			display(init);
		end

        tPrev = cputime;
    end

    % stringwise addition
    
	initializer= str2func([par.method,'_initializer']);
	iterSolver = str2func([par.method,'_iterSolver']);
	iterLogger = str2func([par.method,'_iterLogger']);
	[W,H,par,val,ver] = feval(initializer,A,W,H,par);

	if par.verbose & ~isempty(ver)
		tTemp = cputime;
		REC.HIS = saveHIS(1,ver,REC.HIS);
		tPrev = tPrev+(cputime-tTemp);
	end

	REC(1).par = par;
	REC.start_time = datestr(now);
%     display(par);

    tStart = cputime;, tTotal = 0;
	if par.track_grad
    	initSC = getInitCriterion(par.stop_criterion,A,W,H,par);
	end
    SCconv = 0; SC_COUNT = 3;

    init_time = tic;
    res = struct;
    res.obj = zeros(par.max_iter,1);
    res.time = zeros(par.max_iter,1);
    res.grad = zeros(par.max_iter,1);
    for iter=1:par.max_iter

        par.iter = iter;
		% Actual work of this iteration is executed here.
		[W,H,gradW,gradH,val] = feval(iterSolver,A,W,H,iter,par,val);
        
%        [iter norm(A - W*H, 'fro')]
%        res.obj(iter) = norm(A - W*H,'fro');
        res.obj(iter) = norm(A, 'fro')^2 - 2*trace(W'*(A*H'))+trace((W'*W)*(H*H'));
        res.time(iter) = toc(init_time);

        if par.verbose          % Collect information for analysis/debugging
            elapsed = cputime-tPrev;
            tTotal = tTotal + elapsed;

            clear('ver');
			ver = prepareHIS(A,W,H,prev_W,prev_H,init,par,iter,elapsed,gradW,gradH);

			ver = feval(iterLogger,ver,par,val,W,H,prev_W,prev_H);
			REC.HIS = saveHIS(iter+1,ver,REC.HIS);

			if par.track_prev, prev_W = W; prev_H = H; end
            if par.verbose == 2, display(ver);, end
            tPrev = cputime;
        end

        if (par.verbose && (tTotal > par.max_time)) || (~par.verbose && ((cputime-tStart)>par.max_time))
            break;
        elseif par.track_grad
            SC = getStopCriterion(par.stop_criterion,A,W,H,par,gradW,gradH);
            res.grad(iter) = SC/initSC;
            if (SC/initSC <= par.tol)
                SCconv = SCconv + 1;
%                if (SCconv >= SC_COUNT), break;, end
            else
                SCconv = 0;
            end
        end
    end
    res.iter = iter;
    [m,n]=size(A);
	[W,H]=normalize_by_W(W,H);
    
    if par.verbose
		final.elapsed_total = sum(REC.HIS.elapsed);
    else
        final.elapsed_total = cputime-tStart;
    end
    final.iterations     = iter;
% 	sqErr = getSquaredError(A,W,H,init);
% 	final.relative_error = sqrt(sqErr)/init.norm_A;
% 	final.relative_obj	 = getObj(sqErr,W,H,par)/init.baseObj;
    final.W_density      = length(find(W>0))/(m*k);
    final.H_density      = length(find(H>0))/(n*k);

    if par.verbose
		REC.final = final;
	end
	REC.finish_time = datestr(now);
%     display(final); 
end

%----------------------------------------------------------------------------
%                              Implementation of methods
%----------------------------------------------------------------------------

%----------------- Exclusive NMF Method -----------------------------------

% %----------------- HALS Method : Algorith 2 of Cichocki and Phan -----------------------
% 
% function [W,H,par,val,ver] = hals_initializer(A,W,H,par)
% 	[W,H]=normalize_by_W(W,H);
% 
% 	val = struct([]);
% 	ver = struct([]);
% end
% 
% function [W,H,gradW,gradH,val] = hals_iterSolver(A,W,H,iter,par,val)
% 	epsilon = 1e-16;
% 
% 	WtA = W'*A;
% 	WtW = W'*W;
% 	WtW_reg = applyReg(WtW,par,par.reg_h);
% 	for i = 1:par.k
% 		H(i,:) = max(H(i,:) + WtA(i,:) - WtW_reg(i,:) * H,epsilon);
%     end
% 
%     AHt = A*H';
% 	HHt_reg = applyReg(H*H',par,par.reg_w);
% 	for i = 1:par.k
% 		W(:,i) = max(W(:,i) * HHt_reg(i,i) + AHt(:,i) - W * HHt_reg(:,i),epsilon);
% 		if sum(W(:,i))>0
% 			W(:,i) = W(:,i)/norm(W(:,i));
% 		end
% 	end
% 
% 	if par.track_grad
%     	gradW = W*HHt_reg - AHt;
% 		gradH = getGradientOne(W'*W,W'*A,H,par.reg_h,par);
% 	else
% 		gradH = 0; gradW = 0;
% 	end
% end
% 
% function [ver]= hals_iterLogger(ver,par,val,W,H,prev_W,prev_H)
% end

function [WC,HC,W1,H1,W2,H2,W3,H3,W4,H4,W5,H5,W6,H6,W7,H7,W8,H8,par,val,ver] = ...
exclusive_nmf_initializer(AC,A1,A2,A3,A4,A5,A6,A7,A8,WC,HC,W1,H1,W2,H2,W3,H3,W4,H4,W5,H5,W6,H6,W7,H7,W8,H8,iter,par,val)
    epsilon = 1e-16;
	for iter=1:5
        
        %---------------------------- C
        WCtAC = WC'*AC;
        WCtWC = WC'*WC;
        WCtWC_reg = applyReg(WCtWC,par,par.reg_h);
        for i = 1:par.k1
            HC(i,:) = max(HC(i,:) + WCtAC(i,:) - WCtWC_reg(i,:) * HC,epsilon);
        end

        ACHCt = AC*HC';
        HCHCt_reg = applyReg(HC*HC',par,par.reg_w);
        for i = 1:par.k1
            WC(:,i) = max(WC(:,i) * HCHCt_reg(i,i) + ACHCt(:,i) - WC * HCHCt_reg(:,i),epsilon);
            if sum(WC(:,i))>0
                WC(:,i) = WC(:,i)/norm(WC(:,i));
            end
        end
        
        %---------------------- 1
        
        W1tA1 = W1'*A1;
        W1tW1 = W1'*W1;
        W1tW1_reg = applyReg(W1tW1,par,par.reg_h);
        for i = 1:par.k1
            H1(i,:) = max(H1(i,:) + W1tA1(i,:) - W1tW1_reg(i,:) * H1,epsilon);
        end

        A1H1t = A1*H1';
        H1H1t_reg = applyReg(H1*H1',par,par.reg_w);
        for i = 1:par.k1
            W1(:,i) = max(W1(:,i) * H1H1t_reg(i,i) + A1H1t(:,i) - W1 * H1H1t_reg(:,i),epsilon);
            if sum(W1(:,i))>0
                W1(:,i) = W1(:,i)/norm(W1(:,i));
            end
        end
        
        %------------------------2
        
        W2tA2 = W2'*A2;
        W2tW2 = W2'*W2;
        W2tW2_reg = applyReg(W2tW2,par,par.reg_h);
        for i = 1:par.k1
            H2(i,:) = max(H2(i,:) + W2tA2(i,:) - W2tW2_reg(i,:) * H2,epsilon);
        end

        A2H2t = A2*H2';
        H2H2t_reg = applyReg(H2*H2',par,par.reg_w);
        for i = 1:par.k1
            W2(:,i) = max(W2(:,i) * H2H2t_reg(i,i) + A2H2t(:,i) - W2 * H2H2t_reg(:,i),epsilon);
            if sum(W2(:,i))>0
                W2(:,i) = W2(:,i)/norm(W2(:,i));
            end
        end
        
        %---------------------------3
        
        W3tA3 = W3'*A3;
        W3tW3 = W3'*W3;
        W3tW3_reg = applyReg(W3tW3,par,par.reg_h);
        for i = 1:par.k1
            H3(i,:) = max(H3(i,:) + W3tA3(i,:) - W3tW3_reg(i,:) * H3,epsilon);
        end

        A3H3t = A3*H3';
        H3H3t_reg = applyReg(H3*H3',par,par.reg_w);
        for i = 1:par.k1
            W3(:,i) = max(W3(:,i) * H3H3t_reg(i,i) + A3H3t(:,i) - W3 * H3H3t_reg(:,i),epsilon);
            if sum(W3(:,i))>0
                W3(:,i) = W3(:,i)/norm(W3(:,i));
            end
        end
        
        %---------------------------------4
        
        W4tA4 = W4'*A4;
        W4tW4 = W4'*W4;
        W4tW4_reg = applyReg(W4tW4,par,par.reg_h);
        for i = 1:par.k1
            H4(i,:) = max(H4(i,:) + W4tA4(i,:) - W4tW4_reg(i,:) * H4,epsilon);
        end

        A4H4t = A4*H4';
        H4H4t_reg = applyReg(H4*H4',par,par.reg_w);
        for i = 1:par.k1
            W4(:,i) = max(W4(:,i) * H4H4t_reg(i,i) + A4H4t(:,i) - W4 * H4H4t_reg(:,i),epsilon);
            if sum(W4(:,i))>0
                W4(:,i) = W4(:,i)/norm(W4(:,i));
            end
        end
        
        %-----------------------------------5
        W5tA5 = W5'*A5;
        W5tW5 = W5'*W5;
        W5tW5_reg = applyReg(W5tW5,par,par.reg_h);
        for i = 1:par.k1
            H5(i,:) = max(H5(i,:) + W5tA5(i,:) - W5tW5_reg(i,:) * H5,epsilon);
        end

        A5H5t = A5*H5';
        H5H5t_reg = applyReg(H5*H5',par,par.reg_w);
        for i = 1:par.k1
            W5(:,i) = max(W5(:,i) * H5H5t_reg(i,i) + A5H5t(:,i) - W5 * H5H5t_reg(:,i),epsilon);
            if sum(W5(:,i))>0
                W5(:,i) = W5(:,i)/norm(W5(:,i));
            end
        end
        
        %-----------------------------------6
        
        W6tA6 = W6'*A6;
        W6tW6 = W6'*W6;
        W6tW6_reg = applyReg(W6tW6,par,par.reg_h);
        for i = 1:par.k1
            H6(i,:) = max(H6(i,:) + W6tA6(i,:) - W6tW6_reg(i,:) * H6,epsilon);
        end

        A6H6t = A6*H6';
        H6H6t_reg = applyReg(H6*H6',par,par.reg_w);
        for i = 1:par.k1
            W6(:,i) = max(W6(:,i) * H6H6t_reg(i,i) + A6H6t(:,i) - W6 * H6H6t_reg(:,i),epsilon);
            if sum(W6(:,i))>0
                W6(:,i) = W6(:,i)/norm(W6(:,i));
            end
        end
        
        %------------------------------------7
        
        W7tA7 = W7'*A7;
        W7tW7 = W7'*W7;
        W7tW7_reg = applyReg(W7tW7,par,par.reg_h);
        for i = 1:par.k1
            H7(i,:) = max(H7(i,:) + W7tA7(i,:) - W7tW7_reg(i,:) * H7,epsilon);
        end

        A7H7t = A7*H7';
        H7H7t_reg = applyReg(H7*H7',par,par.reg_w);
        for i = 1:par.k1
            W7(:,i) = max(W7(:,i) * H7H7t_reg(i,i) + A7H7t(:,i) - W7 * H7H7t_reg(:,i),epsilon);
            if sum(W7(:,i))>0
                W7(:,i) = W7(:,i)/norm(W7(:,i));
            end
        end
        
        %-----------------------------------8
        
        W8tA8 = W8'*A8;
        W8tW8 = W8'*W8;
        W8tW8_reg = applyReg(W8tW8,par,par.reg_h);
        for i = 1:par.k1
            H8(i,:) = max(H8(i,:) + W8tA8(i,:) - W8tW8_reg(i,:) * H8,epsilon);
        end

        A8H8t = A8*H8';
        H8H8t_reg = applyReg(H8*H8',par,par.reg_w);
        for i = 1:par.k1
            W8(:,i) = max(W8(:,i) * H8H8t_reg(i,i) + A8H8t(:,i) - W8 * H8H8t_reg(:,i),epsilon);
            if sum(W8(:,i))>0
                W8(:,i) = W8(:,i)/norm(W8(:,i));
            end
        end
        
        [WC,HC]=normalize_by_W(WC,HC);
        [W1,H1]=normalize_by_W(W1,H1);
        [W2,H2]=normalize_by_W(W2,H2);
        [W3,H3]=normalize_by_W(W3,H3);
        [W4,H4]=normalize_by_W(W4,H4);
        [W5,H5]=normalize_by_W(W5,H5);
        [W6,H6]=normalize_by_W(W6,H6);
        [W7,H7]=normalize_by_W(W7,H7);
        [W8,H8]=normalize_by_W(W8,H8);

%         
%         for i = 0:par.ks-1
%             W1tW2 = (W1(:,1:par.k1-i))'*W2(:,1:par.k2-i);
%             [C,I]=max(W1tW2); [C2,I2]=max(C); I1=I(I2);
%             W1(:,[par.k1-i I1]) = W1(:,[I1 par.k1-i]);
%             W2(:,[par.k1-i I2]) = W2(:,[I2 par.k1-i]);
%         end
%         

        val = struct([]);
        ver = struct([]);
        
end

function [WC,HC,W1,H1,W2,H2,W3,H3,W4,H4,W5,H5,W6,H6,W7,H7,W8,H8,gradW,gradH,val] ...
=  exclusive_nmf_iterSolver(AC,A1,A2,A3,A4,A5,A6,A7,A8,WC,HC,W1,H1,W2,H2,W3,H3,W4,H4,W5,H5,W6,H6,W7,H7,W8,H8,iter,par,val)
    epsilon = 1e-16;

    %----- The central part of the execution ------
    WCtAC = WC'*AC;
	WCtWC = WC'*WC;
	WCtWC_reg = applyReg(WCtWC,par,par.reg_h);
	for i = 1:par.k1
		HC(i,:) = max(HC(i,:) + (WCtAC(i,:) - WCtWC_reg(i,:) * HC)/WCtWC_reg(i,i),epsilon);
    end    % okay, here.
    
    ACHCt = AC*HC';
	HCHCt_reg = applyReg(HC*HC',par,par.reg_w);
	for i = 1:par.kd % in fact, here is the difference, discriminating function
		WC(:,i) = max(WC(:,i) + ...
                 (... 
                 ACHCt(:,i) - ...
                 WC * HCHCt_reg(:,i)- ...
                 ((par.beta1/2) * sum(W1(:,1:par.kd),2)+...
                 (par.beta2/2) * sum(W2(:,1:par.kd),2)+...
                 (par.beta3/2) * sum(W3(:,1:par.kd),2)+...
                 (par.beta4/2) * sum(W4(:,1:par.kd),2)+...
                 (par.beta5/2) * sum(W5(:,1:par.kd),2)+...
                 (par.beta6/2) * sum(W6(:,1:par.kd),2)+...
                 (par.beta7/2) * sum(W7(:,1:par.kd),2)+...
                 (par.beta8/2) * sum(W8(:,1:par.kd),2))... 
                 )...
                 /HCHCt_reg(i,i),epsilon); %---what is U?
        % U is the W function that goes in as constant. The past that is
        % added. here, it is inserted as the scalar sum. 
        %--- there has to be 8 betas. take that into account 
        %--- which means that the beta has to change into an array form
        %--- the ni,s are all 1. only the betas are controlled. 
        %--- and also, the definition of U has to be changed as U1, U2, ...
		if sum(WC(:,i))>0
			WC(:,i) = WC(:,i)/norm(WC(:,i));
		end
    end
    
    for i = par.kd+1:par.k1 % The commonality. 
		WC(:,i) = max(WC(:,i) * HCHCt_reg(i,i)...
                  /( HCHCt_reg(i,i)+...
                  (par.alpha1+par.alpha2+par.alpha3+par.alpha4+par.alpha5+...
                  par.alpha6+par.alpha7+par.alpha8) )...
                  + ... 
                  ( ACHCt(:,i)-WC*HCHCt_reg(:,i)...
                  +( par.alpha1*W1(:,i)+par.alpha2*W2(:,i)+par.alpha3*W3(:,i)+par.alpha4*W4(:,i)...
                  +par.alpha5*W5(:,i)+par.alpha6*W6(:,i)+par.alpha7*W7(:,i)+par.alpha8*W8(:,i)) ) ... 
                  /( HCHCt_reg(i,i)+...
                  (par.alpha1+par.alpha2+par.alpha3+par.alpha4+par.alpha5+...
                  par.alpha6+par.alpha7+par.alpha8)),epsilon); 

        if sum(WC(:,i))>0
			WC(:,i) = WC(:,i)/norm(WC(:,i));
        end
        % Similar processes done here. 
    end    
    %----- Central part of the execution terminated------
    
    
   %---- The neighboring parts. -----%
   
   %-------- the first part of the execution --------------%
   
    W1tA1 = W1'*A1;
	W1tW1 = W1'*W1;
	W1tW1_reg = applyReg(W1tW1,par,par.reg_h);
	for i = 1:par.k1
		H1(i,:) = max(H1(i,:) + (W1tA1(i,:) - W1tW1_reg(i,:) * H1)/W1tW1_reg(i,i),epsilon);
    end    
    
    A1H1t = A1*H1';
	H1H1t_reg = applyReg(H1*H1',par,par.reg_w);
	for i = 1:par.kd
		W1(:,i) = max(W1(:,i) + ...
            (A1H1t(:,i) - W1 * H1H1t_reg(:,i)-par.beta1/2*sum(WC(:,1:par.kd),2))/H1H1t_reg(i,i),epsilon);
		if sum(W1(:,i))>0
			W1(:,i) = W1(:,i)/norm(W1(:,i));
		end
    end
    for i = par.kd+1:par.k1
		W1(:,i) = max(W1(:,i) * H1H1t_reg(i,i)/(H1H1t_reg(i,i)+par.alpha1) + ...
            (A1H1t(:,i)+par.alpha1*WC(:,i)-W1*H1H1t_reg(:,i)) / (H1H1t_reg(i,i)+par.alpha1),epsilon);
		if sum(W1(:,i))>0
			W1(:,i) = W1(:,i)/norm(W1(:,i));
		end
    end


       %-------- the second part of the execution --------------%
    W2tA2 = W2'*A2;
	W2tW2 = W2'*W2;
	W2tW2_reg = applyReg(W2tW2,par,par.reg_h);
	for i = 1:par.k1
		H2(i,:) = max(H2(i,:) + (W2tA2(i,:) - W2tW2_reg(i,:) * H2)/W2tW2_reg(i,i),epsilon);
    end    
    
    A2H2t = A2*H2';
	H2H2t_reg = applyReg(H2*H2',par,par.reg_w);
	for i = 1:par.kd
		W2(:,i) = max(W2(:,i) + ...
            (A2H2t(:,i) - W2 * H2H2t_reg(:,i)-par.beta2/2*sum(WC(:,1:par.kd),2))/H2H2t_reg(i,i),epsilon);
		if sum(W2(:,i))>0
			W2(:,i) = W2(:,i)/norm(W2(:,i));
		end
    end
    for i = par.kd+1:par.k1
		W2(:,i) = max(W2(:,i) * H2H2t_reg(i,i)/(H2H2t_reg(i,i)+par.alpha2) + ...
            (A2H2t(:,i)+par.alpha2*WC(:,i)-W2*H2H2t_reg(:,i)) / (H2H2t_reg(i,i)+par.alpha2),epsilon);
		if sum(W2(:,i))>0
			W2(:,i) = W2(:,i)/norm(W2(:,i));
		end
    end


       %-------- the third part of the execution --------------%
    W3tA3 = W3'*A3;
	W3tW3 = W3'*W3;
	W3tW3_reg = applyReg(W3tW3,par,par.reg_h);
	for i = 1:par.k1
		H3(i,:) = max(H3(i,:) + (W3tA3(i,:) - W3tW3_reg(i,:) * H3)/W3tW3_reg(i,i),epsilon);
    end    
    
    A3H3t = A3*H3';
	H3H3t_reg = applyReg(H3*H3',par,par.reg_w);
	for i = 1:par.kd
		W3(:,i) = max(W3(:,i) + ...
            (A3H3t(:,i) - W3 * H3H3t_reg(:,i)-par.beta3/2*sum(WC(:,1:par.kd),2))/H3H3t_reg(i,i),epsilon);
		if sum(W3(:,i))>0
			W3(:,i) = W3(:,i)/norm(W3(:,i));
		end
    end
    for i = par.kd+1:par.k1
		W3(:,i) = max(W3(:,i) * H3H3t_reg(i,i)/(H3H3t_reg(i,i)+par.alpha3) + ...
            (A3H3t(:,i)+par.alpha3*WC(:,i)-W3*H3H3t_reg(:,i)) / (H3H3t_reg(i,i)+par.alpha3),epsilon);
		if sum(W3(:,i))>0
			W3(:,i) = W3(:,i)/norm(W3(:,i));
		end
    end


       %-------- the fourth part of the execution --------------%
    W4tA4 = W4'*A4;
	W4tW4 = W4'*W4;
	W4tW4_reg = applyReg(W4tW4,par,par.reg_h);
	for i = 1:par.k1
		H4(i,:) = max(H4(i,:) + (W4tA4(i,:) - W4tW4_reg(i,:) * H4)/W4tW4_reg(i,i),epsilon);
    end    
    
    A4H4t = A4*H4';
	H4H4t_reg = applyReg(H4*H4',par,par.reg_w);
	for i = 1:par.kd
		W4(:,i) = max(W4(:,i) + ...
            (A4H4t(:,i) - W4 * H4H4t_reg(:,i)-par.beta4/2*sum(WC(:,1:par.kd),2))/H4H4t_reg(i,i),epsilon);
		if sum(W4(:,i))>0
			W4(:,i) = W4(:,i)/norm(W4(:,i));
		end
    end
    for i = par.kd+1:par.k1
		W4(:,i) = max(W4(:,i) * H4H4t_reg(i,i)/(H4H4t_reg(i,i)+par.alpha4) + ...
            (A4H4t(:,i)+par.alpha4*WC(:,i)-W4*H4H4t_reg(:,i)) / (H4H4t_reg(i,i)+par.alpha4),epsilon);
		if sum(W4(:,i))>0
			W4(:,i) = W4(:,i)/norm(W4(:,i));
		end
    end


       %-------- the fifth part of the execution --------------%
    W5tA5 = W5'*A5;
	W5tW5 = W5'*W5;
	W5tW5_reg = applyReg(W5tW5,par,par.reg_h);
	for i = 1:par.k1
		H5(i,:) = max(H5(i,:) + (W5tA5(i,:) - W5tW5_reg(i,:) * H5)/W5tW5_reg(i,i),epsilon);
    end    
    
    A5H5t = A5*H5';
	H5H5t_reg = applyReg(H5*H5',par,par.reg_w);
	for i = 1:par.kd
		W5(:,i) = max(W5(:,i) + ...
            (A5H5t(:,i) - W5 * H5H5t_reg(:,i)-par.beta5/2*sum(WC(:,1:par.kd),2))/H5H5t_reg(i,i),epsilon);
		if sum(W5(:,i))>0
			W5(:,i) = W5(:,i)/norm(W5(:,i));
		end
    end
    for i = par.kd+1:par.k1
		W5(:,i) = max(W5(:,i) * H5H5t_reg(i,i)/(H5H5t_reg(i,i)+par.alpha5) + ...
            (A5H5t(:,i)+par.alpha5*WC(:,i)-W5*H5H5t_reg(:,i)) / (H5H5t_reg(i,i)+par.alpha5),epsilon);
		if sum(W5(:,i))>0
			W5(:,i) = W5(:,i)/norm(W5(:,i));
		end
    end


       %-------- the sixth part of the execution --------------%
    W6tA6 = W6'*A6;
	W6tW6 = W6'*W6;
	W6tW6_reg = applyReg(W6tW6,par,par.reg_h);
	for i = 1:par.k1
		H6(i,:) = max(H6(i,:) + (W6tA6(i,:) - W6tW6_reg(i,:) * H6)/W6tW6_reg(i,i),epsilon);
    end    
    
    A6H6t = A6*H6';
	H6H6t_reg = applyReg(H6*H6',par,par.reg_w);
	for i = 1:par.kd
		W6(:,i) = max(W6(:,i) + ...
            (A6H6t(:,i) - W6 * H6H6t_reg(:,i)-par.beta6/2*sum(WC(:,1:par.kd),2))/H6H6t_reg(i,i),epsilon);
		if sum(W6(:,i))>0
			W6(:,i) = W6(:,i)/norm(W6(:,i));
		end
    end
    for i = par.kd+1:par.k1
		W6(:,i) = max(W6(:,i) * H6H6t_reg(i,i)/(H6H6t_reg(i,i)+par.alpha6) + ...
            (A6H6t(:,i)+par.alpha6*WC(:,i)-W6*H6H6t_reg(:,i)) / (H6H6t_reg(i,i)+par.alpha6),epsilon);
		if sum(W6(:,i))>0
			W6(:,i) = W6(:,i)/norm(W6(:,i));
		end
    end


       %-------- the seventh part of the execution --------------%
    W7tA7 = W7'*A7;
	W7tW7 = W7'*W7;
	W7tW7_reg = applyReg(W7tW7,par,par.reg_h);
	for i = 1:par.k1
		H7(i,:) = max(H7(i,:) + (W7tA7(i,:) - W7tW7_reg(i,:) * H7)/W7tW7_reg(i,i),epsilon);
    end    
    
    A7H7t = A7*H7';
	H7H7t_reg = applyReg(H7*H7',par,par.reg_w);
	for i = 1:par.kd
		W7(:,i) = max(W7(:,i) + ...
            (A7H7t(:,i) - W7 * H7H7t_reg(:,i)-par.beta7/2*sum(WC(:,1:par.kd),2))/H7H7t_reg(i,i),epsilon);
		if sum(W7(:,i))>0
			W7(:,i) = W7(:,i)/norm(W7(:,i));
		end
    end
    for i = par.kd+1:par.k1
		W7(:,i) = max(W7(:,i) * H7H7t_reg(i,i)/(H7H7t_reg(i,i)+par.alpha7) + ...
            (A7H7t(:,i)+par.alpha7*WC(:,i)-W7*H7H7t_reg(:,i)) / (H7H7t_reg(i,i)+par.alpha7),epsilon);
		if sum(W7(:,i))>0
			W7(:,i) = W7(:,i)/norm(W7(:,i));
		end
    end


       %-------- the eighth part of the execution --------------%
    W8tA8 = W8'*A8;
	W8tW8 = W8'*W8;
	W8tW8_reg = applyReg(W8tW8,par,par.reg_h);
	for i = 1:par.k1
		H8(i,:) = max(H8(i,:) + (W8tA8(i,:) - W8tW8_reg(i,:) * H8)/W8tW8_reg(i,i),epsilon);
    end    
    
    A8H8t = A8*H8';
	H8H8t_reg = applyReg(H8*H8',par,par.reg_w);
	for i = 1:par.kd
		W8(:,i) = max(W8(:,i) + ...
            (A8H8t(:,i) - W8 * H8H8t_reg(:,i)-par.beta8/2*sum(WC(:,1:par.kd),2))/H8H8t_reg(i,i),epsilon);
		if sum(W8(:,i))>0
			W8(:,i) = W8(:,i)/norm(W8(:,i));
		end
    end
    for i = par.kd+1:par.k1
		W8(:,i) = max(W8(:,i) * H8H8t_reg(i,i)/(H8H8t_reg(i,i)+par.alpha8) + ...
            (A8H8t(:,i)+par.alpha8*WC(:,i)-W8*H8H8t_reg(:,i)) / (H8H8t_reg(i,i)+par.alpha8),epsilon);
		if sum(W8(:,i))>0
			W8(:,i) = W8(:,i)/norm(W8(:,i));
		end
    end
    
    if par.track_grad
%     	gradW = [W*HHt_reg - AHt, U*VVt_reg - BVt];
% 		gradH = [getGradientOne(W'*W,W'*A,H,par.reg_h,par);getGradientOne(U'*U,U'*B,V,par.reg_h,par)];
        gradH = 0; gradW = 0;
	else
		gradH = 0; gradW = 0;
    end
        
end
function [ver] = exclusive_nmf_iterLogger(ver,par,val,W,H,prev_W,prev_H)
end


%----------------------------------------------------------------------------------------------
%                                    Utility Functions 
%----------------------------------------------------------------------------------------------

% This function prepares information about execution for a experiment purpose
function ver = prepareHIS(A,W,H,prev_W,prev_H,init,par,iter,elapsed,gradW,gradH)
	ver.iter          = iter;
	ver.elapsed       = elapsed;

	sqErr = getSquaredError(A,W,H,init);
	ver.rel_Error 		= sqrt(sqErr)/init.norm_A;
	ver.rel_Obj			= getObj(sqErr,W,H,par)/init.baseObj;
	ver.norm_W		  = norm(W,'fro');
	ver.norm_H		  = norm(H,'fro');
	if par.track_prev
		ver.rel_Change_W  = norm(W-prev_W,'fro')/init.norm_W;
		ver.rel_Change_H  = norm(H-prev_H,'fro')/init.norm_H;
	end
	if par.track_grad
		ver.rel_NrPGrad_W = norm(projGradient(W,gradW),'fro')/init.normGr_W;
		ver.rel_NrPGrad_H = norm(projGradient(H,gradH),'fro')/init.normGr_H;
		ver.SC_NM_PGRAD   = getStopCriterion(1,A,W,H,par,gradW,gradH)/init.SC_NM_PGRAD;
		ver.SC_PGRAD      = getStopCriterion(2,A,W,H,par,gradW,gradH)/init.SC_PGRAD;
		ver.SC_DELTA      = getStopCriterion(3,A,W,H,par,gradW,gradH)/init.SC_DELTA; 
	end
	ver.density_W     = length(find(W>0))/(par.m*par.k);
	ver.density_H     = length(find(H>0))/(par.n*par.k);
end

% Execution information is collected in HIS variable
function HIS = saveHIS(idx,ver,HIS)
	%idx = length(HIS.iter)+1;
	fldnames = fieldnames(ver);

	for i=1:length(fldnames)
		flname = fldnames{i};
		HIS.(flname)(idx) = ver.(flname);
	end
end

%-------------------------------------------------------------------------------
function retVal = getInitCriterion(stopRule,A,W,H,par,gradW,gradH)
% STOPPING_RULE : 1 - Normalized proj. gradient
%                 2 - Proj. gradient
%                 3 - Delta by H. Kim
%                 0 - None (want to stop by MAX_ITER or MAX_TIME)
    if nargin~=7
        [gradW,gradH] = getGradient(A,W,H,par);
    end
    [m,k]=size(W);, [k,n]=size(H);, numAll=(m*k)+(k*n);
    switch stopRule
        case 1
            retVal = norm([gradW(:); gradH(:)])/numAll;
        case 2
            retVal = norm([gradW(:); gradH(:)]);
        case 3
            retVal = getStopCriterion(3,A,W,H,par,gradW,gradH);
        case 0
            retVal = 1;
    end
end
%-------------------------------------------------------------------------------
function retVal = getStopCriterion(stopRule,A,W,H,par,gradW,gradH)
% STOPPING_RULE : 1 - Normalized proj. gradient
%                 2 - Proj. gradient
%                 3 - Delta by H. Kim
%                 0 - None (want to stop by MAX_ITER or MAX_TIME)
    if nargin~=7
        [gradW,gradH] = getGradient(A,W,H,par);
    end

    switch stopRule
        case 1
            pGradW = projGradient(W,gradW);
            pGradH = projGradient(H,gradH);
            pGrad = [pGradW(:); pGradH(:)];
            retVal = norm(pGrad)/length(pGrad);
        case 2
            pGradW = projGradient(W,gradW);
            pGradH = projGradient(H,gradH);
            pGrad = [pGradW(:); pGradH(:)];
            retVal = norm(pGrad);
        case 3
            resmat=min(H,gradH); resvec=resmat(:);
            resmat=min(W,gradW); resvec=[resvec; resmat(:)]; 
            deltao=norm(resvec,1); %L1-norm
            num_notconv=length(find(abs(resvec)>0));
            retVal=deltao/num_notconv;
        case 0
            retVal = 1e100;
    end
end
%-------------------------------------------------------------------------------
function sqErr = getSquaredError(A,W,H,init)
	sqErr = max((init.norm_A)^2 - 2*trace(H*(A'*W))+trace((W'*W)*(H*H')),0 );
end

function retVal = getObj(sqErr,W,H,par)
	retVal = 0.5 * sqErr;
	retVal = retVal + par.reg_w(1) * sum(sum(W.*W));
	retVal = retVal + par.reg_w(2) * sum(sum(W,2).^2);
	retVal = retVal + par.reg_h(1) * sum(sum(H.*H));
	retVal = retVal + par.reg_h(2) * sum(sum(H,1).^2);
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

function [grad] = modifyGradient(grad,X,reg,par)
	if reg(1) > 0
		grad = grad + 2 * reg(1) * X;
	end
	if reg(2) > 0
		grad = grad + 2 * reg(2) * ones(par.k,par.k) * X;
	end
end

function [grad] = getGradientOne(AtA,AtB,X,reg,par)
	grad = AtA*X - AtB;
	grad = modifyGradient(grad,X,reg,par);
end

function [gradW,gradH] = getGradient(A,W,H,par)
	HHt = H*H';
	HHt_reg = applyReg(HHt,par,par.reg_w);

	WtW = W'*W;
	WtW_reg = applyReg(WtW,par,par.reg_h);

    gradW = W*HHt_reg - A*H';
    gradH = WtW_reg*H - W'*A;
end

%-------------------------------------------------------------------------------
function pGradF = projGradient(F,gradF)
	pGradF = gradF(gradF<0|F>0);
end

%-------------------------------------------------------------------------------
function [W,H,weights] = normalize_by_W(W,H)
    norm2=sqrt(sum(W.^2,1));
    toNormalize = norm2>0;

    W(:,toNormalize) = W(:,toNormalize)./repmat(norm2(toNormalize),size(W,1),1);
    H(toNormalize,:) = H(toNormalize,:).*repmat(norm2(toNormalize)',1,size(H,2));

	weights = ones(size(norm2));
	weights(toNormalize) = norm2(toNormalize);
end


