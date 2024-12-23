# -*- coding: utf-8 -*-
"""
The interpolation module allows simple interpolation of data.

It is highly recommended to interpolate data over extent for analysis and optimization.

For experimental data with many data points (e.g. DSC or rheology experiments), a linear 
interpolation is usually more than enough.

For experimental data with scarce data points (e.g. FTIR experiments) 
a cubic spline interpolation might be more appropriate.
"""

import numpy as np
from scipy import interpolate




def limit_of_interpolation(conversions_lists):
    """
    Find the minimum and maximum values in a list of conversion lists.

    Parameters
    ----------
    conversions_lists : list
        List of conversion lists.

    Returns
    -------
    tuple
        Minimum and maximum values found in the conversion lists.
    """
    flat_conversions = np.concatenate(conversions_lists)
    return np.min(flat_conversions), np.max(flat_conversions)


def check_increase_and_remove_if_not(conversions, times, temperatures, rates):
    """
    Check if conversions are increasing and remove any non-increasing segments.

    Parameters
    ----------
    conversions : list
        List of conversion arrays.
    times : list
        List of time arrays.
    temperatures : list
        List of temperature arrays.
    rates : list, optional
        List of rate arrays. Default is None.

    Returns
    -------
    tuple
        New lists of conversions, times, temperatures, and rates with non-increasing segments removed.
    """
    new_conversions = []
    new_times = []
    new_temperatures = []
    new_rates = [] if rates else None
    
    for i in range(len(conversions)):
        conv = np.array(conversions[i])
        time = np.array(times[i])
        temp = np.array(temperatures[i])
        
        increasing_indices = np.where(conv[:-1] < conv[1:])[0]
        increasing_indices = np.append(increasing_indices, len(conv) - 1)
        
        new_conversions.append(conv[increasing_indices])
        new_times.append(time[increasing_indices])
        new_temperatures.append(temp[increasing_indices])
        
        if rates:
            rate = np.array(rates[i])
            new_rates.append(rate[increasing_indices])
    
    if rates:
        return new_conversions, new_times, new_temperatures, new_rates
    else:
        return new_conversions, new_times, new_temperatures

def linear_interpolation(conversions_lists, times_lists, temperatures_lists, rates_lists, number_of_points):
    """
    Perform linear interpolation on conversion, time, temperature, and rate data.

    Parameters
    ----------
    conversions_lists : list
        List of conversion arrays.
    times_lists : list
        List of time arrays.
    temperatures_lists : list
        List of temperature arrays.
    rates_lists : list
        List of rate arrays.
    number_of_points : int
        Number of points for interpolation.

    Returns
    -------
    tuple
        Interpolated conversion, time, temperature, and rate arrays.
    """
    flat_conversions = np.concatenate(conversions_lists)
    minimum, maximum = np.min(flat_conversions), np.max(flat_conversions)
    global_conversion = np.linspace(minimum, maximum, number_of_points)
    
    conv, time, temp, rates = check_increase_and_remove_if_not(conversions_lists, times_lists, temperatures_lists, rates_lists)
    
    new_conversions = np.empty((len(conversions_lists), number_of_points))
    new_times = np.empty((len(conversions_lists), number_of_points))
    new_temperatures = np.empty((len(conversions_lists), number_of_points))
    new_rates = np.empty((len(conversions_lists), number_of_points)) if rates_lists else None
    
    for i in range(len(conversions_lists)):
        f = interpolate.interp1d(conv[i], time[i])
        g = interpolate.interp1d(conv[i], temp[i])
        h = interpolate.interp1d(conv[i], rates[i])
        
        new_times[i] = f(global_conversion)
        new_temperatures[i] = g(global_conversion)  
        new_rates[i] = h(global_conversion)
        
        new_conversions[i] = global_conversion
    
    return new_conversions, new_times, new_temperatures, new_rates

