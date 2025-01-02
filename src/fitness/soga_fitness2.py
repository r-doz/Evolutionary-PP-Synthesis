from algorithm.parameters import params
from fitness.base_ff_classes.base_ff import base_ff
from torch.distributions.multivariate_normal import MultivariateNormal
import random
import time
import signal
import sys
import numpy as np
import re
import torch
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../SOGAtorch/src')
from sogaPreprocessor import *
from producecfg import *
from libSOGA import *

torch.set_default_dtype(torch.float64)
# Define a custom exception for timeouts
class TimeoutException(Exception):
    pass

# Define a handler function for the timeout
def handler(signum, frame):
    raise TimeoutException("Code execution exceeded time limit")

class soga_fitness(base_ff):
    """Fitness function for finding the length of the shortest path between
    two nodes in a grade compared to the known shortest path. Takes a path (
    list of node labels as strings) and returns fitness. Penalises output
    that is not the same length as the target."""

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()

    def evaluate(self, ind, **kwargs):
        self.default_fitness = -np.inf
        # We need to calculate the likelihood of these data
        data_var_list = ['a', 'b']
        #data = np.random.uniform(0, 1, 100)
        #data = [[np.random.normal(1, 2), np.random.normal(8, 2)] for _ in range(5000)]
        data = []
        for _ in range(5000):
            a = np.random.normal(1, 2)
            if a < 0:
                b = a * 3
            else: 
                b = np.random.normal(8, 1)
            data.append([a, b])

        p = ind.phenotype
        p = preprocess_program(p)
        p = smooth_program(p)
        print("\n" + p)
        print("\n -----------------------------------------")

        fitness = 0
        #t0 = time.time()

        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(15)  # Set the timeout to 15 seconds
            compiledText=compile2SOGA_text(p)
            cfg = produce_cfg_text(compiledText)
            output_dist = start_SOGA(cfg)

            # Calculate the likelihood of the data

            likelihood = torch.zeros(len(data), dtype=torch.float32)
            indexes = {element: [index for index, value in enumerate(output_dist.var_list) if value == element] for element in data_var_list}
            marginal_means_components = []
            marginal_covariance_matrices_components = []
            
            for i in range(output_dist.gm.n_comp()):
                marginal_means = []
                covariance_index = []
                marginal_covariance_matrix = []
                
                for element, index_list in indexes.items():
                    marginal_means.append(output_dist.gm.mu[i][index_list][0])
                    covariance_index.append(index_list[0])
                
                covariance_index_tensor = torch.tensor(covariance_index)
                marginal_covariance_matrix.append(output_dist.gm.sigma[i][covariance_index_tensor][:, covariance_index_tensor])
                marginal_means_components.append(torch.tensor(marginal_means))
                marginal_covariance_matrices_components.append(marginal_covariance_matrix)
            
            for j in range(len(data)):
                data_tensor = torch.tensor(data[j])
                for i in range(output_dist.gm.n_comp()):
                    mvn = MultivariateNormal(torch.tensor(marginal_means_components[i]), torch.tensor(marginal_covariance_matrices_components[i][0]))
                    likelihood[j] += output_dist.gm.pi[i] * torch.exp(mvn.log_prob(data_tensor))
                
                likelihood[j] = torch.log(likelihood[j])
            
            sum_likelihood = torch.sum(likelihood)
            fitness = sum_likelihood / len(data)
            signal.alarm(0)  # Cancel the timeout

        except TimeoutException as e:
            print("Caught TimeoutException")
            fitness = self.default_fitness

        except:
            fitness = self.default_fitness
            #I do not define the indiviaduals as invalid in order to allow crossover
            #if not hasattr(params['FITNESS_FUNCTION'], "multi_objective"):
                #stats['invalids'] += 1

        #t1 = time.time()

        #if t1 - t0 > 4:
            #fitness = self.default_fitness
        print(fitness)
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

