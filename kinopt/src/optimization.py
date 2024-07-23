# -*- coding: utf-8 -*-
"""
This module defines functions for optimizing kinetic models and calculating residuals.

Author: alan.tabore
"""

import numpy as np


def model(x, rate_law, experimental_args_for_rate, number_of_parameters_to_optimize_for_rate, vitrification_law, experimental_args_for_vitrification, number_of_parameters_to_optimize_for_vitrification, coupling_law, experimental_args_for_coupling, tg_law, experimental_args_for_tg, tg_args):
    """
    Calculate the overall reaction rate considering both reaction and vitrification.

    Parameters
    ----------
    x : array-like
        Parameter values for the kinetic model.
    rate_law : function
        The rate law function for the reaction.
    experimental_args_for_rate : tuple
        Experimental arguments for the rate law function.
    number_of_parameters_to_optimize_for_rate : int
        Number of parameters to optimize for the rate law.
    vitrification_law : function
        The vitrification law function.
    experimental_args_for_vitrification : tuple
        Experimental arguments for the vitrification law function.
    number_of_parameters_to_optimize_for_vitrification : int
        Number of parameters to optimize for the vitrification law.
    coupling_law : function
        The coupling law for reaction and vitrification.
    experimental_args_for_coupling : tuple
        Experimental arguments for the coupling law function.
    tg_law : function
        The glass transition temperature (tg) law function.
    experimental_args_for_tg : tuple
        Experimental arguments for the tg law function.
    tg_args : tuple
        Additional arguments for the tg law function.
    

    Returns
    -------
    global_rate : float
        Overall global rate considering both reaction and vitrification.
    """
    if rate_law:
        rate_of_reaction = rate_law(*experimental_args_for_rate, *x[:number_of_parameters_to_optimize_for_rate])
        if not coupling_law:
            return rate_of_reaction
    if tg_law:
        tg = tg_law(*experimental_args_for_tg, *tg_args)
    if vitrification_law:
        rate_of_vitrification = vitrification_law(*experimental_args_for_vitrification, tg, *x[number_of_parameters_to_optimize_for_rate:number_of_parameters_to_optimize_for_rate+number_of_parameters_to_optimize_for_vitrification])
        if not coupling_law:
            return rate_of_vitrification
    if coupling_law:
        global_rate = coupling_law(rate_of_reaction, rate_of_vitrification, experimental_args_for_coupling,*x[number_of_parameters_to_optimize_for_rate+number_of_parameters_to_optimize_for_vitrification:])
        return global_rate


def rss_standard(x, experimental_rate, rate_law, experimental_args_for_rate, number_of_parameters_to_optimize_for_rate, vitrification_law, experimental_args_for_vitrification, number_of_parameters_to_optimize_for_vitrification, coupling_law, experimental_args_for_coupling, tg_law, experimental_args_for_tg, tg_args):
    r"""
    Calculate the residual sum of squares (RSS).
    
    .. math:: RSS= \sum (y_{exp_{i}}-f(x_i))^2
    
    with :math:`y_{exp_{i}}` the i-th value of experimental rate and :math:`f(x_i)` the value of rate computed using the given kinetic model :math:`f` and the i-th parameter vector :math:`x_i`.
    
    Parameters
    ----------
    x : array-like
        Vector with parameter values to optimize for the kinetic model.
    experimental_rate : array-like
        Experimental reaction rate data.
    rate_law : function
        The rate law function for the reaction.
    experimental_args_for_rate : tuple
        Experimental arguments for the rate law function.
    number_of_parameters_to_optimize_for_rate : int
        Number of parameters to optimize for the rate law.
    vitrification_law : function
        The vitrification law function.
    experimental_args_for_vitrification : tuple
        Experimental arguments for the vitrification law function.
    tg_law : function
        The glass transition temperature (tg) law function.
    experimental_args_for_tg : tuple
        Experimental arguments for the tg law function.
    tg_args : tuple
        Additional arguments for the tg law function.
    coupling_law_for_reaction_and_vitrification : function
        The coupling law for reaction and vitrification.
    coupling_law_for_reaction_and_vitrification_args : tuple
        Additional arguments for the coupling law function.

    Returns
    -------
    rss : float
        Residual sum of squares (RSS).
    """
    # Calculate model rate using the defined model function
    model_rate = model(x, rate_law, experimental_args_for_rate, number_of_parameters_to_optimize_for_rate, vitrification_law, experimental_args_for_vitrification, number_of_parameters_to_optimize_for_vitrification, coupling_law, experimental_args_for_coupling, tg_law, experimental_args_for_tg, tg_args)
    # Calculate the difference between model rate and experimental rate
    dif = model_rate - experimental_rate
    # Calculate the RSS by summing the squared differences
    return np.dot(dif, dif)

