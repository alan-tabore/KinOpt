"""User-facing guidance for kinetic and optimization selections."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SelectionGuidance:
    """A short explanation displayed next to a selectable option."""

    title: str
    summary: str
    advice: str
    equation: str = ''
    equation_accessible: str = ''

    @property
    def tooltip(self):
        return f"{self.title}: {self.summary} {self.advice}"


GUIDANCE_BY_KIND = {
    'rate': {
        'rate_for_nth_order': SelectionGuidance(
            'Nth-order model',
            'A simple Arrhenius model with a (1 - alpha)^n conversion term.',
            'Useful as a baseline; it does not describe autocatalytic acceleration.',
            r'\frac{d\alpha}{dt}=A_1 e^{-\frac{E_1}{RT}}(1-\alpha)^n',
            'd alpha over d t equals A1 times e to the power minus E1 over R T, times one minus alpha to the power n.',
        ),
        'rate_for_autocatalytic': SelectionGuidance(
            'Autocatalytic model',
            'Adds an alpha^m term so the reaction can accelerate as conversion grows.',
            'For m > 0, a simulation starting exactly at alpha = 0 predicts zero rate.',
            r'\frac{d\alpha}{dt}=A e^{-\frac{E_a}{RT}}\alpha^m(1-\alpha)^n',
            'd alpha over d t equals A times e to the power minus Ea over R T, times alpha to the power m and one minus alpha to the power n.',
        ),
        'rate_for_kamal': SelectionGuidance(
            'Kamal model',
            'Combines separate ordinary and autocatalytic Arrhenius contributions.',
            'Its six fitted parameters need informative experiments and careful bounds.',
            r'\frac{d\alpha}{dt}=\left[A_1 e^{-\frac{E_1}{RT}}+'
            r'A_2 e^{-\frac{E_2}{RT}}\alpha^m\right](1-\alpha)^n',
            'd alpha over d t equals the sum of the ordinary and autocatalytic Arrhenius terms, times one minus alpha to the power n.',
        ),
    },
    'vitrification': {
        'vitrification_WLF_rate': SelectionGuidance(
            'Continuous WLF vitrification term',
            'Models diffusion limitation from the difference between temperature and Tg.',
            'A Tg law is required; this version can remain nonzero below Tg.',
            r'k_v=A_d e^{\frac{C_1(T-T_g)}{C_2+\left|T-T_g\right|}}',
            'k v equals A d times e to the power C1 times T minus Tg, divided by C2 plus the absolute value of T minus Tg.',
        ),
        'vitrification_WLF_rate_no_reaction_below_Tg': SelectionGuidance(
            'WLF term with a Tg cutoff',
            'Uses the WLF vitrification term and sets it to zero when temperature is at or below Tg.',
            'Choose it only when this abrupt cutoff matches the intended physical assumption.',
            r'k_v=0\;(T\leq T_g),\quad k_v=\mathrm{WLF}\;(T>T_g)',
            'k v equals zero when T is at or below Tg; otherwise k v follows the WLF expression.',
        ),
    },
    'coupling': {
        'coupling_harmonic_mean': SelectionGuidance(
            'Reciprocal-rate coupling',
            'Combines chemical and diffusion rates as 1 / (1/kc + 1/kv).',
            'The slower contribution therefore limits the overall rate.',
            r'k=\frac{1}{\frac{1}{k_c}+\frac{1}{k_v}}',
            'k equals one divided by the sum of one over k c and one over k v.',
        ),
        'coupling_product': SelectionGuidance(
            'Product coupling',
            'Multiplies the chemical and diffusion contributions.',
            'Check that the resulting units and physical interpretation match your model.',
            r'k=k_c k_v',
            'k equals k c times k v.',
        ),
    },
    'tg': {
        'tg_diBennedetto': SelectionGuidance(
            'DiBenedetto Tg law',
            'Describes how glass-transition temperature changes with conversion.',
            'Provide Tg_0 and Tg_inf in kelvin and justify the dimensionless coefficient.',
            r'T_g(\alpha)=T_{g,0}+\frac{(T_{g,\infty}-T_{g,0})\lambda\alpha}{1-(1-\lambda)\alpha}',
            'Tg of alpha equals Tg zero plus the fraction with numerator Tg infinity minus Tg zero, times lambda alpha, and denominator one minus one minus lambda times alpha.',
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
            r'J=\sum_i\left(r_{\mathrm{model},i}-r_{\mathrm{exp},i}\right)^2',
            'J equals the sum over i of the squared difference between modeled and experimental rates.',
        ),
        'rss_mean': SelectionGuidance(
            'Mean squared residual',
            'Averages the squared differences between measured and predicted rates.',
            'Use comparable units and scaling when interpreting values across data sets.',
            r'J=\frac{1}{N}\sum_i\left(r_{\mathrm{model},i}-r_{\mathrm{exp},i}\right)^2',
            'J equals one over N times the sum over i of the squared difference between modeled and experimental rates.',
        ),
        'rss_relative': SelectionGuidance(
            'Relative squared residuals',
            'Divides each rate residual by its measured rate before squaring.',
            'It emphasizes low rates and cannot be used when a measured rate is zero.',
            r'J=\sum_i\left[\frac{r_{\mathrm{model},i}-r_{\mathrm{exp},i}}{r_{\mathrm{exp},i}}\right]^2',
            'J equals the sum over i of the squared relative difference between modeled and experimental rates.',
        ),
        'rss_increase_of_small_extents_impact': SelectionGuidance(
            'Early-conversion weighted residuals',
            'Amplifies residuals below a selected conversion threshold.',
            'Use a weight justified by the experiment because it changes the fitted objective.',
            r'J=\frac{1}{N}\sum_i w_i\left(r_{\mathrm{model},i}-r_{\mathrm{exp},i}\right)^2,\quad w_i=w(\alpha_i)',
            'J equals the mean weighted squared rate residual, with each weight set from conversion alpha i.',
        ),
        'rss_increase_of_small_rates_impact_with_zones': SelectionGuidance(
            'Low-rate-zone weighted residuals',
            'Amplifies residuals where the measured rate is below a selected fraction of its maximum.',
            'This can improve low-rate regions while reducing the relative influence of the peak.',
            r'J=\frac{1}{N}\sum_i w_i\left(r_{\mathrm{model},i}-r_{\mathrm{exp},i}\right)^2,\quad w_i=w(r_{\mathrm{exp},i})',
            'J equals the mean weighted squared rate residual, with each weight set from the experimental rate.',
        ),
    },
}


def selection_guidance_for(kind, name):
    """Return guidance for *name*, or ``None`` for an empty/unknown choice."""
    return GUIDANCE_BY_KIND.get(kind, {}).get(name)
