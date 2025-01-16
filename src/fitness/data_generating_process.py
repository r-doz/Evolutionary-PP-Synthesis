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
    if process_name == 'csi':
        data_var_list = ['u', 'v', 'w', 'x']
        dependencies = {'x': ['u', 'v', 'w']}   
        weights = {'x': 0.1}
        return data_var_list, dependencies, weights
    if process_name == 'healthiness':
        data_var_list = ['healthconscius', 'littlefreetime', 'exercise', 'gooddiet', 'normalweight', 'colesterol', 'tested']
        dependencies = {'exercise': ['healthconscius', 'littlefreetime'], 'gooddiet':['healthconcius'], 'normalweight': ['gooddiet', 'exercise'], 'colesterol': ['gooddiet'], 'tested': ['colesterol']}
        weights = {'exercise':0.1, 'gooddiet':0.1, 'normalweight':0.1, 'colesterol':0.1, 'tested':0.1}
        return data_var_list, dependencies, weights 
    if process_name == 'eyecolor':
        data_var_list = ['eyecolor', 'haircolor', 'hairlength']
        dependencies = {'haircolor': ['eyecolor']}
        weights = {}
        return data_var_list, dependencies, weights
    if process_name == 'grass':
        data_var_list = ['rain', 'sprinkler', 'grasswet']
        dependencies = {'sprinkler':['rain'], 'grasswet': ['rain', 'sprinkler']}
        weights = {'sprinkler': 0.1, 'grasswet': 0.1}
        return data_var_list, dependencies, weights
    if process_name == 'hurricane':
        data_var_list = ['preplevel', 'damage']
        dependencies = {'damage': ['preplevel']}
        weights = {'damage': 0.1}
        return data_var_list, dependencies, weights
    if process_name == 'icecream':
        data_var_list = ['currentseason', 'icecream', 'crime']
        dependencies = {'icecream': ['currentseason'], 'crime': ['currentseason']}
        weights = {'icecream': 0.1, 'crime': 0.1}
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
    if process_name == 'csi':
        return generate_csi_dataset(data_size)
    if process_name == 'healthiness':  
        return generate_healthiness_dataset(data_size)
    if process_name == 'eyecolor':
        return generate_eyecolor_dataset(data_size)
    if process_name == 'grass':
        return generate_grass_dataset(data_size)
    if process_name == 'hurricane':
        return generate_hurricane_dataset(data_size)
    if process_name == 'icecream':
        return generate_icecream_dataset(data_size)
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
        burglary = np.random.binomial(1, 0.001)  # 0.001
        earthquake = np.random.binomial(1, 0.002) # 0.002
        if burglary:
            if earthquake:
                alarm = np.random.binomial(1, 0.95)
            else:
                alarm = np.random.binomial(1, 0.94)
        else:
            if earthquake:
                alarm = np.random.binomial(1, 0.29)
            else:
                alarm = np.random.binomial(1, 0.001) # 0.001
        if alarm:
            johncalls = np.random.binomial(1, 0.9)
        else:
            johncalls = np.random.binomial(1, 0.05)
        data.append([burglary, earthquake, alarm, johncalls])
    return data

def generate_csi_dataset(data_size):
    data = []
    for _ in range(data_size):
        u = np.random.binomial(1, 0.3)
        v = np.random.binomial(1, 0.9)
        w = np.random.binomial(1, 0.1)
        if u:
            if w:
                x = np.random.binomial(1, 0.8)
            else:
                x = np.random.binomial(1, 0.2)
        else:
            if v:
                x = np.random.binomial(1, 0.8)
            else:
                x = np.random.binomial(1, 0.2)
        data.append([u, v, w, x])
    return data

