"""Understandable starting configurations for the supported optimizers."""

from dataclasses import dataclass
from typing import Mapping, Optional, Tuple


@dataclass(frozen=True)
class OptimizationProfile:
    """A named set of solver parameters with a user-facing explanation."""

    name: str
    description: str
    method_values: Mapping[str, Mapping[str, Optional[str]]]

    def values_for(self, method: str) -> Mapping[str, Optional[str]]:
        """Return the values for one optimization method."""
        return self.method_values.get(method, {})


_COMMON_METHOD_VALUES = {
    'least_squares_log': {
        'jac': 'auto',
    },
    'Nelder-Mead': {
        'disp': 'No',
        'maxfev': None,
        'return_all': 'No',
        'adaptive': 'Yes',
    },
    'CG': {
        'disp': 'No',
        'jac': 'auto',
        'norm': None,
        'eps': None,
        'return_all': 'No',
    },
    'BFGS': {
        'disp': 'No',
        'jac': 'auto',
        'norm': None,
        'eps': None,
        'return_all': 'No',
    },
    'L-BFGS-B': {
        'disp': 'No',
        'jac': 'auto',
        'maxcor': '10',
        'iprint': None,
        'maxls': '20',
        'eps': None,
    },
    'basinhopping': {
        'disp': 'No',
        'T': '1',
        'stepsize': '0.5',
        'interval': '50',
        'niter_success': None,
        'target_accept_rate': '0.5',
        'stepwise_factor': '0.9',
    },
    'differential_evolution': {
        'disp': 'No',
        'strategy': 'best1bin',
        'mutation': '0.8',
        'recombination': '0.7',
        'polish': 'Yes',
        'init': 'latinhypercube',
        'atol': '0',
        'updating': 'immediate',
        # One worker is reliable from both the GUI and a Windows installation.
        # Users can still edit this field after applying a profile.
        'workers': '1',
        'vectorized': 'No',
    },
    'shgo': {
        'sampling_method': 'simplicial',
        'workers': '1',
    },
}


def _method_values(overrides):
    """Merge profile-specific budgets into complete method dictionaries."""
    return {
        method: {**common, **overrides[method]}
        for method, common in _COMMON_METHOD_VALUES.items()
    }


QUICK_PROFILE_NAME = 'Quick check'
BALANCED_PROFILE_NAME = 'Balanced (recommended)'
THOROUGH_PROFILE_NAME = 'Thorough search'
DEFAULT_PROFILE_NAME = BALANCED_PROFILE_NAME


OPTIMIZATION_PROFILES = {
    QUICK_PROFILE_NAME: OptimizationProfile(
        name=QUICK_PROFILE_NAME,
        description=(
            'Uses a small calculation budget to check the data, model, and '
            'bounds. Treat the result as a preliminary fit.'
        ),
        method_values=_method_values({
            'least_squares_log': {
                'max_nfev': '100',
                'ftol': '1e-6',
                'xtol': '1e-6',
                'gtol': '1e-6',
            },
            'Nelder-Mead': {
                'maxiter': '200',
                'xatol': '1e-3',
                'fatol': '1e-3',
            },
            'CG': {'maxiter': '200', 'gtol': '1e-4'},
            'BFGS': {
                'maxiter': '200',
                'gtol': '1e-4',
                'xrtol': '0',
            },
            'L-BFGS-B': {
                'maxfun': '3000',
                'maxiter': '200',
                'ftol': '1e-7',
                'gtol': '1e-4',
            },
            'basinhopping': {'niter': '25'},
            'differential_evolution': {
                'maxiter': '100',
                'popsize': '8',
                'tol': '0.02',
                'polish': 'No',
            },
            'shgo': {'n': '64', 'iters': '1'},
        }),
    ),
    BALANCED_PROFILE_NAME: OptimizationProfile(
        name=BALANCED_PROFILE_NAME,
        description=(
            'Uses practical budgets and solver tolerances for a routine fit. '
            'Check convergence and residuals before interpreting parameters.'
        ),
        method_values=_method_values({
            'least_squares_log': {
                'max_nfev': '500',
                'ftol': '1e-8',
                'xtol': '1e-8',
                'gtol': '1e-8',
            },
            'Nelder-Mead': {
                'maxiter': '1000',
                'xatol': '1e-4',
                'fatol': '1e-4',
            },
            'CG': {'maxiter': '1000', 'gtol': '1e-5'},
            'BFGS': {
                'maxiter': '1000',
                'gtol': '1e-5',
                'xrtol': '0',
            },
            'L-BFGS-B': {
                'maxfun': '15000',
                'maxiter': '1000',
                'ftol': '1e-9',
                'gtol': '1e-5',
            },
            'basinhopping': {'niter': '100'},
            'differential_evolution': {
                'maxiter': '500',
                'popsize': '15',
                'tol': '0.01',
            },
            'shgo': {'n': '100', 'iters': '2'},
        }),
    ),
    THOROUGH_PROFILE_NAME: OptimizationProfile(
        name=THOROUGH_PROFILE_NAME,
        description=(
            'Uses larger search budgets and tighter tolerances. Compare its '
            'result with the balanced fit before accepting the extra cost.'
        ),
        method_values=_method_values({
            'least_squares_log': {
                'max_nfev': '2000',
                'ftol': '1e-10',
                'xtol': '1e-10',
                'gtol': '1e-10',
            },
            'Nelder-Mead': {
                'maxiter': '3000',
                'xatol': '1e-6',
                'fatol': '1e-6',
            },
            'CG': {'maxiter': '3000', 'gtol': '1e-7'},
            'BFGS': {
                'maxiter': '3000',
                'gtol': '1e-7',
                'xrtol': '1e-8',
            },
            'L-BFGS-B': {
                'maxfun': '50000',
                'maxiter': '3000',
                'ftol': '1e-11',
                'gtol': '1e-7',
            },
            'basinhopping': {'niter': '500'},
            'differential_evolution': {
                'maxiter': '1500',
                'popsize': '25',
                'tol': '1e-3',
            },
            'shgo': {'n': '300', 'iters': '5'},
        }),
    ),
}


def optimization_profile_names() -> Tuple[str, ...]:
    """Return profile names in the order shown in the GUI."""
    return tuple(OPTIMIZATION_PROFILES)


def optimization_profile(name: str) -> OptimizationProfile:
    """Return a profile or raise a clear error for an unknown name."""
    try:
        return OPTIMIZATION_PROFILES[name]
    except KeyError as error:
        raise ValueError(f'Unknown optimization profile: {name}') from error
