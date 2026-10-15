"""Tests for reproducible multi-start configuration generation."""

from dataclasses import replace

import numpy as np
import pytest
from scipy import optimize

from kinopt.src.optimization_multistart import generate_multistart_configs
from kinopt.src.optimization_runner import LOG_SPACE_LEAST_SQUARES


def bounded_config(serializable_config):
    return replace(
        serializable_config,
        local_method=LOG_SPACE_LEAST_SQUARES,
        local_optimizer=optimize.least_squares,
        local_options={
            'jac': 'auto',
            'max_nfev': 100,
            'bounds': (
                (1e5, 1e10),
                (1e3, 2e5),
                (0.1, 5.0),
            ),
        },
    )


def test_multistart_keeps_baseline_and_generates_reproducible_bounded_starts(
    serializable_config,
):
    config = bounded_config(serializable_config)

    first = generate_multistart_configs(config, 5, seed=123)
    second = generate_multistart_configs(config, 5, seed=123)

    assert first[0] is config
    assert len(first) == 5
    np.testing.assert_array_equal(first[0].initial_guess, config.initial_guess)
    for generated, reproduced in zip(first[1:], second[1:]):
        np.testing.assert_array_equal(
            generated.initial_guess,
            reproduced.initial_guess,
        )
        assert np.all(generated.initial_guess >= [1e5, 1e3, 0.1])
        assert np.all(generated.initial_guess <= [1e10, 2e5, 5.0])
        with pytest.raises(ValueError):
            generated.initial_guess[0] = 1.0

    assert any(
        not np.array_equal(generated.initial_guess, config.initial_guess)
        for generated in first[1:]
    )


def test_multistart_uses_a_different_design_for_a_different_seed(
    serializable_config,
):
    config = bounded_config(serializable_config)

    first = generate_multistart_configs(config, 4, seed=1)
    second = generate_multistart_configs(config, 4, seed=2)

    assert any(
        not np.array_equal(left.initial_guess, right.initial_guess)
        for left, right in zip(first[1:], second[1:])
    )


def test_multistart_supports_linear_ranges_containing_zero(
    serializable_config,
):
    config = replace(
        bounded_config(serializable_config),
        initial_guess=np.array([0.0, 55_000.0, 1.4]),
        local_options={
            'bounds': ((-2.0, 2.0), (1e3, 2e5), (0.1, 5.0)),
        },
    )

    generated = generate_multistart_configs(config, 8, seed=7)
    first_parameters = np.array(
        [candidate.initial_guess[0] for candidate in generated[1:]]
    )

    assert np.all(first_parameters > -2.0)
    assert np.all(first_parameters < 2.0)
    assert np.any(first_parameters < 0)
    assert np.any(first_parameters > 0)


def test_multistart_requires_usable_bounds(serializable_config):
    with pytest.raises(ValueError, match='requires finite parameter bounds'):
        generate_multistart_configs(serializable_config, 5, seed=42)


@pytest.mark.parametrize(
    'initial_guess,bounds,message',
    [
        (
            np.array([8e7, 55_000.0, 1.4]),
            ((1e5, 1e10), (1e3, 2e5)),
            'one lower and upper bound',
        ),
        (
            np.array([8e7, 55_000.0, 1.4]),
            ((1e5, np.inf), (1e3, 2e5), (0.1, 5.0)),
            'must be finite',
        ),
        (
            np.array([8e7, 55_000.0, 1.4]),
            ((1e5, 1e10), (1e3, 1e3), (0.1, 5.0)),
            'must be below',
        ),
        (
            np.array([np.nan, 55_000.0, 1.4]),
            ((1e5, 1e10), (1e3, 2e5), (0.1, 5.0)),
            'initial parameter values must be finite',
        ),
        (
            np.array([1e4, 55_000.0, 1.4]),
            ((1e5, 1e10), (1e3, 2e5), (0.1, 5.0)),
            'must lie inside',
        ),
    ],
)
def test_multistart_validates_bounds_and_current_start(
    serializable_config,
    initial_guess,
    bounds,
    message,
):
    config = replace(
        bounded_config(serializable_config),
        initial_guess=initial_guess,
        local_options={'bounds': bounds},
    )

    with pytest.raises(ValueError, match=message):
        generate_multistart_configs(config, 5, seed=42)


@pytest.mark.parametrize('global_method', ['differential_evolution', 'shgo'])
def test_multistart_rejects_global_methods_that_ignore_initial_values(
    serializable_config,
    global_method,
):
    config = replace(
        bounded_config(serializable_config),
        global_method=global_method,
        global_optimizer=getattr(optimize, global_method),
        global_options={
            'bounds': ((1e5, 1e10), (1e3, 2e5), (0.1, 5.0)),
        },
        local_method='',
        local_optimizer=None,
        local_options=None,
    )

    with pytest.raises(ValueError, match='does not use.*initial'):
        generate_multistart_configs(config, 5, seed=42)


@pytest.mark.parametrize(
    'run_count,seed,error_type,message',
    [
        (1, 42, ValueError, 'at least two'),
        (2.5, 42, TypeError, 'count must be an integer'),
        (2, -1, ValueError, 'zero or positive'),
        (2, 1.5, TypeError, 'seed must be an integer'),
    ],
)
def test_multistart_validates_run_count_and_seed(
    serializable_config,
    run_count,
    seed,
    error_type,
    message,
):
    with pytest.raises(error_type, match=message):
        generate_multistart_configs(
            bounded_config(serializable_config),
            run_count,
            seed,
        )
