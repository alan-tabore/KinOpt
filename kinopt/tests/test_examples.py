"""Validate the complete example distributed with installed KinOpt."""

import numpy as np
import pytest

from kinopt.examples import KAMAL_EXAMPLE, included_example_files
from kinopt.src.data_extraction import extract_dsc_data_multiple_files


def test_included_kamal_example_is_complete_and_extractable():
    paths = included_example_files()

    assert [path.name for path in paths] == list(KAMAL_EXAMPLE.file_names)
    assert len(paths) == 4
    with pytest.warns(UserWarning, match="zero initial extent"):
        time, temperature, rate, extent = extract_dsc_data_multiple_files(
            paths,
            delimiter=KAMAL_EXAMPLE.delimiter,
            has_header=KAMAL_EXAMPLE.has_header,
        )

    assert len(time) == len(temperature) == len(rate) == len(extent)
    # Extraction intentionally trims each experiment once conversion reaches 1.
    assert len(time) > 10000
    assert np.all(np.isfinite(rate))
    assert np.min(temperature) >= 293.
    assert np.all((extent >= 0.) & (extent <= 1.))
