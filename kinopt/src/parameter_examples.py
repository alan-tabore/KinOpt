"""Illustrative values shown in empty scientific parameter fields."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ParameterExample:
    """An example value that remains separate from actual user input."""

    value: Optional[str]
    unit: str = ''

    @property
    def placeholder(self):
        if self.value is None:
            return 'Optional - leave blank'
        suffix = f' {self.unit}' if self.unit else ''
        return f'Example: {self.value}{suffix}'

    @property
    def tooltip(self):
        if self.value is None:
            return 'Optional parameter. Leave it blank to use the solver default.'
        suffix = f' {self.unit}' if self.unit else ''
        return (
            f'Illustrative starting value: {self.value}{suffix}. '
            'Adapt it to your material, data, and parameter units.'
        )


MODEL_PARAMETER_EXAMPLES = {
    'A': ParameterExample('1e8', 's^-1'),
    'A1': ParameterExample('1e8', 's^-1'),
    'A2': ParameterExample('1e8', 's^-1'),
    'E': ParameterExample('50000', 'J/mol'),
    'Ea': ParameterExample('50000', 'J/mol'),
    'E1': ParameterExample('50000', 'J/mol'),
    'E2': ParameterExample('50000', 'J/mol'),
    'm': ParameterExample('2'),
    'n': ParameterExample('2'),
    'Ad': ParameterExample('1', 's^-1'),
    'C': ParameterExample('50'),
    'C1': ParameterExample('50'),
    'C2': ParameterExample('50', 'K'),
    'Tg_0': ParameterExample('290', 'K'),
    'Tg_inf': ParameterExample('450', 'K'),
    'coeff': ParameterExample('0.5'),
}


ISOCONVERSIONAL_PARAMETER_EXAMPLES = {
    'initial_guess': ParameterExample('50000', 'J/mol'),
    'min_conv': ParameterExample('0.1'),
    'max_conv': ParameterExample('0.9'),
    'number_of_points': ParameterExample('100'),
}


COST_PARAMETER_EXAMPLES = {
    'extent_limit': ParameterExample('0.707'),
    'amplification_factor': ParameterExample('10'),
    'fraction_to_amplify': ParameterExample('0.5'),
}


OPTIMIZATION_PARAMETER_EXAMPLES = {
    'Nelder-Mead': {
        'maxiter': ParameterExample('1200'),
        'maxfev': ParameterExample(None),
        'xatol': ParameterExample('1e-4'),
        'fatol': ParameterExample('1e-4'),
    },
    'CG': {
        'maxiter': ParameterExample('1200'),
        'gtol': ParameterExample('1e-5'),
        'norm': ParameterExample(None),
        'eps': ParameterExample(None),
    },
    'BFGS': {
        'maxiter': ParameterExample('1200'),
        'gtol': ParameterExample('1e-5'),
        'norm': ParameterExample(None),
        'eps': ParameterExample(None),
        'xrtol': ParameterExample('0'),
    },
    'L-BFGS-B': {
        'maxcor': ParameterExample('10'),
        'maxfun': ParameterExample('15000'),
        'maxiter': ParameterExample('1200'),
        'iprint': ParameterExample(None),
        'maxls': ParameterExample('20'),
        'ftol': ParameterExample('1e-9'),
        'gtol': ParameterExample('1e-5'),
        'eps': ParameterExample(None),
    },
    'basinhopping': {
        'niter': ParameterExample('100'),
        'T': ParameterExample('1'),
        'stepsize': ParameterExample('0.5'),
        'interval': ParameterExample('50'),
        'niter_success': ParameterExample(None),
        'target_accept_rate': ParameterExample('0.5'),
        'stepwise_factor': ParameterExample('0.9'),
    },
    'differential_evolution': {
        'maxiter': ParameterExample('1000'),
        'popsize': ParameterExample('15'),
        'tol': ParameterExample('0.01'),
        'mutation': ParameterExample('0.8'),
        'recombination': ParameterExample('0.7'),
        'atol': ParameterExample('0'),
        'workers': ParameterExample('1'),
    },
    'shgo': {
        'n': ParameterExample('100'),
        'iters': ParameterExample('1'),
        'workers': ParameterExample('1'),
    },
}


BOUND_PARAMETER_EXAMPLES = {
    'A': (ParameterExample('1', 's^-1'), ParameterExample('1e20', 's^-1')),
    'A1': (ParameterExample('1', 's^-1'), ParameterExample('1e20', 's^-1')),
    'A2': (ParameterExample('1', 's^-1'), ParameterExample('1e20', 's^-1')),
    'Ad': (
        ParameterExample('1e-20', 's^-1'),
        ParameterExample('1e20', 's^-1'),
    ),
    'E': (ParameterExample('1000', 'J/mol'), ParameterExample('350000', 'J/mol')),
    'Ea': (ParameterExample('1000', 'J/mol'), ParameterExample('350000', 'J/mol')),
    'E1': (ParameterExample('1000', 'J/mol'), ParameterExample('350000', 'J/mol')),
    'E2': (ParameterExample('1000', 'J/mol'), ParameterExample('350000', 'J/mol')),
    'm': (ParameterExample('0.1'), ParameterExample('20')),
    'n': (ParameterExample('0.1'), ParameterExample('20')),
    'C': (ParameterExample('1'), ParameterExample('350')),
    'C1': (ParameterExample('1'), ParameterExample('350')),
    'C2': (ParameterExample('1', 'K'), ParameterExample('350', 'K')),
}


def model_parameter_example(name):
    return MODEL_PARAMETER_EXAMPLES.get(name)


def isoconversional_parameter_example(name):
    return ISOCONVERSIONAL_PARAMETER_EXAMPLES.get(name)


def cost_parameter_example(name):
    return COST_PARAMETER_EXAMPLES.get(name)


def optimization_parameter_example(method, name):
    return OPTIMIZATION_PARAMETER_EXAMPLES.get(method, {}).get(name)


def bound_parameter_example(name, limit):
    examples = BOUND_PARAMETER_EXAMPLES.get(name)
    if examples is None:
        return None
    return examples[0 if limit == 'min' else 1]
