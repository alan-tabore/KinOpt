"""Coverage for illustrative values shown in parameter fields."""

from kinopt.src.main import (
    get_functions_for_isoconversional_method,
    get_functions_for_kinetics,
    get_functions_for_optimization,
    get_parameters_for_coupling,
    get_parameters_for_isoconversional_method,
    get_parameters_for_optimization,
    get_parameters_for_rate,
    get_parameters_for_rss,
    get_parameters_for_tg,
    get_parameters_for_vitrification,
)
from kinopt.src.parameter_examples import (
    bound_parameter_example,
    cost_parameter_example,
    isoconversional_parameter_example,
    model_parameter_example,
    optimization_parameter_example,
)
from kinopt.src.optimization_profiles import (
    DEFAULT_PROFILE_NAME,
    optimization_profile,
)


EXPERIMENTAL_MODEL_PARAMETERS = {
    'T',
    'Tg',
    'extent',
    'extent_at_gel',
    'experimental_parameters',
    'kc',
    'kv',
    'optional_parameters',
}
EXPERIMENTAL_ISOCONVERSIONAL_PARAMETERS = {
    'conv_lists',
    'rate_lists',
    'temperature_lists',
    'time_lists',
}


def test_every_model_input_has_an_illustrative_value():
    rate, vitrification, coupling, tg = get_functions_for_kinetics()
    parameters = []
    for name in rate:
        parameters.extend(get_parameters_for_rate(name))
    for name in vitrification:
        parameters.extend(get_parameters_for_vitrification(name))
    for name in coupling:
        parameters.extend(get_parameters_for_coupling(name))
    for name in tg:
        parameters.extend(get_parameters_for_tg(name))

    missing = {
        name
        for name in parameters
        if name not in EXPERIMENTAL_MODEL_PARAMETERS
        and model_parameter_example(name) is None
    }
    assert missing == set()


def test_every_fitted_model_input_has_bound_examples():
    rate, vitrification, coupling, _ = get_functions_for_kinetics()
    parameters = []
    for name in rate:
        parameters.extend(get_parameters_for_rate(name))
    for name in vitrification:
        parameters.extend(get_parameters_for_vitrification(name))
    for name in coupling:
        parameters.extend(get_parameters_for_coupling(name))

    fitted = {
        name for name in parameters if name not in EXPERIMENTAL_MODEL_PARAMETERS
    }
    missing = {
        (name, limit)
        for name in fitted
        for limit in ('min', 'max')
        if bound_parameter_example(name, limit) is None
    }
    assert missing == set()


def test_every_isoconversional_input_has_an_illustrative_value():
    parameters = []
    for name in get_functions_for_isoconversional_method():
        parameters.extend(get_parameters_for_isoconversional_method(name))

    missing = {
        name
        for name in parameters
        if name not in EXPERIMENTAL_ISOCONVERSIONAL_PARAMETERS
        and isoconversional_parameter_example(name) is None
    }
    assert missing == set()


def test_every_numeric_optimizer_input_has_a_placeholder():
    global_methods, local_methods, _ = get_functions_for_optimization()
    missing = set()
    for method in global_methods + local_methods:
        for name, details in get_parameters_for_optimization(method).items():
            if details['type'] in (int, float):
                if optimization_parameter_example(method, name) is None:
                    missing.add((method, name))

    assert missing == set()


def test_every_cost_function_input_has_an_illustrative_value():
    _, _, cost_functions = get_functions_for_optimization()
    missing = {
        name
        for function_name in cost_functions
        for name in get_parameters_for_rss(function_name)
        if name not in EXPERIMENTAL_MODEL_PARAMETERS
        and cost_parameter_example(name) is None
    }
    assert missing == set()


def test_placeholder_is_distinct_from_an_actual_value():
    example = model_parameter_example('E1')

    assert example.value == '50000'
    assert example.placeholder == 'Example: 50000 J/mol'
    assert 'Activation energy' in example.tooltip
    assert 'Adapt it to your material' in example.tooltip


def test_optimizer_placeholders_match_the_default_profile():
    global_methods, local_methods, _ = get_functions_for_optimization()
    profile = optimization_profile(DEFAULT_PROFILE_NAME)

    for method in global_methods + local_methods:
        for name, value in profile.values_for(method).items():
            details = get_parameters_for_optimization(method)[name]
            if details['type'] in (int, float):
                assert optimization_parameter_example(method, name).value == value
