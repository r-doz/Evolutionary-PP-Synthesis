# Contains some general purpose classes, functions and variables used by the SOGA Python Libraries. 
# In particular it contains:
# - import statement for auxiliary Python libraries;
# - definition of an handle used for debugging;
# - definition of tolerance parameters used by various functions;
# - classes definition for representing distributions and Gaussian Mixtures;
# - function definitions for numerical stability of the covariance matrices;
# - function definitions invoked by multiple functions in different libraries.

# TO DO:
# -  add controls on the attributes of GaussianMix (lenghts of pi, mu, sigma, dimensions of mu and sigma)

# AUXILIARY LIBRARIES 

from copy import deepcopy, copy
from sympy import *
import re
import numpy as np
from scipy.stats import norm
from scipy.stats import truncnorm
from scipy.stats import multivariate_normal as mvnorm
from itertools import product, chain

from time import time

### DEBUGGING METHOD

import functools

def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        print(f"Calling {func.__name__}({signature})\n")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}\n")           # 4
        return value
    return wrapper_debug 

### TOLERANCE PARAMETERS 

delta_tol = 1e-10 # if the 1-norm of a covariance matrix is <= delta_tol the corresponding Gaussian component is treated as a delta
prob_tol = 1e-10 # probability below prob_tol are treated as zero
eig_tol = 1e-4

### CLASSES FOR DISTRIBUTIONS AND GAUSSIAN MIXTURES

class GaussianMix():
    """ A Gaussian Mixtures is represented by a list of mixing coefficients (stored in pi), a list of means (stored in mu) and a list of covariance matrices (stored in sigma)."""
    
    def __init__(self, pi, mu, sigma):
        self.pi = list(pi)         # pi is a list of scalars whose sum is 1
        self.mu = list(mu)         # mu is a list, with len(mu)==len(pi) and each element is an array
        self.sigma = list(sigma)   # sigma is a list, with len(sigma)==len(pi), and each element is a covariance matrix
    
    def n_comp(self):
        return len(self.pi)
    
    def n_dim(self):
        return len(self.mu[0])
    
    def __repr__(self):
        str_repr = 'pi: ' + str(self.pi) + ' mu: ' + str(self.mu) + ' sigma: ' + str(self.sigma)
        return str_repr
    
    def comp(self, k):
        return GaussianMix([1.], [self.mu[k]], [self.sigma[k]])
        
    # Pdfs and Cdfs 
    def comp_pdf(self, x, k):
        if np.sum(abs(self.sigma[k])) > delta_tol:
            return mvnorm.pdf(x, mean=self.mu[k], cov=self.sigma[k], allow_singular=True)
        else:
            if np.all(x == self.mu[k]):
                return 1.0
            else:
                return 0.0
            
    def marg_comp_pdf(self, x, k, idx):
        if np.sum(abs(self.sigma[k])) > delta_tol:
            return norm.pdf(x, loc=self.mu[k][idx], scale=np.sqrt(self.sigma[k][idx,idx]))
        else:
            if np.all(x == self.mu[k][idx]):
                return 1.0
            else:
                return 0.0
    
    def pdf(self, x):
        return sum([self.pi[k]*self.comp_pdf(x,k) for k in range(self.n_comp())])
    
    def marg_pdf(self, x, idx):
        return sum([self.pi[k]*self.marg_comp_pdf(x,k,idx) for k in range(self.n_comp())])
    
    def comp_cdf(self, x, k):
        return mvnorm.cdf(x, mean=self.mu[k], cov=self.sigma[k], allow_singular=True)
    
    def marg_comp_cdf(self, x, k, idx):
        if np.sum(abs(self.sigma[k])) > delta_tol:
            return norm.cdf(x, loc=self.mu[k][idx], scale=np.sqrt(self.sigma[k][idx,idx]))
        
    def cdf(self, x):
        return sum([self.pi[k]*self.comp_cdf(x,k) for k in range(self.n_comp())])
    
    def marg_cdf(self, x, idx):
        return sum([self.pi[k]*self.marg_comp_cdf(x,k,idx) for k in range(self.n_comp())])
      
    
    # Moments of mixtures
    def mean(self):
        return np.array(self.pi).dot(np.array(self.mu))
    
    def cov(self):
        v = np.array(self.mu) - self.mean()
        cov = np.tensordot(np.array(self.pi), np.array(self.sigma), axes=1) + np.transpose(v).dot((np.array(self.pi).reshape(-1,1)*v))
        return cov


