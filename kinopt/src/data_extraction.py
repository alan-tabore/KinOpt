"""Load and validate kinetic data stored as time, temperature, rate and conversion."""

import os
import warnings

import numpy as np
from scipy.integrate import trapezoid


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
    if not isinstance(skip_lines, (int, np.integer)) or skip_lines < 0:
        raise ValueError("The number of lines to skip must be a nonnegative integer.")
    name = os.path.basename(file_path)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="loadtxt: input contained no data")
            data = np.loadtxt(file_path, delimiter=delimiter,
                              skiprows=skip_lines + int(has_header), ndmin=2)
        if data.shape[0] < 2 or data.shape[1] < 4:
            raise ValueError("at least two rows and four columns are required")
        data = data[:, :4]
        if not np.all(np.isfinite(data)):
            raise ValueError("data contain missing or non-finite values")
        time, temperature, rate, extent = data.T
        if np.any(np.diff(time) <= 0):
            raise ValueError("time must be strictly increasing")
        if np.any(temperature <= 0):
            raise ValueError("temperature must be positive and expressed in Kelvin")
        if np.any((extent < 0) | (extent > 1)):
            raise ValueError("extent of reaction must be between 0 and 1")
        if np.any(np.diff(extent) < 0):
            raise ValueError("extent of reaction must be nondecreasing")
        if not np.isclose(trapezoid(rate, time), extent[-1] - extent[0]):
            raise ValueError("integral of rate does not match the recorded change in extent")
    except ValueError as exc:
        raise ValueError(f"Error in file {name}: {exc}") from exc

    if np.any(temperature < 173.15):
        warnings.warn(f"File {name}: check that temperatures are in Kelvin, not Celsius.", UserWarning)
    if extent[0] == 0:
        warnings.warn(f"File {name}: zero initial extent needs care when simulating an autocatalytic model.", UserWarning)
    stop = np.flatnonzero(extent >= 1)
    end = int(stop[0]) + 1 if stop.size else len(extent)
    return tuple(column[:end].copy() for column in (time, temperature, rate, extent))


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
