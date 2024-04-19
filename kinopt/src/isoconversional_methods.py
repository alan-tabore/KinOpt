# -*- coding: utf-8 -*-
"""
This module defines functions for performing isoconversional analysis.

The isoconversional methods function all starts with 'isoconversional_analysis'
"""


import numpy as np
from bisect import bisect_left
import scipy.optimize
import time as time_module
from tqdm import tqdm
import interpolation
from scipy import stats



def check_boundaries(minimum, maximum, list_of_real_convs):
    """
    Check if the specified conversion boundaries are within the valid range of the input data.

    Parameters
    ----------
    minimum : float
        Minimum conversion level to check.
    maximum : float
        Maximum conversion level to check.
    list_of_real_convs : list of numpy.ndarray
        List of NumPy arrays containing conversion data for multiple experiments.

    Returns
    -------
    None
    
    Raises
    ------
    ValueError
        If the specified boundaries are outside the valid range of the input data.
    """
    for conv_data in list_of_real_convs:
        min_conv_data = np.min(conv_data)
        max_conv_data = np.max(conv_data)

        if minimum < min_conv_data:
            raise ValueError(f"The minimum conversion you want to analyze ({minimum}) is lower than the minimum in the data ({min_conv_data}). Please increase the value of the minimum conversion.")
        if maximum > max_conv_data:
            raise ValueError(f"The maximum conversion you want to analyze ({maximum}) is higher than the maximum in the data ({max_conv_data}). Please lower the value of the maximum conversion.")


def find_closest_value(target_value, sorted_array):
    """
    Find the closest value to the target_value in a sorted NumPy array.

    Parameters
    ----------
    target_value : float
        The value to find the closest value to.
    sorted_array : numpy.ndarray
        A sorted NumPy array of numbers.

    Returns
    -------
    tuple: A tuple containing two elements:
        - closest_index (int): The index of the closest value in the array.
        - closest_value (float): The closest value in the array.

    If two numbers are equally close, the smallest number is returned.
    """
    if len(sorted_array) == 0:
        raise ValueError("Input array must not be empty.")
        
    # Find the index where target_value should be inserted in the sorted array
    insert_index = bisect_left(sorted_array, target_value)

    # If target_value is smaller than or equal to the first element of the array
    if insert_index == 0:
        return 0, sorted_array[0]

    # If target_value is larger than or equal to the last element of the array
    if insert_index == len(sorted_array):
        return len(sorted_array) - 1, sorted_array[-1]

    # Calculate the differences only once
    prev_index = insert_index - 1
    next_index = insert_index

    prev_value, next_value = sorted_array[prev_index], sorted_array[next_index]

    # Check which value is closer to target_value and return it
    if next_value - target_value < target_value - prev_value:
        return next_index, next_value
    else:
        return prev_index, prev_value
    
    



def get_data_at_conversion(target_conversion, conversions, times, temperatures):
    """
    Extract data before the target conversion for each dataset.
    
    Parameters
    ----------
    target_conversion : float
        The target conversion value.
    conversions : list of numpy.ndarray
        List of NumPy arrays containing conversion data.
    times : list of numpy.ndarray
        List of NumPy arrays containing time data.
    temperatures : list of numpy.ndarray
        List of NumPy arrays containing temperature data.
    
    Returns
    -------
    tuple
        A tuple containing three lists:
        - new_conversions (list of numpy.ndarray): List of NumPy arrays with data up to target_conversion.
        - new_times (list of numpy.ndarray): List of NumPy arrays with corresponding time data.
        - new_temperatures (list of numpy.ndarray): List of NumPy arrays with corresponding temperature data.
    """
    new_conversions = []
    new_times = []
    new_temperatures = []

    for i in range(len(conversions)):
        # Find the index and value of the closest conversion value
        index, value = find_closest_value(target_conversion, conversions[i])
        
        # Append data up to and including the closest conversion value
        new_conversions.append(conversions[i][:index+1])
        new_times.append(times[i][:index+1])
        new_temperatures.append(temperatures[i][:index+1])

    return new_conversions, new_times, new_temperatures


