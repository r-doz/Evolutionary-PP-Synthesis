from algorithm.parameters import params
from fitness.base_ff_classes.base_ff import base_ff
#from stats.stats import stats
from scipy.stats import multivariate_normal
import random
import time as timeit
import signal
import sys
import numpy as np
import re
import torch
from torch.distributions.multivariate_normal import MultivariateNormal
import fitness.data_generating_process as dgp
import threading

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../SOGA-main/src')
from sogaPreprocessor import *
from producecfg import *
from libSOGA import *

torch.set_default_dtype(torch.float64)
# Define a custom exception for timeouts
class TimeoutException(Exception):
    pass

def timeout_handler():
    raise TimeoutException()

# Define a handler function for the timeout
#def handler(signum, frame):
#    raise TimeoutException("Code execution exceeded time limit")

def compute_likelihood(output_dist, data_var_list, data):
    """ computes the likelihood of output_dist with respect to variables data_var_list sampled in data """

    data = torch.tensor(data)
    likelihood = 0
    # extract indexes of the variables in the data
    data_var_index = [output_dist.var_list.index(element) for element in data_var_list ]
    
    for k in range(output_dist.gm.n_comp()):
        # extract the covariance matrix only for the variables in the data
        sigma = output_dist.gm.sigma[k][data_var_index][:, data_var_index]
        # selects indices of delta (discrete) variables and non-delta (continuous) variables
        deltas = np.where(np.diag(sigma) == 0)[0]
        not_deltas = np.where(np.diag(sigma) != 0)[0]
        # saves means of delta and non-delta variables and covariance matrix of non-delta
        mu_delta = torch.tensor(output_dist.gm.mu[k][deltas])
        mu_not_delta = torch.tensor(output_dist.gm.mu[k][not_deltas])
        sigma_not_delta = torch.tensor(sigma[not_deltas][:, not_deltas])
        try:
            # computes pdf of non-delta variables 
            if len(mu_not_delta) >= 1:  # if there is at least one continuous variable
                continuous_pdf = output_dist.gm.pi[k]*MultivariateNormal(mu_not_delta, sigma_not_delta).log_prob(data[:,not_deltas]).exp()
            else:
                continuous_pdf = output_dist.gm.pi[k]*torch.ones(len(data))
            # computes pmf of delta variables
            if len(mu_delta) >= 1:   # if there is at least one discrete variable
                discrete_pmf = torch.all((mu_delta == data[:, deltas]),dim=1)
            else:
                discrete_pmf = torch.ones(len(data))
        except ValueError:  # if the covariance matrix is singular
            return torch.tensor(-np.inf)
        except:
            raise
        likelihood += continuous_pdf*discrete_pmf # sums likelihood of every data over all components
    
    return torch.sum(torch.log(likelihood))/len(data)

class soga_fitness_trueskills(base_ff):
    """Fitness function for finding the length of the shortest path between
    two nodes in a grade compared to the known shortest path. Takes a path (
    list of node labels as strings) and returns fitness. Penalises output
    that is not the same length as the target."""

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()
        

    def evaluate(self, ind, **kwargs):
        self.default_fitness = -np.inf
        p = ind.phenotype
        #p = smooth_program(p)
        #print("\n" + p)
        #print("\n -----------------------------------------")

        fitness = 0
        timer = threading.Timer(60, timeout_handler)
        #t0 = time.time()
        try:
            #signal.signal(signal.SIGALRM, handler)
            #signal.alarm(20)  # Set the timeout to 20 seconds
            timer.start()
            fitness = likelihood_of_program_wrt_data(p)
            #signal.alarm(0)  # Cancel the timeout
        except TimeoutException as e:
            print("Caught TimeoutException")
            fitness = self.default_fitness
        #except:
        #    fitness = self.default_fitness
            #I do not define the indiviaduals as invalid in order to allow crossover
            #if not hasattr(params['FITNESS_FUNCTION'], "multi_objective"):
                #stats['invalids'] += 1
        finally:
            timer.cancel()
        
        

        #t1 = time.time()

        #if t1 - t0 > 4:
            #fitness = self.default_fitness
        #print(fitness)
        return fitness

def generate_list():
    return [random.randint(0, round(random.random() * 90 + 10)) for i in range(9)]

def preprocess_program(program):
    p = convert_and_normalize_gm_structure(program)
    p = convert_uniform_structure(p)
    return p


