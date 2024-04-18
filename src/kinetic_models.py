# -*- coding: utf-8 -*-
"""
The kinetic models module provides functions for simulating chemical reaction kinetics using various kinetic models.
To create the global kinetic of reaction, multiple elements are available:

* rate model : describing the rate of purely chemical reaction
* vitrification model : describing a rate depending on vitrification and diffusion phenomenon
* coupling law : describing the relation between rate model and vitrification model
* tg law : describing the evolution of glass transition temperature with respect to extent

"""

import numpy as np
import scipy


def arrhenius_rate_constant(T,A,Ea):
    r"""
    Compute the value of rate constant with the Arrhenius equation.

    Parameters
    ----------
    T : Float
        Temperature of reaction.
    A : Float
        Pre-exponential factor.
    Ea : Float
        Activation energy.

    Returns
    -------
    k : Float
        Rate constant for the Arrhenius equation.
    
    Notes
    -----
     The Arrhenius rate constant is given by:
    
     .. math:: k = A e^{ \left( \frac{-E_a}{RT} \right)}
    
    """
    return A*np.exp(-Ea/(8.31446261815324*T))


def rate_for_nth_order(extent,T,A1,E1,n):
    r"""
    Compute the value of the rate of reaction for a nth order reaction.
    
    .. math:: \dfrac{ d\alpha }{dt} = A e^{ \left( \dfrac{-E_a}{RT} \right) } (1-\alpha)^n 

    Parameters
    ----------
    extent : 1-D array
        Extent of reaction.
    T : 1-D array
        Temperature of reaction.
    A : Float
        Pre-exponential factor of the reaction.
    Ea : Float
        Activation energy of the reaction.
    n : Float
        Order of reaction.

    Returns
    -------
    rate : 1-D array
        Rate of reaction for a nth order reaction.

    """
    return arrhenius_rate_constant(T,A1,E1)*(1-extent)**n



def rate_for_kamal(extent,T,A1,E1,A2,E2,m,n):
    r"""
    Compute the value of the rate of reaction for a Kamal equation.
    
    Parameters
    ----------
     extent : ndarray
         Extent of reaction.
     T : ndarray
         Temperature of reaction.
     A1 : float
         Pre-exponential factor of the regular reaction.
     E1 : float
         Activation energy of the regular reaction.
     A2 : float
         Pre-exponential factor of the autocatalyzed reaction.
     E2 : float
         Activation energy of the autocatalyzed reaction.
     m : float
         Order of reaction for the autocatalyzed reaction.
     n : float
         Order of reaction for the regular reaction.
    
    Returns
    -------
    rate : ndarray
        Rate of reaction for a Kamal equation.
    
    
    Notes
    -----
     The Kamal equation is given by:
    
     .. math:: \frac{d\alpha}{dt} = \left( A_1 e^{ \left( \frac{-E_1}{RT} \right)}  +  A_2 e^{ \left( \frac{-E_2}{RT} \right) } \alpha^m \right) (1-\alpha)^n
     
    References
    ----------
    [1]   G. J. Tsamasphyros, Th. K. Papathanassiou, et S. I. Markolefas, « Some Analytical Solutions of the Kamal Equation for Isothermal Curing With Applications to Composite Patch Repair », Journal of Engineering Materials and Technology, vol. 131, no 1, Dec. 2008, doi: 10.1115/1.3026550.
     
    
    
    Examples
    --------
    >>>  import time as t
    >>>  import numpy as np
    >>>  import matplotlib.pyplot as plt
    ...
    >>>  number_of_points = 10000
    >>>  time_points = np.linspace(0, 1800, number_of_points)  # 30 minutes
    >>>  temperatures = [
        np.linspace(293, 443, number_of_points),  # 5°C/min
        np.linspace(293, 593, number_of_points),  # 10°C/min
        np.linspace(293, 743, number_of_points),  # 15°C/min
        np.linspace(293, 1093, number_of_points)  # 20°C/min
    ]
    >>>  conversions = []
    >>>  rates = []
    ...
    >>>  fig, ax1 = plt.subplots(num=1)
    >>>  ax1_bis = ax1.twinx()
    >>>  ax1.set_xlabel("time")
    >>>  ax1.set_ylabel("conversion")
    >>>  ax1_bis.set_ylabel("rate")
    ...
    >>>  for i, temperature in enumerate(temperatures):
    >>>      t0 = t.time()
    >>>      extent, rate = compute_extent_and_rate(time_points, temperature, rate_for_kamal, (1.666e8, 80000, 1.666e13, 120000, 1, 0.7))
    >>>      t1 = t.time()
    >>>      execution_time = t1 - t0
    >>>      print("Time:", execution_time, "s")
    >>>      conversions.append(extent)
    >>>      rates.append(rate)
    >>>      ax1.plot(time_points, extent, label=f"conversion for a heating rate of {(i+1)*5}°/min", linestyle='dotted')
    >>>      ax1_bis.plot(time_points, rate, label=f"rate for a heating rate of {(i+1)*5}°/min")
    >>>      ax1.legend()
    >>>      ax1_bis.legend()
    ...
    >>>  plt.show()
    
    """
    return (arrhenius_rate_constant(T,A1,E1) + (arrhenius_rate_constant(T,A2,E2) * extent**m)) * (1 - extent)**n

