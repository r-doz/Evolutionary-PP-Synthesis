""" This program cues up and executes multiple runs of PYGE. Results of runs
    are parsed and placed in a spreadsheet for easy visual analysis.

    Copyright (c) 2014 Michael Fenton
    Hereby licensed under the GNU GPL v3."""

from sys import path, executable
#path.append("../src")
#path.insert(1, '../src')

from utilities.algorithm.general import check_python_version

check_python_version()

from multiprocessing import Pool
from subprocess import call
import sys
import time as timeit

from algorithm.parameters import params, set_params
from stats_parser import parse_stats_from_runs

models = [#'burglary', 
          'csi', 
          'eyecolor', 
          'healthiness',
          'hurricane']

parameter_configs = [
    {   'GENERATIONS': 500,
        'POPULATION_SIZE': 200,
        'EXPERIMENT_NAME': model+'_nosketch', # name of the folder
        'GRAMMAR_FILE': "soga_"+model+"_nosketch.pybnf"
    } for model in models 
    ]  

def update_params(config):
    """ Update the parameters in the params dictionary """
    for key, value in config.items():
        params[key] = value

def execute_run(seed, config):
    """
    Initialise all aspects of a run.

    :return: Nothing.
    """

    cmd_args = ''
    for key, value in config.items():
        cmd_args += '--' + key.lower() + ' ' + str(value) + ' '

    exec_str = executable + " ponyge.py " \
               "--random_seed " + str(seed) + " " + cmd_args + " ".join(sys.argv[1:])
    
    call(exec_str, shell=True)


def execute_runs(config):
    """
    Execute multiple runs in series using multiple cores.

    :return: Nothing.
    """

    # Initialise empty list of results.
    results = []

    # Initialise pool of workers.
    pool = Pool(processes=params['CORES'])

    for run in range(params['RUNS']):
        # Execute a single evolutionary run.
        results.append(pool.apply_async(execute_run, (run,config)))

    for result in results:
        result.get()

    # Close pool once runs are finished.
    pool.close()


def check_params():
    """
    Checks the params to ensure an experiment name has been specified and
    that the number of runs has been specified.

    :return: Nothing.
    """

    if not params['EXPERIMENT_NAME']:
        s = "scripts.run_experiments.check_params\n" \
            "Error: Experiment Name not specified.\n" \
            "       Please specify a name for this set of runs."
        raise Exception(s)

    if params['RUNS'] == 1:
        print("Warning: Only 1 run has been specified for this set of runs.")
        print("         The number of runs can be specified with the command-"
              "line parameter `--runs`.")


def main():
    """
    The main function for running the experiment manager. Calls all functions.

    :return: Nothing.
    """

    for config in parameter_configs:
        # Setup run parameters.
        set_params(sys.argv[1:], create_files=True)
        update_params(config)

        # Check the correct parameters are set for this set of runs.
        check_params()

        start = timeit.time()
        # Execute multiple runs.
        execute_runs(config)

        end = timeit.time()
        print("Total time taken: " + str(end - start) + " seconds.")
        print("Average time per run: " + str((end - start) / params['RUNS']) )


        # Save spreadsheets and all plots for all runs in the 'EXPERIMENT_NAME'
        # folder.
        # parse_stats_from_runs(params['EXPERIMENT_NAME'])


if __name__ == "__main__":
    main()