def convert_and_normalize_gm_structure(text):
    # Regular expression to find gm structure
    pattern = r'gm\(\s*(\[[^\]]+\](?:,\s*\[[^\]]+\])*)\s*\)'
    
    # Match all occurrences of the structure
    matches = re.findall(pattern, text)
    
    # Process each match
    converted_text = text
    for match in matches:
        # Find all sets of [pi, mu, s] inside the matched string
        elements = re.findall(r'\[\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\]', match)
        
        # Separate pi, mu, and s into their own lists
        pi_list = [float(e[0]) for e in elements]
        mu_list = [e[1] for e in elements]
        s_list = [e[2] for e in elements]
        
        # Normalize pi_list
        pi_sum = sum(pi_list)
        normalized_pi_list = [pi / pi_sum for pi in pi_list] if pi_sum != 0 else pi_list
        
        # Format the new gm structure with normalized pi_list
        new_gm = f'gm([{", ".join(f"{pi:.6f}" for pi in normalized_pi_list)}], [{", ".join(mu_list)}], [{", ".join(s_list)}])'
        
        # Replace the old structure with the new one in the text
        converted_text = converted_text.replace(f'gm({match})', new_gm)
    
    return converted_text

import re

def convert_uniform_structure(text):
    # Regular expression to find the structure uniform([a, b], c)
    pattern = r'uniform\(\s*\[\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\]\s*,\s*([0-9.-]+)\s*\)'
    
    # Find all matches of uniform([a, b], c)
    matches = re.findall(pattern, text)
    
    # Process each match
    converted_text = text
    for match in matches:
        a = float(match[0])  # Extract 'a'
        b = float(match[1])  # Extract 'b'
        c = match[2]         # Extract 'c'
        
        # New value for 'a + b'
        new_b = a + b
        
        # Format the new uniform structure
        new_uniform = f'uniform([{a:.6f}, {new_b:.6f}], {c})'
        
        # Replace the old structure with the new one in the text
        old_uniform = f'uniform([{match[0]}, {match[1]}], {match[2]})'
        converted_text = converted_text.replace(old_uniform, new_uniform)
    
    return converted_text

def smooth_program(program_text):
    """
    Finds and modifies assignment lines where the variable is a letter or alphanumeric
    and the right-hand side does not contain 'gm' or 'uniform'.
    
    Args:
        program_text (str): The text of the program to analyze and modify.
    
    Returns:
        str: The modified program text.
    """
    # Define the regex pattern to identify assignments
    pattern = r'^(\s*([a-zA-Z]\w*)\s*=\s*([^;]*))(;?)'
    
    # Split the program into lines
    lines = program_text.splitlines()
    modified_lines = []
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            full_assignment, var, expression, semicolon = match.groups()
            # Check if 'gm' or 'uniform' is in the expression
            if 'gm' not in expression and 'uniform' not in expression:
                # Modify the assignment
                modified_assignment = f"{full_assignment} + gauss(0., 0.05){semicolon}"
                modified_lines.append(modified_assignment)
            else:
                # Keep the original line
                modified_lines.append(line)
        else:
            # Keep non-matching lines unchanged
            modified_lines.append(line)
    
    # Join the lines back into a single text
    return '\n'.join(modified_lines)   


def likelihood_of_program_wrt_data(p, data_size = 100):
    
    p = preprocess_program(p)
    data_var_list, dependencies, weights = dgp.get_vars(params['PROGRAM_NAME'])
    dependencies_benefit = 0
    data = dgp.generate_dataset(params['PROGRAM_NAME'], data_size)
    
    # Computes output distribution of the program
    compiledText=compile2SOGA_text(p)
    cfg = produce_cfg_text(compiledText)
    try:                                
        output_dist = start_SOGA(cfg)
    except IndexError: # program has no valid paths
        #stats['invalids'] += 1
        return -np.inf

    # Calculate the benefit of dependencies
    if(params['DEPENDENCIES_BENEFIT']):
        for key, values in dependencies.items():
            key_index = output_dist.var_list.index(key)
            for value in values:
                value_index = output_dist.var_list.index(value)
                cov_value = output_dist.gm.cov()[key_index, value_index]
                #if((output_dist.gm.cov()[key_index, key_index]!= 0) & (output_dist.gm.cov()[value_index, value_index]!= 0) ):
                    #cov_value = cov_value/(torch.sqrt(np.abs(output_dist.gm.cov()[key_index, key_index] * output_dist.gm.cov()[value_index, value_index])))
                #if cov_value < 1e-10:
                    #raise ValueError(f"Variable {key} and {value} have covariance 0")
                dependencies_benefit += weights[key] * np.log(np.abs(cov_value))

    # Calculate the likelihood of the data
    likelihood = compute_likelihood(output_dist, data_var_list, data)

    # Calculate fitness
    fitness = likelihood + dependencies_benefit
    return fitness.item()

# old version of likelihood

#def likelihood_of_program_wrt_data(p, data_size = 100):
#    p = preprocess_program(p)
#    data_var_list, dependencies, weights = dgp.get_vars(params['PROGRAM_NAME'])
#   dependencies_benefit = 0
#    data = dgp.generate_dataset(params['PROGRAM_NAME'], data_size)
    
