"""Metadata and packaged file locations for guided KinOpt examples."""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


@dataclass(frozen=True)
class IncludedExample:
    """A reproducible starting workflow distributed with KinOpt."""

    title: str
    description: str
    file_names: Tuple[str, ...]
    delimiter: str
    has_header: bool
    rate_model: str
    local_method: str
    cost_function: str
    calculation_profile: str


KAMAL_EXAMPLE = IncludedExample(
    title="Kamal model — four heating rates",
    description=(
        "Four synthetic non-isothermal experiments at 5, 10, 15, and "
        "20 °C/min. They demonstrate data extraction and a six-parameter "
        "Kamal rate model."
    ),
    file_names=(
        "data_kamal_heating_rate_5C_per_min.txt",
        "data_kamal_heating_rate_10C_per_min.txt",
        "data_kamal_heating_rate_15C_per_min.txt",
        "data_kamal_heating_rate_20C_per_min.txt",
    ),
    delimiter=",",
    has_header=True,
    rate_model="rate_for_kamal",
    local_method="Nelder-Mead",
    cost_function="rss_mean",
    calculation_profile="Quick check",
)


def included_example_files(example=KAMAL_EXAMPLE):
    """Return existing filesystem paths for one packaged example."""
    data_directory = Path(__file__).resolve().parent / "data"
    paths = tuple(data_directory / name for name in example.file_names)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "The included example is incomplete; missing: " + ", ".join(missing)
        )
    return paths
