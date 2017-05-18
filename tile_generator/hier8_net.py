import logging, logging.config
import numpy as np
import scipy.sparse as sps
import scipy.optimize as opt
import numpy.linalg as nla
import time
import json
from numpy import random


class Hier8_net():

    def __init__(self):

        #print('start hier8')
        m = 0;

    def hier8_net(self,A,k, iteration): 

       # print(np.where(np.sum(A[:,0]))


        trial_allowance = 3 
        unbalance = 0.1 
        vec_norm = 2.0 
        normW = True 
        tol = 1e-4 
        maxiter= 10000 

        m = np.shape(A)[0]
        n = np.shape(A)[1]

        timings = np.zeros((1,k-1))
        #clusters = np.zeros((1,2*(k-1)))
        clusters = []
        #Ws = np.zeros((1,2*(k-1)))
        Ws = []
        W_buffer = [] 
        H_buffer = [] 
        priorities = np.zeros((2*(k-1)))
        is_leaf = -1 * np.ones(2*(k-1))
        tree = np.zeros((2,2*(k-1)))
        splits = -1 * np.ones(k-1)

        term_subset =np.where(np.sum(A, axis=1)!=0) 
        # print(m,n)
        # print(np.shape(term_subset))
        term_subset = np.array(term_subset[0])
        term_subset = term_subset.flatten()
        W = np.random.rand(np.size(term_subset),2)
        H = np.random.rand(n,2)

        #print('hier8')




        if(np.size(term_subset) == m):
            W, H = self.nmfsh_comb_rank2(A, W ,H, iteration )
            #print('done')
        else : 
            W_tmp, H = self.nmfsh_comb_rank2(A[term_subset,:], W, H, iteration)
            #print('done rank2')
            W = np.zeros((m,2))
            W[term_subset,:] = W_tmp

        result_used = 0


        for i in range(0,k-1):
            if(i == 0):
                split_node = 0; 
                new_nodes = np.array([0,1])
                min_priority = 1e308
                split_subset = []
            else: 
                leaves = np.where(is_leaf==1)[0]
                #leaves = np.array(leaves)
                #print('leaves: ',leaves)
                temp_priority = priorities[leaves]
                #print('temp_priority', temp_priority)
                #print('priorities', priorities)
                #min_priority = np.minimum(temp_priority[temp_priority>0])
                #print('min_priority' + min_priority)
                split_node = leaves[split_node]
                is_leaf[split_node] = 0 
                #print('split_node: ',split_node)            
                W = W_buffer[split_node]
                H = H_buffer[split_node]
                split_subset = clusters[split_node]
                new_nodes = np.array([result_used, result_used+1])
                tree[0,split_node] = new_nodes[0]
                tree[1,split_node] = new_nodes[1]
                #print('new nodes', new_nodes)

            result_used = result_used + 2
            max_val, cluster_subset =  H.T.max(0), H.T.argmax(0)  
            #clusters[new_nodes[0]] = np.where(cluster_subset==0)  
            # temp = np.where(cluster_subset == 0 )
            # temp = np.array(temp)
            # temp2 = np.where(cluster_subset == 1)
            # temp2 =np.array(temp2)
            # clusters[new_nodes[0]] = temp
            # clusters.append(temp2)
            clusters.append(np.array(np.where(cluster_subset == 0)))
            clusters.append(np.array(np.where(cluster_subset == 1)))
            #clusters = np.array(clusters)
            Ws.append(W[:,0])
            Ws.append(W[:,1])
            splits[i] = split_node
            is_leaf[new_nodes] = 1 

            #print('length of each clusters', np.shape(clusters[new_nodes[0]]), np.shape(clusters[new_nodes[1]]))

            subset = clusters[new_nodes[0]]
            subset, W_buffer_one, H_buffer_one, priority_one = self.trial_split(trial_allowance, unbalance, min_priority, A, subset, W[:,0])
            #print('done trial_split')
            clusters[new_nodes[0]] = subset
            W_buffer.append(W_buffer_one)
            H_buffer.append(H_buffer_one)
            priorities[new_nodes[0]] = priority_one
            #print('priority_one', priority_one)

            subset = clusters[new_nodes[1]]
            subset, W_buffer_one, H_buffer_one, priority_one = self.trial_split(trial_allowance, unbalance, min_priority, A, subset, W[:,1])
            clusters[new_nodes[1]] = subset
            W_buffer.append(W_buffer_one)
            H_buffer.append(H_buffer_one)
            priorities[new_nodes[1]] = priority_one
            #logging.debug('done one cicle')


        #print(Ws)
        #print(np.shape(Ws))
        return Ws 
              #  else:    
              #      min_priority = min(temp_priority[temp_priority>0])


    def  trial_split(self, trial_allowance, unbalance, min_priority, A, subset, W_parent):

        #logging.debug('trial_split')

        trial = 0
        subset = np.array(subset)[0]
        subset_backup = subset 
        while(trial < trial_allowance):
            cluster_subset, W_buffer_one, H_buffer_one, priority_one = self.actual_split(A, subset, W_parent)
            if(priority_one < 0 ):
                break;
            unique_cluster_subset  = np.unique(cluster_subset)
            temp = np.where(cluster_subset == unique_cluster_subset[0])
            temp = np.array(temp)
            temp = temp.flatten()
            length_cluster1 = len(temp)

            temp2 = np.where(cluster_subset == unique_cluster_subset[1])
            temp2 = np.array(temp2)
            temp2 = temp2.flatten()
            length_cluster2 = len(temp2)

            if(np.minimum(length_cluster1, length_cluster2) < unbalance * len(cluster_subset)):
                min_val = np.minimum(length_cluster1,length_cluster2)
                if (length_cluster1 - length_cluster2 >=0):
                    idx_small = 0
                else:
                    idx_small = 1
                subset_small = np.where(cluster_subset == unique_cluster_subset[idx_small])[0]
                #print(np.shape(subset))
                #print(subset_small)
                subset_small = subset[subset_small]
                cluster_subset_small, W_buffer_one_small, H_buffer_one_small, priority_one_small = self.actual_split(A, subset_small, W_buffer_one[:,idx_small])
                if (priority_one_small < min_priority):
                    trial = trial + 1 
                    if(trial < trial_allowance):
                        subset = np.setdiff1d(subset, subset_small)
                    else: 
                        break;
                else:
                    break; 
            else:
                break;        

                #subset_small = np.array(subset_small)
                #subset_small = subset_small.faltten()
                #print(subset_small)

        if( trial == trial_allowance):

            subset = subset_backup
            W_buffer_one = np.zeros((m,2))
            H_buffer_one = np.zeros(len(subset,2))
            priority_one = -2

        return subset, W_buffer_one, H_buffer_one, priority_one

    def actual_split(self, A, subset, W_parent):

        #logging.debug('actual_split')

        m = np.shape(A)[0]
        n = np.shape(A)[1]
        #print(np.size(subset))

        if( np.size(subset) <= 3):
            cluster_subset = np.ones((1,len(subset)))
            W_buffer_one = np.zeros((m,2))
            H_buffer_one = np.zeros((len(subset),2))
            priority_one = -1 
        else:
            subset = subset.flatten()
            #print(np.sum(A[:,subset], axis=1))
            #print(np.shape(np.sum(A[:,subset], axis=1)))
            term_subset = np.where(np.sum(A[:,subset], axis=1) !=0)
            term_subset = np.array(term_subset)[0]
            term_subset = term_subset.flatten()
            #print('actual_split')
            #print(np.shape(term_subset))
            # print(A[term_subset][:,subset])
            #print(np.shape(A[term_subset][:,subset]))
            A_subset = A[term_subset][:,subset]; 
            W = random.rand(len(term_subset),2)
            H = random.rand(len(subset),2)
            W, H = self.nmfsh_comb_rank2(A_subset, W, H, 200)
            #print(np.shape(H))
            max_val, cluster_subset =  H.T.max(0), H.T.argmax(0)  
            W_buffer_one = np.zeros((m,2))
            W_buffer_one[term_subset,:] = W 
            H_buffer_one = H 
            if(len(np.unique(cluster_subset))>1):
                priority_one = self.compute_priority(W_parent, W_buffer_one)
                #print('priority_one',priority_one)
            else:
                priority_one = -1 

        return cluster_subset, W_buffer_one, H_buffer_one, priority_one

    def compute_priority(self, W_parent, W_child):

        #logging.debug('compute_priority')


        #print('compute_priority')
        n = len(W_parent)
        #print(n)
        sorted_parent, idx_parent = np.sort(W_parent)[::-1], np.argsort(W_parent[::-1]) #descending order
        sorted_child1, idx_child1 = -np.sort(-W_child[:,0]), np.argsort(-W_child[:,0])
        sorted_child2, idx_child2 = -np.sort(-W_child[:,1]), np.argsort(-W_child[:,1])

        temp = np.array(np.where(W_parent !=0))
        temp = temp.flatten()
        n_part = len(temp)
    
        if(n_part <= 1):
            priority = -3
        else:
            weight = np.log(np.arange(n,0,-1))
            first_zero = np.where(sorted_parent==0 & 1)[0]
            if(len(first_zero)>0):
                weight[first_zero] = 1 
            weight_part = np.zeros((n,1)).flatten()
            weight_part[0:n_part] = np.log(np.arange(n_part,0,-1))
            sorted1, idx1 = np.sort(idx_child1), np.argsort(idx_child1)
            sorted2, idx2 = np.sort(idx_child2), np.argsort(idx_child2)
          
            max_pos =  np.maximum(idx1, idx2) 
            discount = np.log(n - max_pos[idx_parent]+1)
            discount[discount ==0] = np.log(2)
            weight = weight / discount
            weight_part = weight_part / discount
            #print(weight, weight_part)
            priority = self.NDCG_part(idx_parent, idx_child1, weight, weight_part) * self.NDCG_part(idx_parent, idx_child2, weight, weight_part)
        


        return priority        


    def NDCG_part(self, ground, test, weight, weight_part):

        #logging.debug('NDCG_part')

        #print('NDCG_part')
        #print('ground', ground)
        sorted1, seq_idx = np.sort(ground), np.argsort(ground)
        # print(sorted1)
        # print(seq_idx)
        # print(weight_part)
        weight_part = weight_part[seq_idx]
        # print(weight_part)
        

        n = len(test)
        uncum_score = weight_part[test]
        uncum_score[1:n-1:1] = uncum_score[1:n-1:1] / np.log2(np.arange(2,n,1))
        #print(uncum_score)
        cum_score = np.cumsum(uncum_score)

        ideal_score = np.sort(weight)[::-1]
        ideal_score[1:n-1:1] = ideal_score[1:n-1:1] / np.log2(np.arange(2,n,1))
        cum_ideal_score = np.cumsum(ideal_score)

        score = cum_score / cum_ideal_score 
        score = score[-1]

        #print(score)

        return score
                


    def nmfsh_comb_rank2(self,A, Winit, Hinit, iteration):

            
        m = np.shape(A)[0]
        n = np.shape(A)[1]
        tol = 1e-4
        vec_norm = 2.0
        normW = True

        W = Winit 
        H = Hinit.T

        #print('nmfsh_comb_rank2')

        #logging.debug('nmfsh_comb_rank2')



        left = H.dot(H.T)
        right = A.dot(H.T)

        #print(np.shape(left), np.shape(right))
        #print('shape of A:' ,np.shape(A))

        for i in range(0,iteration):
            if(nla.matrix_rank(left)<2):
                #print('The matrix H is singular')
                W = np.zeros((m,2))
                H = np.zeros((2,n))
                # U, S, V = scipy.linalg.svd(A)
             
                # if(np.sum(U)<0):
                #     U = - U 
                #     V = - V 
                # W[:,0] = U 
                # H[0,:] = V.T 

      
            W = self.anls_entry_rank2_precompute(left,right,W);

            #print('W shape', np.shape(W))
            norms_W = np.sqrt(np.sum(np.square(W)))
            W = W/norms_W
            left = W.T.dot(W)
            right = A.T.dot(W)
            #print(np.shape(A), np.shape(right))

            H = self.anls_entry_rank2_precompute(left, right, H.T).T
            gradH = left.dot(H) - right.T 
            left = H.dot(H.T)
            right = A.dot(H.T)

            gradW = W.dot(left) - right


        if vec_norm !=0:
            if normW :
                norms = np.sum(np.power(W,vec_norm), axis=0)*(1/vec_norm)

                #logging.debug(norms)
                #norms = np.matrix(norms)
                H[:,0] = H[:,0] * norms[0]
                H[:,1] = H[:,1] * norms[1]
                #logging.debug('qwewq')

                if(norms[0] != 0):
                    #logging.debug('divide')
                    W[:,0] = W[:,0] / norms[0]

                if(norms[1] != 0):
                    #logging.debug('22432')
                    W[:,1] = W[:,1] / norms[1]
                
                #logging.debug('sada')

                #W[:,1] = W[:,1] / norms[1]
            else :
                norms = np.sum(np.power(H,vec_norm),axis = 0)*(1/vec_norm)
                #norms = np.matrix(norms)
                H[:,0] = H[:,0] * norms[0]
                H[:,1] = H[:,1] * norms[1]

                if(norms[0] != 0):
                    W[:,0] = W[:,0] / norms[0]
              
                if(norms[1] != 0):
                    W[:,1] = W[:,1] / norms[1] 

        H = H.T

        #logging.debug(np.shape(H))
             


        return (W,H)



    def anls_entry_rank2_precompute(self, left, right, H):


        n = np.shape(right)[0]

        solve_either = np.zeros((n,2)) 
        if(left[0,0] !=0):
            solve_either[:,0] =  right[:,0] / left[0,0]
        else:
            solve_either[:,0] = right[:,0]
        if(left[1,1] !=0):
            solve_either[:,1] =  right[:,1] / left[1,1]
        else:
            solve_either[:,1] = right[:,1]


        #solve_either[:,0] = right[:,0] * (1/left[0,0])
        #solve_either[:,1] = right[:,1] * (1/left[1,1])

        #print('solve_either: ', solve_either)

        cosine_either = np.zeros((n,2))
        cosine_either[:,0] = np.multiply(solve_either[:,0] , np.sqrt(left[0,0]))
        cosine_either[:,1] = np.multiply(solve_either[:,1] , np.sqrt(left[1,1]))

        choose_first = (cosine_either[:,0] >= cosine_either[:,1])

        #print('choose_first', choose_first)
        #print(solve_either[:,1])
        #print(solve_either[choose_first,1])


        solve_either[choose_first,1] = 0
        solve_either[~choose_first,0] = 0

        #print('solve_either after: ',solve_either)


        if ( abs(left[0,0]) >= abs(left[0,1])):

            t = 0
            
            if(left[0,0]!=0):
               t = left[1,0]/left[0,0];     


            #t = left[1,0]/left[0,0];
            a2 = left[0,0] + t*left[1,0];
            b2 = left[0,1] + t*left[1,1];
            d2 = left[1,1] - t*left[0,1];

            e2 = right[:,0] + t * right[:,1]
            f2 = right[:,1] - t * right[:,0]

        else:
            ct = 0 

            if(left[1,0]!=0):
                ct = left[1,0]/left[1,0];

            #ct = left[0,0] / left[1,0]
            a2 = left[1,0] + ct * left[0,0]
            b2 = left[1,1] + ct * left[0,1]
            d2 = -left[0,1] + ct * left[1,1]

            e2 = right[:,1] + ct * right[:,0]
            f2 = -right[:,0] + ct * right[:,1]

        if (d2!=0):
            H[:,1] = f2 /d2
        if(a2!=0):
            H[:,0] = (e2-b2*H[:,1])/a2   



        # H[:,1] = f2 * (1/d2)
        # H[:,0] = (e2-b2*H[:,1])*(1/a2)    


        use_either = ~np.all(H>0, axis=1)

        #print('use_either:', np.shape(use_either))
        H[use_either,:] = solve_either[use_either,:]


        return H


    def nmfsh_comb_rank2_2(self,A, Winit, Hinit):
            
        m = np.shape(A)[0]
        n = np.shape(A)[1]
        tol = 1e-4
        vec_norm = 2.0
        normW = True

        W = Winit 
        H = Hinit.T

        #print('nmfsh_comb_rank2')


        left = H.dot(H.T)
        right = A.dot(H.T)

        #print(np.shape(left), np.shape(right))

        for i in range(0,1000):
            if(nla.matrix_rank(left)<2):
                #print('The matrix H is singular')
                W = np.zeors((m,2))
                H = np.zeros((2,n))
                U, S, V = nla.svd(A,1)
                if(np.sum(U)<0):
                    U = - U 
                    V = - V 
                W[:,0] = U 
                H[0,:] = V.T 

      
            W = self.anls_entry_rank2_precompute_2(left,right,W);

            #print('W shape', np.shape(W))
            norms_W = np.sqrt(np.sum(np.square(W)))
            W = W/norms_W
            left = W.T.dot(W)
            right = A.T.dot(W)
            #print(np.shape(A), np.shape(right))

            H = self.anls_entry_rank2_precompute_2(left, right, H.T).T
            gradH = left.dot(H) - right.T 
            left = H.dot(H.T)
            right = A.dot(H.T)

            gradW = W.dot(left) - right


        if vec_norm !=0:
            if normW :
                norms = np.sum(np.power(W,vec_norm), axis=0)*(1/vec_norm)
                #norms = np.matrix(norms)
                H[:,0] = H[:,0] * norms[0]
                H[:,1] = H[:,1] * norms[1]
                W[:,0] = W[:,0] / norms[0]
                W[:,1] = W[:,1] / norms[1]
            else :
                norms = np.sum(np.power(H,vec_norm),axis = 0)*(1/vec_norm)
                #norms = np.matrix(norms)
                H[:,0] = H[:,0] * norms[0]
                H[:,1] = H[:,1] * norms[1]
                W[:,0] = W[:,0] / norms[0]
                W[:,1] = W[:,1] / norms[1]

        H = H.T
             


        return (W,H)



    def anls_entry_rank2_precompute_2(self, left, right, H):


        n = np.shape(right)[0]

        solve_either = np.zeros((n,2)) 
        solve_either[:,0] = right[:,0] * (1/left[0,0])
        solve_either[:,1] = right[:,1] * (1/left[1,1])
        cosine_either = np.zeros((n,2))
        cosine_either[:,0] = np.multiply(solve_either[:,0] , np.sqrt(left[0,0]))
        cosine_either[:,1] = np.multiply(solve_either[:,1] , np.sqrt(left[1,1]))

        choose_first = (cosine_either[:,0] >= cosine_either[:,1])


        solve_either[choose_first,1] = 0
        solve_either[~choose_first,0] = 0

        if ( abs(left[0,0]) >= abs(left[0,1])):

            t = left[1,0]/left[0,0];
            a2 = left[0,0] + t*left[1,0];
            b2 = left[0,1] + t*left[1,1];
            d2 = left[1,1] - t*left[0,1];

            e2 = right[:,0] + t * right[:,1]
            f2 = right[:,1] - t * right[:,0]

        else:

            ct = left[0,0] / left[1,0]
            a2 = left[1,0] + ct * left[0,0]
            b2 = left[1,1] + ct * left[0,1]
            d2 = -left[0,1] + ct * left[1,1]

            e2 = right[:,1] + ct * right[:,0]
            f2 = -right[:,0] + ct * right[:,1]


        H[:,1] = f2 * (1/d2)
        H[:,0] = (e2-b2*H[:,1])*(1/a2)    


        use_either = ~np.all(H>0, axis= 1)
        H[use_either,:] = solve_either[use_either,:]


        return H