def rate_for_autocatalytic(extent,T,A,Ea,m,n):
    r"""
    Compute the rate of reaction for an autocatalytic reaction.
    
    Parameters
    ----------
    extent : ndarray
        Extent of reaction.
    T : ndarray
        Temperature of reaction.
    A : float
        Pre-exponential factor of the reaction.
    Ea : float
        Activation energy of the reaction.
    m : float
        Order of reaction for the autocatalyzed reaction.
    n : float
        Order of reaction for the regular reaction.
    
    Returns
    -------
    rate : ndarray
        Rate of reaction for an autocatalytic equation.     
        
    Notes
    -----
     The rate for an autocatalytic reaction is given by:
    
     .. math:: \frac{d\alpha}{dt} =  A e^{ \left( \frac{-E_a}{RT} \right)} \alpha^m (1-\alpha)^n
     
    References
    ----------
    [1] M. R. Keenan, « Autocatalytic cure kinetics from DSC measurements: Zero initial cure rate », J. Appl. Polym. Sci., vol. 33, nᵒ 5, p. 1725‑1734, avr. 1987, doi: 10.1002/app.1987.070330525.

    """
    if np.any(extent) <= 0:
        raise ValueError("Be careful, for an autocatalytic model the extent can't be inferior or equal to 0 !!! \n It would result in a rate of reaction equal to 0 and no reaction would occur.")
    return arrhenius_rate_constant(T,A,Ea) * extent**m * (1 - extent)**n

    
def vitrification_WLF_rate(T,Tg,Ad,C1,C2):
    r"""
    Compute the vitrification term for a WLF-like model.
    
    The vitrification term is given by the WLF model:
    
    .. math:: k_v = A_d e^{ \left( \frac{C_1(T - T_g(\alpha))}{C_2 + |T - T_g(\alpha)|} \right) }
    
    where:
        * :math:`T` is the temperature of the reaction (in Kelvin). 
        * :math:`A_d` is the pre-exponential factor of the vitrification term
        * :math:`C_1` is Constant 1 of the WLF model
        * :math:`C_2` is Constant 2 of the WLF model
        * :math:`T_g` is the glass transition temperature (in Kelvin).
        
        
    
    Usually, the glass transition temperature is determined by using the DiBenedetto equation.
    
    Parameters
    ----------
    T : array-like
        Temperature of the reaction (in Kelvin)
    Ad : float
        Pre-exponential factor of the vitrification term
    C1 : float
        Constant 1 of the WLF model
    C2 : float
        Constant 2 of the WLF model
    Tg : float
        Glass transition temperature (in Kelvin)
    
    Returns
    -------
    rate : array-like
        Rate of the reaction
    
    References
    ----------
    [1] G. Wisanrakkit et J. K. Gillham, "The glass transition temperature (Tg) as an index of chemical
    conversion for a high-Tg amine/epoxy system: Chemical and diffusion-controlled reaction kinetics",
    Journal of Applied Polymer Science, vol. 41, no. 11-12, p. 2885-2929, 1990, doi: 10.1002/app.1990.070411129.
    """
    #Check if temperature of reaction is above glass transition temperature
    #If so, the vitrification term is computed, else the rate is equal to 0
    return Ad*np.exp( (C1*(T-Tg)) / (C2+abs(T-Tg)))

def vitrification_WLF_rate_no_reaction_below_Tg(T,Tg,Ad,C1,C2):
    r"""
    Compute the vitrification term for a WLF-like model when the reaction temperature is above Tg.
    The vitrification term is equal to 0 when below Tg.
    
    .. math:: k_v = A_d e^{ \left( \dfrac{C_1(T-T_g(\alpha))}{C_2+ |T-T_g(\alpha)|} \right) }

    Usually the glass transition temperature is determined by using the DiBenedetto equation
    See: G. Wisanrakkit et J. K. Gillham, « The glass transition temperature (Tg) as an index of chemical conversion for a high-Tg amine/epoxy system: Chemical and diffusion-controlled reaction kinetics », Journal of Applied Polymer Science, vol. 41, nᵒ 11‑12, p. 2885‑2929, 1990, doi: 10.1002/app.1990.070411129.

    Parameters
    ----------
    T : Array-like
       Temperature of reaction (in Kelvin)
    Ad : Float
        Pre-exponential factor of the vitrification term
    C1 : Float
        Constant 1 of WLF model
    C2 : Float
        Constant 2 of WLF model
    Tg : Float
        Glass transition temperature (in Kelvin)

    Returns
    -------
    Rate : Array-like
        Rate of reaction
        
    References
    ----------
    [1] G. Wisanrakkit et J. K. Gillham, "The glass transition temperature (Tg) as an index of chemical
    conversion for a high-Tg amine/epoxy system: Chemical and diffusion-controlled reaction kinetics",
    Journal of Applied Polymer Science, vol. 41, no. 11-12, p. 2885-2929, 1990, doi: 10.1002/app.1990.070411129.
    """
    #Check if temperature of reaction is above glass transition temperature
    #If so, the vitrification term is computed, else the rate is equal to 0
    return np.where( T>Tg, Ad*np.exp( (C1*(T-Tg)) / (C2+abs(T-Tg))), 0)


