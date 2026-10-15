"""Build a readable, solver-independent review of an optimization run."""

from dataclasses import dataclass
from html import escape
from inspect import signature
from typing import Optional, Sequence, Tuple

import numpy as np

from kinopt.src.optimization_runner import OptimizationRunConfig
from kinopt.src.selection_guidance import selection_guidance_for


@dataclass(frozen=True)
class ReviewParameter:
    """One free parameter and its starting value."""

    name: str
    initial_value: float


@dataclass(frozen=True)
class ReviewBound:
    """One lower and upper bound associated with a free parameter."""

    name: str
    lower: Optional[float]
    upper: Optional[float]


@dataclass(frozen=True)
class ReviewBoundSet:
    """Bounds supplied to one selected optimization method."""

    method: str
    bounds: Tuple[ReviewBound, ...]


@dataclass(frozen=True)
class OptimizationReview:
    """User-facing facts and checks derived from an immutable run snapshot."""

    datasets: Tuple[str, ...]
    data_points: int
    models: Tuple[str, ...]
    parameters: Tuple[ReviewParameter, ...]
    fixed_tg_parameters: Tuple[ReviewParameter, ...]
    bound_sets: Tuple[ReviewBoundSet, ...]
    global_method: str
    local_method: str
    cost_function: str
    profile_name: Optional[str]
    budget: str
    warnings: Tuple[str, ...]
    notes: Tuple[str, ...]


def _function_name(function):
    return '' if function is None else function.__name__


def _selection_title(kind, name):
    guidance = selection_guidance_for(kind, name)
    if guidance is not None:
        return guidance.title
    return name or 'None selected'


def _parameter_names(function, count):
    if function is None or count <= 0:
        return ()
    names = tuple(signature(function).parameters)
    if count > len(names):
        return tuple(f'parameter_{index + 1}' for index in range(count))
    return names[-count:]


def _free_parameter_names(config, parameter_count):
    coupling_count = (
        parameter_count
        - config.rate_parameter_count
        - config.vitrification_parameter_count
    )
    if coupling_count < 0:
        return tuple(
            f'parameter_{index + 1}' for index in range(parameter_count)
        )
    names = (
        _parameter_names(config.rate_law, config.rate_parameter_count)
        + _parameter_names(
            config.vitrification_law,
            config.vitrification_parameter_count,
        )
        + _parameter_names(config.coupling_law, coupling_count)
    )
    if len(names) != parameter_count:
        return tuple(
            f'parameter_{index + 1}' for index in range(parameter_count)
        )
    return names


def _bounds_from(options):
    if options is None:
        return None
    return options.get('bounds')


def _bound_sets(config, parameter_names):
    sources = (
        (config.global_method, _bounds_from(config.global_options)),
        (config.local_method, _bounds_from(config.local_options)),
    )
    sets = []
    for method, values in sources:
        if not method or values is None:
            continue
        bounds = []
        for index, value in enumerate(values):
            name = (
                parameter_names[index]
                if index < len(parameter_names)
                else f'parameter_{index + 1}'
            )
            lower, upper = value
            bounds.append(
                ReviewBound(
                    name=name,
                    lower=None if lower is None else float(lower),
                    upper=None if upper is None else float(upper),
                )
            )
        sets.append(ReviewBoundSet(method=method, bounds=tuple(bounds)))
    return tuple(sets)


def _budget_description(config, parameter_count):
    base = f'{config.max_iterations:,} iteration budget'
    if config.global_method == 'differential_evolution':
        options = config.global_options or {}
        population_size = options.get('popsize')
        maximum_iterations = options.get('maxiter')
        if population_size is not None and maximum_iterations is not None:
            evaluations = (
                (int(maximum_iterations) + 1)
                * int(population_size)
                * max(1, parameter_count)
            )
            return (
                f'{base}; approximately {evaluations:,} population '
                'evaluations before optional polishing'
            )
    if config.global_method == 'shgo':
        options = config.global_options or {}
        samples = options.get('n')
        iterations = options.get('iters')
        if samples is not None and iterations is not None:
            return (
                f'{base}; {int(samples):,} sampling points over '
                f'{int(iterations):,} iteration(s)'
            )
    return base


def _guidance_notes(selections):
    notes = []
    for kind, name in selections:
        guidance = selection_guidance_for(kind, name)
        if guidance is not None and guidance.advice not in notes:
            notes.append(guidance.advice)
    return tuple(notes)


