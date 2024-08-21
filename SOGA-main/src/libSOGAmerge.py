# Contains the functions for computing the resulting distribution when a merge is invoked according to the following dependencies.

# SOGA (defined in SOGA.py)
# |- merge
#     |- prune
#        |- classic_prune
#        |   |- compute_matrix_mean
#        |   |- dist
#        |   |- merge_comp
#        |- ranking_prune


from libSOGAshared import *


def merge(list_dist):
    """
    Given a list of couples (p,dist), where each dist is a GaussianMix object, computes a couple (current_p, current_dist), in which current_pi is the sum of p and current_dist is a single GaussianMix object.
    """
    final_pi = []
    final_mu = []
    final_sigma = []
    current_p = 0
    ## creates a single mixture
    for (p, dist) in list_dist:
        if p > 0:
            current_p += p
            final_pi = final_pi + list(p*np.array(dist.gm.pi))
            final_mu = final_mu + list(dist.gm.mu)
            final_sigma = final_sigma + list(dist.gm.sigma)
    
    if len(final_pi) == 0:
        d = len(list_dist[0][1].gm.mu[0])
        #print('no components found')
        return 0, Dist(list_dist[0][1].var_list, GaussianMix([0], [np.array([0]*d)], [np.zeros((d,d))]))
    
    final_pi = list(np.array(final_pi)/current_p)
    
    # deletes components with probability less than tol
    zero_list = np.where(np.array(final_pi) < prob_tol)[0]
    if len(zero_list)>0:
        if len(zero_list) == len(final_pi):
            d = len(dist.gm.mu[0])
            #print('no components found')
            return 0, Dist(list_dist[0][1].var_list, GaussianMix([0], [np.array([0]*d)], [np.zeros((d,d))]))
        else:
            for index in sorted(zero_list, reverse=True):
                del final_pi[index]
                del final_mu[index]
                del final_sigma[index]
    current_dist = Dist(list_dist[0][1].var_list, GaussianMix(final_pi, final_mu, final_sigma))
    return current_p, current_dist


def prune(current_dist, pruning, Kmax):
    if pruning == 'classic':
        current_dist = classic_prune(current_dist, Kmax)
    elif pruning == 'ranking':
        current_dist = ranking_prune(current_dist, Kmax)
    return current_dist


def ranking_prune(current_dist, Kmax):
    """ Keeps only the Kmax component with higher prob"""
    if current_dist.gm.n_comp() > Kmax:
        rank = np.argsort(current_dist.gm.pi)[::-1]
        current_dist.gm.pi = list(np.array(current_dist.gm.pi)[rank])[:Kmax]
        current_dist.gm.mu = list(np.array(current_dist.gm.mu)[rank])[:Kmax]
        current_dist.gm.sigma = list(np.array(current_dist.gm.sigma)[rank])[:Kmax]
        current_dist.gm.pi = list(np.array(current_dist.gm.pi)/sum(current_dist.gm.pi))
    return current_dist

def compute_matrix_mean(current_dist):
    s = len(current_dist.gm.pi)
    pi = np.array(current_dist.gm.pi)
    pmu = np.array(pi).reshape(-1,1)*np.array(current_dist.gm.mu)
    sums = pmu[:,None] + pmu
    pis = (pi + pi[:,None]).reshape(s,s,1)
    return sums/pis
        
def classic_prune(current_dist, Kmax):
    """ Merges components with optimal cost"""
    if current_dist.gm.n_comp() > Kmax:
        n = current_dist.gm.n_comp()
        #computes a matrix containing the weighted means
        matrix_mu = compute_matrix_mean(current_dist)
        # At the first iteration computes the whole matrix cot
        matrixcost = np.ones((n,n))*np.inf
        for i in range(n):
            for j in range(i):
                matrixcost[i,j] = current_dist.gm.pi[i]*dist(current_dist.gm.mu[i],matrix_mu[i,j]) + current_dist.gm.pi[j]*dist(current_dist.gm.mu[j],matrix_mu[i,j])
       
        while n > Kmax:
            # Computes indices of components with minimal cost
            min_idx = np.where(matrixcost == np.min(matrixcost))
            i, j = min_idx
            i = i[0]
            j = j[0]      
            # Merges components
            current_dist = merge_comp(current_dist, i, j, matrix_mu[i,j])
            # Updates 
            n = current_dist.gm.n_comp()
            matrix_mu = compute_matrix_mean(current_dist)
            matrixcost = matrix_delete(matrixcost, i, j)
            # If number of components still too high computes the new matrix cost adding just one row
            if n > Kmax:
                for j in range(n-1):
                    matrixcost[n-1,j] = current_dist.gm.pi[n-1]*dist(current_dist.gm.mu[n-1],matrix_mu[n-1,j]) + current_dist.gm.pi[j]*dist(current_dist.gm.mu[j],matrix_mu[n-1,j])
    return current_dist


def matrix_delete(matrix, i, j):
    matrix = np.delete(matrix, max(i,j), axis=0)
    matrix = np.delete(matrix, max(i,j), axis=1)
    matrix = np.delete(matrix, min(i,j), axis=0)
    matrix = np.delete(matrix, min(i,j), axis=1)
    matrix = np.vstack([matrix, np.ones((1, len(matrix)))*np.inf])
    matrix = np.hstack([matrix, np.ones((matrix.shape[0],1))*np.inf])
    return matrix

def dist(vec1, vec2):
    return sum((np.array(vec1)-np.array(vec2))**2)


def merge_comp(current_dist, i, j, tot_mean):
    pii, pij = current_dist.gm.pi[i], current_dist.gm.pi[j]
    compi, compj = current_dist.gm.comp(i), current_dist.gm.comp(j)
    # deletes component to be merged from the current dist
    idx_list = [i,j]
    idx_list.sort(reverse=True)
    for idx in idx_list:
        del current_dist.gm.pi[idx]
        del current_dist.gm.mu[idx]
        del current_dist.gm.sigma[idx]
    # computes statistics of the merged component
    tot_p = pii + pij
    v = np.array(np.array([compi.mu[0], compj.mu[0]])) - tot_mean
    tot_cov = np.tensordot(np.array([pii, pij])/tot_p, np.array([compi.sigma[0], compj.sigma[0]]), axes=1) + np.transpose(v).dot(((np.array([pii,pij])/tot_p).reshape(-1,1)*v))
    # updates distribution
    current_dist.gm.pi.append(tot_p)
    current_dist.gm.mu.append(tot_mean)
    current_dist.gm.sigma.append(tot_cov)
    return current_dist


