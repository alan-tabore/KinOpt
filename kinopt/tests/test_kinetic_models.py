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


def test_kamal_jacobian_matches_finite_differences_for_vector_data():
    extent = np.array([0.05, 0.2, 0.55, 0.9])
    temperature = np.array([330.0, 360.0, 410.0, 470.0])
    parameters = np.array([1.3e7, 52_000.0, 4.1e9, 76_000.0, 0.8, 1.4])

    analytic = km.jac_for_rate_for_kamal(
        extent,
        temperature,
        *parameters,
    )
    numerical_columns = []
    for parameter_index, parameter in enumerate(parameters):
        step = max(abs(parameter) * 1e-5, 1e-7)
        lower = parameters.copy()
        upper = parameters.copy()
        lower[parameter_index] -= step
        upper[parameter_index] += step
        numerical_columns.append(
            (
                km.rate_for_kamal(extent, temperature, *upper)
                - km.rate_for_kamal(extent, temperature, *lower)
            )
            / (2 * step)
        )

    numerical = np.column_stack(numerical_columns)
    assert analytic.shape == (extent.size, parameters.size)
    np.testing.assert_allclose(analytic, numerical, rtol=2e-8, atol=1e-12)


def test_combined_kamal_evaluation_reuses_prepared_experimental_data():
    extent = np.array([0.05, 0.2, 0.55, 0.9])
    temperature = np.array([330.0, 360.0, 410.0, 470.0])
    parameters = (1.3e7, 52_000.0, 4.1e9, 76_000.0, 0.8, 1.4)

    direct_rate, direct_jacobian = km.kamal_rate_and_jacobian(
        extent,
        temperature,
        *parameters,
    )
    prepared = km.prepare_kamal_data(extent, temperature)
    prepared_rate, prepared_jacobian = (
        km.kamal_rate_and_jacobian_from_prepared(prepared, *parameters)
    )

    np.testing.assert_allclose(
        direct_rate,
        km.rate_for_kamal(extent, temperature, *parameters),
        rtol=2e-15,
    )
    np.testing.assert_array_equal(prepared_rate, direct_rate)
    np.testing.assert_array_equal(prepared_jacobian, direct_jacobian)


def test_kamal_jacobian_is_finite_at_conversion_endpoints():
    jacobian = km.jac_for_rate_for_kamal(
        np.array([0.0, 1.0]),
        np.array([350.0, 450.0]),
        1e8,
        50_000.0,
        1e10,
        75_000.0,
        0.8,
        1.2,
    )

    assert jacobian.shape == (2, 6)
    assert np.all(np.isfinite(jacobian))
    assert jacobian[0, 4] == 0
    np.testing.assert_array_equal(jacobian[1], np.zeros(6))


def test_kamal_jacobian_keeps_scalar_shape():
    jacobian = km.jac_for_rate_for_kamal(
        0.5,
        400.0,
        1e8,
        50_000.0,
        1e10,
        75_000.0,
        0.8,
        1.2,
    )

    assert jacobian.shape == (6,)


@pytest.mark.parametrize("extent", [-0.1, 1.1, np.nan, np.inf])
def test_kamal_jacobian_rejects_invalid_conversion(extent):
    with pytest.raises(ValueError, match="between 0 and 1"):
        km.jac_for_rate_for_kamal(
            extent,
            400.0,
            1e8,
            50_000.0,
            1e10,
            75_000.0,
            0.8,
            1.2,
        )


@pytest.mark.parametrize("extent", [-0.1, 1.1, np.nan, np.inf])
def test_autocatalytic_rejects_invalid_conversion(extent):
    with pytest.raises(ValueError, match="between 0 and 1"):
        km.rate_for_autocatalytic(np.array([.2, extent]), 400., 1e8, 60000., .5, 1.)


def test_autocatalytic_zero_conversion_has_zero_rate_but_cannot_start_simulation():
    assert km.rate_for_autocatalytic(0., 400., 1e8, 60000., .5, 1.) == 0
    with pytest.raises(ValueError, match="positive initial extent"):
        km.compute_extent_and_rate([0, 1], [400, 400], km.rate_for_autocatalytic,
                                   (1e8, 60000., .5, 1.), initial_extent=0)


def test_harmonic_coupling_handles_zero_scalar_and_array_rates():
    with np.errstate(all='raise'):
        assert km.coupling_harmonic_mean(0, 1) == 0
        assert km.coupling_harmonic_mean(0, 0) == 0
        np.testing.assert_allclose(km.coupling_harmonic_mean(np.array([0., 2.]), np.array([3., 3.])), [0., 1.2])

    
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