def get_index_area_of_calculation(conversion_lists, list_of_points_for_analysis):
    """
    Return the indexes of the interval of calculation for the modified integral J.

    Parameters
    ----------
    conversion_lists : List
        List with conversions at different heating rates (one list element for one heating rate)
    list_of_points_for_analysis : List
        List containing all the point of conversion at which the activation energy will be calculated

    Raises
    ------
    ValueError
        return an error if starting point is smaller than step

    Returns
    -------
    index_list : List
        Return the indexes of the interval of calculation for the modified integral J
        
    References
    ----------
    [1] S. Vyazovkin, « Modification of the integral isoconversional method to account for variation in the activation energy », Journal of Computational Chemistry, vol. 22, nᵒ 2, p. 178‑183, 2001, doi: 10.1002/1096-987X(20010130)22:2<178::AID-JCC5>3.0.CO;2-#.
    """
    index_list = []
    conversions_array = np.array(conversion_lists)
    
    # Compute the difference between values of experimental conversions
    delta_alpha_exp = conversions_array[:,1] - conversions_array[:,0]
    
    # Compute the minimum delta to use for analysis
    
    # The same point must not be analyzed 2 times, so the analysis delta must 
    # be greater than the maximum delta between experimental conversions.
    min_delta_alpha_analysis = max(delta_alpha_exp)
    
    min_alpha_analysis = max(conversions_array[:,0]) + min_delta_alpha_analysis
    
    delta_analysis = list_of_points_for_analysis[1] - list_of_points_for_analysis[0]
    
    max_alpha_analysis = min( [min(conversions_array[:,-1]), (list_of_points_for_analysis[0] + delta_analysis*len(list_of_points_for_analysis)) ])
    
    
    
    if list_of_points_for_analysis[0] < min_alpha_analysis:
        raise ValueError(f'\nThe minimum conversion for your analysis points is too low.\nCurrent minimum conversion = {list_of_points_for_analysis[0]}\nMinimum conversion allowed = {min_alpha_analysis}\nPlease increase the minimum conversion to analyze.')
        return
                         
    if list_of_points_for_analysis[-1] > max_alpha_analysis:
        raise ValueError(f'\nThe maximum conversion for your analysis points is too high.\nCurrent maximum conversion = {list_of_points_for_analysis[-1]}\nMaximum conversion allowed for {str(len(list_of_points_for_analysis))} points = {max_alpha_analysis}\nPlease decrease the maximum conversion to analyze.')
        return                 
    
    if delta_analysis < min_delta_alpha_analysis:
        raise ValueError(f'\nThe step between your analysis points is too high.\nCurrent step = {delta_analysis}\nMinimum step = {min_delta_alpha_analysis}\nPlease reduce the number of points you want to analyze.')
        return                 
    
    start_value = list_of_points_for_analysis[0] - delta_analysis
        
                
    for i in range(len(conversion_lists)):
        index_of_start_value, value_of_start_value = find_closest_value(
            start_value, conversion_lists[i])
        index_list.append([index_of_start_value])
        for k in range(len(list_of_points_for_analysis)):
            index, value = find_closest_value(
                list_of_points_for_analysis[k], conversion_lists[i])
            index_list[i].append(index)

    return index_list


