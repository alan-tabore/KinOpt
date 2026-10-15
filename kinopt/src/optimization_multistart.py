"""Generate reproducible bounded starting points for optimization batches."""

from dataclasses import replace

import numpy as np


_GLOBAL_METHODS_WITHOUT_STARTING_POINT = frozenset({
    "differential_evolution",
    "shgo",
})


def bounds_for_multistart(config):
    """Return finite parameter bounds used by a start-dependent strategy."""
    if config.global_method in _GLOBAL_METHODS_WITHOUT_STARTING_POINT:
        raise ValueError(
            f"{config.global_method} does not use KinOpt's initial parameter "
            "values, so repeating it with different starts would duplicate "
            "the same setup."
        )

    local_options = config.local_options or {}
    bounds = local_options.get("bounds")
    if bounds is None:
        raise ValueError(
            "Multi-start generation requires finite parameter bounds in the "
            "selected local optimization method."
        )

    initial_guess = np.asarray(config.initial_guess, dtype=float)
    pairs = np.asarray(bounds, dtype=float)
    expected_shape = (initial_guess.size, 2)
    if pairs.shape != expected_shape:
        raise ValueError(
            "Multi-start generation requires one lower and upper bound for "
            f"each parameter; expected {expected_shape[0]} pairs."
        )
    if not np.all(np.isfinite(pairs)):
        raise ValueError("Multi-start bounds must be finite.")
    lower, upper = pairs.T
    if np.any(lower >= upper):
        raise ValueError("Each multi-start lower bound must be below its upper bound.")
    if not np.all(np.isfinite(initial_guess)):
        raise ValueError("The current initial parameter values must be finite.")
    if np.any(initial_guess < lower) or np.any(initial_guess > upper):
        raise ValueError(
            "Every current initial parameter value must lie inside its bounds."
        )
    return pairs


def _latin_hypercube(sample_count, dimension_count, random_generator):
    """Return a small Latin-hypercube design in the open unit interval."""
    unit_samples = np.empty((sample_count, dimension_count), dtype=float)
    for dimension in range(dimension_count):
        strata = (
            np.arange(sample_count, dtype=float)
            + random_generator.random(sample_count)
        ) / sample_count
        unit_samples[:, dimension] = strata[
            random_generator.permutation(sample_count)
        ]
    return unit_samples


def generate_multistart_configs(config, run_count, seed):
    """Return a baseline plus reproducible starts sampled inside its bounds.

    Strictly positive parameter ranges are sampled uniformly in logarithmic
    space. Ranges containing zero or negative values are sampled linearly.
    """
    if isinstance(run_count, bool) or not isinstance(
        run_count,
        (int, np.integer),
    ):
        raise TypeError("The multi-start run count must be an integer.")
    if run_count < 2:
        raise ValueError("A multi-start batch requires at least two runs.")
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise TypeError("The multi-start seed must be an integer.")
    if seed < 0:
        raise ValueError("The multi-start seed must be zero or positive.")

    bounds = bounds_for_multistart(config)
    lower, upper = bounds.T
    generated_count = run_count - 1
    unit_samples = _latin_hypercube(
        generated_count,
        lower.size,
        np.random.default_rng(int(seed)),
    )
    starts = lower + unit_samples * (upper - lower)
    logarithmic = lower > 0
    starts[:, logarithmic] = np.exp(
        np.log(lower[logarithmic])
        + unit_samples[:, logarithmic]
        * (np.log(upper[logarithmic]) - np.log(lower[logarithmic]))
    )

    return (
        config,
        *(
            replace(config, initial_guess=initial_guess)
            for initial_guess in starts
        ),
    )
