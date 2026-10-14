"""Validate stable and safe JSON optimization configurations."""

from dataclasses import replace
import json

import numpy as np
import pytest
from scipy import optimize

from kinopt.src.optimization_runner import run_optimization
from kinopt.src.optimization_serialization import (
    config_from_dict,
    deserialize_config,
    serialize_config,
)


def test_configuration_round_trip_preserves_run(serializable_config):
    serialized = serialize_config(serializable_config)
    restored = deserialize_config(serialized)

    payload = json.loads(serialized)
    assert payload['schema_version'] == 1
    assert payload['cost_function'] == 'rss_mean'
    assert payload['rate_law'] == 'rate_for_nth_order'
    assert restored.cost_function is serializable_config.cost_function
    assert restored.rate_law is serializable_config.rate_law
    np.testing.assert_array_equal(
        restored.experimental_args_for_rate[0],
        serializable_config.experimental_args_for_rate[0],
    )
    assert restored.local_options['options']['maxiter'] == 10

    original_outcome = run_optimization(serializable_config)
    restored_outcome = run_optimization(restored)
    np.testing.assert_array_equal(
        restored_outcome.result.x,
        original_outcome.result.x,
    )
    assert restored_outcome.result.fun == original_outcome.result.fun


def test_unregistered_functions_are_not_persisted(serializable_config):
    config = replace(serializable_config, cost_function=lambda *args: 0.)

    with pytest.raises(ValueError, match='unregistered cost function'):
        serialize_config(config)


@pytest.mark.parametrize(
    'method,options',
    [
        ('basinhopping', {'niter': 2, 'seed': 42}),
        (
            'differential_evolution',
            {'bounds': [(-5., 5.)] * 3, 'maxiter': 2, 'seed': 42},
        ),
        ('shgo', {'bounds': [(-5., 5.)] * 3, 'n': 16, 'iters': 1}),
    ],
)
def test_supported_global_method_options_round_trip(
    serializable_config,
    method,
    options,
):
    config = replace(
        serializable_config,
        global_method=method,
        global_optimizer=getattr(optimize, method),
        global_options=options,
    )

    restored = deserialize_config(serialize_config(config))

    assert restored.global_method == method
    assert restored.global_optimizer is getattr(optimize, method)
    if 'bounds' in options:
        assert restored.global_options['bounds'] == tuple(options['bounds'])


def test_unknown_schema_and_model_are_rejected(serializable_config):
    payload = json.loads(serialize_config(serializable_config))
    payload['schema_version'] = 99
    with pytest.raises(ValueError, match='Unsupported.*schema'):
        config_from_dict(payload)

    payload['schema_version'] = 1
    payload['rate_law'] = 'not_a_model'
    with pytest.raises(ValueError, match='Unknown rate law'):
        config_from_dict(payload)


@pytest.mark.parametrize(
    'field,value,message',
    [
        ('cost_function', None, 'cost function is required'),
        ('rate_law', None, 'At least one rate or vitrification'),
        ('local_method', 'not-a-solver', 'Unknown local method'),
    ],
)
def test_incomplete_or_unsupported_run_is_rejected(
    serializable_config,
    field,
    value,
    message,
):
    payload = json.loads(serialize_config(serializable_config))
    payload[field] = value

    with pytest.raises(ValueError, match=message):
        config_from_dict(payload)


def test_nonstandard_numeric_constants_are_rejected(serializable_config):
    payload = serialize_config(serializable_config).replace(
        '"max_iterations":10',
        '"max_iterations":NaN',
    )

    with pytest.raises(ValueError, match='Invalid numeric constant'):
        deserialize_config(payload)