def linear_interpolation_multiple_limits(conversions_lists, times_lists, temperatures_lists, rates_lists, number_of_points):
    """
    Perform linear interpolation on conversion, time, temperature, and rate data with multiple limits.

    Parameters
    ----------
    conversions_lists : list
        List of conversion arrays.
    times_lists : list
        List of time arrays.
    temperatures_lists : list
        List of temperature arrays.
    rates_lists : list
        List of rate arrays.
    number_of_points : int
        Number of points for interpolation.

    Returns
    -------
    tuple
        Interpolated conversion, time, temperature, and rate arrays.
    """
    new_conversions = np.empty((len(conversions_lists), number_of_points))
    new_times = np.empty((len(conversions_lists), number_of_points))
    new_temperatures = np.empty((len(conversions_lists), number_of_points))
    new_rates = np.empty((len(conversions_lists), number_of_points))
    
    for i, conv_list in enumerate(conversions_lists):
        minimum = conv_list[0]
        maximum = conv_list[-1]
        global_conversion = np.linspace(minimum, maximum, number_of_points)
        
        f = interpolate.interp1d(conv_list, times_lists[i])
        g = interpolate.interp1d(conv_list, temperatures_lists[i])
        h = interpolate.interp1d(conv_list, rates_lists[i])
        
        new_times[i] = f(global_conversion)
        new_temperatures[i] = g(global_conversion)            
        new_rates[i] = h(global_conversion)
        
        new_conversions[i] = global_conversion
    
    return new_conversions, new_times, new_temperatures, new_rates
    
def cubic_spline_interpolation(conversions_lists, times_lists, temperatures_lists, rates_lists, number_of_points):
    """
    Perform cubic spline interpolation on conversion, time, temperature, and rate data.

    Parameters
    ----------
    conversions_lists : list
        List of conversion arrays.
    times_lists : list
        List of time arrays.
    temperatures_lists : list
        List of temperature arrays.
    rates_lists : list
        List of rate arrays.
    number_of_points : int
        Number of points for interpolation.

    Returns
    -------
    tuple
        Interpolated conversion, time, temperature, and rate arrays.
    """
    flat_conversions = np.concatenate(conversions_lists)
    minimum, maximum = np.min(flat_conversions), np.max(flat_conversions)
    global_conversion = np.linspace(minimum, maximum, number_of_points)
    
    conv, time, temp, rates = check_increase_and_remove_if_not(conversions_lists, times_lists, temperatures_lists, rates_lists)
    
    new_conversions = np.empty((len(conversions_lists), number_of_points))
    new_times = np.empty((len(conversions_lists), number_of_points))
    new_temperatures = np.empty((len(conversions_lists), number_of_points))
    new_rates = np.empty((len(conversions_lists), number_of_points)) if rates_lists else None
    
    for i in range(len(conversions_lists)):
        f = interpolate.CubicSpline(conv[i], time[i])
        g = interpolate.CubicSpline(conv[i], temp[i])
        h = interpolate.CubicSpline(conv[i], rates[i])
        
        new_times[i] = f(global_conversion)
        new_temperatures[i] = g(global_conversion)
        new_rates[i] = h(global_conversion)
        
        new_conversions[i] = global_conversion
    
    return new_conversions, new_times, new_temperatures, new_rates

def cubic_spline_interpolation_multiple_limits(conversions_lists, times_lists, temperatures_lists, rates_lists, number_of_points):
    """
    Perform cubic spline interpolation on conversion, time, and temperature data with multiple limits.

    Parameters
    ----------
    conversions_lists : list
        List of conversion arrays.
    times_lists : list
        List of time arrays.
    temperatures_lists : list
        List of temperature arrays.
    number_of_points : int
        Number of points for interpolation.

    Returns
    -------
    tuple
        Interpolated conversion, time, and temperature arrays.
    """
    # Preallocate arrays for interpolated values
    new_conversions = np.empty((len(conversions_lists), number_of_points))
    new_times = np.empty((len(conversions_lists), number_of_points))
    new_temperatures = np.empty((len(conversions_lists), number_of_points))
    new_rates = np.empty((len(conversions_lists), number_of_points))
    
    for i, conv_list in enumerate(conversions_lists):
        minimum = conv_list[0]
        maximum = conv_list[-1]
        global_conversion = np.linspace(minimum, maximum, number_of_points)
        
        # Perform cubic spline interpolation
        f = interpolate.CubicSpline(conversions_lists[i], times_lists[i])
        g = interpolate.CubicSpline(conversions_lists[i], temperatures_lists[i])
        h = interpolate.CubicSpline(conv_list, rates_lists[i])
        
        # Evaluate interpolations at global conversion points
        new_conv = global_conversion
        new_time = f(global_conversion)
        new_temp = g(global_conversion)
        new_rate = h(global_conversion)
        
        # Append to results
        new_conversions.append(new_conv)
        new_times.append(new_time)
        new_temperatures.append(new_temp)
        new_rates.append(new_rate)

    return np.array(new_conversions), np.array(new_times), np.array(new_temperatures)








