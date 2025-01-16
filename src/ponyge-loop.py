#! /usr/bin/env python

# PonyGE2
# Copyright (c) 2017 Michael Fenton, James McDermott,
#                    David Fagan, Stefan Forstenlechner,
#                    and Erik Hemberg
# Hereby licensed under the GNU GPL v3.
""" Python GE implementation """

from utilities.algorithm.general import check_python_version

check_python_version()

from stats.stats import get_stats
from algorithm.parameters import params, set_params
import sys

models = [#'burglary', 
          #'csi', 
          #'eyecolor', 
          #'grass', 
          #'healthiness',
          'hurricane']

# Define a list of parameter configurations
parameter_configs = [
    {   'GENERATIONS': 1000,
        'POPULATION_SIZE': 250,
        'EXPERIMENT_NAME': model, # name of the folder
        'PROGRAM_NAME': model,
        'GRAMMAR_FILE': "soga_"+model+"_nosketch.pybnf"
    } for model in models 
    ] + [
    {   'GENERATIONS': 1000,
        'POPULATION_SIZE': 250,
        'EXPERIMENT_NAME': model, # name of the folder
        'PROGRAM_NAME': model,
        'GRAMMAR_FILE': "soga_"+model+"_sketch.pybnf"
    } for model in models 
    ] 

def update_params(config):
    """ Update the parameters in the params dictionary """
    for key, value in config.items():
        params[key] = value

def mane():
    """ Run program """
    set_params(sys.argv[1:])  # exclude the ponyge.py arg itself

    # Run evolution
    individuals = params['SEARCH_LOOP']()

    # Print final review
    get_stats(individuals, end=True)

if __name__ == "__main__":
    for config in parameter_configs:
        print(f"Running with parameters: {config}")
        update_params(config)
        mane()