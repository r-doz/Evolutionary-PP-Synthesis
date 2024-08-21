# Contains the functions for computing the resulting distribution when an assignment instruction is encountered (in state nodes).

# SOGA (defined in SOGA.py)
# |- update_rule
#    |- sym_expr
#    |- update_gaussian

from libSOGAshared import *
from ASGMTListener import *
from ASGMTParser import * 
from ASGMTLexer import *

class AsgmtRule(ASGMTListener):
    
    def __init__(self, var_list, data):
        self.var_list = var_list
        self.data = data
        self.func = None           # stores the function
        self.target = None         # stores the index of the target variable
        
        self.aux_pis = []          # stores the weights of auxiliary variables
        self.aux_means = []        # stores the means of auxiliary variables
        self.aux_covs = []         # stores the cov matrices of auxiliary variables
        
        self.is_prod = None        # checks whether a term is a product of two vars
        
    def enterAssignment(self, ctx):
        self.target = self.var_list.index(ctx.symvars().getVar(self.data))
   
       
    def enterAdd(self, ctx):
        
        if len(ctx.add_term())==1 and len(ctx.add_term(0).term()) == 2:
            self.is_prod = 1
            for term in ctx.add_term(0).term():
                self.is_prod = self.is_prod*term.is_var(self.data)
        if self.is_prod:
            self.mul_idx = []
        else:
            self.add_coeff = [0.]*len(self.var_list)
            self.add_const = 0
            
            
    def enterAdd_term(self,ctx):
        # product between variables
        if self.is_prod:
            for term in ctx.term():
                if not term.gm() is None:
                    self.aux_pis.append(eval(term.gm().list_()[0].getText()))
                    self.aux_means.append(eval(term.gm().list_()[1].getText()))
                    self.aux_covs.append(np.array(eval(term.gm().list_()[2].getText()))**2)
                    self.mul_idx.append(int(len(self.var_list)+len(self.aux_pis)-1))
                elif not term.symvars() is None:
                    self.mul_idx.append(self.var_list.index(term.symvars().getVar(self.data)))
            
            def mul_func(comp):
                i = self.target
                j, k = self.mul_idx
                mu = comp.gm.mu[0]
                sigma = comp.gm.sigma[0]
                final_pi = []
                final_mu = []
                final_sigma = []
                for part in product(*[range(len(mean)) for mean in self.aux_means]):
                    # STEP 1: for a given combination of components of the auxiliary variables, creates a new component extending comp
                    aux_pi = 1
                    aux_mean = list(copy(mu))
                    aux_sigma = []
                    for p,q in zip(range(len(self.aux_means)), part):
                        aux_pi = aux_pi*self.aux_pis[p][q]
                        aux_mean.append(self.aux_means[p][q])
                        aux_sigma.append(self.aux_covs[p][q])
                    aux_mean = np.array(aux_mean)
                    aux_sigma = np.diag(aux_sigma)
                    aux_cov = np.block([[sigma, np.zeros((len(sigma), len(aux_sigma)))], [np.zeros((len(aux_sigma), len(sigma))), aux_sigma]])
                    # STEP 2: computes mean and covariance matrix for the extended component
                    new_mu = copy(mu)
                    new_mu[i] = (aux_cov[j,k] + aux_mean[j]*aux_mean[k])
                    new_sigma = copy(sigma)
                    new_sigma[i,:] = new_sigma[:,i] = (aux_mean[j]*aux_cov[k,:] + aux_mean[k]*aux_cov[j,:])[:len(mu)] 
                    new_sigma[i,i] = (aux_cov[j,k]**2 + 2*aux_cov[j,k]*aux_mean[j]*aux_mean[k] + aux_cov[j,j]*aux_cov[k,k] + aux_cov[j,j]*aux_mean[k]**2 + aux_cov[k,k]*aux_mean[j]**2)
                    # STEP 3: appends weight, new mean and new covariance matrix to the final vectors
                    final_pi.append(aux_pi)
                    final_mu.append(new_mu)
                    final_sigma.append(new_sigma)
                return GaussianMix(final_pi, final_mu, final_sigma)
                        
            self.func = mul_func
        # linear combination
        else:
            coeff = 1
            var_idx = None
            for term in ctx.term():
                if term.sub() is not None:
                    coeff = -1*coeff
                else:
                    coeff = 1*coeff
                if term.is_const(self.data):
                    coeff = coeff*term.getValue(self.data)
                elif not term.symvars() is None:
                    var_idx = self.var_list.index(term.symvars().getVar(self.data))
                elif not term.gm() is None:
                    self.aux_pis.append(eval(term.gm().list_()[0].getText()))
                    self.aux_means.append(eval(term.gm().list_()[1].getText()))
                    self.aux_covs.append(np.array(eval(term.gm().list_()[2].getText()))**2)
                    var_idx = len(self.add_coeff) + 1
            if not var_idx is None:
                if var_idx < len(self.add_coeff):
                    self.add_coeff[var_idx] = coeff
                else:
                    self.add_coeff.append(coeff)
            else:
                self.add_const = self.add_const + coeff
                                
    def exitAdd(self, ctx):
        if not self.is_prod:
            if not np.all(np.array(self.add_coeff) == 0):
                
                def add_func(comp):
                    i = self.target
                    mu = comp.gm.mu[0]
                    sigma = comp.gm.sigma[0]
                    final_pi = []
                    final_mu = []
                    final_sigma = []
                    for part in product(*[range(len(mean)) for mean in self.aux_means]):
                        # STEP 1: for a given combination of components of the auxiliary variables, creates a new component extending comp
                        aux_pi = 1
                        aux_mean = list(copy(mu))
                        aux_sigma = []
                        for p,q in zip(range(len(self.aux_means)), part):
                            aux_pi = aux_pi*self.aux_pis[p][q]
                            aux_mean.append(self.aux_means[p][q])
                            aux_sigma.append(self.aux_covs[p][q])
                        aux_mean = np.array(aux_mean)
                        aux_sigma = np.diag(aux_sigma)
                        aux_cov = np.block([[sigma, np.zeros((len(sigma), len(aux_sigma)))], [np.zeros((len(aux_sigma), len(sigma))), aux_sigma]])
                        # STEP 2: computes mean and covariance matrix for the extended component
                        # implementation 1
                        #A = np.eye(len(aux_mean)) 
                        #A[i,:] = np.array(self.add_coeff)
                        #b = np.zeros(len(aux_mean))
                        #b[i] = self.add_const
                        #new_mu = A.dot(aux_mean) + b
                        #new_mu = new_mu[:len(mu)]
                        #new_sigma = A.dot(aux_cov).dot(np.transpose(A))
                        #new_sigma = new_sigma[:len(mu),:len(mu)]
                        # implementation 2
                        new_mu = copy(mu)
                        new_mu[i] = np.array(self.add_coeff).dot(aux_mean) + np.array(self.add_const)
                        new_sigma = copy(sigma)
                        new_sigma[i,:] = new_sigma[:,i] = np.array(self.add_coeff).dot(aux_cov)[:len(mu)]
                        new_sigma[i,i] = np.array(self.add_coeff).dot(aux_cov).dot(np.array(self.add_coeff))
                        # STEP 3: appends weight, new mean and new covariance matrix to the final vectors
                        final_pi.append(aux_pi)
                        final_mu.append(new_mu)
                        final_sigma.append(new_sigma)
                    return GaussianMix(final_pi, final_mu, final_sigma)
            
                self.func = add_func
            
            else:
                
                c = self.add_const
                
                def const_func(comp):
                    i = self.target
                    new_mu = copy(comp.gm.mu[0])
                    new_sigma = copy(comp.gm.sigma[0])
                    new_mu[i] = c
                    new_sigma[i,:] = np.zeros(len(new_mu))
                    new_sigma[:,i] = np.zeros(len(new_mu))
                    return GaussianMix(comp.gm.pi, [new_mu], [new_sigma])
            
                self.func = const_func
        
    
