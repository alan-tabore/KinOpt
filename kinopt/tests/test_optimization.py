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
    """
    Test that all RSS functions have the correct argument names and order.
    """
    # Get all RSS functions from the optimization module
    rss_functions = [func for func in dict(inspect.getmembers(opt, inspect.isfunction)).values() 
                     if func.__name__.startswith('rss')]
    
    # Check that we found some functions
    assert len(rss_functions) > 0, "No RSS functions found in optimization module"
    
    # Define the expected argument names in the correct order
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
        # Get actual parameter names while preserving their order
        params = list(inspect.signature(func).parameters.items())
        actual_arguments = [param[0] for param in params[:13]]
        
        # Compare each parameter name and position
        for expected, actual in zip(expected_arguments, actual_arguments):
            assert expected == actual, f"In function {func.__name__}, expected parameter '{expected}' but got '{actual}'"

def test_rss_standard_with_known_function():
    """
    Test RSS standard calculation using a simple quadratic function with carefully chosen values:
    - Using just 3 time points: t = [0, 1, 2]
    - True function: f(t) = t² + t + 1  (a=1, b=1, c=1)
    - Test function: f(t) = 2t² + t + 1  (a=2, b=1, c=1)
    
    This gives us:
    t=0: diff = 0        → (0)² = 0
    t=1: diff = 1        → (1)² = 1
    t=2: diff = 4        → (4)² = 16
    
    Total RSS = 0 + 1 + 16 = 17
    """
    def simple_rate_law(t, temp, a, b, c, *args):
        t = np.asarray(t)
        return a * t**2 + b * t + c
    
    t_data = np.array([0, 1, 2])
    temp_data = 298 * np.ones_like(t_data)
    true_params = [1.0, 1.0, 1.0]
    experimental_rate = simple_rate_law(t_data, temp_data, *true_params)
    x_test = [2.0, 1.0, 1.0]
    
    rss = opt.rss_standard(x_test, experimental_rate, simple_rate_law,
                          (t_data, temp_data), 3,
                          None, None, 0, None, None, None, None, None)
    
    assert np.isclose(rss, 17.0, rtol=1e-10)

def test_rss_mean_with_known_function():
    """
    Test RSS mean calculation with same function but divided by n points:
    Total RSS = (0 + 1 + 16) / 3 = 5.6667
    """
    def simple_rate_law(t, temp, a, b, c, *args):
        t = np.asarray(t)
        return a * t**2 + b * t + c
    
    t_data = np.array([0, 1, 2])
    temp_data = 298 * np.ones_like(t_data)
    true_params = [1.0, 1.0, 1.0]
    experimental_rate = simple_rate_law(t_data, temp_data, *true_params)
    x_test = [2.0, 1.0, 1.0]
    
    rss = opt.rss_mean(x_test, experimental_rate, simple_rate_law,
                       (t_data, temp_data), 3,
                       None, None, 0, None, None, None, None, None)
    
    assert np.isclose(rss, 17.0/3, rtol=1e-10)

def test_rss_relative_with_known_function():
    """
    Test RSS relative calculation with simple values:
    - True values: [1, 2, 4]
    - Test values: [0.9, 1.8, 3.6]
    
    Relative differences: (0.9-1)/1 = -0.1, (1.8-2)/2 = -0.1, (3.6-4)/4 = -0.1
    RSS = (-0.1)² + (-0.1)² + (-0.1)² = 0.03
    """
    def simple_rate_law(t, temp, k, *args):
        return k * np.array([0.9, 1.8, 3.6])
    
    t_data = np.array([1.0, 2.0, 3.0])
    temp_data = 298 * np.ones_like(t_data)
    experimental_rate = np.array([1.0, 2.0, 4.0])
    
    rss = opt.rss_relative([1.0], experimental_rate, simple_rate_law,
                          (t_data, temp_data), 1,
                          None, None, 0, None, None, None, None, None)
    
    assert np.isclose(rss, 0.03, rtol=1e-10)

def test_rss_small_extents_impact():
    """
    Test RSS with small extents impact:
    - Experimental rate: [1, 1, 1]
    - Model rate: [0.9, 0.9, 0.9]
    - Extents: [0.1, 0.5, 0.9]
    - Extent limit: 0.3
    - Amplification factor: 2
    
    Differences: all are 0.1
    First point amplified (extent < 0.3): (0.1 * 2)² = 0.04
    Other points normal: (0.1)² + (0.1)² = 0.02
    Mean RSS = (0.04 + 0.02) / 3 = 0.02
    """
    def simple_rate_law(t, temp, k, *args):
        return k * np.array([0.9, 0.9, 0.9])
    
    t_data = np.array([1.0, 2.0, 3.0])
    temp_data = 298 * np.ones_like(t_data)
    experimental_rate = np.array([1.0, 1.0, 1.0])
    extent = np.array([0.1, 0.5, 0.9])
    
    rss = opt.rss_increase_of_small_extents_impact(
        [1.0], experimental_rate, simple_rate_law,
        (t_data, temp_data), 1,
        None, None, 0, None, None, None, None, None,
        extent, 0.3, 2.0
    )
    
    assert np.isclose(rss, 0.02, rtol=1e-10)

def test_rss_small_rates_zones():
    """
    Test RSS with zones:
    - Experimental rate: [0.1, 1.0, 2.0]
    - Model rate: [0.2, 1.1, 2.1]
    - Max rate = 2.0
    - Fraction to amplify = 4 (threshold = 0.5)
    - Amplification factor = 2
    
    First point amplified (rate < max/4): ((0.2-0.1)*2)² = 0.04
    Other points normal: (0.1)² + (0.1)² = 0.02
    Mean RSS = (0.04 + 0.02) / 3 = 0.02
    """
    def simple_rate_law(t, temp, k, *args):
        return k * np.array([0.2, 1.1, 2.1])
    
    t_data = np.array([1.0, 2.0, 3.0])
    temp_data = 298 * np.ones_like(t_data)
    experimental_rate = np.array([0.1, 1.0, 2.0])
    
    rss = opt.rss_increase_of_small_rates_impact_with_zones(
        [1.0], experimental_rate, simple_rate_law,
        (t_data, temp_data), 1,
        None, None, 0, None, None, None, None, None,
        4.0, 2.0
    )
    
    assert np.isclose(rss, 0.02, rtol=1e-10)