def rss_mean(x, experimental_rate, rate_law, experimental_args_for_rate, number_of_parameters_to_optimize_for_rate, vitrification_law, experimental_args_for_vitrification, number_of_parameters_to_optimize_for_vitrification, coupling_law, experimental_args_for_coupling, tg_law, experimental_args_for_tg, tg_args):
    r"""
    Calculate the mean squared error.
    
    .. math:: \overline{RSS}= \frac{\sum (f(x_i)-y_{exp_{i}})^2}{n}
    
    with :math:`y_{exp_{i}}` the i-th value of experimental rate and :math:`f(x_i)` the value of rate computed using the given kinetic model :math:`f` and the i-th parameter vector :math:`x_i` and :math:`n` the number of points.
    
    
    Parameters
    ----------
    x : array-like
        Vector with parameter values to optimize for the kinetic model.
    experimental_rate : array-like
        Experimental reaction rate data.
    rate_law : function
        The rate law function for the reaction.
    experimental_args_for_rate : tuple
        Experimental arguments for the rate law function.
    number_of_parameters_to_optimize_for_rate : int
        Number of parameters to optimize for the rate law.
    vitrification_law : function
        The vitrification law function.
    experimental_args_for_vitrification : tuple
        Experimental arguments for the vitrification law function.
    tg_law : function
        The glass transition temperature (tg) law function.
    experimental_args_for_tg : tuple
        Experimental arguments for the tg law function.
    tg_args : tuple
        Additional arguments for the tg law function.
    coupling_law_for_reaction_and_vitrification : function
        The coupling law for reaction and vitrification.
    coupling_law_for_reaction_and_vitrification_args : tuple
        Additional arguments for the coupling law function.

    Returns
    -------
    rss : float
        Mean of residual sum of squares (RSS).
    """
    # Calculate model rate using the defined model function
    model_rate = model(x, rate_law, experimental_args_for_rate, number_of_parameters_to_optimize_for_rate, vitrification_law, experimental_args_for_vitrification, number_of_parameters_to_optimize_for_vitrification, coupling_law, experimental_args_for_coupling, tg_law, experimental_args_for_tg, tg_args)
    # Calculate the difference between model rate and experimental rate
    dif = model_rate - experimental_rate
    # Calculate the RSS by summing the squared differences
    return np.dot(dif, dif)/len(dif)