def build_optimization_review(
    config: OptimizationRunConfig,
    dataset_names: Sequence[str] = (),
    profile_name: Optional[str] = None,
) -> OptimizationReview:
    """Derive a review from the exact immutable configuration to be run."""
    initial_values = np.asarray(config.initial_guess, dtype=float).reshape(-1)
    parameter_names = _free_parameter_names(config, len(initial_values))
    parameters = tuple(
        ReviewParameter(name, float(value))
        for name, value in zip(parameter_names, initial_values)
    )

    tg_values = () if config.tg_args is None else tuple(config.tg_args)
    tg_names = _parameter_names(config.tg_law, len(tg_values))
    fixed_tg_parameters = tuple(
        ReviewParameter(name, float(value))
        for name, value in zip(tg_names, tg_values)
    )

    models = []
    selections = []
    for kind, function in (
        ('rate', config.rate_law),
        ('vitrification', config.vitrification_law),
        ('coupling', config.coupling_law),
        ('tg', config.tg_law),
    ):
        name = _function_name(function)
        if name:
            models.append(_selection_title(kind, name))
            selections.append((kind, name))

    if config.global_method:
        selections.append(('global_optimization', config.global_method))
    if config.local_method:
        selections.append(('local_optimization', config.local_method))
    cost_name = _function_name(config.cost_function)
    selections.append(('cost_function', cost_name))

    bound_sets = _bound_sets(config, parameter_names)
    warnings = []
    if len(config.experimental_rate) <= len(parameters):
        warnings.append(
            'The number of measured points is not greater than the number of '
            'free parameters; the fit may be underdetermined.'
        )
    if config.global_method == 'differential_evolution' and config.local_method:
        warnings.append(
            f"The selected local method ({config.local_method}) is not run "
            'after differential evolution. Its polish option is a separate '
            'SciPy step.'
        )
    if config.local_method in {'CG', 'BFGS'}:
        warnings.append(
            f'{config.local_method} is unconstrained in KinOpt; parameter '
            'bounds will not limit this local search.'
        )
    for bound_set in bound_sets:
        if len(bound_set.bounds) != len(parameters):
            warnings.append(
                f'{bound_set.method} has {len(bound_set.bounds)} bound pair(s) '
                f'for {len(parameters)} free parameter(s).'
            )
            continue
        for parameter, bound in zip(parameters, bound_set.bounds):
            outside_lower = (
                bound.lower is not None
                and parameter.initial_value < bound.lower
            )
            outside_upper = (
                bound.upper is not None
                and parameter.initial_value > bound.upper
            )
            if outside_lower or outside_upper:
                warnings.append(
                    f'The initial value of {parameter.name} '
                    f'({parameter.initial_value:g}) is outside the '
                    f'{bound_set.method} bounds.'
                )

    datasets = tuple(str(name) for name in dataset_names)
    if not datasets:
        datasets = ('Current extracted data',)
    return OptimizationReview(
        datasets=datasets,
        data_points=int(np.size(config.experimental_rate)),
        models=tuple(models),
        parameters=parameters,
        fixed_tg_parameters=fixed_tg_parameters,
        bound_sets=bound_sets,
        global_method=config.global_method or 'None',
        local_method=config.local_method or 'None',
        cost_function=_selection_title('cost_function', cost_name),
        profile_name=profile_name,
        budget=_budget_description(config, len(parameters)),
        warnings=tuple(warnings),
        notes=_guidance_notes(selections),
    )


def _number(value):
    if value is None:
        return 'No limit'
    return format(value, '.6g')


def _list(items):
    return '<ul>' + ''.join(f'<li>{escape(item)}</li>' for item in items) + '</ul>'


def review_to_html(review: OptimizationReview) -> str:
    """Render an optimization review as compact Qt-compatible HTML."""
    model_items = review.models or ('None selected',)
    parameter_rows = ''.join(
        '<tr>'
        f'<td>{escape(parameter.name)}</td>'
        f'<td align="right">{escape(_number(parameter.initial_value))}</td>'
        '</tr>'
        for parameter in review.parameters
    )
    fixed_rows = ''.join(
        '<tr>'
        f'<td>{escape(parameter.name)}</td>'
        f'<td align="right">{escape(_number(parameter.initial_value))}</td>'
        '</tr>'
        for parameter in review.fixed_tg_parameters
    )
    bounds_html = ''
    for bound_set in review.bound_sets:
        rows = ''.join(
            '<tr>'
            f'<td>{escape(bound.name)}</td>'
            f'<td align="right">{escape(_number(bound.lower))}</td>'
            f'<td align="right">{escape(_number(bound.upper))}</td>'
            '</tr>'
            for bound in bound_set.bounds
        )
        bounds_html += (
            f'<h3>{escape(bound_set.method)} bounds</h3>'
            '<table cellspacing="5"><tr><th>Parameter</th><th>Minimum</th>'
            f'<th>Maximum</th></tr>{rows}</table>'
        )
    if not bounds_html:
        bounds_html = '<p>No parameter bounds are supplied to the selected method.</p>'

    profile = review.profile_name or 'Custom or not recorded'
    warnings = (
        _list(review.warnings)
        if review.warnings
        else '<p>No structural warning was detected.</p>'
    )
    return (
        '<h2>Data</h2>'
        f'{_list(review.datasets)}'
        f'<p><b>Measured points:</b> {review.data_points:,}</p>'
        '<h2>Model</h2>'
        f'{_list(model_items)}'
        '<h3>Free parameters and starting values</h3>'
        '<table cellspacing="5"><tr><th>Parameter</th><th>Initial value</th></tr>'
        f'{parameter_rows}</table>'
        + (
            '<h3>Fixed Tg parameters</h3>'
            '<table cellspacing="5"><tr><th>Parameter</th><th>Value</th></tr>'
            f'{fixed_rows}</table>'
            if fixed_rows else ''
        )
        + '<h2>Optimization</h2>'
        '<table cellspacing="5">'
        f'<tr><td><b>Global method</b></td><td>{escape(review.global_method)}</td></tr>'
        f'<tr><td><b>Local method</b></td><td>{escape(review.local_method)}</td></tr>'
        f'<tr><td><b>Cost function</b></td><td>{escape(review.cost_function)}</td></tr>'
        f'<tr><td><b>Last applied profile</b></td><td>{escape(profile)}</td></tr>'
        f'<tr><td><b>Budget</b></td><td>{escape(review.budget)}</td></tr>'
        '</table>'
        '<h2>Bounds</h2>'
        f'{bounds_html}'
        '<h2>Checks before starting</h2>'
        f'{warnings}'
        '<h2>Interpretation notes</h2>'
        f'{_list(review.notes)}'
        '<p><i>This review checks the configuration structure. It does not '
        'guarantee convergence or physical validity.</i></p>'
    )