def get_data_in_interval(conversion_lists, time_lists, temperature_lists, list_of_points_for_analysis):
    """
    Return the conversion, time and temperature lists for each heating and for each interval of calculation.
    
    1st level of the list corresponds to heating rate
    2nd level of the list corresponds to interval of calculation

    Parameters
    ----------
    conversion_lists : List
        List with conversions at different heating rates (one list element for one heating rate).
    time_lists : List
        List with times at different heating rates (one list element for one heating rate)
    temperature_lists : List
        List with temperatures at different heating rates (one list element for one heating rate)
    list_of_points_for_analysis : List
        List containing all the point of conversion at which the activation energy will be calculated

    Returns
    -------
    new_list_of_conversions : List
        List with conversions at different heating rates for different intervals
    new_list_of_times : List
        List with times at different heating rates for different intervals
    new_list_of_temperatures : List
        List with temperatures at different heating rates for different intervals

    """
    new_list_of_conversions = []
    new_list_of_times = []
    new_list_of_temperatures = []
    index_list = get_index_area_of_calculation(
        conversion_lists, list_of_points_for_analysis)
    for i in range(len(index_list)):
        new_list_of_conversions.append([])
        new_list_of_times.append([])
        new_list_of_temperatures.append([])
        for k in range(len(index_list[i])-1):
            new_list_of_conversions[i].append(
                conversion_lists[i][index_list[i][k]:index_list[i][k+1]])
            new_list_of_times[i].append(
                time_lists[i][index_list[i][k]:index_list[i][k+1]])
            new_list_of_temperatures[i].append(
                temperature_lists[i][index_list[i][k]:index_list[i][k+1]])
        
    

    return new_list_of_conversions, new_list_of_times, new_list_of_temperatures


            
            
    

def compute_integral_J(Ea, time_array, temperature_array):
    r"""
    Compute the integral described in Vyazovkin's paper.
    
    Parameters
    ----------
    Ea : float
        Activation energy for the reaction.
    time_array : numpy.ndarray
        NumPy array of time intervals for the DSC scan.
    temperature_array : numpy.ndarray
        NumPy array of temperatures during the DSC scan.

    Returns
    -------
    float
        The computed integral value.
    
    Notes
    -----
    The integral is computed using the following formula:
    
    .. math::
        J = \int_{t_0}^{t_f} e^{-\frac{E_a}{R\cdot T(t)}} \cdot dt

    where:
        - J is the computed integral value.
        - Ea is the activation energy for the reaction.
        - R is the universal gas constant (8.314 J/(mol·K)).
        - T(t) is the temperature at time t during the DSC scan.
        - :math:`t_0` and :math:`t_f` are the initial and final times in the time_array.
    """
    R = 8.314  # Universal gas constant

    # Calculate the average temperature between adjacent time points
    avg_temperatures = (temperature_array[:-1] + temperature_array[1:]) / 2

    # Calculate the differences in time
    time_diff = np.diff(time_array)

    # Calculate the contributions using the Arrhenius equation
    contributions = np.exp(-Ea / (R * avg_temperatures)) * time_diff

    # Compute the integral using the trapezoidal rule
    integral_value = np.sum(contributions)

    return integral_value




def compute_function_to_minimize(Ea, time_arrays, temperature_arrays):
    r"""
    Compute the function to minimize described in Vyazovkin's paper.

    Parameters
    ----------
    Ea : float
        Activation energy for which the function will be computed.
    time_arrays : list of numpy.ndarray
        List of NumPy arrays containing time data for multiple experiments.
    temperature_arrays : list of numpy.ndarray
        List of NumPy arrays containing temperature data for multiple experiments.

    Returns
    -------
    float
        Value of the function for the given activation energy.

    Notes
    -----
    The function to minimize is computed using the following formula:
    
    .. math::
        F(E_a) = \sum_{i=1}^{N} \sum_{k=1, k \neq i}^{N} \frac{J_i}{J_k}

    where:
        - :math:`F(E_a)` is the computed function to minimize.
        - N is the number of experiments.
        - :math:`J_i` and :math:`J_k` are the integrals computed using the Vyazovkin formula for experiments i and k.
    """
    num_experiments = len(time_arrays)
    
    # Calculate integrals for all experiments and store them in integrals_J list
    integrals_J = [compute_integral_J(Ea, time_arrays[i], temperature_arrays[i]) for i in range(num_experiments)]
    
    # Create a 2D array to store ratios of integrals
    ratios = np.zeros((num_experiments, num_experiments))

    # Calculate the ratios of integrals using NumPy broadcasting
    for i in range(num_experiments):
        for k in range(num_experiments):
            if i != k:
                ratios[i, k] = integrals_J[i] / integrals_J[k]

    # Sum all ratios to compute the function to minimize
    func_sum = np.sum(ratios)

    return func_sum





