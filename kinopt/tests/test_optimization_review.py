"""Tests for the readable pre-run optimization review."""

from dataclasses import replace

from scipy import optimize

from kinopt.src.optimization_review import (
    build_optimization_review,
    review_to_html,
)


def test_review_describes_the_frozen_configuration(serializable_config):
    review = build_optimization_review(
        serializable_config,
        dataset_names=('synthetic.csv',),
        profile_name='Balanced (recommended)',
    )

    assert review.datasets == ('synthetic.csv',)
    assert review.data_points == 3
    assert review.models == ('Nth-order model',)
    assert [parameter.name for parameter in review.parameters] == [
        'A1',
        'E1',
        'n',
    ]
    assert [parameter.initial_value for parameter in review.parameters] == [
        8e7,
        55000.,
        1.4,
    ]
    assert review.global_method == 'None'
    assert review.local_method == 'Nelder-Mead'
    assert review.cost_function == 'Mean squared residual'
    assert review.profile_name == 'Balanced (recommended)'
    assert review.budget == '10 iteration budget'
    assert any('underdetermined' in warning for warning in review.warnings)


def test_review_warns_about_bounds_and_an_ignored_local_method(
    serializable_config,
):
    config = replace(
        serializable_config,
        global_method='differential_evolution',
        global_optimizer=optimize.differential_evolution,
        global_options={
            'maxiter': 100,
            'popsize': 8,
            'bounds': ((1., 2.), (1000., 350000.), (0.1, 20.)),
        },
        max_iterations=100,
    )

    review = build_optimization_review(config)

    assert review.budget == (
        '100 iteration budget; approximately 2,424 population evaluations '
        'before optional polishing'
    )
    assert review.bound_sets[0].method == 'differential_evolution'
    assert review.bound_sets[0].bounds[0].name == 'A1'
    assert any('not run after differential evolution' in item for item in review.warnings)
    assert any('initial value of A1' in item for item in review.warnings)


def test_review_reports_unconstrained_gradient_method(serializable_config):
    config = replace(
        serializable_config,
        local_method='BFGS',
        local_options={
            'method': 'BFGS',
            'jac': None,
            'options': {'maxiter': 10},
        },
    )

    review = build_optimization_review(config)

    assert any('BFGS is unconstrained' in item for item in review.warnings)
    assert review.bound_sets == ()


def test_review_html_escapes_user_controlled_dataset_names(serializable_config):
    review = build_optimization_review(
        serializable_config,
        dataset_names=('<unsafe>.csv',),
    )

    html = review_to_html(review)

    assert '&lt;unsafe&gt;.csv' in html
    assert '<unsafe>.csv' not in html
    assert 'Free parameters and starting values' in html
    assert 'Checks before starting' in html
