---
title: 'KinOpt: A Python package for chemical kinetics analysis and optimization'
tags:
  - Python
  - reaction kinetics
  - kinetics
  - isoconversional analysis
  - optimization
  - cost function
authors:
  - name: Alan Taboré
    orcid: 0009-0009-6666-7207
    equal-contrib: true
    affiliation: 1 

affiliations:
 - name: Mines Paris, PSL University, Centre for Material Forming (CEMEF), UMR CNRS 7635, 06904 Sophia Antipolis, France
   index: 1
date: 03 January 2025
bibliography: paper.bib
---

# Summary

Chemical reaction kinetics are a frequent research topic, and modeling them is becoming increasingly common [@corezzi_modeling_2010; @wang_new_2022; @dimier_curing_2004]. Generally, this modeling is taken into account by means of temperature dependence $g(T)$ coupled to a model of reaction $f(\alpha)$:

$$ \frac{d\alpha}{dt} = g(T)\times f(\alpha) $$

with $\frac{d\alpha}{dt}$ the rate of reaction, $\alpha$ the extent of reaction and $T$ the temperature.

In most of the cases, the temperature dependence is an Arrhenius law: $g(T)= A  \exp^{(\frac{-E_a}{RT})}$ with $A$ the pre-exponential factor, $E_a$ the activation energy and $R$ the universal gas constant. But, this temperature dependance is not always valid. To ensure its validity, isoconversional analysis can be performed. Isoconversional analysis is also a method that can be used to elucidate actual reaction mechanisms (thereby facilitating the selection of the appropriate $f(\alpha)$ reaction model).

The selection of a kinetic equation does not guarantee the optimization of the model to the experimental data, particularly in cases of a complex topology of the response surface (as seen in @adenson_kinetics_2018). Consequently, the efficacy of multiple optimization strategies must be thoroughly evaluated.

# Statement of need

KinOpt is a Python package designed to streamline the process of kinetic data analysis and optimization. With a suite of features tailored to meet the diverse needs of researchers. 

The motivation behind the creation of this software stems from two primary factors: 
1. There is currently no open-source software available for isoconversional analysis or kinetic model optimization. 
2. The identification, implementation, and use of isoconversional methods or reaction models is a time-consuming process, necessitating the selection of an appropriate optimization method and cost function to find the parameters of the kinetic model. Furthermore, the risk of human error increases with each step in this process.

The Python programming language was selected on the basis that optimization does not necessitate exceptional computational performance. Additionally, the connection between the code and the graphical interface is straightforward. Finally, given the prevalence of non-programmers within the field of chemical reaction kinetics, the adoption of a straightforward programming language such as Python facilitates enhanced contributions from this community (*for example, a reaction model not included in the program can be added simply by defining a function starting with `rate_` in the `kinetic_models.py`* file).

Key Features of KinOpt:
- **Isoconversional Analysis**: Uncover the conversion dependence of activation energies through rigorous isoconversional analysis. The current version of KinOpt supports three different methods: Friedman method [@sbirrazzuoli_is_2007], Vyazovkin method [@vyazovkin_evaluation_1997] and Advanced Vyazovkin method [@vyazovkin_modification_2001].
- **Kinetic Rate Law Selection**: Select your reaction model using standard reaction law such as n-th order reaction, autocatalytic reaction, Kamal and Sourour model [@sourour_differential_1976]. You can also add a vitrification/diffusion term  if necessary.
- **Kinetic Rate Law Optimization**: Fine-tune the parameters of the main kinetic rate law using global and local optimization algorithms [@virtanen_scipy_2020], ensuring accurate modeling of reaction kinetics under various conditions.
- **User-Friendly Interface**: Navigate effortlessly through KinOpt’s intuitive graphical user interface (GUI), making complex analyses accessible to users of all levels.
- **Easy Data Interpretation and Management**: Generate results files that are seamlessly readable within KinOpt, simplifying the process of analyzing and interpreting kinetic data. All data used for optimization can be found in a human-readable `.txt` file.

# Documentation

The project's documentation is hosted on readthedocs at: [KinOpt Documentation](https://kinopt.readthedocs.io/en/latest/index.html)

Tutorials are also available on **[Youtube ](https://youtube.com/playlist?list=PLxgAQK6NxsvJIZDw5gI6Xi16PfxUrXFI0&si=ICWPLX2gbCdEuDp9)**.


# Acknowledgements

I would like to express my gratitude to Franck Pigeonneau and Jean-Luc Bouvard for their support during the project's early stages, as well as to EssilorLuxottica for its role in facilitating our university's involvement in this research initiative.

# References
