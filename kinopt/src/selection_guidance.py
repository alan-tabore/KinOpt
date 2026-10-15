"""User-facing guidance for kinetic and optimization selections."""

from dataclasses import dataclass

from kinopt.src.model_metadata import KINETIC_MODELS


@dataclass(frozen=True)
class SelectionGuidance:
    """A short explanation displayed next to a selectable option."""

    title: str
    summary: str
    advice: str
    equation: str = ''

    @property
    def tooltip(self):
        return f"{self.title}: {self.summary} {self.advice}"


GUIDANCE_BY_KIND = {
    'global_optimization': {
        'basinhopping': SelectionGuidance(
            'Basin-hopping',
            'Alternates random moves with local minimizations to leave some local minima.',
            'It depends on the starting point and random path; compare repeated runs.',
        ),
        'differential_evolution': SelectionGuidance(
            'Differential evolution',
            'Explores required parameter bounds with a population of candidates.',
            'It is robust but evaluation-intensive; keep the total worker budget under control.',
        ),
        'shgo': SelectionGuidance(
            'SHGO',
            'Samples bounded parameter space and launches local searches from promising points.',
            'It is systematic, but its cost can grow quickly with dimension and sampling effort.',
        ),
    },
    'local_optimization': {
        'least_squares_log': SelectionGuidance(
            'Log-space least squares',
            'Fits the rate residuals directly while scaling every positive parameter logarithmically.',
            'Recommended for positive kinetic parameters with justified bounds; keep jac on auto, and do not combine it with a global method.',
        ),
        'Nelder-Mead': SelectionGuidance(
            'Nelder-Mead',
            'A derivative-free local search that moves a simplex through parameter space.',
            'It is a useful first pass but can be slow and sensitive to parameter scales.',
        ),
        'CG': SelectionGuidance(
            'Conjugate gradient',
            'A local method for smooth objectives that follows gradient-based directions.',
            'This option is unconstrained and works best with well-scaled parameters; keep jac on auto to use analytic derivatives when available.',
        ),
        'BFGS': SelectionGuidance(
            'BFGS',
            'A local method that builds an approximation of objective curvature.',
            'This option is unconstrained and depends on the initial guess; keep jac on auto to use analytic derivatives when available.',
        ),
        'L-BFGS-B': SelectionGuidance(
            'L-BFGS-B',
            'A memory-efficient local method for smooth objectives with parameter bounds.',
            'It is a strong bounded local choice; keep jac on auto, and compare solutions from justified starting values.',
        ),
    },
    'cost_function': {
        'rss_standard': SelectionGuidance(
            'Sum of squared residuals',
            'Adds the squared differences between measured and predicted rates.',
            'Experiments containing more points have more influence on the total.',
            'J = Σ (r<sub>model,i</sub> − r<sub>exp,i</sub>)<sup>2</sup>',
        ),
        'rss_mean': SelectionGuidance(
            'Mean squared residual',
            'Averages the squared differences between measured and predicted rates.',
            'Use comparable units and scaling when interpreting values across data sets.',
            'J = (1/N) Σ (r<sub>model,i</sub> − r<sub>exp,i</sub>)<sup>2</sup>',
        ),
        'rss_relative': SelectionGuidance(
            'Relative squared residuals',
            'Divides each rate residual by its measured rate before squaring.',
            'It emphasizes low rates and cannot be used when a measured rate is zero.',
            'J = Σ [(r<sub>model,i</sub> − r<sub>exp,i</sub>)'
            '/r<sub>exp,i</sub>]<sup>2</sup>',
        ),
        'rss_increase_of_small_extents_impact': SelectionGuidance(
            'Early-conversion weighted residuals',
            'Amplifies residuals below a selected conversion threshold.',
            'Use a weight justified by the experiment because it changes the fitted objective.',
            'J = (1/N) Σ w<sub>i</sub>(r<sub>model,i</sub> − '
            'r<sub>exp,i</sub>)<sup>2</sup>, with w<sub>i</sub> set by α',
        ),
        'rss_increase_of_small_rates_impact_with_zones': SelectionGuidance(
            'Low-rate-zone weighted residuals',
            'Amplifies residuals where the measured rate is below a selected fraction of its maximum.',
            'This can improve low-rate regions while reducing the relative influence of the peak.',
            'J = (1/N) Σ w<sub>i</sub>(r<sub>model,i</sub> − '
            'r<sub>exp,i</sub>)<sup>2</sup>, with w<sub>i</sub> set by rate',
        ),
    },
}

for metadata in KINETIC_MODELS:
    GUIDANCE_BY_KIND.setdefault(metadata.kind, {})[
        metadata.function_name
    ] = SelectionGuidance(
        metadata.display_name,
        metadata.summary,
        metadata.advice,
        metadata.equation,
    )


def selection_guidance_for(kind, name):
    """Return guidance for *name*, or ``None`` for an empty/unknown choice."""
    return GUIDANCE_BY_KIND.get(kind, {}).get(name)
