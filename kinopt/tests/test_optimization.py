# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 10:32:20 2024

@author: alan.tabore
"""

import pytest
import inspect
import numpy as np
import src.optimization as opt

# Define some sample data for testing
experimental_rate = np.array([0.5, 0.7, 1.0, 1.5])
x = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, ])
fraction_to_amplify = 0.5
amplification_factor = 2.0

# Define some mock rate laws for testing
def mock_rate_law(*args):
    return np.array([0.3, 0.6, 0.9, 1.2])

def mock_vitrification_law(*args):
    return np.array([0.1, 0.2, 0.3, 0.4])

def mock_tg_law(*args):
    return 100.0

def mock_coupling_law(*args):
    return np.array([0.2, 0.3, 0.4, 0.5])

# Test rss_increase_of_small_rates_impact_with_zones function
def test_rss_increase_of_small_rates_impact_with_zones():
    rss = opt.rss_increase_of_small_rates_impact_with_zones(x, experimental_rate, mock_rate_law, (), 0, mock_vitrification_law, (), 0, mock_coupling_law, (), mock_tg_law, (), (), fraction_to_amplify, amplification_factor)
    assert np.isclose(rss, 0.025, atol=1e-3)

# Test rss_increase_of_small_extents_impact function
def test_rss_increase_of_small_extents_impact():
    extent = np.array([0.05, 0.1, 0.15, 0.2])
    extent_limit = 0.1
    rss = opt.rss_increase_of_small_extents_impact(x, experimental_rate, mock_rate_law, (), 0, mock_vitrification_law, (), 0, mock_coupling_law, (), mock_tg_law, (), (), extent, extent_limit, amplification_factor)
    assert np.isclose(rss, 0.0325, atol=1e-3)


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