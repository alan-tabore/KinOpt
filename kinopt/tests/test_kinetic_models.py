# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 11:39:41 2023

@author: alan.tabore
"""
import pytest
import numpy as np
import inspect
from kinopt.src import kinetic_models as km
    
def test_vitrification_WLF_rate_no_reaction_below_Tg():
    # Test case 1: All temperatures above Tg
    temperature = np.array([350, 400, 450])
    Ad = 1.0
    C1 = 1.0
    C2 = 10
    Tg = 320
    expected_result = np.array([np.exp(3/4), np.exp(8/9), np.exp(13/14)])
    result = km.vitrification_WLF_rate_no_reaction_below_Tg(temperature, Tg, Ad, C1, C2)
    assert np.allclose(result, expected_result), "Test case 1 failed"

    # Test case 2: All temperatures below Tg
    temperature = np.array([280, 300, 310])
    Ad = 1.0
    C1 = 0.5
    C2 = 0.2
    Tg = 320
    expected_result = np.array([0, 0, 0])
    result = km.vitrification_WLF_rate_no_reaction_below_Tg(temperature, Tg, Ad, C1, C2)
    assert np.allclose(result, expected_result), "Test case 2 failed. When the reaction temperature is below the glass transition temperature, this vitrification rate should return a rate equal to 0."



def test_rate_functions_signature():
    for name, func in inspect.getmembers(km, inspect.isfunction):
        if name.startswith("rate_"):
            sig = inspect.signature(func)
            params = list(sig.parameters.values())
            assert len(params) >= 2, f"{name} should have at least 2 parameters"
            assert params[0].name == "extent", f"{name}: first argument should be 'extent'"
            assert params[1].name == "T", f"{name}: second argument should be 'T'"

def test_vitrification_functions_signature():
    for name, func in inspect.getmembers(km, inspect.isfunction):
        if name.startswith("vitrification_"):
            sig = inspect.signature(func)
            params = list(sig.parameters.values())
            assert len(params) >= 2, f"{name} should have at least 2 parameters"
            assert params[0].name == "T", f"{name}: first argument should be 'T'"
            assert params[1].name == "Tg", f"{name}: second argument should be 'Tg'"

def test_tg_functions_signature():
    for name, func in inspect.getmembers(km, inspect.isfunction):
        if name.startswith("tg_"):
            sig = inspect.signature(func)
            params = list(sig.parameters.values())
            assert len(params) >= 1, f"{name} should have at least 1 parameter"
            assert params[0].name == "extent", f"{name}: first argument should be 'extent'"

print("All test cases passed!")
    
    
if __name__=="__main__":

    
    test_vitrification_WLF_rate_no_reaction_below_Tg()
    
    