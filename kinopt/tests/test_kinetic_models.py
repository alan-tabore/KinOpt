# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 11:39:41 2023

@author: alan.tabore
"""
import pytest
import numpy as np
import inspect
from kinopt.src import kinetic_models as km

def test_arrhenius_rate_constant():
    A = 1.0  # Pre-exponential factor
    Ea = 831.446261815324  # Activation energy in J/mol
    T = 100.0  # Temperature in Kelvin
    
    expected_result = np.exp(-1)
    result = km.arrhenius_rate_constant(T, A, Ea)
    assert np.allclose(result, expected_result), "Arrhenius rate constant calculation failed."
   
def test_rate_for_nth_order():
    extent = np.array([0, 0.1, 0.3, 0.5, 0.6, 1])
    T = np.array([100.0, 200.0, 300.0, 400.0, 500.0, 600.0])
    A = 1.0  # Pre-exponential factor
    Ea = 831.446261815324  # Activation energy in J/mol
    n = 2  # Order of the reaction
    
    expected_results = [np.exp(-1), ((0.9)**2)*np.exp(-1/2), ((0.7)**2)*np.exp(-1/3), ((0.5)**2)*np.exp(-1/4), ((0.4)**2)*np.exp(-1/5), 0]
    results = km.rate_for_nth_order(extent, T, A, Ea, n)
    assert np.allclose(results, expected_results), "Rate for nth order reaction calculation failed."

def test_rate_for_autocatalytic():
    extent = np.array([0, 0.1, 0.3, 0.5, 0.6, 1])
    T = np.array([100.0, 200.0, 300.0, 400.0, 500.0, 600.0])
    A = 1.0  # Pre-exponential factor
    Ea = 831.446261815324  # Activation energy in J/mol
    n = 2  # Order of the reaction
    m = 0.3 # Autocatalytic order
    
    expected_results = [0, (0.1**0.3)*((0.9)**2)*np.exp(-1/2), (0.3**0.3)*((0.7)**2)*np.exp(-1/3), (0.5**0.3)*((0.5)**2)*np.exp(-1/4), (0.6**0.3)*((0.4)**2)*np.exp(-1/5), 0]
    results = km.rate_for_autocatalytic(extent, T, A, Ea, m, n)
    assert np.allclose(results, expected_results), "Rate for nth order reaction calculation failed."

def test_rate_for_kamal():
    extent = np.array([0, 0.1, 0.3, 0.5, 0.6, 1])
    T = np.array([100.0, 200.0, 300.0, 400.0, 500.0, 600.0])
    A1 = 1.0  # Pre-exponential factor
    E1 = 831.446261815324  # Activation energy in J/mol
    A2 = 2  # Pre-exponential factor for second reaction
    E2 = 415.723130907662  # Activation energy for second reaction in J/mol
    n = 2  # Order of the reaction
    m = 0.3 # Autocatalytic order
    
    expected_results = [np.exp(-1), 
                        (np.exp(-1/2)+2*np.exp(-1/4)*0.1**0.3)*(0.9**2), 
                        (np.exp(-1/3)+2*np.exp(-1/6)*0.3**0.3)*(0.7**2), 
                        (np.exp(-1/4)+2*np.exp(-1/8)*0.5**0.3)*(0.5**2),
                        (np.exp(-1/5)+2*np.exp(-1/10)*0.6**0.3)*(0.4**2),
                        0]
    results = km.rate_for_kamal(extent,T,A1,E1,A2,E2,m,n)
    assert np.allclose(results, expected_results), "Rate for kamal reaction calculation failed."

    
def test_vitrification_WLF_rate():
    # Test case 1: All temperatures above Tg
    temperature = np.array([350, 400, 450])
    Ad = 1.0
    C1 = 1.0
    C2 = 10
    Tg = 320
    expected_result = np.array([np.exp(3/4), np.exp(8/9), np.exp(13/14)])
    result = km.vitrification_WLF_rate(temperature, Tg, Ad, C1, C2)
    assert np.allclose(result, expected_result), "Test case 1 failed. When the reaction temperature is above the glass transition temperature, this vitrification rate should return a non-zero value."

    # Test case 2: All temperatures below Tg
    temperature = np.array([280, 300, 310])
    Ad = 1.0
    C1 = 1.0
    C2 = 10
    Tg = 320
    expected_result = np.array([np.exp(-4/5), np.exp(-2/3), np.exp(-1/2)])
    result = km.vitrification_WLF_rate(temperature, Tg, Ad, C1, C2)
    assert np.allclose(result, expected_result), "Test case 2 failed. When the reaction temperature is below the glass transition temperature, this vitrification rate should return a rate equal to 0."


    
def test_vitrification_WLF_rate_no_reaction_below_Tg():
    # Test case 1: All temperatures above Tg
    temperature = np.array([350, 400, 450])
    Ad = 1.0
    C1 = 1.0
    C2 = 10
    Tg = 320
    expected_result = np.array([np.exp(3/4), np.exp(8/9), np.exp(13/14)])
    result = km.vitrification_WLF_rate_no_reaction_below_Tg(temperature, Tg, Ad, C1, C2)
    assert np.allclose(result, expected_result), "Test case 1 failed. When the reaction temperature is above the glass transition temperature, this vitrification rate should return a non-zero value."

    # Test case 2: All temperatures below Tg
    temperature = np.array([280, 300, 310])
    Ad = 1.0
    C1 = 1.0
    C2 = 10
    Tg = 320
    expected_result = np.array([0, 0, 0])
    result = km.vitrification_WLF_rate_no_reaction_below_Tg(temperature, Tg, Ad, C1, C2)
    assert np.allclose(result, expected_result), "Test case 2 failed. When the reaction temperature is below the glass transition temperature, this vitrification rate should return a rate equal to 0."


def test_tg_diBennedetto():
    Tg_0 = -100
    Tg_inf = 100
    coeff = 0.5
    extent = np.array([0, 0.1, 0.3, 0.5, 0.6, 1])
    
    expected_result = np.array([-100, -100+200*1/19, -100+200*3/17, -100+200*1/3, -100+200*3/7, 100])
    result = km.tg_diBennedetto(extent, Tg_0, Tg_inf, coeff)
    assert np.allclose(result, expected_result), "DiBenedetto Tg calculation failed."

    
def test_coupling_harmonic_mean():
    kc = 2
    kv = 3
    
    expected_result = 1.2
    result = km.coupling_harmonic_mean(kc, kv)
    assert np.allclose(result, expected_result), "Harmonic mean coupling calculation failed."


def test_coupling_product():
    kc = 2
    kv = 3
    
    expected_result = 6
    result = km.coupling_product(kc, kv)
    assert np.allclose(result, expected_result), "Product coupling calculation failed."


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
    
def test_coupling_functions_signature():
    for name, func in inspect.getmembers(km, inspect.isfunction):
        if name.startswith("coupling_"):
            sig = inspect.signature(func)
            params = list(sig.parameters.values())
            assert len(params) >= 3, f"{name} should have at least 3 parameters: kc, kv, and experimental_parameters (that can be set to 'None' if no experimental parameter is required for the coupling) "
            assert params[0].name == "kc", f"{name}: first argument should be 'kc' (purely chemical rate)"
            assert params[1].name == "kv", f"{name}: second argument should be 'kv' (vitrification rate)"    
    
        
if __name__=="__main__":

    
    test_vitrification_WLF_rate_no_reaction_below_Tg()
    
    