def tg_diBennedetto(extent,Tg_0,Tg_inf,coeff):
    r"""
    Compute the glass transition temperature using the DiBennedetto equation.
    
    Parameters
    ----------
    alpha : array-like
        conversion or extent of reaction
    Tg_0 : Float
        glass transition temperature of unreacted material
    Tg_inf : Float
        glass transition temperature of fully reacted material
    coeff : Float
        ratio of the changes in isobaric heat capacities at Tg of the fully reacted material and of the initial unreacted material

    Returns
    -------
    Tg : array-like
        Glass transition temperature
        
    Notes
    -----
    The DiBennedetto equation is given by:
        
    .. math::
        Tg = Tg_{0} +  \dfrac{ (Tg_{\infty}-Tg_{0}). \lambda .\alpha}{1-(1-\lambda)\alpha} \\
        with: \\
        Tg_{0}: \textrm{The glass transition temperature of unreacted material} \\
        Tg_{\infty}: \textrm{The glass transition temperature of completely cured material} \\
        \lambda : \dfrac{\Delta C_{p_{\infty}}}{\Delta C_{p_{0}}} \textrm{the ratio of the changes in isobaric heat capacities at} \\
        \textrm{Tg of the fully reacted material and of the initial unreacted material}\\

    """
    return Tg_0 + (Tg_inf - Tg_0)*((coeff*extent)/(1-(1-coeff)*extent))

def coupling_harmonic_mean(kc,kv,experimental_parameters=None):
    r"""
    Return the harmonic mean of a chemical rate and vitrification rate.
    
    .. math::
        \dfrac{ d\alpha }{dt} = \dfrac{1}{\dfrac{1}{k_c } + \dfrac{1}{k_v}} 


    Parameters
    ----------
    kc : 1-D array
        Rate of chemical reaction
    kv : 1-D array
        Vitrification term
    experimental_parameters : NoneType
        NoneType argument to stick with guideline of function creation    


    Returns
    -------
    Rate : 1-D array
        Rate of reaction
        
    References
    ----------
    [1]   G. Wisanrakkit et J. K. Gillham, « The glass transition temperature (Tg) as an index of chemical conversion for a high-Tg amine/epoxy system: Chemical and diffusion-controlled reaction kinetics », Journal of Applied Polymer Science, vol. 41, nᵒ 11‑12, p. 2885‑2929, 1990, doi: 10.1002/app.1990.070411129.
     
    """    
    #If kc or kv are equal to 0, then it returns 0
    rate = 1 / ((1/kc)+(1/kv))
    
    return rate

def coupling_product(kc,kv,experimental_parameters=None):
    r"""
    Return the product of a chemical rate and vitrification rate.
    
    .. math::
        \dfrac{ d\alpha }{dt} = k_c * k_v

    Parameters
    ----------
    kc : 1-D array
        Rate of chemical reaction
    kv : 1-D array
        Vitrification term
    experimental_parameters : NoneType
        NoneType argument to stick with guideline of function creation    


    Returns
    -------
    Rate : 1-D array
        Rate of reaction
    """
    #If kc or kv are equal to 0, then it returns 0
    rate = 1 / ((1/kc)+(1/kv))
    
    return rate


def jac_for_rate_for_kamal(extent, T, A1, E1, A2, E2, m, n):
    r"""
    Compute the Jacobian vector for the Kamal equation.

    Parameters
    ----------
    extent : float
        Extent of the reaction.
    T : float
        Temperature in Kelvin.
    A1 : float
        Pre-exponential factor for reaction 1.
    E1 : float
        Activation energy for reaction 1 in J/mol.
    A2 : float
        Pre-exponential factor for reaction 2.
    E2 : float
        Activation energy for reaction 2 in J/mol.
    m : int
        Power term for reaction 2.
    n : int
        Power term for both reactions.

    Returns
    -------
    jac : ndarray
        Jacobian vector of shape (6,) representing the first derivatives
        of the rate expression with respect to (A1, E1, A2, E2, m, n).

    Notes
    -----
    This function computes the Jacobian vector for a rate expression
    based on the extent of the reaction, temperature, pre-exponential
    factors, activation energies, and power terms for two reactions.
    The Jacobian vector represents the first derivatives of the rate
    expression with respect to the extent of the reaction.

    The Jacobian vector J is given by:

    .. math::
        J = \begin{bmatrix}
        (1 - x)^n e^{-\frac{E_1}{RT}} \\
        -\frac{A_1 (1 - x)^n e^{-\frac{E_1}{RT}}}{RT} \\
        x^m (1 - x)^n e^{-\frac{E_2}{RT}} \\
        -\frac{A_2 x^m (1 - x)^n e^{-\frac{E_2}{RT}}}{RT} \\
        A_2 x^m (1 - x)^n \log(x) e^{-\frac{E_2}{RT}} \\
        (1 - x)^n \log(1 - x) (A_2 x^m e^{-\frac{E_2}{RT}} + A_1 e^{-\frac{E_1}{RT}})
        \end{bmatrix}
    """
    R = 8.31446261815324  # Ideal gas constant
    
    exp_E1_RT = np.exp(-E1 / (R * T))
    exp_E2_RT = np.exp(-E2 / (R * T))
    log_extent = np.log(extent)
    log_1_minus_extent = np.log(1 - extent)
    extent_to_m = extent ** m
    one_minus_extent_to_n = (1 - extent) ** n
    
    jac = np.zeros(6)
    
    jac[0] = one_minus_extent_to_n * exp_E1_RT
    jac[1] = -(A1 * one_minus_extent_to_n * exp_E1_RT) / (R * T)
    jac[2] = extent_to_m * one_minus_extent_to_n * exp_E2_RT
    jac[3] = -(A2 * extent_to_m * one_minus_extent_to_n * exp_E2_RT) / (R * T)
    jac[4] = A2 * extent_to_m * one_minus_extent_to_n * log_extent * exp_E2_RT
    jac[5] = one_minus_extent_to_n * log_1_minus_extent * (A2 * extent_to_m * exp_E2_RT + A1 * exp_E1_RT)
    
    return jac


