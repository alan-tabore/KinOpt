"""Import KinOpt's historical human-readable optimization result files."""

import ast
from dataclasses import dataclass
from pathlib import Path
import re

import numpy as np
from scipy import optimize
from scipy.optimize import OptimizeResult

from kinopt.src import kinetic_models, optimization
from kinopt.src.optimization_runner import (
    OptimizationRunConfig,
    OptimizationRunResult,
)


@dataclass(frozen=True)
class LegacyImportedResult:
    """Structured completed run recovered from one historical text file."""

    name: str
    config: OptimizationRunConfig
    outcome: OptimizationRunResult


def _sections(text):
    matches = list(
        re.finditer(r"^=+\s*(.*?)\s*=+\s*$", text, flags=re.MULTILINE)
    )
    result = {}
    for index, match in enumerate(matches):
        start = match.end()
        stop = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[match.group(1).strip()] = text[start:stop].strip()
    return result


def _line_value(section, label, required=True):
    match = re.search(
        rf"^{re.escape(label)}:\s*(.+?)\s*$",
        section,
        flags=re.MULTILINE,
    )
    if match is None:
        if required:
            raise ValueError(f"Missing legacy result field: {label}")
        return None
    return match.group(1).strip()


def _literal(value, label):
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError) as error:
        raise ValueError(f"Invalid legacy {label}: {value}") from error


def _parameter_block(section, heading):
    match = re.search(
        rf"^{re.escape(heading)}:\s*$([\s\S]*?)(?=^\S.*:\s*$|\Z)",
        section,
        flags=re.MULTILINE,
    )
    if match is None:
        return ()
    values = []
    for line in match.group(1).splitlines():
        item = re.match(r"^-\s*[^:]+:\s*(.+?)\s*$", line.strip())
        if item is not None:
            values.append(float(item.group(1)))
    return tuple(values)


def _initial_values(section, heading):
    return _parameter_block(section, heading)


def _parse_data(section):
    lines = [line for line in section.splitlines() if line.strip()]
    if len(lines) < 3:
        raise ValueError("Legacy result data need a header and at least two rows.")
    headers = lines[0].split("\t")
    if len(headers) % 4:
        raise ValueError("Legacy result data columns are not grouped by experiment.")
    try:
        matrix = np.asarray(
            [[float(value) for value in line.split("\t")] for line in lines[1:]],
            dtype=float,
        )
    except ValueError as error:
        raise ValueError("Legacy result data contain a nonnumeric value.") from error
    if matrix.ndim != 2 or matrix.shape[1] != len(headers):
        raise ValueError("Legacy result data rows have inconsistent column counts.")

    experiments = []
    for start in range(0, matrix.shape[1], 4):
        values = matrix[:, start:start + 4]
        missing_rows = np.all(np.isnan(values), axis=1)
        if np.any(np.isnan(values[~missing_rows])):
            raise ValueError("Legacy result data contain partially missing rows.")
        values = values[~missing_rows]
        if len(values) < 2 or not np.all(np.isfinite(values)):
            raise ValueError("Each legacy experiment needs two finite data rows.")
        if np.any(np.diff(values[:, 0]) <= 0):
            raise ValueError("Legacy experiment time must increase strictly.")
        experiments.append(tuple(values[:, column] for column in range(4)))
    combined = tuple(
        np.concatenate([experiment[column] for experiment in experiments])
        for column in range(4)
    )
    return tuple(experiments), combined


def _experimental_arguments(labels, combined, experiments, *, skip_tg=False):
    time, temperature, rate, extent = combined
    lists = tuple(tuple(experiment[index] for experiment in experiments) for index in range(4))
    values = {
        "time": time,
        "T": temperature,
        "rate": rate,
        "extent": extent,
        "time_lists": lists[0],
        "temperature_lists": lists[1],
        "rate_lists": lists[2],
        "conv_lists": lists[3],
    }
    arguments = []
    for label in labels:
        if skip_tg and label == "Tg":
            continue
        if label not in values:
            raise ValueError(f"Unsupported legacy experimental parameter: {label}")
        arguments.append(values[label])
    return tuple(arguments)


def _model_section(sections, name, law_label, guess_heading):
    section = sections.get(name)
    if section is None:
        return None, (), ()
    law_name = _line_value(section, law_label)
    law = getattr(kinetic_models, law_name, None)
    if not callable(law):
        raise ValueError(f"Unknown legacy kinetic law: {law_name}")
    labels = tuple(
        _literal(
            _line_value(
                section,
                next(
                    line.split(":", 1)[0]
                    for line in section.splitlines()
                    if "Experimental parameters" in line
                ),
            ),
            "experimental parameters",
        )
    )
    initial = _initial_values(section, guess_heading)
    return law, labels, initial


