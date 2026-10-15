"""Validate the central kinetic-model metadata catalogue."""

import inspect

from kinopt.src import kinetic_models
from kinopt.src.model_metadata import (
    KINETIC_MODELS,
    kinetic_model_metadata,
    kinetic_model_names,
)
from kinopt.src.parameter_examples import (
    bound_parameter_example,
    model_parameter_example,
)
from kinopt.src.selection_guidance import selection_guidance_for


def test_catalogue_matches_supported_function_signatures():
    for model in KINETIC_MODELS:
        function = getattr(kinetic_models, model.function_name)
        assert tuple(inspect.signature(function).parameters) == (
            model.function_parameters
        )
        assert kinetic_model_metadata(model.kind, model.function_name) is model


def test_catalogue_defines_every_selectable_model_family():
    assert kinetic_model_names('rate') == (
        'rate_for_nth_order',
        'rate_for_autocatalytic',
        'rate_for_kamal',
    )
    assert kinetic_model_names('vitrification') == (
        'vitrification_WLF_rate',
        'vitrification_WLF_rate_no_reaction_below_Tg',
    )
    assert kinetic_model_names('coupling') == (
        'coupling_harmonic_mean',
        'coupling_product',
    )
    assert kinetic_model_names('tg') == ('tg_diBennedetto',)


def test_guidance_and_parameter_examples_are_derived_from_catalogue():
    kamal = kinetic_model_metadata('rate', 'rate_for_kamal')
    guidance = selection_guidance_for('rate', kamal.function_name)

    assert guidance.title == kamal.display_name
    assert guidance.summary == kamal.summary
    assert guidance.advice == kamal.advice
    assert guidance.equation == kamal.equation
    for parameter in kamal.parameters:
        example = model_parameter_example(parameter.name)
        assert example.value == parameter.example
        assert example.unit == parameter.unit
        assert parameter.role
        assert bound_parameter_example(parameter.name, 'min').value == (
            parameter.lower_bound
        )
        assert bound_parameter_example(parameter.name, 'max').value == (
            parameter.upper_bound
        )
