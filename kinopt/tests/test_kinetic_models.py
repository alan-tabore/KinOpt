# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 11:39:41 2023

@author: alan.tabore
"""
import pytest
import numpy as np
import src.kinetic_models as km
    
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
    assert np.allclose(result, expected_result), "Test case 2 failed"


    # Test case 3: Large values for Ad, C1, and C2
    temperature = np.array([350, 400, 450])
    Ad = 1e6
    C1 = 1e6
    C2 = 1e6
    Tg = 320
    expected_result = np.array([1.06768614e+19, 5.50527845e+40, 2.82451591e+62])
    result = km.vitrification_WLF_rate_no_reaction_below_Tg(temperature, Tg, Ad, C1, C2)
    assert np.allclose(result, expected_result), "Test case 4 failed"

    print("All test cases passed!")
    
    
if __name__=="__main__":

    
    test_vitrification_WLF_rate_no_reaction_below_Tg()
    
    