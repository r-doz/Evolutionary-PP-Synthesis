# SOGA 
This is the user manual for using SOGA, a tool for Inference of Probabilistic Programs by Second-order Gaussian Approximation. SOGA is implemented in Python and depends on several Python packages listed in the `requirements.txt` file.

## Requirements
The following tools are required to install and run SOGA:

- `Python 3.9+`
- `pip 21.2.4+`

You can download and install Python from the [Python website](https://www.python.org/).

## Installation
To install dependencies, run the following command:

```bash
pip install -r requirements.txt
```

This command will automatically download and install all the required packages. Now that you've installed all the dependencies, you're ready to start using SOGA. Below, we provide instructions on how to run and use it.

## Usage
The SOGA's command-line interface provides the following options:

```bash
usage: python3 src/SOGA.py [-h] -f MODELFILE [-o OUTPUTFILE] [-t TIMEOUT] [-c] [-p PARALLEL] [-v [VARS ...]]
```

Here's a breakdown of each option:

- -h, --help: Shows the help message and exits.
- -f MODELFILE, --modelfile MODELFILE: Specifies the SOGA model path.
- -o OUTPUTFILE, --outputfile OUTPUTFILE: Specifies the output file path.
- -t TIMEOUT, --timeout TIMEOUT: Sets the timeout (in seconds) for SOGA computation (default: 600).
- -c, --covariance: Outputs the covariance.
- -p PARALLEL, --parallel PARALLEL: Specifies the number of parallel processes to use for the analysis (default: 1).
- -v [VARS ...], --vars [VARS ...]: Lists the output variables.

## Example
Suppose you want to analyze the probabilistic program `Bernoulli.soga` contained in the folder `programs/Example/` using SOGA. Here's how you would use the SOGA CLI to perform the analysis:

```bash
python3 src/SOGA.py -f programs/Example/Bernoulli.soga
```

obtaining the following output

```bash
SOGA preprocessing in: 11.943 s
      CFG produced in:  0.027 s
              Runtime: 10.249 s
c: 1954
d: 2
E[theta]: 0.25689
E[y]: 1.0
```
In the first three lines, the tool reports the execution runtimes, in particular: 
- the time required for fitting all the non-Gaussian distributions as gaussian mixture via expectation maximation
- the time required for producing the control flow graph of the program
- the time required for the actual inference. 

Below this, SOGA reports the main results of the analysis where: 
- c is the number of components of the final distribution 
- d is the number of model variables; 
- E[x] is the posterior mean for each model variable x. 

You can find other examples of SOGA models in the folder `programs/SOGA/`. A detailed guide on how to build your own model can be found in the file [ReusabilityGuide](Manual/ReusabilityGuide.md). 

## Replicability
To reproduce the paper's results please follow the replicability instructions contained in the file [ReplicabilityGuide](Manual/ReplicabilityGuide.md)