def import_legacy_result(path):
    """Parse one historical result file into a queue-ready completed run."""
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    sections = _sections(text)
    if "Results" not in sections or "Data used for optimization" not in sections:
        raise ValueError("This file does not contain a complete KinOpt result.")

    experiments, combined = _parse_data(sections["Data used for optimization"])
    rate_law, rate_labels, rate_initial = _model_section(
        sections,
        "Rate",
        "Rate law",
        "Rate parameters initial guess",
    )
    vitrification_law, vitrification_labels, vitrification_initial = _model_section(
        sections,
        "Vitrification",
        "Vitrification law",
        "Vitrification parameters initial guess",
    )
    coupling_law, _, coupling_initial = _model_section(
        sections,
        "Coupling",
        "Coupling law",
        "Coupling parameters initial guess",
    )
    tg_law, tg_labels, _ = _model_section(
        sections,
        "Tg",
        "Tg law",
        "Tg parameters",
    )
    tg_args = (
        ()
        if "Tg" not in sections
        else _parameter_block(sections["Tg"], "Tg parameters")
    )

    cost_section = sections.get("Cost Function", "")
    cost_name = _line_value(cost_section, "Cost function")
    cost_function = getattr(optimization, cost_name, None)
    if not callable(cost_function):
        raise ValueError(f"Unknown legacy cost function: {cost_name}")
    cost_labels = tuple(
        _literal(
            _line_value(
                cost_section,
                "Experimental parameters for cost function computation",
            ),
            "cost-function parameters",
        )
    )
    cost_args = tuple(
        _literal(
            _line_value(cost_section, "Cost function parameters"),
            "cost-function arguments",
        )
    )

    results_section = sections["Results"]
    result_parameters = (
        _parameter_block(results_section, "Rate optimization results")
        + _parameter_block(results_section, "Vitrification optimization results")
        + _parameter_block(results_section, "Coupling optimization results")
    )
    if not result_parameters:
        raise ValueError("The legacy result has no fitted parameters.")
    initial_guess = rate_initial + vitrification_initial + coupling_initial
    if len(initial_guess) != len(result_parameters):
        initial_guess = result_parameters
    final_cost = float(_line_value(results_section, "Final cost function value"))
    duration_text = _line_value(
        results_section,
        "Total time for optimization",
        required=False,
    )
    elapsed_seconds = 0.0 if duration_text is None else float(duration_text)
    success_match = re.search(r"^\s*success:\s*(True|False)", results_section, re.MULTILINE)
    evaluations_match = re.search(r"^\s*nfev:\s*(\d+)", results_section, re.MULTILINE)
    iterations_match = re.search(r"^\s*nit:\s*(\d+)", results_section, re.MULTILINE)

    config = OptimizationRunConfig(
        cost_function=cost_function,
        initial_guess=np.asarray(initial_guess, dtype=float),
        global_method="",
        global_optimizer=None,
        global_options=None,
        local_method="Nelder-Mead",
        local_optimizer=optimize.minimize,
        local_options={
            "method": "Nelder-Mead",
            "options": {"maxiter": max(1, int(iterations_match.group(1)) if iterations_match else 1)},
        },
        experimental_rate=combined[2],
        rate_law=rate_law,
        experimental_args_for_rate=_experimental_arguments(
            rate_labels, combined, experiments
        ),
        rate_parameter_count=len(rate_initial),
        vitrification_law=vitrification_law,
        experimental_args_for_vitrification=_experimental_arguments(
            vitrification_labels,
            combined,
            experiments,
            skip_tg=True,
        ),
        vitrification_parameter_count=len(vitrification_initial),
        coupling_law=coupling_law,
        experimental_args_for_coupling=(),
        tg_law=tg_law,
        experimental_args_for_tg=_experimental_arguments(
            tg_labels, combined, experiments
        ),
        tg_args=tg_args or None,
        cost_function_args=cost_args,
        experimental_args_for_cost_function=_experimental_arguments(
            cost_labels, combined, experiments
        ),
        max_iterations=max(1, int(iterations_match.group(1)) if iterations_match else 1),
        experiment_lengths=tuple(len(experiment[0]) for experiment in experiments),
    )
    result = OptimizeResult(
        x=np.asarray(result_parameters, dtype=float),
        fun=final_cost,
        success=(None if success_match is None else success_match.group(1) == "True"),
        message="Imported from a legacy KinOpt text result.",
        nit=None if iterations_match is None else int(iterations_match.group(1)),
        nfev=None if evaluations_match is None else int(evaluations_match.group(1)),
    )
    return LegacyImportedResult(
        name=f"Imported legacy result - {source.stem}",
        config=config,
        outcome=OptimizationRunResult(result, elapsed_seconds),
    )
