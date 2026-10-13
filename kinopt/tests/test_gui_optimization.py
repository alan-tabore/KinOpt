"""Regression tests for parameters passed from the GUI to the optimizer."""

import numpy as np
import pytest


@pytest.fixture
def optimization_window(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "matplotlib"))
    from kinopt.src import main

    app = main.QApplication.instance() or main.QApplication([])
    errors = []
    started = []
    monkeypatch.setattr(
        main.QMessageBox, "critical",
        lambda parent, title, message: errors.append(message),
    )
    monkeypatch.setattr(main.QMessageBox, "information", lambda *args: None)
    monkeypatch.setattr(main.QMessageBox, "warning", lambda *args: None)
    # Keep the real worker and its parameters, without starting a background fit.
    monkeypatch.setattr(main.OptimizationThread, "start", lambda worker: started.append(worker))
    window = main.MainWindow()
    try:
        yield main, window, started, errors
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


def configure_optimization(window, with_vitrification=True):
    window.ui.comboBox_rate_model.setCurrentText("rate_for_nth_order")
    window.update_rate_formLayout(None)
    for name, value in {"A1": 1e8, "E1": 60000, "n": 1.5}.items():
        window.line_edit_dict_rate_model[name].setText(str(value))

    if with_vitrification:
        window.ui.comboBox_vitrification_model.setCurrentText("vitrification_WLF_rate")
        window.update_vitrification_formLayout(None)
        window.ui.comboBox_coupling_law.setCurrentText("coupling_harmonic_mean")
        window.update_coupling_formLayout(None)
        window.ui.comboBox_tg_law.setCurrentText("tg_diBennedetto")
        window.update_tg_formLayout(None)
        for name, value in {"Ad": 1, "C1": 50, "C2": 50}.items():
            window.line_edit_dict_vitrification_model[name].setText(str(value))
        for name, value in {"Tg_0": 290, "Tg_inf": 450, "coeff": 0.5}.items():
            window.line_edit_dict_tg_law[name].setText(str(value))

    window.ui.comboBox_local_optimization_methods.setCurrentText("Nelder-Mead")
    window.update_local_optimization_gridLayout()
    window.ui.comboBox_cost_functions.setCurrentText("rss_mean")
    window.update_cost_functions_formLayout()
    window.autofill_optimization_parameters()
    window.successful_extraction = True
    window.experimental_extent = np.array([0.1, 0.3, 0.6])
    window.experimental_temperature = np.array([350., 400., 450.])
    window.experimental_time = np.array([0., 1., 2.])
    window.experimental_rate = np.array([0.01, 0.02, 0.03])


def test_launch_uses_tg_fields_in_coupled_model(optimization_window):
    main, window, started, errors = optimization_window
    configure_optimization(window)

    window.launch_optimization()

    assert errors == []
    assert len(started) == 1
    worker = started[0]
    np.testing.assert_array_equal(worker.tg_args, [290., 450., 0.5])
    np.testing.assert_array_equal(worker.initial_guess, [1e8, 60000., 1.5, 1., 50., 50.])

    # Check the resulting coupled rate, not only the parameter container.
    extent = window.experimental_extent
    temperature = window.experimental_temperature
    expected_tg = 290 + 160 * 0.5 * extent / (1 - 0.5 * extent)
    chemical_rate = 1e8 * np.exp(-60000 / (8.31446261815324 * temperature)) * (1 - extent)**1.5
    diffusion_rate = np.exp(50 * (temperature - expected_tg) / (50 + abs(temperature - expected_tg)))
    expected_rate = chemical_rate * diffusion_rate / (chemical_rate + diffusion_rate)
    actual_rate = main.opt.model(
        worker.initial_guess, worker.rate_law, worker.experimental_args_for_rate,
        worker.number_of_parameters_to_optimize_for_rate, worker.vitrification_law,
        worker.experimental_args_for_vitrification,
        worker.number_of_parameters_to_optimize_for_vitrification,
        worker.coupling_law, worker.experimental_args_for_coupling,
        worker.tg_law, worker.experimental_args_for_tg, worker.tg_args,
    )
    np.testing.assert_allclose(actual_rate, expected_rate, rtol=1e-12, atol=0)


def test_launch_without_tg_keeps_rate_parameters(optimization_window):
    _, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)

    window.launch_optimization()

    assert errors == []
    assert len(started) == 1
    assert started[0].tg_law is None
    assert started[0].tg_args is None
    np.testing.assert_array_equal(started[0].initial_guess, [1e8, 60000., 1.5])


@pytest.mark.parametrize("invalid_value", ["", "invalid", "nan", "inf", "-inf"])
def test_invalid_tg_is_rejected_before_start(optimization_window, invalid_value):
    _, window, started, errors = optimization_window
    configure_optimization(window)
    window.line_edit_dict_tg_law["Tg_0"].setText(invalid_value)

    window.launch_optimization()

    assert started == []
    assert len(errors) == 1
    assert "Tg" in errors[0]
    assert window.ui.pushButton_launch_optimization.text() == "Start optimization"


def test_extraction_reports_failure_without_redirecting_stdout(optimization_window, tmp_path):
    import sys
    main, _, _, _ = optimization_window
    original_stdout = sys.stdout
    result = main.launch_extraction([tmp_path / "missing.csv"])
    assert result[0] is False
    assert "missing.csv" in result[1]
    assert all(array.size == 0 for array in result[2:])
    assert sys.stdout is original_stdout


def test_failed_import_invalidates_previous_data(optimization_window):
    _, window, _, errors = optimization_window
    configure_optimization(window)
    window.selected_full_file_paths = ["unused.csv"]
    window.ui.lineEdit_number_of_lines_to_skip.setText("invalid")
    window.extract_data()
    assert window.successful_extraction is False
    assert len(errors) == 1
