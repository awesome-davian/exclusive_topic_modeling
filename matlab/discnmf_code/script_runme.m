clear all; 
close all;

load('infovasttt.mat');
disp('Topic modeling of two document sets (InfoVisVAST papers) published in 1995-2005 vs. 2006-2010');
AAA = A(:,[1:151,303:392]); BBB = A(:,[152:302,393:515]); % 1995-2005 vs. 2006-2010
k=10; kd=5;
[m,n1] = size(AAA);
[~,n2] = size(BBB);

init.W=rand(m,k); init.U=rand(m,k); init.H=rand(k,n1); init.V=rand(k,n2);

par.dic = dictionary; par.num = num2str(sum(AAA,2)); par.num2 = num2str(sum(BBB,2));
par.k = 10;



num = par.num; num2 = par.num2;
if size(num,2)>size(num2,2)
    n = size(num,2)-size(num2,2);
    num2 = [repmat(' ',size(num,1),n) num2];
end
if size(num,2)<size(num2,2)
    n = size(num2,2)-size(num,2);
    num = [repmat(' ',size(num,1),n) num];
end
par.num = num; par.num2 = num2;




% 2. baseline : batch NMF
[W,H,U,V,~,iter,~]=nmf2(AAA,BBB,k,kd,1000,100,'method','comp','verbose',0,'init',init);
batch.W=W;batch.H=H;batch.U=U;batch.V=V;


par.num1 = num2str(sum(AAA,2)); par.num2 = num2str(sum(BBB,2));
if size(par.num1,2)>size(par.num2,2)
    n = size(par.num1,2)-size(par.num2,2);
    par.num2 = [repmat(' ',size(par.num1,1),n) par.num2];
end
if size(par.num1,2)<size(par.num2,2)
    n = size(par.num2,2)-size(par.num1,2);
    par.num1 = [repmat(' ',size(par.num1,1),n) par.num1];
end

disp('');
disp('batch discNMF results: The first 5 is discrominative topics and the latter 5 is common ones.');
batch.topics = print(batch.W,batch.U,par);