def generate_healthiness_dataset(data_size):
    data = []
    for _ in range(data_size):
        healthconscius = np.random.binomial(1, 0.5)
        littlefreetime = np.random.binomial(1, 0.5)
        if healthconscius:
            if littlefreetime:
                exercise = np.random.binomial(1, 0.5)
            else:
                exercise = np.random.binomial(1, 0.9)
        else:
            if littlefreetime:
                exercise = np.random.binomial(1, 0.1)
            else:
                exercise = np.random.binomial(1, 0.5)
        
        if healthconscius:
            gooddiet = np.random.binomial(1, 0.7)
        else:
            gooddiet = np.random.binomial(1, 0.3)
        
        if gooddiet:
            if exercise:
                normalweight = np.random.binomial(1, 0.8)
            else:
                normalweight = np.random.binomial(1, 0.5)
        else:
            if exercise:
                normalweight = np.random.binomial(1, 0.5)
            else:
                normalweight = np.random.binomial(1, 0.2)
        
        if gooddiet:
            colesterol = np.random.binomial(1, 0.3)
        else:
            colesterol = np.random.binomial(1, 0.7)
        
        if colesterol:
            tested = np.random.binomial(1, 0.9)
        else:
            tested = np.random.binomial(1, 0.1)
        data.append([healthconscius, littlefreetime, exercise, gooddiet, normalweight, colesterol, tested])
    return data

def generate_eyecolor_dataset(data_size):
    data = []
    for _ in range(data_size):
        eyecolor = np.random.choice([0, 1, 2, 3], p=[0.82, 0.08, 0.08, 0.02])
        if eyecolor == 0:
            haircolor = np.random.choice([0, 1, 2, 3, 4], p=[0.8, 0.05, 0.04, 0.01, 0.1])
        elif eyecolor == 1:
            haircolor = np.random.choice([0, 1, 2, 3, 4], p=[0.7, 0.15, 0.04, 0.01, 0.1])
        elif eyecolor == 2:
            haircolor = np.random.choice([0, 1, 2, 3, 4], p=[0.4, 0.3, 0.18, 0.02, 0.1])
        else:
            haircolor = np.random.choice([0, 1, 2, 3, 4], p=[0.4, 0.29, 0.18, 0.03, 0.1])
        hairlength = np.random.choice([0, 1, 2], p=[0.6, 0.15, 0.25])
        data.append([eyecolor, haircolor, hairlength])
    return data

def generate_grass_dataset(data_size):
    data = []
    for _ in range(data_size):
        rain = np.random.normal(4, 2)
        if rain < 1:
            sprinkler = 1
        else:
            sprinkler = 0
        if rain > 2:
            grasswet = 1
        else:
            if sprinkler:
                grasswet = 1
            else:
                grasswet = 0
        data.append([rain, sprinkler, grasswet])
    return data

def generate_hurricane_dataset(data_size):
    data = []
    for _ in range(data_size):
        preplevel = np.random.choice([0, 1, 2], p=[0.5, 0.2, 0.3])
        if preplevel == 0:
            damage = np.random.choice([0,1], p=[0.2, 0.8])
        elif preplevel == 1:
            damage = np.random.choice([0,1], p=[0.2, 0.8])
        elif preplevel == 2:
            damage = np.random.choice([0,1], p=[0.8, 0.2])
        data.append([preplevel, damage])
    return 

def generate_icecream_dataset(data_size):
    data = []
    for _ in range(data_size):
        currentseason = np.random.choice([0, 1, 2, 3], p=[0.25, 0.25, 0.25, 0.25])
        if currentseason == 0:
            icecream = np.random.normal(10, 1)
            crime = np.random.normal(10, 1)
        elif currentseason == 1:
            icecram = np.random.normal(15, 3)
            crime = np.rancom.normal(15, 3)
        elif currentseason == 2:
            icecream = np.random.normal(50, 6)
            crime = np.random.normal(50, 6)
        elif currentseason == 3:
            icecram = np.random.normal(17, 4)
            crime = np.random.normal(17, 4)
        data.append([currentseason, icecream, crime])
    return data