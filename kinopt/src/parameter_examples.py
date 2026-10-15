"""Illustrative values shown in empty scientific parameter fields."""

from dataclasses import dataclass
from typing import Optional

from kinopt.src.optimization_profiles import (
    DEFAULT_PROFILE_NAME,
    optimization_profile,
)


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
    values = optimization_profile(DEFAULT_PROFILE_NAME).values_for(method)
    if name not in values:
        return None
    return ParameterExample(values[name])


def bound_parameter_example(name, limit):
    examples = BOUND_PARAMETER_EXAMPLES.get(name)
    if examples is None:
        return None
    return examples[0 if limit == 'min' else 1]
