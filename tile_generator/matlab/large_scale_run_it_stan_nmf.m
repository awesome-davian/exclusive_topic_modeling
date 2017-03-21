
clear all;
% 
% fp = fopen('data/voca/voca_131103-131105');
% glob_data = textscan(fp,'%s %d');
% fclose(fp);
% glob_dict = glob_data(:,1);
tic
k = 5;
topk = 5;

fp = fopen('data/voca/voca_131103-131105');
voc_temp = textscan(fp,'%s %d');
fclose(fp);
dict = voc_temp(:,1);

basic_address_mtx = './data/mtx_neighbor/131103-131105/';
basic_address_voc = './data/voca/voca_131103-131105';
type = 'mtx';
year = '2013';
day = '308';
level = '11';
xfrom = 601;
xto = 604;
yfrom = 1276;
yto =  1279;


% initialization
voc_data = cell(xto-xfrom+1,yto-yfrom+1);
mtx_data = cell(xto-xfrom+1,yto-yfrom+1);
xcl_score = cell(xto-xfrom+1,yto-yfrom+1);
Topics = cell(xto-xfrom+1,yto-yfrom+1);
Freq_words = cell(xto-xfrom+1,yto-yfrom+1);
address_string = cell(xto-xfrom+1,yto-yfrom+1);
Sum_swd = cell(xto-xfrom+1,yto-yfrom+1);
Fr_wds = cell(xto-xfrom+1,yto-yfrom+1);

% Stop Words
Stop_words = {'http','gt','ye','wa','thi','ny','lt','im','ll','ya','rt','ha','lol','ybgac','ve','destexx','ur','mta','john','kennedi','st','wat','atl',' ',...
    'dinahjanefollowspre','nj ','york','nk','ili','bx','idk','doe','rn', '  ','pg','dimezthebulli','wu'};


for x = 1 : xto-xfrom+1
    for y = 1 : yto-yfrom+1
        address_string{x,y} = strcat( basic_address_mtx,type,'_',year,'_d',day,'_',level,'_',int2str(xfrom + x -1),'_',int2str(yfrom +y -1 ) );
        if exist( address_string{x,y}, 'file' ) 
            mtx_data{x,y} = load(address_string{x,y});
            [Topics{x,y},~,~,xcl_score{x,y},Freq_words{x,y}] = func_run_stanNMF_hals(mtx_data{x,y}, Stop_words, dict, k, topk);
            clear mtx_data{x,y}
        else
            xcl_score{x,y} = -1
            continue;
        end
    end
end

mat_xcl_score = zeros(xto-xfrom+1,yto-yfrom+1);
for x = 1 : xto-xfrom+1
    for y = 1 : yto-yfrom+1
            mat_xcl_score(x,y) = xcl_score{x,y};
    end
end

imagesc(mat_xcl_score)
colorbar


for x = 1:xto-xfrom+1   
    for  y =  1:yto-yfrom+1  
        if exist( address_string{x,y}, 'file' ) 
            
            text(xto-xfrom+1 - (x-1)-0.45 , yto-yfrom+1 -0.3 - (y-1), {Freq_words{x,y}{1}(1:3)}, 'FontSize', 10,'Color', 'red');
         %   text(xto-xfrom+1 - (x-1)-0.25 , yto-yfrom+1 -0.3 - (y-1), {Freq_words{x,y}{2}(1:3)}, 'FontSize', 10,'Color', 'red');
            text(xto-xfrom+1 - (x-1) , yto-yfrom+1 -0.3 - (y-1),Topics{x,y}(1:3), 'FontSize', 10,'Color', 'red');
         %   text(xto-xfrom+1 - (x-1)+0.3 , yto-yfrom+1 -0.3 - (y-1),Sum_swd{x,y}(1:2), 'FontSize', 11,'Color', 'black');
            
            text(xto-xfrom+1 - (x-1)-0.45, yto-yfrom+1 - (y-1),{Freq_words{x,y}{1}(6:8)}, 'FontSize', 10,'Color', 'black');
         %   text(xto-xfrom+1 - (x-1)-0.25, yto-yfrom+1 - (y-1), {Freq_words{x,y}{2}(6:8)}, 'FontSize', 10,'Color', 'black');
            text(xto-xfrom+1 - (x-1), yto-yfrom+1 - (y-1),Topics{x,y}(6:8), 'FontSize', 10,'Color', 'black');
         %   text(xto-xfrom+1 - (x-1)+0.3 , yto-yfrom+1 -0.3 - (y-1),Sum_swd{x,y}(1:2), 'FontSize', 11,'Color', 'black');
            
            text(xto-xfrom+1 - (x-1)-0.45, yto-yfrom+1 +0.3 - (y-1),{Freq_words{x,y}{1}(11:13)}, 'FontSize', 10,'Color', 'blue');
         %   text(xto-xfrom+1 - (x-1)-0.25, yto-yfrom+1 +0.3 - (y-1), {Freq_words{x,y}{2}(11:13)}, 'FontSize', 10,'Color', 'blue');
            text(xto-xfrom+1 - (x-1), yto-yfrom+1 + 0.3 - (y-1),Topics{x,y}(11:13), 'FontSize', 10,'Color', 'blue');
         %   text(xto-xfrom+1 - (x-1)+0.3 , yto-yfrom+1 -0.3 - (y-1),Sum_swd{x,y}(1:2), 'FontSize', 11,'Color', 'black');
            
 
            
        end
    end
end

elapsed_time = toc
% the global dictionary

%glob_data = load('voca_131103-131105');
%local_data
% loc_data = load('./data/mtx_neighbor/131103-131105/12_voc/voca_2013_d308_12_1202_2552');
% 
% % choose neighboring_matrix
% Tdm = load('./data/mtx_neighbor/131103-131105/12_mtx/308/mtx_2013_d308_12_1202_2552');

% % 2. proceed the NMF algorithm
% exclusiveness = 0.7;
% k=5;
% topk=5;
% Topics = {}; wtopk_score = {}; topic_score = {}; xcl_score = {};
% [Topics, wtopk_score, topic_score,xcl_score] = function_run_extm_updated0316(Tdm, exclusiveness, dict, k, topk);