def rss_relative(x, experimental_rate, rate_law, experimental_args_for_rate, number_of_parameters_to_optimize_for_rate, vitrification_law, experimental_args_for_vitrification, number_of_parameters_to_optimize_for_vitrification, coupling_law, experimental_args_for_coupling, tg_law, experimental_args_for_tg, tg_args):
    r"""
    Compute the cost function based on the relaitve difference between the experimental rate and model rate.
    
    .. math:: Cost = \sum \left( \frac{f(x_i) - y_{\text{exp}_i}}{y_{\text{exp}_i}} \right)^2
    
    with :math:`y_{exp_{i}}` the i-th value of experimental rate and :math:`f(x_i)` the value of rate computed using the given kinetic model :math:`f` and the i-th parameter vector :math:`x_i`.
    
    Parameters
    ----------
    x : array-like
        Vector with parameter values to optimize for the kinetic model.
    experimental_rate : array-like
        Experimental reaction rate data.
    rate_law : function
        The rate law function for the reaction.
    experimental_args_for_rate : tuple
        Experimental arguments for the rate law function.
    number_of_parameters_to_optimize_for_rate : int
        Number of parameters to optimize for the rate law.
    vitrification_law : function
        The vitrification law function.
    experimental_args_for_vitrification : tuple
        Experimental arguments for the vitrification law function.
    tg_law : function
        The glass transition temperature (tg) law function.
    experimental_args_for_tg : tuple
        Experimental arguments for the tg law function.
    tg_args : tuple
        Additional arguments for the tg law function.
    coupling_law_for_reaction_and_vitrification : function
        The coupling law for reaction and vitrification.
    coupling_law_for_reaction_and_vitrification_args : tuple
        Additional arguments for the coupling law function.

    Returns
    -------
    rss : float
        Residual sum of squares (RSS).
    """
    # Calculate model rate using the defined model function
    model_rate = model(x, rate_law, experimental_args_for_rate, number_of_parameters_to_optimize_for_rate, vitrification_law, experimental_args_for_vitrification, number_of_parameters_to_optimize_for_vitrification, coupling_law, experimental_args_for_coupling, tg_law, experimental_args_for_tg, tg_args)
    # Calculate the difference between model rate and experimental rate
    dif = (model_rate - experimental_rate)/experimental_rate
    # Calculate the RSS by summing the squared differences
    return np.dot(dif, dif)

def rss_increase_of_small_extents_impact(x, experimental_rate, rate_law, experimental_args_for_rate, number_of_parameters_to_optimize_for_rate, vitrification_law, experimental_args_for_vitrification, number_of_parameters_to_optimize_for_vitrification, coupling_law, experimental_args_for_coupling, tg_law, experimental_args_for_tg, tg_args, extent, extent_limit, amplification_factor):
    r"""
    Calculate the modified residual sum of squares (RSS) with an impact increase for small extents.

    This function calculates the mean squared error with modifications based on the extent of the reaction.
    For extents smaller than a specified limit, the differences between the model rate and experimental rate
    are amplified by a given factor before computing the RSS.

    Parameters
    ----------
    x : array-like
        Vector with parameter values to optimize for the kinetic model.
    experimental_rate : array-like
        Experimental reaction rate data.
    rate_law : function
        The rate law function for the reaction.
    experimental_args_for_rate : tuple
        Experimental arguments for the rate law function.
    number_of_parameters_to_optimize_for_rate : int
        Number of parameters to optimize for the rate law.
    vitrification_law : function
        The vitrification law function.
    experimental_args_for_vitrification : tuple
        Experimental arguments for the vitrification law function.
    tg_law : function
        The glass transition temperature (tg) law function.
    experimental_args_for_tg : tuple
        Experimental arguments for the tg law function.
    tg_args : tuple
        Additional arguments for the tg law function.
    extent : array-like
        Extent of the reaction.
    extent_limit : float
        Threshold value for the extent. Extents smaller than this limit will have an impact amplification.
    amplification_factor : float
        Factor by which the differences are amplified for extents smaller than the limit.

    Returns
    -------
    modified_rss : float
        Modified mean of residual sum of squares (RSS).
        
    Notes
    -----
    The modified RSS is calculated as follows:

    .. math::
        \overline{RSS_{mod}} = \frac{\sum \left(\left(A*\left(y_{exp_{i}}(\alpha<\alpha_{lim})-f(x_i,\alpha<\alpha_{lim})\right)\right)^2\right)+\sum \left(\left(y_{exp_{i}}(\alpha\ge\alpha_{lim})-f(x_i,\alpha\ge\alpha_{lim})\right)^2\right)}{n}

    where :math:`A` is the amplification factor, :math:`y_{exp_{i}}(\alpha<\alpha_{lim})` and :math:`y_{exp_{i}}(\alpha\ge\alpha_{lim})` are the experimental rates for extents smaller and larger than or equal to the limit respectively,
    :math:`f(x_i,\alpha<\alpha_{lim})` is the model rate for extents smaller than the limit, :math:`f(x_i,\alpha\ge\alpha_{lim})` is the model rate for extents larger than or equal to the limit, and :math:`n` is the number of points.
    """
    # Calculate model rate using the defined model function
    model_rate = model(x, rate_law, experimental_args_for_rate, number_of_parameters_to_optimize_for_rate, vitrification_law, experimental_args_for_vitrification, number_of_parameters_to_optimize_for_vitrification, coupling_law, experimental_args_for_coupling, tg_law, experimental_args_for_tg, tg_args)
    
    # Calculate the difference between model rate and experimental rate
    dif = model_rate - experimental_rate
    
    # Modify the differences based on the extent limit
    modified_dif = np.where(extent < extent_limit, dif * amplification_factor, dif)
    
    # Calculate the modified RSS by summing the squared differences
    return np.dot(modified_dif, modified_dif)/len(modified_dif)

