"""Load and validate kinetic data stored as time, temperature, rate and conversion."""

import csv
from dataclasses import dataclass
import os
import warnings

import numpy as np
from scipy.integrate import trapezoid


TIME_UNITS = {"seconds": 1.0, "minutes": 60.0}
TEMPERATURE_UNITS = {"kelvin": (1.0, 0.0), "celsius": (1.0, 273.15)}
RATE_UNITS = {"per_second": 1.0, "per_minute": 1.0 / 60.0}
EXTENT_UNITS = {"fraction": 1.0, "percent": 0.01}


@dataclass(frozen=True)
class DataImportSettings:
    """Describe how columns and units in an experimental file are interpreted."""

    delimiter: str = ","
    has_header: bool = False
    skip_lines: int = 0
    columns: tuple = (0, 1, 2, 3)
    time_unit: str = "seconds"
    temperature_unit: str = "kelvin"
    rate_unit: str = "per_second"
    extent_unit: str = "fraction"

    def __post_init__(self):
        if not isinstance(self.skip_lines, (int, np.integer)) or self.skip_lines < 0:
            raise ValueError(
                "The number of lines to skip must be a nonnegative integer."
            )
        if len(self.columns) != 4:
            raise ValueError("Select one column for time, temperature, rate, and extent.")
        if any(isinstance(value, bool) or not isinstance(value, (int, np.integer))
               or value < 0 for value in self.columns):
            raise ValueError("Column indices must be nonnegative integers.")
        if len(set(int(value) for value in self.columns)) != 4:
            raise ValueError("Time, temperature, rate, and extent need distinct columns.")
        if not isinstance(self.delimiter, str) or not self.delimiter:
            raise ValueError("The delimiter cannot be empty.")
        if len(self.delimiter) != 1:
            raise ValueError("The delimiter must be one character.")
        for value, allowed, label in (
            (self.time_unit, TIME_UNITS, "time unit"),
            (self.temperature_unit, TEMPERATURE_UNITS, "temperature unit"),
            (self.rate_unit, RATE_UNITS, "rate unit"),
            (self.extent_unit, EXTENT_UNITS, "extent unit"),
        ):
            if value not in allowed:
                raise ValueError(f"Unknown {label}: {value!r}")


def normalize_delimiter(value):
    """Translate the two documented tab spellings into one character."""
    text = str(value)
    if text.lower() == "tab" or text == "\\t":
        return "\t"
    return text or ","


def preview_delimited_file(file_path, delimiter=",", skip_lines=0, max_rows=8):
    """Return a small textual preview without interpreting units or columns."""
    delimiter = normalize_delimiter(delimiter)
    if len(delimiter) != 1:
        raise ValueError("The delimiter must be one character.")
    if not isinstance(skip_lines, (int, np.integer)) or skip_lines < 0:
        raise ValueError("The number of lines to skip must be a nonnegative integer.")
    if max_rows < 1:
        raise ValueError("The preview must contain at least one row.")
    rows = []
    with open(file_path, "r", encoding="utf-8-sig", newline="") as stream:
        for _ in range(int(skip_lines)):
            next(stream, None)
        reader = csv.reader(stream, delimiter=delimiter)
        for row in reader:
            if row:
                rows.append(tuple(cell.strip() for cell in row))
            if len(rows) >= max_rows:
                break
    if not rows:
        raise ValueError(f"File {os.path.basename(file_path)} contains no previewable data.")
    return tuple(rows)


def _validate_and_trim(data, name):
    if data.shape[0] < 2 or data.shape[1] != 4:
        raise ValueError("at least two rows and four selected columns are required")
    if not np.all(np.isfinite(data)):
        raise ValueError("data contain missing or non-finite values")
    time, temperature, rate, extent = data.T
    if np.any(np.diff(time) <= 0):
        raise ValueError("time must be strictly increasing")
    if np.any(temperature <= 0):
        raise ValueError("temperature must be positive after conversion to Kelvin")
    if np.any((extent < 0) | (extent > 1)):
        raise ValueError("extent of reaction must be between 0 and 1")
    if np.any(np.diff(extent) < 0):
        raise ValueError("extent of reaction must be nondecreasing")
    if not np.isclose(trapezoid(rate, time), extent[-1] - extent[0]):
        raise ValueError("integral of rate does not match the recorded change in extent")

    if np.any(temperature < 173.15):
        warnings.warn(
            f"File {name}: check that temperatures are in Kelvin, not Celsius.",
            UserWarning,
        )
    if extent[0] == 0:
        warnings.warn(
            f"File {name}: zero initial extent needs care when simulating an "
            "autocatalytic model.",
            UserWarning,
        )
    stop = np.flatnonzero(extent >= 1)
    end = int(stop[0]) + 1 if stop.size else len(extent)
    return tuple(column[:end].copy() for column in (time, temperature, rate, extent))


