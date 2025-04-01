import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import multivariate_normal
from os import getcwd, listdir, path, sep


def create_histogram(data, data_var_list):
    """ Creates a plot with one histogram for each variable in data_var_list, where data are the samples of the variables (data has shape (n_samples, n_vars)). """

    # Number of histograms to plot
    num_histograms = len(data_var_list)

    # Create subplots
    fig, axs = plt.subplots(1, num_histograms, figsize=(20, 5))

    data = np.array(data)
    # Plot each histogram
    for i in range(num_histograms):
        values = np.unique(data[:,i])
        axs[i].hist(data[:,i], bins=[ -0.5 + i for i in range(int(min(values)), int(max(values))+2)], density=True, stacked=True, alpha=0.7, color='blue', rwidth=0.8)
        axs[i].set_title(data_var_list[i])
        axs[i].set_xlabel('Value')
        axs[i].set_ylabel('Frequency')

    # Adjust layout and show the plot
    plt.tight_layout()
    plt.show()

def create_histograms(data_list, name_list, data_var_list):
    """ Works like create histogram but for each set of data in data_list shows a different bar """

    # Number of histograms to plot
    num_histograms = len(data_var_list)

    # Create subplots
    fig, axs = plt.subplots(1, num_histograms, figsize=(20, 5))

    
    # Plot each histogram
    for i in range(num_histograms):

        # looks at the value for variables i in all data
        values_list = []
        for data in data_list:
            data = np.array(data)
            values_list.append(np.unique(data[:,i]))
        values = np.unique(np.concatenate(values_list))
        bins = [ -0.5 + i for i in range(int(min(values)), int(max(values))+2)]
        
        # creates the histograms 
        hist_list = [np.histogram(data, bins=bins, density=True)[0] for data in data_list]

        # Define the positions for the bars
        bar_width = 0.25
        r = np.arange(len(hist_list[0]))
        positions = [r + i * bar_width for i in range(len(data_list))]

        # Create the bar plot
        for k, hist in enumerate(hist_list):
            axs[i].bar(positions[k], hist, width=bar_width, edgecolor='grey', label=name_list[k])
        axs[i].set_title(data_var_list[i])
        axs[i].set_xlabel('Value')
        axs[i].set_ylabel('Frequency')

    # Adjust layout and show the plot
    plt.legend()
    plt.tight_layout()
    plt.show()

def sample_gmm(dist, n_samples):
    """ Samples from dist where dist is a SOGA distribution """

    n_components = dist.gm.n_comp()
    weights = dist.gm.pi
    weights = np.array(weights)
    weights /= weights.sum()
    means = dist.gm.mu
    covariances = dist.gm.sigma
    samples = []

    # Sample component indices based on weights
    component_indices = np.random.choice(n_components, size=n_samples, p=weights)

    for i in range(n_components):
        # Number of samples for this component
        n_samples_i = np.sum(component_indices == i)
        if n_samples_i > 0:
            # Sample from the i-th Gaussian component
            samples_i = multivariate_normal.rvs(mean=means[i], cov=covariances[i], size=n_samples_i)
            samples.append(samples_i)

    # Concatenate all samples
    samples = np.vstack(samples)
    np.random.shuffle(samples)  # Shuffle to mix samples from different components

    return samples


def read_fitness_and_program(model_name):
    file_path = path.join(getcwd(), "..", "results")
    file_path = path.join(file_path, model_name)

    # Find list of all runs contained in the specified folder.
    runs = [run for run in listdir(file_path) if
            path.isdir(path.join(file_path, run))]

    avg_fitness_5000 = []

    # Iterate over all runs
    for run in runs:
        # Get file name
        file_name = path.join(file_path, str(run), "best.txt")

        try:
            # Load in data
            file = open(file_name) 
        except:
            avg_fitness_5000.append(np.nan)
            continue
        flag = False
        for line in file.readlines():
            if 'Fitness on 5000 data' in line:
                flag = True
                continue
            if flag:
                try:
                    avg_fitness_5000.append(float(line[:-2]))
                except:
                    print("run ", run, " did not converge")  
                    break
                break

    best_program_file = path.join(file_path, str(runs[np.nanargmax(avg_fitness_5000)-2]), "best.txt")
    file = open(best_program_file)
    text_bf = ''
    flag = False
    for line in file.readlines():
        if 'Phenotype' in line:
            flag = True
            continue
        if 'Genotype' in line:
            flag = False
            break
        if flag:
            text_bf += line + ' '

    return avg_fitness_5000, text_bf