def isoconversional_analysis_vyazovkin_method(conv_lists, time_lists, temperature_lists, initial_guess, min_conv, max_conv, number_of_points):
    """
    Find the energy of activation for multiple conversions using the Vyazovkin method with a BFGS optimization algorithm.

    Parameters
    ----------
    conv_lists : list of numpy.ndarray
        List containing a list of evolution of conversion for various heating rates (n, m) with n the number of heating rates and m the number of conversion points.
    time_lists : list of numpy.ndarray
        List containing a list of evolution of time for various heating rates (n, m) with n the number of heating rates and m the number of time points.
    temperature_lists : list of numpy.ndarray
        List containing a list of evolution of temperature for various heating rates (n, m) with n the number of heating rates and m the number of temperature points.
    initial_guess : float
        Initial guess of the activation energy for the first desired conversion.
    min_conv : float
        Minimum conversion at which the activation energy will be computed.
    max_conv : float
        Maximum conversion at which the activation energy will be computed.
    number_of_points : int
        Number of conversion points at which the activation energy will be computed.
    
    
    Returns
    -------
    conv_values : numpy.ndarray
        Array containing conversion points at which activation energy was assessed.
    Ea_calculated : numpy.ndarray
        Array containing assessed activation energy.

    Notes
    -----
        It is crucial to provide interpolated data based on the conversion for stability. Without interpolation,
        this method may produce unreliable results.
        
    References
    ----------
    [1] S. Vyazovkin, « Evaluation of activation energy of thermally stimulated solid-state reactions under arbitrary variation of temperature », Journal of Computational Chemistry, vol. 18, nᵒ 3, p. 393‑402, 1997, doi: 10.1002/(SICI)1096-987X(199702)18:3<393::AID-JCC9>3.0.CO;2-P.

    """
    t_start = time_module.process_time()
    
    # Check boundaries and data integrity
    check_boundaries(min_conv, max_conv, conv_lists)
    
    print("Progress of optimization:")
    
    # Create an array of conversion levels to sample
    conv_values = np.linspace(min_conv, max_conv, int(number_of_points))
    
    # Create an empty array to store the activation energies obtained after optimization
    Ea_calculated = np.empty(int(number_of_points))
    
    # Initialize initial_guess
    current_guess = initial_guess

    # Iterates through conv_values while displaying a progress bar
    for i, conv_value in enumerate(tqdm(conv_values, ncols=100)):
        # Extract conversion, time, and temperature required to compute the integrals J
        conv, time_, temperature = get_data_at_conversion(conv_value, conv_lists, time_lists, temperature_lists)

        # Perform minimization of function described in the article using BFGS method
        result = scipy.optimize.minimize(compute_function_to_minimize, x0=current_guess, args=(time_, temperature), method='BFGS', options={'gtol': 1e-15})

        # Store the calculated activation energy
        Ea_calculated[i] = result.x

        # Update the current_guess for the next optimization step
        current_guess = result.x

    t_stop = time_module.process_time()
    print("Done! It took", t_stop - t_start, "s for the optimization to be performed")
    
    return conv_values, Ea_calculated







