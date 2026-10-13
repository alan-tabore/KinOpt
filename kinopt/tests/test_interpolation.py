import pytest
import numpy as np
from kinopt.src import interpolation as interp


@pytest.mark.parametrize("method", [interp.linear_interpolation, interp.cubic_spline_interpolation])
def test_shared_grid_uses_only_common_domain(method):
    conversions = [np.array([0., .5, 1.]), np.array([.1, .5, .9])]
    times = [2 * values for values in conversions]
    temperatures = [300 + values for values in conversions]
    rates = [3 * values for values in conversions]
    result = method(conversions, times, temperatures, rates, 5)
    expected = np.tile(np.linspace(.1, .9, 5), (2, 1))
    np.testing.assert_allclose(result[0], expected)
    np.testing.assert_allclose(result[1], 2 * expected)
    np.testing.assert_allclose(result[2], 300 + expected)
    np.testing.assert_allclose(result[3], 3 * expected)


@pytest.mark.parametrize("method", [interp.linear_interpolation_multiple_limits,
                                   interp.cubic_spline_interpolation_multiple_limits])
def test_per_experiment_grid_returns_all_four_columns(method):
    conversions = [np.array([0., .3, .6]), np.array([.1, .5, .9])]
    result = method(conversions, conversions, [300 + c for c in conversions], conversions, 5)
    expected = np.array([np.linspace(0, .6, 5), np.linspace(.1, .9, 5)])
    assert len(result) == 4
    np.testing.assert_allclose(result[0], expected)
    np.testing.assert_allclose(result[1], expected)
    np.testing.assert_allclose(result[2], 300 + expected)
    np.testing.assert_allclose(result[3], expected)


def test_monotonic_filter_keeps_columns_aligned():
    conversion = np.array([0., .4, .5, .2, .3, .6])
    with pytest.warns(UserWarning, match="removed 2"):
        actual = interp.check_increase_and_remove_if_not(
            [conversion], [np.arange(6.)], [np.arange(6.) + 300], [np.arange(6.) + 10])
    indices = [0, 1, 2, 5]
    np.testing.assert_array_equal(actual[0][0], conversion[indices])
    np.testing.assert_array_equal(actual[1][0], indices)
    np.testing.assert_array_equal(actual[2][0], np.array(indices) + 300)
    np.testing.assert_array_equal(actual[3][0], np.array(indices) + 10)


def test_interpolation_without_rates():
    data = [np.array([0., .5, 1.])]
    result = interp.linear_interpolation(data, data, data, None, 5)
    np.testing.assert_allclose(result[1][0], np.linspace(0, 1, 5))
    assert result[3] is None


def test_disjoint_experiments_are_rejected():
    data = [np.array([0., .2]), np.array([.3, .4])]
    with pytest.raises(ValueError, match="no common"):
        interp.linear_interpolation(data, data, data, data, 5)


@pytest.mark.parametrize("points", [0, 1, -1, 2.5])
def test_invalid_interpolation_point_count(points):
    data = [np.array([0., 1.])]
    with pytest.raises(ValueError, match="point count"):
        interp.linear_interpolation(data, data, data, data, points)

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
