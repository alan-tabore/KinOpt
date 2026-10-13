import numpy as np
import pytest

from kinopt.src import data_extraction as extraction


@pytest.fixture
def valid_data():
    return np.array([[0., 350., .1, .1], [1., 360., .1, .2], [2., 370., .1, .3]])


def test_single_and_multiple_files_agree(tmp_path, valid_data):
    paths = [tmp_path / name for name in ("first.csv", "second.csv")]
    for path in paths:
        np.savetxt(path, valid_data, delimiter=',')
    single = extraction.extract_dsc_data_single_file(paths[0])
    combined = extraction.extract_dsc_data_multiple_files(paths)
    for column, one, both in zip(valid_data.T, single, combined):
        np.testing.assert_array_equal(one, column)
        np.testing.assert_array_equal(both, np.concatenate([column, column]))


def test_header_delimiter_and_extra_columns(tmp_path, valid_data):
    path = tmp_path / "data.txt"
    extended = np.column_stack([valid_data, np.ones(3)])
    with path.open('w') as stream:
        stream.write("experiment notes\ntime;temperature;rate;extent;extra\n")
        np.savetxt(stream, extended, delimiter=';')
    actual = extraction.extract_dsc_data_single_file(path, delimiter=';', has_header=True, skip_lines=1)
    np.testing.assert_array_equal(np.column_stack(actual), valid_data)


@pytest.mark.parametrize("row,column,value,message", [
    (1, 0, 0, "strictly increasing"),
    (1, 0, -1, "strictly increasing"),
    (1, 1, 0, "Kelvin"),
    (1, 1, -100, "Kelvin"),
    (1, 3, -0.1, "between 0 and 1"),
    (1, 3, 1.1, "between 0 and 1"),
    (1, 3, 0.05, "nondecreasing"),
    (1, 2, 10, "integral"),
] + [(1, column, value, "non-finite") for column in range(4) for value in (np.nan, np.inf)])
def test_invalid_data_is_rejected(tmp_path, valid_data, row, column, value, message):
    valid_data[row, column] = value
    path = tmp_path / "invalid.csv"
    np.savetxt(path, valid_data, delimiter=',')
    for loader, argument in [(extraction.extract_dsc_data_single_file, path),
                             (extraction.extract_dsc_data_multiple_files, [path])]:
        with pytest.raises(ValueError, match=message) as error:
            loader(argument)
        assert "invalid.csv" in str(error.value)


@pytest.mark.parametrize("contents", [
    "", "0,350,.1,.1\n", "0,350,.1\n1,360,.2\n",
    "0,350,no,.1\n1,360,.1,.2\n", "0,350,,.1\n1,360,.1,.2\n",
])
def test_bad_file_structure(tmp_path, contents):
    path = tmp_path / "invalid.csv"
    path.write_text(contents)
    with pytest.raises(ValueError, match="invalid.csv"):
        extraction.extract_dsc_data_single_file(path)


def test_no_files_and_missing_file(tmp_path):
    with pytest.raises(ValueError, match="at least one"):
        extraction.extract_dsc_data_multiple_files([])
    with pytest.raises(OSError):
        extraction.extract_dsc_data_single_file(tmp_path / "missing.csv")


def test_failure_in_second_file_returns_no_partial_data(tmp_path, valid_data):
    path = tmp_path / "valid.csv"
    np.savetxt(path, valid_data, delimiter=',')
    with pytest.raises(OSError):
        extraction.extract_dsc_data_multiple_files([path, tmp_path / "missing.csv"])


@pytest.mark.parametrize("skip_lines", [-1, 0.5])
def test_invalid_skip_count(tmp_path, skip_lines):
    with pytest.raises(ValueError, match="nonnegative integer"):
        extraction.extract_dsc_data_single_file(tmp_path / "unused.csv", skip_lines=skip_lines)


def test_temperature_warning_preserves_original_values(tmp_path, valid_data):
    valid_data[:, 1] = 50
    path = tmp_path / "units.csv"
    np.savetxt(path, valid_data, delimiter=',')
    with pytest.warns(UserWarning, match="Kelvin"):
        arrays = extraction.extract_dsc_data_single_file(path)
    np.testing.assert_array_equal(np.column_stack(arrays), valid_data)


def test_data_are_trimmed_after_completion(tmp_path):
    path = tmp_path / "complete.csv"
    data = np.array([[0, 350, .1, .8], [1, 350, .1, .9],
                     [2, 350, .1, 1], [3, 350, -.1, 1]])
    np.savetxt(path, data, delimiter=',')
    np.testing.assert_allclose(np.column_stack(extraction.extract_dsc_data_single_file(path)), data[:3])
