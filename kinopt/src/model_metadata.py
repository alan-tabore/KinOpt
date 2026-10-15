"""Central user-facing metadata for KinOpt's supported kinetic models."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class ModelParameterMetadata:
    """Meaning, unit, and illustrative values for one model parameter."""

    name: str
    label: str
    role: str
    unit: str
    example: str
    lower_bound: Optional[str] = None
    upper_bound: Optional[str] = None


@dataclass(frozen=True)
class KineticModelMetadata:
    """One selectable model and the information needed to present it."""

    kind: str
    function_name: str
    display_name: str
    summary: str
    advice: str
    equation: str
    experimental_parameters: Tuple[str, ...]
    parameters: Tuple[ModelParameterMetadata, ...]

    @property
    def function_parameters(self):
        return self.experimental_parameters + tuple(
            parameter.name for parameter in self.parameters
        )


PREEXPONENTIAL_A = ModelParameterMetadata(
    "A",
    "A",
    "Pre-exponential factor for the Arrhenius contribution.",
    "s^-1",
    "1e8",
    "1",
    "1e20",
)
PREEXPONENTIAL_A1 = ModelParameterMetadata(
    "A1",
    "A₁",
    "Pre-exponential factor for the ordinary Arrhenius contribution.",
    "s^-1",
    "1e8",
    "1",
    "1e20",
)
PREEXPONENTIAL_A2 = ModelParameterMetadata(
    "A2",
    "A₂",
    "Pre-exponential factor for the autocatalytic Arrhenius contribution.",
    "s^-1",
    "1e8",
    "1",
    "1e20",
)
ACTIVATION_E = ModelParameterMetadata(
    "E",
    "E",
    "Activation energy for the Arrhenius contribution.",
    "J/mol",
    "50000",
    "1000",
    "350000",
)
ACTIVATION_EA = ModelParameterMetadata(
    "Ea",
    "Eₐ",
    "Activation energy for the autocatalytic model.",
    "J/mol",
    "50000",
    "1000",
    "350000",
)
ACTIVATION_E1 = ModelParameterMetadata(
    "E1",
    "E₁",
    "Activation energy for the ordinary Arrhenius contribution.",
    "J/mol",
    "50000",
    "1000",
    "350000",
)
ACTIVATION_E2 = ModelParameterMetadata(
    "E2",
    "E₂",
    "Activation energy for the autocatalytic Arrhenius contribution.",
    "J/mol",
    "50000",
    "1000",
    "350000",
)
ORDER_M = ModelParameterMetadata(
    "m",
    "m",
    "Reaction order applied to the conversion term alpha.",
    "",
    "2",
    "0.1",
    "20",
)
ORDER_N = ModelParameterMetadata(
    "n",
    "n",
    "Reaction order applied to the remaining-conversion term.",
    "",
    "2",
    "0.1",
    "20",
)
VITRIFICATION_AD = ModelParameterMetadata(
    "Ad",
    "A_d",
    "Pre-exponential factor for the diffusion-limited contribution.",
    "s^-1",
    "1",
    "1e-20",
    "1e20",
)
WLF_C1 = ModelParameterMetadata(
    "C1",
    "C₁",
    "Dimensionless sensitivity in the WLF-like expression.",
    "",
    "50",
    "1",
    "350",
)
WLF_C2 = ModelParameterMetadata(
    "C2",
    "C₂",
    "Temperature scale in the WLF-like denominator.",
    "K",
    "50",
    "1",
    "350",
)
TG_ZERO = ModelParameterMetadata(
    "Tg_0",
    "Tg,0",
    "Glass-transition temperature of the uncured material.",
    "K",
    "290",
)
TG_INFINITY = ModelParameterMetadata(
    "Tg_inf",
    "Tg,∞",
    "Glass-transition temperature of the fully cured material.",
    "K",
    "450",
)
TG_COEFFICIENT = ModelParameterMetadata(
    "coeff",
    "λ",
    "DiBenedetto coefficient related to heat-capacity changes.",
    "",
    "0.5",
)

MODEL_PARAMETERS = (
    PREEXPONENTIAL_A,
    PREEXPONENTIAL_A1,
    PREEXPONENTIAL_A2,
    ACTIVATION_E,
    ACTIVATION_EA,
    ACTIVATION_E1,
    ACTIVATION_E2,
    ORDER_M,
    ORDER_N,
    VITRIFICATION_AD,
    WLF_C1,
    WLF_C2,
    TG_ZERO,
    TG_INFINITY,
    TG_COEFFICIENT,
)


KINETIC_MODELS = (
    KineticModelMetadata(
        "rate",
        "rate_for_nth_order",
        "Nth-order model",
        "A simple Arrhenius model with a (1 - alpha)^n conversion term.",
        "Useful as a baseline; it does not describe autocatalytic acceleration.",
        "<i>dα/dt</i> = A<sub>1</sub> exp(−E<sub>1</sub>/(RT)) "
        "(1 − α)<sup>n</sup>",
        ("extent", "T"),
        (PREEXPONENTIAL_A1, ACTIVATION_E1, ORDER_N),
    ),
    KineticModelMetadata(
        "rate",
        "rate_for_autocatalytic",
        "Autocatalytic model",
        "Adds an alpha^m term so the reaction can accelerate as conversion grows.",
        "For m > 0, a simulation starting exactly at alpha = 0 predicts zero rate.",
        "<i>dα/dt</i> = A exp(−E<sub>a</sub>/(RT)) "
        "α<sup>m</sup>(1 − α)<sup>n</sup>",
        ("extent", "T"),
        (PREEXPONENTIAL_A, ACTIVATION_EA, ORDER_M, ORDER_N),
    ),
    KineticModelMetadata(
        "rate",
        "rate_for_kamal",
        "Kamal model",
        "Combines separate ordinary and autocatalytic Arrhenius contributions.",
        "Its six fitted parameters need informative experiments and careful bounds.",
        "<i>dα/dt</i> = [A<sub>1</sub> exp(−E<sub>1</sub>/(RT)) + "
        "A<sub>2</sub> exp(−E<sub>2</sub>/(RT)) α<sup>m</sup>] "
        "(1 − α)<sup>n</sup>",
        ("extent", "T"),
        (
            PREEXPONENTIAL_A1,
            ACTIVATION_E1,
            PREEXPONENTIAL_A2,
            ACTIVATION_E2,
            ORDER_M,
            ORDER_N,
        ),
    ),
    KineticModelMetadata(
        "vitrification",
        "vitrification_WLF_rate",
        "Continuous WLF vitrification term",
        "Models diffusion limitation from the difference between temperature and Tg.",
        "A Tg law is required; this version can remain nonzero below Tg.",
        "k<sub>v</sub> = A<sub>d</sub> exp[C<sub>1</sub>"
        "(T − T<sub>g</sub>)/(C<sub>2</sub> + |T − T<sub>g</sub>|)]",
        ("T", "Tg"),
        (VITRIFICATION_AD, WLF_C1, WLF_C2),
    ),
    KineticModelMetadata(
        "vitrification",
        "vitrification_WLF_rate_no_reaction_below_Tg",
        "WLF term with a Tg cutoff",
        "Uses the WLF term and sets it to zero at or below Tg.",
        "Choose it only when this abrupt cutoff matches the physical assumption.",
        "k<sub>v</sub> = 0 for T ≤ T<sub>g</sub>; WLF expression otherwise",
        ("T", "Tg"),
        (VITRIFICATION_AD, WLF_C1, WLF_C2),
    ),
    KineticModelMetadata(
        "coupling",
        "coupling_harmonic_mean",
        "Reciprocal-rate coupling",
        "Combines chemical and diffusion rates as 1 / (1/kc + 1/kv).",
        "The slower contribution therefore limits the overall rate.",
        "k = 1/(1/k<sub>c</sub> + 1/k<sub>v</sub>)",
        ("kc", "kv", "experimental_parameters"),
        (),
    ),
    KineticModelMetadata(
        "coupling",
        "coupling_product",
        "Product coupling",
        "Multiplies the chemical and diffusion contributions.",
        "Check that the resulting units and interpretation match your model.",
        "k = k<sub>c</sub> k<sub>v</sub>",
        ("kc", "kv", "experimental_parameters"),
        (),
    ),
    KineticModelMetadata(
        "tg",
        "tg_diBennedetto",
        "DiBenedetto Tg law",
        "Describes how glass-transition temperature changes with conversion.",
        "Provide Tg_0 and Tg_inf in kelvin and justify the dimensionless coefficient.",
        "T<sub>g</sub>(α) = T<sub>g,0</sub> + "
        "(T<sub>g,∞</sub> − T<sub>g,0</sub>)λα/[1 − (1 − λ)α]",
        ("extent",),
        (TG_ZERO, TG_INFINITY, TG_COEFFICIENT),
    ),
)


_MODEL_BY_KEY = {
    (metadata.kind, metadata.function_name): metadata
    for metadata in KINETIC_MODELS
}


def kinetic_model_metadata(kind, function_name):
    """Return metadata for one selectable model, or ``None`` if unknown."""
    return _MODEL_BY_KEY.get((kind, function_name))


def kinetic_model_names(kind):
    """Return selectable function names for one model family."""
    return tuple(
        metadata.function_name
        for metadata in KINETIC_MODELS
        if metadata.kind == kind
    )


def model_parameter_metadata(name):
    """Return shared metadata for a named model parameter."""
    for parameter in MODEL_PARAMETERS:
        if parameter.name == name:
            return parameter
    return None
