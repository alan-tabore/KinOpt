"""Coverage for the built-in optimization calculation profiles."""

from kinopt.src.main import (
    get_functions_for_optimization,
    get_parameters_for_optimization,
)
from kinopt.src.optimization_profiles import (
    BALANCED_PROFILE_NAME,
    DEFAULT_PROFILE_NAME,
    QUICK_PROFILE_NAME,
    THOROUGH_PROFILE_NAME,
    optimization_profile,
    optimization_profile_names,
)


def test_profiles_cover_every_supported_optimizer_parameter():
    global_methods, local_methods, _ = get_functions_for_optimization()

    for profile_name in optimization_profile_names():
        profile = optimization_profile(profile_name)
        for method in global_methods + local_methods:
            expected = set(get_parameters_for_optimization(method)) - {'bounds'}
            assert set(profile.values_for(method)) == expected


def test_profiles_fill_every_required_optimizer_parameter():
    global_methods, local_methods, _ = get_functions_for_optimization()

    for profile_name in optimization_profile_names():
        profile = optimization_profile(profile_name)
        for method in global_methods + local_methods:
            parameter_details = get_parameters_for_optimization(method)
            for parameter, details in parameter_details.items():
                if parameter != 'bounds' and not details['optional']:
                    assert profile.values_for(method)[parameter] is not None


def test_profile_budgets_increase_with_requested_effort():
    quick = optimization_profile(QUICK_PROFILE_NAME)
    balanced = optimization_profile(BALANCED_PROFILE_NAME)
    thorough = optimization_profile(THOROUGH_PROFILE_NAME)

    budget_parameters = {
        'Nelder-Mead': 'maxiter',
        'CG': 'maxiter',
        'BFGS': 'maxiter',
        'L-BFGS-B': 'maxiter',
        'basinhopping': 'niter',
        'differential_evolution': 'maxiter',
        'shgo': 'n',
    }
    for method, parameter in budget_parameters.items():
        values = [
            int(profile.values_for(method)[parameter])
            for profile in (quick, balanced, thorough)
        ]
        assert values[0] < values[1] < values[2]


def test_default_profile_is_the_recommended_balanced_profile():
    assert DEFAULT_PROFILE_NAME == BALANCED_PROFILE_NAME
    assert optimization_profile_names() == (
        QUICK_PROFILE_NAME,
        BALANCED_PROFILE_NAME,
        THOROUGH_PROFILE_NAME,
    )
