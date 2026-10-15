"""Illustrative values shown in empty scientific parameter fields."""

from dataclasses import dataclass
from typing import Optional

from kinopt.src.model_metadata import model_parameter_metadata
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


_MODEL_PARAMETER_NAMES = (
    'A',
    'A1',
    'A2',
    'E',
    'Ea',
    'E1',
    'E2',
    'm',
    'n',
    'Ad',
    'C1',
    'C2',
    'Tg_0',
    'Tg_inf',
    'coeff',
)


def _example_from_metadata(name):
    metadata = model_parameter_metadata(name)
    if metadata is None:
        return None
    return ParameterExample(metadata.example, metadata.unit)


MODEL_PARAMETER_EXAMPLES = {
    name: _example_from_metadata(name)
    for name in _MODEL_PARAMETER_NAMES
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
    name: (
        ParameterExample(metadata.lower_bound, metadata.unit),
        ParameterExample(metadata.upper_bound, metadata.unit),
    )
    for name in _MODEL_PARAMETER_NAMES
    for metadata in (model_parameter_metadata(name),)
    if metadata is not None
    and metadata.lower_bound is not None
    and metadata.upper_bound is not None
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