#    compiledText=compile2SOGA_text(p)
#    cfg = produce_cfg_text(compiledText)
#    output_dist = start_SOGA(cfg)
   
#    if(params['DEPENDENCIES_BENEFIT']):
#        for key, values in dependencies.items():
#            key_index = output_dist.var_list.index(key)
#            for value in values:
#                value_index = output_dist.var_list.index(value)
#                cov_value = output_dist.gm.cov()[key_index, value_index]
#                #if((output_dist.gm.cov()[key_index, key_index]!= 0) & (output_dist.gm.cov()[value_index, value_index]!= 0) ):
#                    #cov_value = cov_value/(torch.sqrt(np.abs(output_dist.gm.cov()[key_index, key_index] * output_dist.gm.cov()[value_index, value_index])))
#                #if cov_value < 1e-10:
#                    #raise ValueError(f"Variable {key} and {value} have covariance 0")
#                dependencies_benefit += weights[key] * np.log(np.abs(cov_value))

    # Calculate the likelihood of the data
#    start = timeit.time()
#    likelihood = torch.zeros(len(data))
#    indexes = {element: [index for index, value in enumerate(output_dist.var_list) if value == element] for element in data_var_list}
#    marginal_means_components = []
#    filtered_means_components = []
#    marginal_covariance_matrices_components = []
#    excluded_indices_components = []


#    for i in range(output_dist.gm.n_comp()):    
#        marginal_means = []
#        covariance_index = []
#        marginal_covariance_matrix = []
#        excluded_indices = []
        
#        for element, index_list in indexes.items():
#            marginal_means.append(output_dist.gm.mu[i][index_list][0]) # le medie delle variabili di cui calcola la marginale
#            covariance_index.append(index_list[0])  # gli indici delle variabili di cui calcola la marginale
        
#        covariance_index_tensor = torch.tensor(covariance_index)
#        cov_matrix = output_dist.gm.sigma[i][covariance_index_tensor][:, covariance_index_tensor]

        # Exclude variables whose covariance is 0 and memorize their indices
#        filtered_covariance_index = []
#        ind = 0
#        for idx, cov in zip(covariance_index, torch.diag(torch.tensor(cov_matrix))):
#            if cov != 0:
#                filtered_covariance_index.append(idx)
#            else:
#                excluded_indices.append(ind)  # why ind?
#            ind += 1

#        filtered_covariance_index_tensor = torch.tensor(filtered_covariance_index)
#        filtered_cov_matrix = output_dist.gm.sigma[i][filtered_covariance_index_tensor][:, filtered_covariance_index_tensor]

        #marginal_covariance_matrix.append(output_dist.gm.sigma[i][covariance_index_tensor][:, covariance_index_tensor])
#        marginal_means_components.append(torch.tensor(marginal_means))
#        filtered_means_components.append(torch.tensor([value for idx, value in enumerate(marginal_means) if idx not in excluded_indices]))
#        marginal_covariance_matrices_components.append(filtered_cov_matrix)
#        excluded_indices_components.append(excluded_indices)
    
#    for j in range(len(data)):
#        for i in range(output_dist.gm.n_comp()):
#           # Check if the original data values not filtered are equal to the marginal means components not filtered
#            original_data_values = [data[j][idx] for idx in range(len(data[j])) if idx in excluded_indices]
#            original_means_values = [marginal_means_components[i][idx].item() for idx in range(len(marginal_means_components[i])) if idx in excluded_indices]
            
#            if original_data_values != original_means_values:
#                likelihood[j] += 0
#                continue

 #           filtered_data = torch.tensor([value for idx, value in enumerate(data[j]) if idx not in excluded_indices_components[i]])
 #           mvn = MultivariateNormal(filtered_means_components[i], torch.tensor(marginal_covariance_matrices_components[i]))
 #           likelihood[j] += output_dist.gm.pi[i] * torch.exp(mvn.log_prob(filtered_data))
       
 #       likelihood[j] = torch.log(likelihood[j])
   
#    sum_likelihood = torch.sum(likelihood)
#    fitness = (sum_likelihood)/ len(data) + dependencies_benefit
#    end = timeit.time()
#    print('Time: ', end - start, 'Fitness: ', fitness)
#    start = timeit.time()
#    fitness2 = compute_likelihood(output_dist, data_var_list, data) + dependencies_benefit
#    end = timeit.time()
#    print('Time: ', end - start, 'Fitness2: ', fitness2)
   #print('likelihood: ', (sum_likelihood)/ len(data))
   #print('dependencies benefit: ', dependencies_benefit )
#    return fitness

