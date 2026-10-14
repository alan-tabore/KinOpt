"""Coverage for the selectable-model guidance catalogue."""

from kinopt.src.main import (
    get_functions_for_kinetics,
    get_functions_for_optimization,
)
from kinopt.src.selection_guidance import selection_guidance_for


def test_every_selectable_model_and_optimization_option_has_guidance():
    rate, vitrification, coupling, tg = get_functions_for_kinetics()
    global_methods, local_methods, cost_functions = get_functions_for_optimization()

    selections = {
        'rate': rate,
        'vitrification': vitrification,
        'coupling': coupling,
        'tg': tg,
        'global_optimization': global_methods,
        'local_optimization': local_methods,
        'cost_function': cost_functions,
    }
    missing = {
        kind: [name for name in names if selection_guidance_for(kind, name) is None]
        for kind, names in selections.items()
    }

    assert not {kind: names for kind, names in missing.items() if names}


def test_guidance_contains_a_title_explanation_and_practical_advice():
    guidance = selection_guidance_for('rate', 'rate_for_kamal')

    assert guidance.title == 'Kamal model'
    assert 'autocatalytic' in guidance.summary
    assert 'six fitted parameters' in guidance.advice
    assert guidance.title in guidance.tooltip


def test_unknown_or_empty_selection_has_no_guidance():
    assert selection_guidance_for('rate', '') is None
    assert selection_guidance_for('unknown', 'rate_for_kamal') is None