def hess_for_rate_for_kamal(extent, T, A1, E1, A2, E2, m, n):
    r"""
    Compute the Hessian matrix for the Kamal equation.
    
    Parameters
    ----------
    extent : float
        Extent of the reaction.
    T : float
        Temperature in Kelvin.
    A1 : float
        Pre-exponential factor for reaction 1.
    E1 : float
        Activation energy for reaction 1 in J/mol.
    A2 : float
        Pre-exponential factor for reaction 2.
    E2 : float
        Activation energy for reaction 2 in J/mol.
    m : int
        Power term for reaction 2.
    n : int
        Power term for both reactions.
    
    Returns
    -------
    hessian : ndarray
        Hessian matrix of shape (6, 6) representing the second derivatives
        of the rate expression with respect to (A1, E1, A2, E2, m, n).
    
    Notes
    -----
    The Hessian matrix H is given by:
        
    .. math::
        H = \begin{bmatrix}
        0 & -\frac{(1 - x)^n e^{-E_1/(RT)}}{RT} & 0 & 0 & 0 & (1 - x)^n \log(1 - x) e^{-E_1/(RT)} \\
        -\frac{(1 - x)^n e^{-E_1/(RT)}}{RT} & \frac{A_1 (1 - x)^n e^{-E_1/(RT)}}{(R^2 T^2)} & 0 & 0 & 0 & -\frac{A_1 (1 - x)^n \log(1 - x) e^{-E_1/(RT)}}{RT} \\
        0 & 0 & 0 & -\frac{x^m (1 - x)^n e^{-E_2/(RT)}}{RT} & x^m (1 - x)^n \log(x) e^{-E_2/(RT)} & x^m (1 - x)^n \log(1 - x) e^{-E_2/(RT)} \\
        0 & 0 & -\frac{x^m (1 - x)^n e^{-E_2/(RT)}}{RT} & \frac{A_2 x^m (1 - x)^n e^{-E_2/(RT)}}{(R^2 T^2)} & -\frac{A_2 x^m (1 - x)^n \log(x) e^{-E_2/(RT)}}{RT} & -\frac{A_2 x^m (1 - x)^n \log(1 - x) e^{-E_2/(RT)}}{RT} \\
        0 & 0 & x^m (1 - x)^n \log(x) e^{-E_2/(RT)} & -\frac{A_2 x^m (1 - x)^n \log(x) e^{-E_2/(RT)}}{RT} & A_2 x^m (1 - x)^n \log^2(x) e^{-E_2/(RT)} & A_2 x^m (1 - x)^n \log(1 - x) \log(x) e^{-E_2/(RT)} \\
        (1 - x)^n \log(1 - x) e^{-E_1/(RT)} & -\frac{A_1 (1 - x)^n \log(1 - x) e^{-E_1/(RT)}}{RT} & x^m (1 - x)^n \log(1 - x) e^{-E_2/(RT)} & -\frac{A_2 x^m (1 - x)^n \log(1 - x) e^{-E_2/(RT)}}{RT} & A_2 x^m (1 - x)^n \log(1 - x) \log(x) e^{-E_2/(RT)} & (1 - x)^n \log^2(1 - x) (A_2 x^m e^{-E_2/(RT)} + A_1 e^{-E_1/(RT)})
        \end{bmatrix}
        
    """
    R = 8.31446261815324  # Ideal gas constant
    
    exp_E1_RT = np.exp(-E1 / (R * T))
    exp_E2_RT = np.exp(-E2 / (R * T))
    log_1_minus_x = np.log(1 - extent)
    log_x = np.log(extent)
    x_to_m = extent ** m
    one_minus_x_to_n = (1 - extent) ** n
    
    hessian = np.zeros((6, 6))
    
    hessian[0, 1] = -one_minus_x_to_n * exp_E1_RT / (R * T)
    hessian[0, 5] = one_minus_x_to_n * log_1_minus_x * exp_E1_RT
    
    hessian[1, 0] = hessian[0, 1]
    hessian[1, 1] = A1 * one_minus_x_to_n * exp_E1_RT / (R**2 * T**2)
    hessian[1, 5] = -A1 * one_minus_x_to_n * log_1_minus_x * exp_E1_RT / (R * T)
    
    hessian[2, 3] = -x_to_m * one_minus_x_to_n * exp_E2_RT / (R * T)
    hessian[2, 4] = x_to_m * one_minus_x_to_n * log_x * exp_E2_RT
    hessian[2, 5] = x_to_m * one_minus_x_to_n * log_1_minus_x * exp_E2_RT
    
    hessian[3, 3] = A2 * x_to_m * one_minus_x_to_n * exp_E2_RT / (R**2 * T**2)
    hessian[3, 4] = -A2 * x_to_m * one_minus_x_to_n * log_x * exp_E2_RT / (R * T)
    hessian[3, 5] = -A2 * x_to_m * one_minus_x_to_n * log_1_minus_x * exp_E2_RT / (R * T)
    
    hessian[4, 2] = hessian[2, 4]
    hessian[4, 3] = hessian[3, 4]
    hessian[4, 4] = A2 * x_to_m * one_minus_x_to_n * log_x**2 * exp_E2_RT
    hessian[4, 5] = A2 * x_to_m * one_minus_x_to_n * log_1_minus_x * log_x * exp_E2_RT
    
    hessian[5, 0] = hessian[0, 5]
    hessian[5, 1] = hessian[1, 5]
    hessian[5, 2] = hessian[2, 5]
    hessian[5, 3] = hessian[3, 5]
    hessian[5, 4] = hessian[4, 5]
    hessian[5, 5] = one_minus_x_to_n * log_1_minus_x**2 * (A2 * x_to_m * exp_E2_RT + A1 * exp_E1_RT)
    
    return hessian



