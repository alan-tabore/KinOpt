"""User-facing guidance for kinetic and optimization selections."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SelectionGuidance:
    """A short explanation displayed next to a selectable option."""

    title: str
    summary: str
    advice: str

    @property
    def tooltip(self):
        return f"{self.title}: {self.summary} {self.advice}"


GUIDANCE_BY_KIND = {
    'rate': {
        'rate_for_nth_order': SelectionGuidance(
            'Nth-order model',
            'A simple Arrhenius model with a (1 - alpha)^n conversion term.',
            'Useful as a baseline; it does not describe autocatalytic acceleration.',
        ),
        'rate_for_autocatalytic': SelectionGuidance(
            'Autocatalytic model',
            'Adds an alpha^m term so the reaction can accelerate as conversion grows.',
            'For m > 0, a simulation starting exactly at alpha = 0 predicts zero rate.',
        ),
        'rate_for_kamal': SelectionGuidance(
            'Kamal model',
            'Combines separate ordinary and autocatalytic Arrhenius contributions.',
            'Its six fitted parameters need informative experiments and careful bounds.',
        ),
    },
    'vitrification': {
        'vitrification_WLF_rate': SelectionGuidance(
            'Continuous WLF vitrification term',
            'Models diffusion limitation from the difference between temperature and Tg.',
            'A Tg law is required; this version can remain nonzero below Tg.',
        ),
        'vitrification_WLF_rate_no_reaction_below_Tg': SelectionGuidance(
            'WLF term with a Tg cutoff',
            'Uses the WLF vitrification term and sets it to zero when temperature is at or below Tg.',
            'Choose it only when this abrupt cutoff matches the intended physical assumption.',
        ),
    },
    'coupling': {
        'coupling_harmonic_mean': SelectionGuidance(
            'Reciprocal-rate coupling',
            'Combines chemical and diffusion rates as 1 / (1/kc + 1/kv).',
            'The slower contribution therefore limits the overall rate.',
        ),
        'coupling_product': SelectionGuidance(
            'Product coupling',
            'Multiplies the chemical and diffusion contributions.',
            'Check that the resulting units and physical interpretation match your model.',
        ),
    },
    'tg': {
        'tg_diBennedetto': SelectionGuidance(
            'DiBenedetto Tg law',
            'Describes how glass-transition temperature changes with conversion.',
            'Provide Tg_0 and Tg_inf in kelvin and justify the dimensionless coefficient.',
        ),
    },
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
        'Nelder-Mead': SelectionGuidance(
            'Nelder-Mead',
            'A derivative-free local search that moves a simplex through parameter space.',
            'It is a useful first pass but can be slow and sensitive to parameter scales.',
        ),
        'CG': SelectionGuidance(
            'Conjugate gradient',
            'A local method for smooth objectives that follows gradient-based directions.',
            'This KinOpt option is unconstrained and works best with well-scaled parameters.',
        ),
        'BFGS': SelectionGuidance(
            'BFGS',
            'A local method that builds an approximation of objective curvature.',
            'This KinOpt option is unconstrained and still depends on the initial guess.',
        ),
        'L-BFGS-B': SelectionGuidance(
            'L-BFGS-B',
            'A memory-efficient local method for smooth objectives with parameter bounds.',
            'It is a strong bounded local choice, but the initial guess can select the final minimum.',
        ),
    },
    'cost_function': {
        'rss_standard': SelectionGuidance(
            'Sum of squared residuals',
            'Adds the squared differences between measured and predicted rates.',
            'Experiments containing more points have more influence on the total.',
        ),
        'rss_mean': SelectionGuidance(
            'Mean squared residual',
            'Averages the squared differences between measured and predicted rates.',
            'Use comparable units and scaling when interpreting values across data sets.',
        ),
        'rss_relative': SelectionGuidance(
            'Relative squared residuals',
            'Divides each rate residual by its measured rate before squaring.',
            'It emphasizes low rates and cannot be used when a measured rate is zero.',
        ),
        'rss_increase_of_small_extents_impact': SelectionGuidance(
            'Early-conversion weighted residuals',
            'Amplifies residuals below a selected conversion threshold.',
            'Use a weight justified by the experiment because it changes the fitted objective.',
        ),
        'rss_increase_of_small_rates_impact_with_zones': SelectionGuidance(
            'Low-rate-zone weighted residuals',
            'Amplifies residuals where the measured rate is below a selected fraction of its maximum.',
            'This can improve low-rate regions while reducing the relative influence of the peak.',
        ),
    },
}


def selection_guidance_for(kind, name):
    """Return guidance for *name*, or ``None`` for an empty/unknown choice."""
    return GUIDANCE_BY_KIND.get(kind, {}).get(name)