class Dist():
    """ A distribution is given by a ordered list of variable names, stored in var_list, and a Gaussian Mixture, stored in gm, describing the joint distribution over the variable vector"""
    def __init__(self, var_list, gm):
        self.var_list = var_list
        self.gm = gm
        
    def __str__(self):
        return 'Dist<{},{}>'.format(self.var_list, self.gm)
    
    def __repr__(self):
        return str(self)
        
### FUNCTIONS FOR NUMERICAL STABILITY OF COVARIANCE MATRICES

def make_psd(sigma):
    """
    Triggered when sigma is not positive semidefinite. Sets to 1e-10 negative eigenvalues of sigma. If the eigenvalues or the total error in the substitution are above a certain threshold prints an error message.
    """
    new_sigma = make_sym(sigma)
    eig, M = np.linalg.eigh(new_sigma)
    add = 0
    delta_eig = 1e-8
    c_it = 0
    while not np.all(eig > 1e-15):
    #while True:
        c_it+=1
        add = add + delta_eig
        for i, e in enumerate(eig):
            if e <= 1e-15:
                #if abs(e) > eig_tol:
                    #print('Warning: substituting eigenvelue {} can lead to a large error'.format(e))
                eig[i] = add
        new_sigma = M.dot(np.diag(eig)).dot(M.transpose())
        #new_sigma = make_sym(new_sigma)
        eig, M = np.linalg.eigh(new_sigma)
    
    rel_err = np.sum(abs(new_sigma-sigma))
    if rel_err > eig_tol:
        print('Warning: eigenvalue substitution led to an error of: {}'.format(rel_err))
    #mvnorm.cdf([0]*len(new_sigma), mean=[0]*len(new_sigma), cov=new_sigma, allow_singular=False)
    return new_sigma

def make_sym(sigma):
    """ 
    Reassigns sigma to make it symmetric. For sigma[i,j]!=sigma[j,i] substitutes both with the average value. If the substitution leads to an error above a certain threshold prints an error message.
    """
    for i in range(len(sigma)):
        for j in range(i+1,len(sigma)):
            if sigma[i,j] != sigma[j,i]:
                v = (sigma[i,j] + sigma[j,i])/2
                if abs(v-sigma[i,j]) > eig_tol: 
                    print('substituting {} with {}'.format(sigma[i,j], v))
                if abs(v-sigma[i,j]) > eig_tol: 
                    print('substituting {} with {}'.format(sigma[j,i], v))
                sigma[i,j] = sigma[j,i] = v
    return sigma

        
### SHARED FUNCTIONS 

def extract_aux(dist, trunc):
    """ Parses a string trunc to check for any gm(pi, mu, sigma) variable and adds it to dist in the form of an auxialiary variable with suitable parameters """
    groups = [m.group() for m in re.finditer('gm\(.*?\)', trunc)]
    aux_dist = deepcopy(dist)
    aux_trunc = trunc
    # for each gm(pi, mu, sigma) a new variable is added
    for n_aux, group in enumerate(groups):
        new_pi = []
        new_mu = []
        new_sigma = []
        aux_name = 'aux{}'.format(n_aux)
        aux_trunc = aux_trunc.replace(group, aux_name)
        pi_list, mu_list, sigma_list = [eval(m.group()) for m in re.finditer('\[.*?\]', group)]
        aux_dist.var_list.append(aux_name)
        # for each component of the original distribution dist and for each component of a variable gm(pi, mu, sigma) a new Gaussian component is generated with mixing coefficient dist.pi[i]*pi[i].
        for k in range(aux_dist.gm.n_comp()):
            for j in range(len(pi_list)):
                new_pi.append(aux_dist.gm.pi[k]*pi_list[j])
                new_mu.append(np.hstack((aux_dist.gm.mu[k], mu_list[j])))
                old_sigma = aux_dist.gm.sigma[k]
                d = len(old_sigma)
                aux_sigma = np.zeros((d+1,d+1))
                aux_sigma[:d,:d] = old_sigma
                aux_sigma[-1,-1] = sigma_list[j]**2
                new_sigma.append(aux_sigma)
        aux_dist.gm = GaussianMix(new_pi, new_mu, new_sigma)
    return aux_dist, aux_trunc

def substitute_deltas(dist, trunc):
    """ Substitutes variables in trunc which are Dirac Delta """
    mu = dist.gm.mu[0]
    sigma = dist.gm.sigma[0]
    for i in range(len(sigma)):
        if sigma[i,i] < delta_tol:
            trunc = trunc.subs({dist.var_list[i]:mu[i]})
    return trunc