if __name__ == "__main__":
    #%% Example 1 - Experiment with a lot of experimental data points
    import matplotlib.pyplot as plt
    import kinetic_models as km

    number_of_points = 500
    time_list = np.linspace(0, 25, number_of_points)  # 30 minutes
    times = [time_list, time_list, time_list, time_list]
    temperatures = [np.linspace(293, 443, number_of_points),  # 5°C/min
                    np.linspace(293, 593, number_of_points),  # 10°C/min
                    np.linspace(293, 743, number_of_points),  # 15°C/min
                    np.linspace(293, 893, number_of_points)]  # 20°C/min
    A1 = 1e10
    E1 = 70000
    A2 = 1e13
    E2 = 85000
    m = 0.45
    n = 1
    
    conversions = []
    rates = []
    
    for i in range(len(times)):
        extent, rate, _, _, _ = km.compute_extent_and_rate(times[i], 
                                                           temperatures[i],
                                                           rate_law=km.rate_for_kamal,
                                                           rate_law_args=(A1,E1,A2,E2,m,n))
        conversions.append(extent)
        rates.append(rate)    
    
    linear_conversions, linear_times, linear_temperatures, linear_rates = linear_interpolation(conversions,times,temperatures,rates,1000)
    cubic_conversions, cubic_times, cubic_temperatures, cubic_rates = cubic_spline_interpolation(conversions,times,temperatures,rates,5)
    
    #%% Plot linear interpolation
    # Rate over time
    fig, ax = plt.subplots()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Rate")
    ax.set_title("Linear interpolation vs Original data")
    
    for i in range(len(rates)):
        line_original, =ax.plot(times[i],rates[i],label="Original data for " + str((i+1)*5) + "°/min",alpha=0.5)
        curve_color = line_original.get_color()
        ax.plot(linear_times[i],linear_rates[i],label="Linear interpolation for " + str((i+1)*5) + "°/min", color=curve_color, linestyle="dashed") 
    ax.legend()
    
    # Rate over extent
    fig, ax = plt.subplots()
    ax.set_xlabel("Extent")
    ax.set_ylabel("Rate")
    ax.set_title("Linear interpolation vs Original data")
    
    for i in range(len(rates)):
        line_original, = ax.plot(conversions[i],rates[i],label="Original data for " + str((i+1)*5) + "°/min",alpha=0.5)
        curve_color = line_original.get_color()
        ax.plot(linear_conversions[i],linear_rates[i],label="Linear interpolation for " + str((i+1)*5) + "°/min", color=curve_color, linestyle="dashed")
    ax.legend()
    
    
    
    # Extent over time
    fig, ax = plt.subplots()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Extent")
    ax.set_title("Interpolation vs Original data")
    
    for i in range(len(rates)):
        line_original, = ax.plot(times[i],conversions[i],label="Original data for " + str((i+1)*5) + "°/min",alpha=0.5)
        curve_color = line_original.get_color()
        ax.plot(linear_times[i],linear_conversions[i],label="Linear interpolation for " + str((i+1)*5) + "°/min", color=curve_color, linestyle="dashed")
        
    ax.legend()
    
    #%% Plot cubic interpolation
    # Rate over time
    fig, ax = plt.subplots()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Rate")
    ax.set_title("Cubic interpolation vs Original data")
    
    for i in range(len(rates)):
        line_original, =ax.plot(times[i],rates[i],label="Original data for " + str((i+1)*5) + "°/min",alpha=0.5)
        curve_color = line_original.get_color()
        ax.plot(cubic_times[i],cubic_rates[i],label="Cubic interpolation for " + str((i+1)*5) + "°/min", color=curve_color, linestyle="dashed") 
    ax.legend()
    
    # Rate over extent
    fig, ax = plt.subplots()
    ax.set_xlabel("Extent")
    ax.set_ylabel("Rate")
    ax.set_title("Cubic interpolation vs Original data")
    
    for i in range(len(rates)):
        line_original, = ax.plot(conversions[i],rates[i],label="Original data for " + str((i+1)*5) + "°/min",alpha=0.5)
        curve_color = line_original.get_color()
        ax.plot(cubic_conversions[i],cubic_rates[i],label="Cubic interpolation for " + str((i+1)*5) + "°/min", color=curve_color, linestyle="dashed")
    ax.legend()
    
    
    
    # Extent over time
    fig, ax = plt.subplots()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Extent")
    ax.set_title("Cubic interpolation vs Original data")
    
    for i in range(len(rates)):
        line_original, = ax.plot(times[i],conversions[i],label="Original data for " + str((i+1)*5) + "°/min",alpha=0.5)
        curve_color = line_original.get_color()
        ax.plot(cubic_times[i],cubic_conversions[i],label="Cubic interpolation for " + str((i+1)*5) + "°/min", color=curve_color, linestyle="dashed")
        
    ax.legend()
    
