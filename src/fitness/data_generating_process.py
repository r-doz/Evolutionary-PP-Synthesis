import numpy as np

def get_vars(process_name):
    if process_name == 'trueskills':
        data_var_list = ['skillA', 'skillB', 'skillC','rA', 'rB', 'rC']
        dependencies = {'perfA': ['skillA'], 'perfB': ['skillB'], 'perfC': ['skillC']}
        weights = {'perfA': 0.3, 'perfB': 0.3, 'perfC': 0.3}  # Weights for the dependencies
        return data_var_list, dependencies, weights
    if process_name == 'mog1':
        data_var_list = ['mu', 'sigma', 'x']
        dependencies = {'x': ['mu', 'sigma']}
        weights = {'x': 0.1}  # Weights for the dependencies
        return data_var_list, dependencies, weights       
    else:
        raise ValueError(f"Unknown process name: {process_name}")

def generate_dataset(process_name, data_size):
    if process_name == 'trueskills':
        return generate_trueskills_dataset(data_size)
    if process_name == 'mog1':
        return generate_mog1_dataset(data_size)
    else:
        raise ValueError(f"Unknown process name: {process_name}")

def generate_trueskills_dataset(data_size):
    data = []
    for _ in range(data_size):
        rA = 0
        rB = 0
        rC = 0
        skillA = np.random.normal(100, 10)
        skillB = np.random.normal(100, 10)
        skillC = np.random.normal(100, 10)
        perfA = np.random.normal(0, 15) + skillA
        perfB = np.random.normal(0, 15) + skillB
        perfC = np.random.normal(0, 15) + skillC
        if perfA > perfB:
            rA = 1.0
        if perfB > perfC:
            rB = 1.0
        if perfA > perfC:
            rC = 1.0
        data.append([skillA, skillB, skillC, rA, rB, rC])
    return data

def generate_mog1_dataset(data_size):
    data = []
    for _ in range(data_size):
        mu = np.random.normal(20, 3)
        sigma = np.random.normal(2, 1)
        x = mu + sigma * np.random.normal(1, 1)
        data.append([mu, sigma, x])
    return data