def compute_extent_and_rate(time, temperature, rate_law=None, rate_law_args=None, vitrification_law=None, vitrification_law_args=None, tg_law=None, tg_law_args=None, coupling_law=None, coupling_law_args=None, initial_extent=0):
    """
    Compute the evolution of extent and rate during a reaction, with or without vitrification.

    Parameters
    ----------
    time : array-like
        List or array containing the times during the reaction.
    temperature : array-like
        List or array containing the temperatures during the reaction.
    rate_law : function
        The rate law function that calculates the rate of reaction.
    rate_law_args : tuple
        Additional arguments to be passed to the rate law function.
    vitrification_law : function, optional
        The vitrification law function that calculates the vitrification term.
    vitrification_args : tuple, optional
        Additional arguments to be passed to the vitrification law function.
    tg_law : function, optional
        The glass transition temperature law function that calculates the Tg.
    tg_law_args : tuple, optional
        Additional arguments to be passed to the Tg law function.
    coupling_law : function, optional
        Law used to mix the rate of chemical reaction and rate of vitrification.
    coupling_law_args : tuple, optional
        Additional arguments to be passed to the coupling law function.
    initial_extent : float, optional
        The initial extent of reaction. Default is 0. It must be positive and inferior to 1.

    Returns
    -------
    extent : ndarray
        Evolution of extent during the reaction.
    global_rate : ndarray
        Evolution of the global rate of reaction.
    chemical_rate : ndarray
        Evolution of the chemical rate of reaction.
    vitrification_term : ndarray, optional
        Evolution of the vitrification rate of reaction (if vitrification parameters are provided).
    tg : ndarray, optional
        Evolution of the Tg (if Tg parameters are provided).
    """
    # Importation of a module to display a progress bar for the finite difference
    from tqdm import tqdm
    
    if coupling_law:
        if not rate_law:
            raise NameError("Please, provide the rate law to use for computation or indicate 'None' for the coupling law")
        if not vitrification_law:
            raise NameError("Please, provide the vitrification law to use for computation or indicate 'None' for the coupling law")
    # The number of iterations for the finite difference is equal to the number of time points
    n = len(time)
    
    # Creation and initialization of numpy arrays
    extent = np.zeros(n)
    extent[0] = initial_extent
    
    if rate_law:
        chemical_rate = np.zeros(n)
        chemical_rate[0] = rate_law(extent[0], temperature[0], *rate_law_args)
    if tg_law:
        tg = np.zeros(n)
        tg[0] = tg_law(extent[0],*tg_law_args)
    if vitrification_law:
        vitrification_term = np.zeros(n)
        vitrification_term[0] = vitrification_law(temperature[0],tg[0],*vitrification_law_args)
    if coupling_law:
        global_rate = np.zeros(n)    
        global_rate[0] = coupling_law(chemical_rate[0], vitrification_term[0], *coupling_law_args) if vitrification_law is not None else chemical_rate[0]


    for i in tqdm(range(n - 1), desc="Progress"):
        dt = time[i + 1] - time[i]
        
        if coupling_law:
            extent_for_next_step = extent[i] + global_rate[i] * dt  # Compute extent for the next step
        elif vitrification_law:
            extent_for_next_step = extent[i] + vitrification_term[i] * dt
        else:
            extent_for_next_step = extent[i] + chemical_rate[i] * dt
            
        
        if extent_for_next_step > 1:
            extent[i + 1:] = 1
            if coupling_law: 
                global_rate[i + 1:] = 0
            if rate_law:
                chemical_rate[i + 1:] = 0
            if tg_law:
                tg[i + 1:] = 0
            if vitrification_law:
                vitrification_term[i + 1:] = 0
            
            break

        else:
            extent[i + 1] = extent_for_next_step  # Update extent for the next step
            if rate_law:
                chemical_rate[i + 1] = rate_law(extent[i + 1], temperature[i + 1], *rate_law_args)
            if tg_law:
                tg[i + 1] = tg_law(extent[i + 1], *tg_law_args)
            if vitrification_law:
                vitrification_term[i + 1] = vitrification_law(temperature[i + 1], tg[i + 1], *vitrification_law_args)
            if coupling_law:
                global_rate[i + 1] = coupling_law(chemical_rate[i + 1], vitrification_term[i + 1], *coupling_law_args)

        
    # Return appropriate results based on the provided parameters
    if coupling_law:
        if tg_law:
            return extent, global_rate, chemical_rate, vitrification_term, tg
        else:
            return extent, global_rate, chemical_rate, vitrification_term, None
        
    if vitrification_law:
        if tg_law:
            return extent, vitrification_term, None, vitrification_term, tg
        else:
            return extent, vitrification_term, None, vitrification_term, None
        
    if rate_law:
        if tg_law:
            return extent, chemical_rate, chemical_rate, None, tg
        else:
            return extent, chemical_rate, chemical_rate, None, None
    else:
        return AttributeError("No law was given for calculations.")




