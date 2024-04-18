# -*- coding: utf-8 -*-
"""
The data extraction allows to retrieve kinetic data from one or multiple files.

In addition to retrieving data from .txt or .csv files, this module also check the validity
of provided data.

.. note::
    To improve computational costs, the data is retrieved as numpy arrays.
"""

import numpy as np
import os

def extract_dsc_data_multiple_files(file_paths, delimiter=',', has_header=False, skip_lines=0):
    """
    Extract DSC data from multiple txt or csv files and perform data validation.

    Parameters
    ----------
    file_paths : list
        List of file paths to input txt or csv files containing DSC data.
    delimiter : str, optional
        Delimiter used in the input files. Default is ','.
    has_header : bool, optional
        Whether the input files have headers. Default is False.
    skip_lines : int, optional
        Number of lines to skip at the beginning of each file. Default is 0.

    Returns
    -------
    Tuple of concatenated numpy arrays
        (time, temperature, rate_of_reaction, extent_of_reaction)
    """
    try:
        concatenated_time = []
        concatenated_temperature = []
        concatenated_rate_of_reaction = []
        concatenated_extent_of_reaction = []
        
        for file_path in file_paths:
            # Load data from the file
            if has_header:
                data = np.loadtxt(file_path, delimiter=delimiter, skiprows=1 + skip_lines)  # Skip the header and specified lines
            else:
                data = np.loadtxt(file_path, delimiter=delimiter, skiprows=skip_lines)
            
            # Separate columns from the data
            time = data[:, 0]
            temperature = data[:, 1]
            rate_of_reaction = data[:, 2]
            extent_of_reaction = data[:, 3]
            
            # Check if extent of reaction is within [0, 1] range
            initial_extent = extent_of_reaction[0]
            final_extent = extent_of_reaction[-1]
            
            # Integral of reaction rate should be equal to extent of reaction
            extent_of_reaction_recorded = extent_of_reaction[-1]-extent_of_reaction[0]
            
            if initial_extent < 0 or initial_extent > 1 or final_extent < 0 or final_extent > 1:
                print(f"Error in file {os.path.basename(file_path)}: Extent of reaction should be between 0 and 1. Initial extent: {initial_extent}, Final extent: {final_extent}")
            else:
                print(f"Info in file {os.path.basename(file_path)}:\n Initial extent: {initial_extent}, Final extent: {final_extent}")
            
            # Warn about issues with initial extent being zero
            if initial_extent == 0:
                print(f"Info: in file {os.path.basename(file_path)}: Initial extent being zero can lead to issues for some kinetic models.")
            
            # Check if extent of reaction is non-decreasing
            if not np.all(np.diff(extent_of_reaction) >= 0):
                print(f"Error in file {os.path.basename(file_path)}: Extent of reaction is not non-decreasing.")
            
            # Check temperature unit
            if temperature[0] < 173.15:
                print(f"Warning in file {os.path.basename(file_path)}: Starting temperature should be in Kelvin not Celsius.\n Make sure you're using the appropriate units.")
            
            # Calculate the integral of rate of reaction and compare with global extent
            integral_rate = np.trapz(rate_of_reaction, time)
            if not np.isclose(integral_rate, extent_of_reaction_recorded):
                print(f"Error in file {os.path.basename(file_path)}: Integral of rate of reaction is not equal to the final extent.")
            
            #Check if there's extent equal or greater than 1
            if np.any(extent_of_reaction >= 1):
                # Remove data after extent reaches 1
                complete_reaction_index = np.argmax(extent_of_reaction >= 1) + 1
            else:
                complete_reaction_index = len(extent_of_reaction)
            
            time = time[:complete_reaction_index]
            temperature = temperature[:complete_reaction_index]
            rate_of_reaction = rate_of_reaction[:complete_reaction_index]
            extent_of_reaction = extent_of_reaction[:complete_reaction_index]
            
            concatenated_time.extend(time)
            concatenated_temperature.extend(temperature)
            concatenated_rate_of_reaction.extend(rate_of_reaction)
            concatenated_extent_of_reaction.extend(extent_of_reaction)
        
        concatenated_time = np.array(concatenated_time)
        concatenated_temperature = np.array(concatenated_temperature)
        concatenated_rate_of_reaction = np.array(concatenated_rate_of_reaction)
        concatenated_extent_of_reaction = np.array(concatenated_extent_of_reaction)

        return concatenated_time, concatenated_temperature, concatenated_rate_of_reaction, concatenated_extent_of_reaction
    except Exception as e:
        print(f"Error in file {os.path.basename(file_path)}:{e}")
        return 0,0,0,0

def extract_dsc_data_single_file(file_path, delimiter=',', has_header=False, skip_lines=0):
    """
    Extract DSC data from multiple txt or csv files and perform data validation.

    Parameters
    ----------
    file_path : list
        File path to input txt or csv files containing DSC data.
    delimiter : str, optional
        Delimiter used in the input file. Default is ','.
    has_header : bool, optional
        Whether the input file has headers. Default is False.
    skip_lines : int, optional
        Number of lines to skip at the beginning of the file. Default is 0.

    Returns
    -------
    Tuple of numpy arrays
        (time, temperature, rate_of_reaction, extent_of_reaction)
    """
    # Load data from the file
    if has_header:
        data = np.loadtxt(file_path, delimiter=delimiter, skiprows=1 + skip_lines)  # Skip the header and specified lines
    else:
        data = np.loadtxt(file_path, delimiter=delimiter, skiprows=skip_lines)
    
    # Separate columns from the data
    time = data[:, 0]
    temperature = data[:, 1]
    rate_of_reaction = data[:, 2]
    extent_of_reaction = data[:, 3]
    
    
    #Check if there's extent equal or greater than 1
    if np.any(extent_of_reaction >= 1):
        # Remove data after extent reaches 1
        complete_reaction_index = np.argmax(extent_of_reaction >= 1) + 1
    else:
        complete_reaction_index = len(extent_of_reaction)
        
    time = time[:complete_reaction_index]
    temperature = temperature[:complete_reaction_index]
    rate_of_reaction = rate_of_reaction[:complete_reaction_index]
    extent_of_reaction = extent_of_reaction[:complete_reaction_index]

    
    return time, temperature, rate_of_reaction, extent_of_reaction

if __name__=="__main__":
    print("You've run the data extraction module.")
    
    
    