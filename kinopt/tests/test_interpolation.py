import pytest
import numpy as np
from kinopt.src import interpolation as interp

def test_linear_interpolation():
    """
    Test the linear_interpolation function to ensure it correctly interpolates
    conversion, time, temperature, and rate arrays to a specified number of points.

    The test sets up a simple case with known input arrays for conversions, times,
    temperatures, and rates, and specifies 9 desired interpolation points. It then
    verifies that the output arrays match the expected interpolated values using
    np.allclose for numerical comparison.
    """
    conversions = [np.array([0.0, 0.25, 0.5, 0.75, 1.0])]
    times = [np.array([0.0, 2.5, 5.0, 7.5, 10.0])]
    temperatures = [np.array([300, 325, 350, 350, 300])]
    rates = [np.array([0.0, 0.25, 0.5, 0.25, 0.0])]
    
    num_points = 9
    
    expected_conversions = np.linspace(0.0, 1, num_points) 
    expected_times = np.linspace(0.0, 10.0, num_points)
    expected_temperatures = [300, 312.5, 325, 337.5, 350, 350, 350, 325, 300]
    expected_rates = [0.0, 0.125, 0.25, 0.375, 0.5, 0.375, 0.25, 0.125, 0.0]
    
    new_conversions, new_times, new_temperatures, new_rates = interp.linear_interpolation(
        conversions, times, temperatures, rates, num_points
    )

    assert np.allclose(new_conversions[0], expected_conversions)
    assert np.allclose(new_times[0], expected_times)
    assert np.allclose(new_temperatures[0], expected_temperatures)
    assert np.allclose(new_rates[0], expected_rates)
    
def test_linear_interpolation_multiple_limits():
    """
    Test the linear_interpolation_multiple_limits function to ensure it correctly interpolates
    conversion, time, temperature, and rate arrays to a specified number of points.


    """
    conversions = [np.array([0.0, 0.2, 0.4, 0.6, 0.7, 0.9]),
                   np.array([0, 0.2, 0.4, 0.6, 0.9]),
                   np.array([0.1, 0.4, 0.6, 0.8, 1.0])]
    
    times = [np.array([0.0, 2.0, 4.0, 6.0, 8.0, 10.0]),
             np.array([0, 5, 15, 30, 45]),
             np.array([1.0, 2.0, 4.0, 7.0, 20])]
    
    temperatures = [np.array([300, 340, 380, 400, 340, 300]),
                    np.array([300, 340, 360, 360, 300]),
                    np.array([300, 360, 360, 340, 300])]
    
    rates = [np.array([0.0, 0.2, 0.6, 0.4, 0.2, 0.0]),
             np.array([0.0, 0.4, 0.6, 0.3, 0.0]),
             np.array([0.0, 0.3, 0.4, 0.6, 0.1]),]
    
    num_points = 10
    
    # conversion is an increasing function so np.linspace is used
    expected_conversions = [np.linspace(0.0, 0.9, num_points),
                            np.linspace(0.0, 0.9, num_points),
                            np.linspace(0.1, 1.0, num_points)]
    
    # time is an increasing function so np.linspace is used
    expected_times = [[0, 1, 2, 3, 4, 5, 6, 8, 9, 10],
                      [0, 2.5, 5, 10, 15, 22.5, 30, 35, 40, 45],
                      [1, 4/3,  5/3,  2, 3, 4, 5.5, 7, 13.5, 20]]
    # trivial solution to interpolation
    expected_temperatures = [[300, 320, 340, 360, 380, 390, 400, 340, 320, 300],
                             [300, 320, 340, 350, 360, 360, 360, 340, 320, 300],
                             [300, 320, 340, 360, 360, 360, 350, 340, 320, 300]]
    # trivial solution to interpolation                          
    expected_rates = [[0, 0.1, 0.2, 0.4, 0.6, 0.5, 0.4, 0.2, 0.1 , 0],
                      [0, 0.2 , 0.4, 0.5, 0.6, 0.45, 0.3, 0.2, 0.1, 0],
                      [0,0.1,0.2, 0.3, 0.35, 0.4, 0.5, 0.6, 0.35, 0.1]] 
    
    new_conversions, new_times, new_temperatures, new_rates = interp.linear_interpolation_multiple_limits(
        conversions, times, temperatures, rates, num_points
    )

    assert np.allclose(new_conversions, expected_conversions)
    assert np.allclose(new_times, expected_times)
    assert np.allclose(new_temperatures, expected_temperatures)
    assert np.allclose(new_rates, expected_rates)