def rss_increase_of_small_rates_impact_with_zones(x, experimental_rate, rate_law, experimental_args_for_rate, number_of_parameters_to_optimize_for_rate, vitrification_law, experimental_args_for_vitrification, number_of_parameters_to_optimize_for_vitrification, coupling_law, experimental_args_for_coupling, tg_law, experimental_args_for_tg, tg_args, fraction_to_amplify, amplification_factor):
    r"""
    Calculate the modified residual sum of squares (RSS) with an impact increase for small rates in specific zones.
    
    This function calculates the mean squared error with modifications based on the experimental rate.
    For zones where the experimental rate is small compared to the maximum experimental rate,
    the differences between the model rate and experimental rate are amplified by a given factor before computing the RSS.
    
    Parameters
    ----------
    x : array-like
        Vector with parameter values to optimize for the kinetic model.
    experimental_rate : array-like
        Experimental reaction rate data.
    rate_law : function
        The rate law function for the reaction.
    experimental_args_for_rate : tuple
        Experimental arguments for the rate law function.
    number_of_parameters_to_optimize_for_rate : int
        Number of parameters to optimize for the rate law.
    vitrification_law : function
        The vitrification law function.
    experimental_args_for_vitrification : tuple
        Experimental arguments for the vitrification law function.
    tg_law : function
        The glass transition temperature (tg) law function.
    experimental_args_for_tg : tuple
        Experimental arguments for the tg law function.
    tg_args : tuple
        Additional arguments for the tg law function.
    fraction_to_amplify : float
        Fraction of the maximum experimental rate to consider as the threshold for amplification.
    amplification_factor : float
        Factor by which the differences are amplified for rates below the threshold.
    
    Returns
    -------
    modified_rss : float
        Modified mean of residual sum of squares (RSS).
    
    Notes
    -----
    The modified RSS is calculated as follows:

    .. math::
        \overline{RSS_{mod}} = \frac{\left(\sum \left(\text{{modified_dif}}^2\right)\right)}{n}

    where :math:`y_{exp_{i}}` is the experimental rate and :math:`f(x_i)` is the model rate,
    and :math:`n` is the number of points.

    The difference :math:`\text{{dif}}_i` is modified as follows:
    
    .. math::
        \text{{modified_dif}}_i = 
        \begin{cases}
        \left(y_{exp_{i}}-f(x_i)\right) \times A, & \text{if } y_i < \frac{{\max(y)}}{p} \\
        y_{exp_{i}}-f(x_i), & \text{otherwise}
        \end{cases}
    """
    # Calculate the maximum experimental rate
    max_exp_rate = np.full(experimental_rate.shape, np.max(experimental_rate))
    
    # Calculate the model rate using provided laws and arguments
    model_rate = model(x, rate_law, experimental_args_for_rate, number_of_parameters_to_optimize_for_rate, vitrification_law, experimental_args_for_vitrification, number_of_parameters_to_optimize_for_vitrification, coupling_law, experimental_args_for_coupling, tg_law, experimental_args_for_tg, tg_args)
    
    # Calculate the difference between model rate and experimental rate
    dif = model_rate - experimental_rate
    
    # Modify the difference in certain zones where experimental rate is small
    modified_dif = np.where(experimental_rate < max_exp_rate/fraction_to_amplify, dif*amplification_factor, dif)
    
    return np.dot(modified_dif, modified_dif)/len(modified_dif)






if __name__ == "__main__":
    print("You've run the optimization module.")