def extract_configured_data_single_file(file_path, settings):
    """Load selected columns, convert their units, and validate one experiment."""
    if not isinstance(settings, DataImportSettings):
        raise TypeError("settings must be DataImportSettings.")
    name = os.path.basename(file_path)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="loadtxt: input contained no data")
            data = np.loadtxt(
                file_path,
                delimiter=settings.delimiter,
                skiprows=settings.skip_lines + int(settings.has_header),
                usecols=tuple(int(value) for value in settings.columns),
                ndmin=2,
            )
        data = np.asarray(data, dtype=float)
        data[:, 0] *= TIME_UNITS[settings.time_unit]
        temperature_scale, temperature_offset = TEMPERATURE_UNITS[
            settings.temperature_unit
        ]
        data[:, 1] = data[:, 1] * temperature_scale + temperature_offset
        data[:, 2] *= RATE_UNITS[settings.rate_unit]
        data[:, 3] *= EXTENT_UNITS[settings.extent_unit]
        return _validate_and_trim(data, name)
    except ValueError as exc:
        raise ValueError(f"Error in file {name}: {exc}") from exc


def extract_configured_data_multiple_files(file_paths, settings):
    """Load several files with one shared mapping and concatenate the results."""
    if isinstance(file_paths, (str, os.PathLike)):
        raise ValueError("Provide a list of data files, not a single path.")
    datasets = [
        extract_configured_data_single_file(path, settings)
        for path in file_paths
    ]
    if not datasets:
        raise ValueError("Please select at least one data file.")
    return tuple(np.concatenate(columns) for columns in zip(*datasets))


def extract_dsc_data_single_file(file_path, delimiter=',', has_header=False, skip_lines=0):
    """Return four arrays, validating the complete file before trimming at conversion 1.

    Times must increase strictly, temperatures must be positive (Kelvin), and
    conversions must be nondecreasing and within [0, 1]. At least two rows and
    four columns are required. Extra columns are ignored for compatibility.
    The integral of rate must match the recorded conversion change, using the
    existing NumPy isclose tolerances (rtol=1e-5, atol=1e-8).

    Invalid input raises ValueError with the file name; filesystem failures
    raise OSError. Suspicious units produce a warning without changing data.
    """
    settings = DataImportSettings(
        delimiter=normalize_delimiter(delimiter),
        has_header=bool(has_header),
        skip_lines=skip_lines,
    )
    return extract_configured_data_single_file(file_path, settings)


def extract_dsc_data_multiple_files(file_paths, delimiter=',', has_header=False, skip_lines=0):
    """Validate every file and concatenate its four columns, or raise an error.

    No partial result or numeric sentinel is returned when one file fails.
    Each file's time axis is validated separately; experiments may start at 0.
    """
    if isinstance(file_paths, (str, os.PathLike)):
        raise ValueError("Provide a list of data files, not a single path.")
    datasets = [extract_dsc_data_single_file(path, delimiter, has_header, skip_lines)
                for path in file_paths]
    if not datasets:
        raise ValueError("Please select at least one data file.")
    return tuple(np.concatenate(columns) for columns in zip(*datasets))


def launch_extraction(file_paths, delimiter=",", has_header=False, skip_lines=0):
    """Return the historical success/message/arrays extraction response."""
    try:
        with warnings.catch_warnings(record=True) as messages:
            warnings.simplefilter("always", UserWarning)
            arrays = extract_dsc_data_multiple_files(
                file_paths,
                delimiter,
                has_header,
                skip_lines,
            )
        return True, "\n".join(str(item.message) for item in messages), *arrays
    except (OSError, ValueError) as error:
        empty = tuple(np.array([], dtype=float) for _ in range(4))
        return False, str(error), *empty