def asgmt_parse(var_list, expr, data):
    """ Parses expr using ANTLR4. Returns a function """
    lexer = ASGMTLexer(InputStream(expr))
    stream = CommonTokenStream(lexer)
    parser = ASGMTParser(stream)
    tree = parser.assignment()
    asgmt_rule = AsgmtRule(var_list, data)
    walker = ParseTreeWalker()
    walker.walk(asgmt_rule, tree) 
    return asgmt_rule.func
        
        
def update_rule(dist, expr, data):
    """ Applies expr to dist. It first parses expr using the function asgmt_parse, implemented as an ANTLR listener. asgmt_parse returns a function rule_func, such that, rule_func(GaussianMix) returns a new GaussianMix object obtained applying expr to the initial distribution. rule_func is applied to each component of dist, and the resulting Gaussian mixtures are stored in a single GaussianMix object."""
    
    if expr == 'skip':
        return dist
    else:
        rule_func = asgmt_parse(dist.var_list, expr, data)    # define function
        new_pi = []
        new_mu = []
        new_sigma = []
        for k in range(dist.gm.n_comp()):
            comp = Dist(dist.var_list, dist.gm.comp(k))
            new_mix = rule_func(comp)
            new_pi += list(dist.gm.pi[k]*np.array(new_mix.pi))
            new_mu += new_mix.mu
            new_sigma += new_mix.sigma
        return Dist(dist.var_list, GaussianMix(new_pi, new_mu, new_sigma))
    
    


    
    
    