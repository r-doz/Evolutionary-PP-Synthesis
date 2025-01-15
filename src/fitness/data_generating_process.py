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
    if process_name == 'burglary':
        data_var_list = ['burglary', 'earthquake', 'alarm', 'johncalls']
        dependencies = {'alarm': ['burglary', 'earthquake'], 'johncalls': ['alarm']}
        weights = {'alarm': 0.1, 'johncalls':0.1}  # Weights for the dependencies
        return data_var_list, dependencies, weights  
    if process_name == 'easytugwar':
        data_var_list = ['skill1', 'skill2', 'p1wins']
        dependencies = {'p1wins': ['skill1', 'skill2']}
        weights = {'p1wins': 0.1} 
        return data_var_list, dependencies, weights    
    else:
        raise ValueError(f"Unknown process name: {process_name}")

def generate_dataset(process_name, data_size):
    if process_name == 'trueskills':
        return generate_trueskills_dataset(data_size)
    if process_name == 'mog1':
        return generate_mog1_dataset(data_size)
    if process_name == 'burglary':
        return generate_burglary_dataset(data_size)
    if process_name == 'easytugwar':
        return generate_easytugwar_dataset(data_size)
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

def generate_burglary_dataset(data_size):
    data = []
    for _ in range(data_size):
        burglary = np.random.binomial(1, 0.001)
        earthquake = np.random.binomial(1, 0.002)
        if burglary:
            if earthquake:
                alarm = np.random.binomial(1, 0.95)
            else:
                alarm = np.random.binomial(1, 0.94)
        else:
            if earthquake:
                alarm = np.random.binomial(1, 0.29)
            else:
                alarm = np.random.binomial(1, 0.001)
        if alarm:
            johncalls = np.random.binomial(1, 0.9)
        else:
            johncalls = np.random.binomial(1, 0.05)
        data.append([burglary, earthquake, alarm, johncalls])
    return data

def generate_easytugwar_dataset(data_size):
    data = []
    for _ in range(data_size):
        skill1 = np.random.normal(20, 4)
        skill2 = np.random.normal(20, 4)
        if skill1 > skill2:
            p1wins = 1.0
        else:
            p1wins = 0.0
        data.append([skill1, skill2, p1wins])
    return data