def compute_extent_and_rate_using_scipy(t0, tf, temperature_program, rate_law, rate_law_args, vitrification_law=None, vitrification_args=None, tg_law=None, tg_law_args=None, coupling_law=None, coupling_law_args=None, initial_extent=0):
    """
    Compute extent and rate using scipy's solve_ivp.

    Parameters
    ----------
    t0 : float
        Initial time.
    tf : float
        Final time.
    temperature_program : callable
        A function that takes time as input and returns temperature.
    rate_law : callable
        Rate law function.
    rate_law_args : tuple
        Arguments for the rate law function.
    vitrification_law : callable
        Vitrification law function.
    vitrification_args : tuple
        Arguments for the vitrification law function.
    tg_law : callable
        Tg law function.
    tg_law_args : tuple
        Arguments for the Tg law function.
    coupling_law : callable
        Coupling law function.
    coupling_law_args : tuple
        Arguments for the coupling law function.
    initial_extent : float, optional
        Initial extent. Default is 0.

    Returns
    -------
    scipy.integrate.OdeResult
        Solution object from solve_ivp.
    """
    if (vitrification_law is not None) and (tg_law is None):
        raise ValueError("Please make sure to indicate a tg law since you have selected a vitrification law.")
    if (vitrification_law is not None) and (coupling_law is None):
        raise ValueError("Please make sure to indicate a tg law since you have selected a vitrification law.")
    if (coupling_law is not None) and (vitrification_law is None):
        raise ValueError("Please make sure to indicate a tg law since you have selected a vitrification law.")
    if (coupling_law is not None) and (tg_law is None):
        raise ValueError("Please make sure to indicate a tg law since you have selected a vitrification law.")
    if (tg_law is not None) and (vitrification_law is None):
        raise ValueError("Please make sure to indicate a tg law since you have selected a vitrification law.")
    if (tg_law is not None) and (coupling_law is None):
        raise ValueError("Please make sure to indicate a tg law since you have selected a vitrification law.")

    def rate(t, extent, temperature, *args):
        """
        Compute the rate at a given time.

        Parameters
        ----------
        t : float
            Time.
        extent : float
            Current extent.
        temperature : float
            Current temperature.
        *args : tuple
            Additional arguments.

        Returns
        -------
        float
            Rate.
        """
        rate = rate_law(extent, temperature_program(t), *rate_law_args)

        if vitrification_law is not None:
            tg = tg_law(extent, *tg_law_args)
            vitrification_term = vitrification_law(temperature_program(t), tg, *vitrification_args)
            rate = coupling_law(rate, vitrification_term, *coupling_law_args)
        
        return rate
    
    initial_extent = np.atleast_1d(initial_extent)
    return scipy.integrate.solve_ivp(rate, [t0, tf], initial_extent,
                                     args=(temperature_program, *rate_law_args,
                                           vitrification_law, *vitrification_args,
                                           tg_law, *tg_law_args,
                                           coupling_law, *coupling_law_args))