def isoconversional_analysis_advanced_vyazovkin_method(conv_lists, time_lists, temperature_lists, initial_guess, min_conv, max_conv, number_of_points):
    """
    Find the energy of activation for multiple conversions using the advanced Vyazovkin method with a Broyden-Fletcher-Goldfarb-Shanno algorithm to find the optimal Ea.

    Parameters
    ----------
    conv_lists : list of numpy.ndarray
        List containing a list of evolution of conversion for various heating rates (n, m) with n the number of heating rates and m the number of conversion points.
    time_lists : list of numpy.ndarray
        List containing a list of evolution of time for various heating rates (n, m) with n the number of heating rates and m the number of time points.
    temperature_lists : list of numpy.ndarray
        List containing a list of evolution of temperature for various heating rates (n, m) with n the number of heating rates and m the number of temperature points.
    initial_guess : float
        Initial guess of the activation energy for the first desired conversion.
    min_conv : float
        Minimum conversion at which the activation energy will be computed.
    max_conv : float
        Maximum conversion at which the activation energy will be computed.
    number_of_points : int
        Number of conversion points at which the activation energy will be computed.
    
    
    Returns
    -------
    conv_values : numpy.ndarray
        Array containing conversion points at which activation energy was assessed.
    Ea_calculated : list
        List containing assessed activation energy.
    average_time_at_calculation_point : list
        List containing the average time of all heating programs at the conversion points at which activation energy was assessed.
    average_temperature_at_calculation_point : list
        List containing the average temperature of all heating programs at the conversion points at which activation energy was assessed.
        
    Notes
    -----
        It is crucial to provide interpolated data based on the conversion for stability. Without interpolation,
        this method may produce unreliable results.
    
    References
    ----------
    [1] S. Vyazovkin, « Modification of the integral isoconversional method to account for variation in the activation energy », Journal of Computational Chemistry, vol. 22, nᵒ 2, p. 178‑183, 2001, doi: 10.1002/1096-987X(20010130)22:2<178::AID-JCC5>3.0.CO;2-#.
    """
    t_start = time_module.process_time()
    
    # Check boundaries and data integrity
    check_boundaries(min_conv, max_conv, conv_lists)
    
    print("Progress of optimization:")
    conv_values = np.linspace(min_conv, max_conv, int(number_of_points))
    Ea_calculated = []
    average_time_at_calculation_point = []
    average_temperature_at_calculation_point = []
    
    # Separate data into intervals
    conversions_intervals, times_intervals, temperatures_intervals = get_data_in_interval(conv_lists, time_lists, temperature_lists, conv_values)
    
    for i in tqdm(range(len(conv_values)), ncols=100):
        # Get the experimental data for the computation of the function to minimize
        times = [heating_rate[i] for heating_rate in times_intervals]
        temperatures = [heating_rate[i] for heating_rate in temperatures_intervals]
        
        result = scipy.optimize.minimize(compute_function_to_minimize, x0=initial_guess, args=(
            times, temperatures), method='BFGS', options={'gtol': 1e-15})

        Ea_calculated.append(float(result.x))
        initial_guess = float(result.x)

    t_stop = time_module.process_time()
    
    # Calculate average time and temperature at each calculation point
    for i in range(len(temperatures_intervals[0])):
        time_sum = 0
        temp_sum = 0
        for k in range(len(temperatures_intervals)):
            time_sum += times_intervals[k][i][-1]
            temp_sum += temperatures_intervals[k][i][-1]
        average_time_at_calculation_point.append(time_sum / len(temperatures_intervals))
        average_temperature_at_calculation_point.append(temp_sum / len(temperatures_intervals))
    
    print("Done! It took ", t_stop - t_start, "s for the optimization to be performed")
    
    return conv_values, Ea_calculated, average_time_at_calculation_point, average_temperature_at_calculation_point



