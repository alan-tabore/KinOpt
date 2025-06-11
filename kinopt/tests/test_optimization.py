# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 10:32:20 2024

@author: alan.tabore
"""

import pytest
import inspect
import numpy as np
from kinopt.src import optimization as opt


def test_rss_functions_arguments():
    rss_functions = [func for func in locals().values() if inspect.isfunction(func) and func.__name__.startswith('rss')]
    expected_arguments = [
        'x', 
        'experimental_rate', 
        'rate_law', 
        'experimental_args_for_rate', 
        'number_of_parameters_to_optimize_for_rate', 
        'vitrification_law', 
        'experimental_args_for_vitrification', 
        'number_of_parameters_to_optimize_for_vitrification', 
        'coupling_law', 
        'experimental_args_for_coupling', 
        'tg_law', 
        'experimental_args_for_tg', 
        'tg_args'
    ]
    for func in rss_functions:
        actual_arguments = inspect.signature(func).parameters.keys()
        assert list(actual_arguments) == expected_arguments, f"Function {func.__name__} has incorrect arguments: {list(actual_arguments)}"