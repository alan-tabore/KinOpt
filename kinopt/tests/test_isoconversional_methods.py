"""Recover a known activation energy from synthetic isothermal experiments."""

import numpy as np
import pytest

from kinopt.src import isoconversional_methods as icm


@pytest.fixture
def isothermal_experiments():
    extent = np.linspace(0.01, 0.99, 101)
    temperatures = [np.full_like(extent, value) for value in (380., 400., 420.)]
    constants = [1e6 * np.exp(-60000 / (8.314 * values[0])) for values in temperatures]
    times = [-np.log1p(-extent) / constant for constant in constants]
    rates = [constant * (1 - extent) for constant in constants]
    return [extent.copy() for _ in temperatures], times, temperatures, rates


@pytest.mark.parametrize("method", [
    icm.isoconversional_analysis_vyazovkin_method,
    icm.isoconversional_analysis_advanced_vyazovkin_method,
])
def test_vyazovkin_recovers_known_energy(method, isothermal_experiments):
    extents, times, temperatures, _ = isothermal_experiments
    result = method(extents, times, temperatures, 60000., 0.1, 0.9, 5)
    np.testing.assert_allclose(result[0], np.linspace(0.1, 0.9, 5))
    np.testing.assert_allclose(result[1], 60000., rtol=1e-4)


def test_friedman_recovers_known_energy(isothermal_experiments):
    extents, _, temperatures, rates = isothermal_experiments
    result = icm.isoconversional_analysis_friedman_method(extents, rates, temperatures, 0.1, 0.9, 5)
    np.testing.assert_allclose(result[1], 60000., rtol=1e-10)


def test_analysis_rejects_conversion_outside_experiments(isothermal_experiments):
    extents, times, temperatures, _ = isothermal_experiments
    with pytest.raises(ValueError, match="minimum"):
        icm.isoconversional_analysis_vyazovkin_method(extents, times, temperatures, 60000., 0., 0.9, 5)