#%% Example 1 - Kamal
if __name__=="__main__":
    
    import matplotlib.pyplot as plt
    import time as t
    
    number_of_points = 10000
    time = np.linspace(0, 1800, number_of_points)  # 30 minutes
    times = [time, time, time, time]
    temperatures = [np.linspace(293, 443, number_of_points),  # 5°C/min
                   np.linspace(293, 593, number_of_points),  # 10°C/min
                   np.linspace(293, 743, number_of_points),  # 15°C/min
                   np.linspace(293, 1093, number_of_points)]  # 20°C/min
    conversions=[]
    rates=[]

    fig, ax1 = plt.subplots()
    ax1_bis = ax1.twinx()
    ax1.set_xlabel("time")
    ax1.set_ylabel("conversion")
    ax1_bis.set_ylabel("rate")
    
    
    for i in range(len(temperatures)):
        t0=t.time()
        extent,rate,_,_,_ = compute_extent_and_rate(time,
                                                    temperatures[i], 
                                                    rate_law=rate_for_kamal, 
                                                    rate_law_args=(1.666e8,80000,1.666e13,120000,1,0.7))
        t1=t.time()
        print("Time: ",t1-t0,"s")
        conversions.append(extent)
        rates.append(rate)
        ax1.plot(time,extent,label="conversion for a heating rate of " + str((i+1)*5) + "°/min",linestyle='dotted')
        ax1_bis.plot(time,rate,label="rate for a heating rate of " + str((i+1)*5) + "°/min")
        ax1.legend()
        ax1_bis.legend()

    

    
    
    #%% Test main kinetic models  
    
    num_points = 10000
    time = np.linspace(0, 1800, int(num_points))
    temperature = np.full(int(num_points), 293.15)
    # Chemical rate parameters
    A1 = 1e10
    E1 = 70000
    A2 = 1e13
    E2 = 85000
    m = 0.45
    n = 1
    # Vitrification parameters extracted from [1] G. Wisanrakkit et J. K. Gillham, « The glass transition temperature (Tg) as an index of chemical conversion for a high-Tg amine/epoxy system: Chemical and diffusion-controlled reaction kinetics », Journal of Applied Polymer Science, vol. 41, nᵒ 11‑12, p. 2885‑2929, 1990, doi: 10.1002/app.1990.070411129.
    Ad = 30.64
    C1 = 42.61
    C2 = 51.6
    # Tg parameters taken 
    Tg0 = -100 + 273.15
    Tginf = 100 + 273.15
    lmbd = 0.4
    
    
    extent_nth_order, rate_nth_order, _, _, tg_nth_order = compute_extent_and_rate(time, 
                                                                                   temperature, 
                                                                                   rate_law=rate_for_nth_order,
                                                                                   rate_law_args=(A1,E1,n),
                                                                                   tg_law = tg_diBennedetto,
                                                                                   tg_law_args = (Tg0, Tginf, lmbd),
                                                                                   initial_extent=0.001)
    
    extent_autocatalytic, rate_autocatalytic, _, _, tg_autocatalytic = compute_extent_and_rate(time, 
                                                                                               temperature,
                                                                                               rate_law=rate_for_autocatalytic, 
                                                                                               rate_law_args=(A1,E1,m,n),
                                                                                               tg_law = tg_diBennedetto,
                                                                                               tg_law_args = (Tg0, Tginf, lmbd),
                                                                                               initial_extent=0.001)
    
    extent_kamal, rate_kamal, _, _, tg_kamal = compute_extent_and_rate(time, 
                                                                 temperature, 
                                                                 rate_for_kamal, 
                                                                 rate_law_args=(A1,E1,A2,E2,m,n),
                                                                 tg_law = tg_diBennedetto,
                                                                 tg_law_args = (Tg0, Tginf, lmbd),
                                                                 initial_extent=0.001)
    
    extent_nth_order_vitrification, rate_nth_order_vitrification, _, _, tg_nth_order_vitrification = compute_extent_and_rate(time,
                                                                                                      temperature,
                                                                                                      rate_law=rate_for_nth_order,
                                                                                                      rate_law_args=(A1,E1,n),
                                                                                                      vitrification_law=vitrification_WLF_rate,
                                                                                                      vitrification_law_args=(Ad,C1,C2),
                                                                                                      tg_law = tg_diBennedetto,
                                                                                                      tg_law_args = (Tg0, Tginf, lmbd),
                                                                                                      coupling_law=coupling_harmonic_mean,
                                                                                                      coupling_law_args=(),
                                                                                                      initial_extent=0.001)
    
    

    
    extent_nth_order_vitrification_no_reac, rate_nth_order_vitrification_no_reac, _, _, tg_nth_order_vitrification_no_reac = compute_extent_and_rate(time,
                                                                                                      temperature,
                                                                                                      rate_law=rate_for_nth_order,
                                                                                                      rate_law_args=(A1,E1,n),
                                                                                                      vitrification_law=vitrification_WLF_rate_no_reaction_below_Tg,
                                                                                                      vitrification_law_args=(Ad,C1,C2),
                                                                                                      tg_law = tg_diBennedetto,
                                                                                                      tg_law_args = (Tg0, Tginf, lmbd),
                                                                                                      coupling_law=coupling_harmonic_mean,
                                                                                                      coupling_law_args=(),
                                                                                                      initial_extent=0.001)

    
    
    fig, ax = plt.subplots()
    
    ax.plot(time,extent_nth_order,label="n-th order")
    ax.plot(time,extent_autocatalytic,label="autocatalytic")
    ax.plot(time,extent_kamal,label="kamal")
    ax.plot(time,extent_nth_order_vitrification,label="n-th order with vitrification")
    ax.plot(time,extent_nth_order_vitrification_no_reac,label="n-th order with vitrification_no_reac")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Extent")
    ax.legend()
    ax.set_title("Comparison of the extent evolution for multiple kinetic models")
    
    
    fig, ax = plt.subplots()
    
    ax.plot(time,rate_nth_order,label="n-th order")
    ax.plot(time,rate_autocatalytic,label="autocatalytic")
    ax.plot(time,rate_kamal,label="kamal")
    ax.plot(time,rate_nth_order_vitrification,label="n-th order with vitrification")
    ax.plot(time,rate_nth_order_vitrification_no_reac,label="n-th order with vitrification_no_reac")
    
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Rate")
    ax.legend()
    ax.set_title("Comparison of the rate evolution for multiple kinetic models")
    
    
    fig, ax = plt.subplots()
    ax.plot(time,temperature- 273.15,color='black',alpha=0.2)
    ax.plot(time,tg_nth_order - 273.15,label="n-th order")
    ax.plot(time,tg_autocatalytic - 273.15,label="autocatalytic")
    ax.plot(time,tg_kamal - 273.15,label="kamal")
    ax.plot(time,tg_nth_order_vitrification - 273.15,label="n-th order with vitrification")
    ax.plot(time,tg_nth_order_vitrification_no_reac - 273.15,label="n-th order with vitrification_no_reac")
    
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Tg")
    ax.legend()
    ax.set_title("Comparison of the Tg evolution for multiple kinetic models")
    
    # Save data to a text file
    with open('kinetic_data.txt', 'w') as file:
        file.write("Time(s)\tTemperature(K)\tExtent_nth_order\tRate_nth_order\tTg_nth_order\tExtent_autocatalytic\tRate_autocatalytic\tTg_autocatalytic\tExtent_kamal\tRate_kamal\tTg_kamal\tExtent_nth_order_vitrification\tRate_nth_order_vitrification\tTg_nth_order_vitrification\tExtent_nth_order_vitrification_no_reac\tRate_nth_order_vitrification_no_reac\tTg_nth_order_vitrification_no_reac\n")
        for i in range(len(time)):
            file.write(f"{time[i]}\t{temperature[i]}\t{extent_nth_order[i]}\t{rate_nth_order[i]}\t{tg_nth_order[i]}\t{extent_autocatalytic[i]}\t{rate_autocatalytic[i]}\t{tg_autocatalytic[i]}\t{extent_kamal[i]}\t{rate_kamal[i]}\t{tg_kamal[i]}\t{extent_nth_order_vitrification[i]}\t{rate_nth_order_vitrification[i]}\t{tg_nth_order_vitrification[i]}\t{extent_nth_order_vitrification_no_reac[i]}\t{rate_nth_order_vitrification_no_reac[i]}\t{tg_nth_order_vitrification_no_reac[i]}\n")

    
    
   
    #%% Convergence graph for multiple rate laws
    
    def compute_trap_sums(numbers_of_points, rate_law, rate_law_args, vitrification_law=None, vitrification_args=None, tg_law=None, tg_law_args=None, coupling_law=None, coupling_law_args=None, initial_extent=0.001):
        trap_sums = []
    
        for num_points in numbers_of_points:
            time = np.linspace(0, 1800, int(num_points))
            temperature = np.full(int(num_points), 443)
            extent, rate, _, _, _ = compute_extent_and_rate(time, temperature, rate_law=rate_law, rate_law_args=rate_law_args, vitrification_law=None, vitrification_law_args=None, tg_law=None, tg_law_args=None, coupling_law=None, coupling_law_args=None, initial_extent=initial_extent)
            trap_sums.append(np.trapz(rate, time))
        return np.array(trap_sums)-1
    
    A1 = 1e10
    E1 = 70000
    A2 = 1e13
    E2 = 85000
    m = 0.45
    n = 1
    # Vitrification parameters extracted from [1] G. Wisanrakkit et J. K. Gillham, « The glass transition temperature (Tg) as an index of chemical conversion for a high-Tg amine/epoxy system: Chemical and diffusion-controlled reaction kinetics », Journal of Applied Polymer Science, vol. 41, nᵒ 11‑12, p. 2885‑2929, 1990, doi: 10.1002/app.1990.070411129.
    Ad = 30.64
    C1 = 42.61
    C2 = 51.6
    # Tg parameters taken 
    Tg0 = -100 + 273.15
    Tginf = 100 + 273.15
    lmbd = 0.4
    
    # Compute trap_sums
    numbers_of_points = np.logspace(0, 6, 100)
    trap_sums_nth_order = compute_trap_sums(numbers_of_points, rate_for_nth_order, (A1,E1,n),tg_law = tg_diBennedetto, tg_law_args = (Tg0, Tginf, lmbd),initial_extent=0.001)
    trap_sums_autocatalytic = compute_trap_sums(numbers_of_points, rate_for_autocatalytic, (A1,E1,m,n),tg_law = tg_diBennedetto,tg_law_args = (Tg0, Tginf, lmbd),initial_extent=0.001)
    trap_sums_kamal = compute_trap_sums(numbers_of_points, rate_for_kamal, (A1,E1,A2,E2,m,n),tg_law = tg_diBennedetto,tg_law_args = (Tg0, Tginf, lmbd),initial_extent=0.001)
    trap_sums_nth_order_vitrification = compute_trap_sums(numbers_of_points, rate_for_nth_order, (A1,E1,n), vitrification_law=vitrification_WLF_rate, vitrification_args=(Ad,C1,C2), tg_law = tg_diBennedetto, tg_law_args = (Tg0, Tginf, lmbd), coupling_law=coupling_harmonic_mean, coupling_law_args=(), initial_extent=0.001)
    trap_sums_nth_order_vitrification_no_reac = compute_trap_sums(numbers_of_points, rate_for_nth_order, (A1,E1,n), vitrification_law=vitrification_WLF_rate_no_reaction_below_Tg, vitrification_args=(Ad,C1,C2), tg_law = tg_diBennedetto, tg_law_args = (Tg0, Tginf, lmbd), coupling_law=coupling_harmonic_mean, coupling_law_args=(), initial_extent=0.001)
    
    # Plot the convergence graph
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.plot(1/numbers_of_points,trap_sums_nth_order,label="n-th order",linewidth=8,alpha=0.2)
    ax.plot(1/numbers_of_points,trap_sums_autocatalytic,label="autocatalytic")
    ax.plot(1/numbers_of_points,trap_sums_kamal,label="kamal")
    ax.plot(1/numbers_of_points,trap_sums_nth_order_vitrification,label="n-th order with vitrification",linewidth=4,alpha=0.6)
    ax.plot(1/numbers_of_points,trap_sums_nth_order_vitrification_no_reac,label="n-th order with vitrification_no_reac")
    
    plt.xscale("log")
    plt.yscale("log")
    ax.legend()
    ax.set_xlabel("Timestep (s)")
    ax.set_ylabel("Trapezoïdal sum")
    ax.set_title("Convergence for multiple kinetic models")

    
    # Show the plot
    plt.show()