def isoconversional_analysis_friedman_method(conv_lists, rate_lists, temperature_lists, min_conv, max_conv, number_of_points):
    """
    
    Parameters
    ----------
    conv_lists : list of numpy.ndarray
        List containing a list of evolution of conversion for various heating rates (n, m) with n the number of heating rates and m the number of conversion points.
    rate_lists : list of numpy.ndarray
        List containing a list of evolution of temperature for various heating rates (n, m) with n the number of heating rates and m the number of temperature points.
    temperature_lists : list of numpy.ndarray
        List containing a list of evolution of temperature for various heating rates (n, m) with n the number of heating rates and m the number of temperature points.
    min_conv : Float
        Minimum conversion at which the activation energy will be computed.
    max_conv : Float
        Maximum conversion at which the activation energy will be computed.
    number_of_points : Float
        Number of conversion points at which the activation energy will be computed. 

    Returns
    -------
    conv_list : List
        List containing conversion points at which activation energy was assessed.
    Ea_calculated : List
        List containing assessed activation energy.
    Intercept : List
        List containing the intercept from the linear regressions 
        of ln(dx/dt) as function of 1/T.
        
    References
    ----------
    [1] N. Sbirrazzuoli, « Is the Friedman Method Applicable to Transformations with Temperature Dependent Reaction Heat? », Macromolecular Chemistry and Physics, vol. 208, nᵒ 14, p. 1592‑1597, 2007, doi: 10.1002/macp.200700100.

    """  
    t_start = time_module.process_time()
    
    # Check boundaries and data integrity
    check_boundaries(min_conv, max_conv, conv_lists)
    
    print("Progress of optimization:")
    
    conv_list = np.linspace(min_conv, max_conv, int(number_of_points))  #Creates the list of conversion points at which the activation energy will be computed
    Ea_calculated = []
    intercept=[]
    
    
    
    for i in tqdm(range(len(conv_list)), ncols=100):
        one_over_T=[]
        rate=[]
        for k in range(len(conv_lists)):
            index,value=find_closest_value(conv_list[i], conv_lists[k])
            one_over_T.append(1/temperature_lists[k][index])
            rate.append(rate_lists[k][index])
        result = stats.linregress(one_over_T, np.log(rate))
        Ea_calculated.append(result.slope*(-8.314))
        intercept.append(result.intercept)
    
    
    t_stop = time_module.process_time()

    print("Done! It took ", t_stop - t_start, "s for the analysis to be performed")

    return conv_list, Ea_calculated, intercept


if __name__ == "__main__":   
    
    import kinetic_models as km
    import matplotlib.pyplot as plt
    import interpolation as interp
    color_list = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red',
                  'tab:purple', 'tab:brown', 'tab:pink', 'tab:grey', 'tab:olive', 'tab:cyan']
    linestyle = ['dashed', ]
    marker = ['o']
    

    number_of_points = 10000
    time_list = np.linspace(0, 25, number_of_points)  # 30 minutes
    time_lists = [time_list, time_list, time_list, time_list]
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
    
    for i in range(len(time_lists)):
        extent, rate, _, _, _ = km.compute_extent_and_rate(time_lists[i], 
                                                           temperatures[i],
                                                           rate_law=km.rate_for_kamal,
                                                           rate_law_args=(A1,E1,A2,E2,m,n))
        conversions.append(extent)
        rates.append(rate)

    
    linear_conversions, linear_times, linear_temperatures, linear_rates = interp.linear_interpolation(conversions,time_lists,temperatures,rates,1000)

    
    

    
    conv_friedman, Ea_friedman, _ = isoconversional_analysis_friedman_method(linear_conversions, 
                                                                             linear_rates, 
                                                                             linear_temperatures,
                                                                             0.01,
                                                                             0.99,
                                                                             100)




    conv_vyazovkin, Ea_vyazovkin = isoconversional_analysis_vyazovkin_method(linear_conversions, 
                                                                             linear_rates, 
                                                                             linear_temperatures,
                                                                             50000,
                                                                             0.01,
                                                                             0.99,
                                                                             100)

    conv_advanced_vyazovkin, Ea_advanced_vyazovkin, _, _ = isoconversional_analysis_advanced_vyazovkin_method(linear_conversions, 
                                                                                                            linear_rates, 
                                                                                                            linear_temperatures,
                                                                                                            50000,
                                                                                                            0.01,
                                                                                                            0.99,
                                                                                                            250)
    fig, ax = plt.subplots(figsize=(8,6))
    for i in range(len(linear_times)):
        ax.plot(linear_times[i],linear_rates[i])
    ax.legend()
    
    
    fig, ax = plt.subplots(figsize=(8,6))
    ax.plot(conv_friedman,Ea_friedman,label="Friedman method")
    ax.plot(conv_vyazovkin, Ea_vyazovkin, label="Vyazovkin method")
    ax.plot(conv_advanced_vyazovkin, Ea_advanced_vyazovkin, label="Advanced Vyazovkin method")
    ax.legend()

    
   


