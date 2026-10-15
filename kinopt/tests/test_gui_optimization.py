"""Regression tests for parameters passed from the GUI to the optimizer."""

from dataclasses import replace

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
    window = main.MainWindow(
        results_directory=tmp_path / 'results',
        queue_database=tmp_path / 'queue.sqlite3',
    )
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
    window.experimental_times = [window.experimental_time]
    window.experimental_temperatures = [window.experimental_temperature]
    window.experimental_rates = [window.experimental_rate]
    window.experimental_extents = [window.experimental_extent]
    window.selected_shortened_file_paths = ["synthetic.csv"]


def test_small_window_keeps_every_section_reachable(optimization_window):
    main, window, _, _ = optimization_window
    configure_optimization(window, with_vitrification=True)

    window.resize(640, 480)
    window.show()
    main.QApplication.processEvents()

    assert window.width() == 640
    assert window.height() == 480
    assert window.minimumWidth() == 640
    assert window.minimumHeight() == 480
    assert window.central_scroll_area.widget() is window.ui.centralwidget
    assert window.central_scroll_area.horizontalScrollBar().maximum() > 0
    assert window.central_scroll_area.verticalScrollBar().maximum() > 0

    dock_contents = {
        "dockWidgetData_extraction": window.ui.dockWidgetOpenFileContents,
        "dockWidgetIsoconversionalAnalysis": (
            window.ui.dockWidgetContents_IsoconversionalAnalysis
        ),
        "dockWidgetOptimization": window.ui.dockWidgetContents_Optimization,
        "dockWidgetResultsViewer": window.ui.dockWidgetContents_ResultsViewer,
    }
    for dock_name, contents in dock_contents.items():
        dock = getattr(window.ui, dock_name)
        scroll_area = window.dock_scroll_areas[dock_name]
        assert dock.isVisible()
        assert scroll_area.widget() is contents
        assert dock.geometry().intersects(window.contentsRect())

    optimization_scroll = window.dock_scroll_areas["dockWidgetOptimization"]
    optimization_scroll.ensureWidgetVisible(window.pushButton_batch_optimizations)
    main.QApplication.processEvents()
    button_position = window.pushButton_batch_optimizations.mapTo(
        optimization_scroll.viewport(),
        window.pushButton_batch_optimizations.rect().topLeft(),
    )
    assert button_position.y() < optimization_scroll.viewport().height()
    assert (
        button_position.y() + window.pushButton_batch_optimizations.height()
        > 0
    )

    compact_left_width = window.ui.dockWidgetData_extraction.width()
    # Native Windows controls require more horizontal space than their Linux
    # counterparts, so verify the scrollbar-free desktop layout at a width
    # that accommodates both platform styles.
    window.resize(1600, 900)
    main.QApplication.processEvents()
    assert window.ui.dockWidgetData_extraction.width() > compact_left_width
    for dock_name in (
        "dockWidgetData_extraction",
        "dockWidgetIsoconversionalAnalysis",
        "dockWidgetResultsViewer",
    ):
        scroll_area = window.dock_scroll_areas[dock_name]
        assert scroll_area.horizontalScrollBar().maximum() == 0


def test_model_and_optimizer_selections_show_contextual_guidance(
    optimization_window,
):
    main, window, _, _ = optimization_window
    rate_guidance = window.selection_guidance_labels['rate']
    rate_equation = window.selection_guidance_equation_labels['rate']
    local_guidance = window.selection_guidance_labels['local_optimization']

    assert rate_guidance.isHidden()
    assert rate_equation.isHidden()
    assert local_guidance.isHidden()

    window.ui.comboBox_rate_model.setCurrentText('rate_for_kamal')
    window.ui.comboBox_local_optimization_methods.setCurrentText('L-BFGS-B')
    main.QApplication.processEvents()

    assert not rate_guidance.isHidden()
    assert 'Kamal model' in rate_guidance.text()
    assert 'six fitted parameters' in rate_guidance.text()
    assert rate_guidance.textFormat() == main.Qt.RichText
    assert not rate_equation.isHidden()
    assert rate_equation.pixmap() is not None
    assert not rate_equation.pixmap().isNull()
    assert rate_equation.pixmap().width() > 0
    assert 'ordinary and autocatalytic' in (
        rate_equation.accessibleDescription()
    )
    assert not local_guidance.isHidden()
    assert 'parameter bounds' in local_guidance.text()

    rate_index = window.ui.comboBox_rate_model.findText('rate_for_kamal')
    tooltip = window.ui.comboBox_rate_model.itemData(
        rate_index,
        main.Qt.ToolTipRole,
    )
    assert 'Kamal model' in tooltip

    window.clear_models_and_parameters_forms_and_combobox()
    window.clear_optimization_grids_and_combobox()
    main.QApplication.processEvents()
    assert rate_guidance.isHidden()
    assert rate_equation.isHidden()
    assert local_guidance.isHidden()


def test_empty_parameter_fields_show_examples_without_entering_values(
    optimization_window,
):
    main, window, _, _ = optimization_window

    window.ui.comboBox_rate_model.setCurrentText('rate_for_kamal')
    window.update_rate_formLayout(None)
    assert window.line_edit_dict_rate_model['A1'].text() == ''
    assert (
        window.line_edit_dict_rate_model['A1'].placeholderText()
        == 'Example: 1e8 s^-1'
    )
    assert (
        window.line_edit_dict_rate_model['E1'].placeholderText()
        == 'Example: 50000 J/mol'
    )

    window.ui.comboBox_tg_law.setCurrentText('tg_diBennedetto')
    window.update_tg_formLayout(None)
    assert (
        window.line_edit_dict_tg_law['Tg_0'].placeholderText()
        == 'Example: 290 K'
    )
    assert window.line_edit_dict_tg_law['Tg_0'].text() == ''

    window.ui.comboBox_global_optimization_methods.setCurrentText(
        'differential_evolution'
    )
    window.update_global_optimization_gridLayout()
    numeric_entries = [
        entry
        for entry in window.entries_dict_global_optimization.values()
        if isinstance(entry, main.QLineEdit)
    ]
    assert numeric_entries
    assert all(entry.placeholderText() for entry in numeric_entries)
    assert all(entry.text() == '' for entry in numeric_entries)

    window.ui.comboBox_cost_functions.setCurrentText(
        'rss_increase_of_small_extents_impact'
    )
    window.update_cost_functions_formLayout()
    assert (
        window.entries_dict_cost_function['extent_limit'].placeholderText()
        == 'Example: 0.707'
    )

    window.ui.comboBox_isoconversional_analysis_methods.setCurrentText(
        'isoconversional_analysis_vyazovkin_method'
    )
    window.update_isoconversional_formLayout()
    assert (
        window.line_edit_dict_isoconversional_analysis[
            'initial_guess'
        ].placeholderText()
        == 'Example: 50000 J/mol'
    )

    window.autofill_models_parameters()
    assert window.line_edit_dict_tg_law['Tg_0'].text() == '290'
    assert window.line_edit_dict_tg_law['Tg_inf'].text() == '450'
    assert window.line_edit_dict_tg_law['coeff'].text() == '0.5'


def test_included_kamal_example_prepares_a_complete_quick_setup(
    optimization_window,
):
    _, window, started, errors = optimization_window

    window.pushButton_load_example.click()

    assert errors == []
    assert started == []
    assert window.successful_extraction is True
    assert len(window.selected_full_file_paths) == 4
    assert window.selected_shortened_file_paths[0].endswith(
        '5C_per_min.txt'
    )
    assert window.ui.checkBox_file_has_headers.isChecked()
    assert window.ui.lineEdit_delimiter.text() == ','
    assert window.ui.lineEdit_number_of_lines_to_skip.text() == '0'
    assert window.selected_rate == 'rate_for_kamal'
    assert set(window.line_edit_dict_rate_model) == {
        'A1', 'E1', 'A2', 'E2', 'm', 'n',
    }
    assert all(
        field.text()
        for field in window.line_edit_dict_rate_model.values()
    )
    assert window.selected_local_optimization == 'Nelder-Mead'
    assert window.selected_cost_function == 'rss_mean'
    assert window.applied_optimization_profile == 'Quick check'
    assert window.entries_dict_local_optimization['maxiter'].text() == '200'
    assert 'Kamal example ready' in window.statusBar().currentMessage()


def test_calculation_profiles_explain_and_fill_selected_methods(
    optimization_window,
):
    main, window, _, errors = optimization_window
    window.ui.comboBox_rate_model.setCurrentText('rate_for_nth_order')
    window.update_rate_formLayout(None)

    window.ui.comboBox_global_optimization_methods.setCurrentText(
        'differential_evolution'
    )
    window.update_global_optimization_gridLayout()
    window.ui.comboBox_local_optimization_methods.setCurrentText('Nelder-Mead')
    window.update_local_optimization_gridLayout()
    window.ui.comboBox_cost_functions.setCurrentText(
        'rss_increase_of_small_extents_impact'
    )
    window.update_cost_functions_formLayout()

    assert window.optimization_profile_combo.currentText() == (
        'Balanced (recommended)'
    )
    assert 'routine fit' in window.optimization_profile_description.text()
    assert window.ui.pushButton_autofill_optimization.text() == 'Apply profile'

    window.optimization_profile_combo.setCurrentText('Quick check')
    main.QApplication.processEvents()
    assert 'preliminary fit' in window.optimization_profile_description.text()
    window.ui.pushButton_autofill_optimization.click()

    global_entries = window.entries_dict_global_optimization
    local_entries = window.entries_dict_local_optimization
    assert global_entries['maxiter'].text() == '100'
    assert global_entries['popsize'].text() == '8'
    assert global_entries['polish'].currentText() == 'No'
    assert global_entries['workers'].text() == '1'
    assert global_entries['minA1'].text() == '1'
    assert global_entries['maxE1'].text() == '350000'
    assert local_entries['maxiter'].text() == '200'
    assert local_entries['xatol'].text() == '1e-3'
    assert (
        window.entries_dict_cost_function['extent_limit'].text() == '0.707'
    )

    local_entries['maxiter'].setText('42')
    window.optimization_profile_combo.setCurrentText('Thorough search')
    main.QApplication.processEvents()
    assert local_entries['maxiter'].text() == '42'
    window.apply_optimization_profile()
    assert local_entries['maxiter'].text() == '3000'
    assert errors == []

    window.ui.toolBox_models_and_optimization_parameters.setCurrentWidget(
        window.ui.page_optimization_methods_and_parameters
    )
    window.resize(640, 480)
    window.show()
    profile_scroll = window.ui.scrollArea_optimization_methods
    profile_scroll.ensureWidgetVisible(
        window.ui.pushButton_autofill_optimization
    )
    main.QApplication.processEvents()
    button_position = window.ui.pushButton_autofill_optimization.mapTo(
        profile_scroll.viewport(),
        window.ui.pushButton_autofill_optimization.rect().topLeft(),
    )
    assert button_position.y() < profile_scroll.viewport().height()
    assert (
        button_position.y()
        + window.ui.pushButton_autofill_optimization.height()
        > 0
    )


def test_profile_converts_none_jacobian_choice_for_scipy(optimization_window):
    _, window, _, errors = optimization_window
    window.ui.comboBox_rate_model.setCurrentText('rate_for_nth_order')
    window.update_rate_formLayout(None)
    window.ui.comboBox_local_optimization_methods.setCurrentText('BFGS')
    window.update_local_optimization_gridLayout()

    window.apply_optimization_profile()
    arguments = window.get_local_optimization_args_dict('BFGS')

    assert arguments['jac'] is None
    assert arguments['options']['maxiter'] == 1000
    assert errors == []


def test_current_setup_can_be_added_to_batch(optimization_window):
    _, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)

    window.show_batch_optimizations()
    window.batch_dialog.add_current_setup()

    jobs = window.batch_dialog.queue.list_jobs()
    assert started == []
    assert errors == []
    assert len(jobs) == 1
    assert jobs[0].config.rate_law.__name__ == 'rate_for_nth_order'
    assert jobs[0].config.local_method == 'Nelder-Mead'


def test_reviewed_snapshot_is_the_one_started(
    optimization_window,
    monkeypatch,
):
    main, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)
    reviewed = []

    def accept_after_editing(dialog):
        reviewed.append(dialog.review)
        window.line_edit_dict_rate_model['A1'].setText('42')
        return main.QDialog.Accepted

    monkeypatch.setattr(
        main.OptimizationReviewDialog,
        'exec_',
        accept_after_editing,
    )

    window.review_optimization_setup()

    assert errors == []
    assert len(reviewed) == 1
    assert reviewed[0].datasets == ('synthetic.csv',)
    assert reviewed[0].profile_name == 'Balanced (recommended)'
    assert len(started) == 1
    np.testing.assert_array_equal(
        started[0].config.initial_guess,
        [1e8, 60000., 1.5],
    )


def test_leaving_review_does_not_start_optimization(
    optimization_window,
    monkeypatch,
):
    main, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)
    monkeypatch.setattr(
        main.OptimizationReviewDialog,
        'exec_',
        lambda dialog: main.QDialog.Rejected,
    )

    window.pushButton_review_optimization.click()

    assert started == []
    assert errors == []
    assert window.ui.pushButton_launch_optimization.isEnabled()


def test_launch_uses_tg_fields_in_coupled_model(optimization_window):
    main, window, started, errors = optimization_window
    configure_optimization(window)

    window.launch_optimization()

    assert errors == []
    assert len(started) == 1
    worker = started[0]
    config = worker.config
    np.testing.assert_array_equal(config.tg_args, [290., 450., 0.5])
    np.testing.assert_array_equal(
        config.initial_guess, [1e8, 60000., 1.5, 1., 50., 50.]
    )

    # Check the resulting coupled rate, not only the parameter container.
    extent = window.experimental_extent
    temperature = window.experimental_temperature
    expected_tg = 290 + 160 * 0.5 * extent / (1 - 0.5 * extent)
    chemical_rate = 1e8 * np.exp(-60000 / (8.31446261815324 * temperature)) * (1 - extent)**1.5
    diffusion_rate = np.exp(50 * (temperature - expected_tg) / (50 + abs(temperature - expected_tg)))
    expected_rate = chemical_rate * diffusion_rate / (chemical_rate + diffusion_rate)
    actual_rate = main.opt.model(
        config.initial_guess, config.rate_law, config.experimental_args_for_rate,
        config.rate_parameter_count, config.vitrification_law,
        config.experimental_args_for_vitrification,
        config.vitrification_parameter_count,
        config.coupling_law, config.experimental_args_for_coupling,
        config.tg_law, config.experimental_args_for_tg, config.tg_args,
    )
    np.testing.assert_allclose(actual_rate, expected_rate, rtol=1e-12, atol=0)


def test_launch_without_tg_keeps_rate_parameters(optimization_window):
    _, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)

    window.launch_optimization()

    assert errors == []
    assert len(started) == 1
    assert started[0].config.tg_law is None
    assert started[0].config.tg_args is None
    np.testing.assert_array_equal(
        started[0].config.initial_guess, [1e8, 60000., 1.5]
    )


def test_launch_captures_data_and_settings_before_the_form_changes(
    optimization_window,
):
    _, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)

    window.launch_optimization()
    config = started[0].config
    window.experimental_rate[:] = 99.
    window.line_edit_dict_rate_model['A1'].setText('42')
    window.local_optimization_args_dict['options']['maxiter'] = 1

    np.testing.assert_array_equal(config.experimental_rate, [0.01, 0.02, 0.03])
    np.testing.assert_array_equal(config.initial_guess, [1e8, 60000., 1.5])
    assert config.local_options['options']['maxiter'] != 1
    assert errors == []


def test_gui_configuration_can_be_restored_for_a_future_queue(
    optimization_window,
):
    from kinopt.src.optimization_serialization import (
        deserialize_config,
        serialize_config,
    )

    _, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=True)
    window.launch_optimization()

    original = started[0].config
    restored = deserialize_config(serialize_config(original))

    assert errors == []
    assert restored.rate_law is original.rate_law
    assert restored.vitrification_law is original.vitrification_law
    assert restored.coupling_law is original.coupling_law
    assert restored.tg_law is original.tg_law
    np.testing.assert_array_equal(restored.initial_guess, original.initial_guess)
    np.testing.assert_array_equal(restored.tg_args, original.tg_args)
    np.testing.assert_array_equal(
        restored.experimental_args_for_rate[0],
        original.experimental_args_for_rate[0],
    )


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


@pytest.mark.parametrize("missing", ["data", "model", "optimizer", "cost", "coupling", "tg"])
def test_missing_configuration_blocks_start(optimization_window, missing):
    _, window, started, errors = optimization_window
    configure_optimization(window)
    if missing == "data":
        window.successful_extraction = False
    elif missing == "model":
        window.selected_rate = window.selected_vitrification = ''
    elif missing == "optimizer":
        window.selected_local_optimization = ''
    elif missing == "cost":
        window.selected_cost_function = ''
    elif missing == "coupling":
        window.selected_coupling_law = ''
    else:
        window.selected_tg_law = ''
    window.launch_optimization()
    assert started == []
    assert len(errors) == 1


@pytest.mark.parametrize("budget", ["", "invalid", "0", "-1"])
def test_invalid_iteration_budget_is_a_single_error(optimization_window, budget):
    _, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)
    window.entries_dict_local_optimization['maxiter'].setText(budget)
    window.launch_optimization()
    assert started == []
    assert len(errors) == 1


def test_nonfinite_initial_guess_is_rejected(optimization_window):
    _, window, started, errors = optimization_window
    configure_optimization(window)
    window.line_edit_dict_rate_model['A1'].setText('nan')
    window.launch_optimization()
    assert started == []
    assert len(errors) == 1


def test_relative_cost_rejects_zero_measurements(optimization_window):
    _, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)
    window.ui.comboBox_cost_functions.setCurrentText('rss_relative')
    window.update_cost_functions_formLayout()
    window.experimental_rate[0] = 0
    window.launch_optimization()
    assert started == []
    assert len(errors) == 1
    assert 'nonzero' in errors[0]


def test_worker_failure_restores_start_button(optimization_window):
    main, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)
    window.launch_optimization()
    worker = started[0]

    def fail(*args, **kwargs):
        raise ValueError("synthetic solver failure")
    worker.config = replace(worker.config, local_optimizer=fail)
    worker.run()
    worker.finished.emit()
    assert len(errors) == 1
    assert 'synthetic solver failure' in errors[0]
    assert main.OptimizationQueue(window.queue_database).list_jobs() == []
    assert window.ui.pushButton_launch_optimization.text() == "Start optimization"
    assert window.ui.toolBox_models_and_optimization_parameters.isEnabled()
    window.ui.pushButton_launch_optimization.click()
    assert len(started) == 2


def test_actual_short_fit_saves_and_allows_another_run(optimization_window, tmp_path):
    main, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)
    window.entries_dict_local_optimization['maxiter'].setText('2')
    window.entries_dict_local_optimization['disp'].setCurrentText('No')
    window.show_batch_optimizations()
    window.launch_optimization()
    worker = started[0]
    worker.run()
    worker.finished.emit()
    assert errors == []
    assert np.isfinite(window.results.fun)
    assert 'Results' in next((tmp_path / 'results').glob('*.txt')).read_text()
    history = main.OptimizationQueue(window.queue_database).list_jobs()
    assert len(history) == 1
    assert history[0].status.value == 'completed'
    assert history[0].name.startswith('Direct optimization - ')
    assert history[0].result.parameters == pytest.approx(window.results.x)
    assert window.batch_dialog.table.rowCount() == 1
    assert window.batch_dialog.table.item(0, 3).text() == 'Completed'
    assert 'Added to optimization comparisons' in (
        window.ui.textEdit_output_of_optimization.toPlainText()
    )

    window._record_direct_optimization_result(
        window.results,
        window.total_time_for_optimization,
    )
    assert len(main.OptimizationQueue(window.queue_database).list_jobs()) == 1

    queue = main.OptimizationQueue(window.queue_database)
    reference = queue.add(history[0].config, name='Batch reference')
    queue.set_status(reference.identifier, 'running')
    queue.complete(
        reference.identifier,
        main.OptimizationRunResult(
            window.results,
            window.total_time_for_optimization,
        ),
    )
    window.batch_dialog.refresh()
    assert window.batch_dialog.compare_button.isEnabled()
    window.batch_dialog.show_completed_comparison()
    main.QApplication.processEvents()
    comparison_names = {
        window.batch_dialog.comparison_dialog.table.item(row, 2).text()
        for row in range(
            window.batch_dialog.comparison_dialog.table.rowCount()
        )
    }
    assert history[0].name in comparison_names
    assert 'Batch reference' in comparison_names

    assert window.ui.pushButton_launch_optimization.text() == "Start optimization"
    assert 'args' not in window.local_optimization_args_dict
    window.ui.pushButton_launch_optimization.click()
    assert len(started) == 2


def test_cancellation_uses_interruption_and_unwinds_worker(optimization_window, monkeypatch):
    main, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)
    window.launch_optimization()
    worker = started[0]
    requested = []
    monkeypatch.setattr(worker, 'isRunning', lambda: True)
    monkeypatch.setattr(worker, 'requestInterruption', lambda: requested.append(True))
    monkeypatch.setattr(worker, 'isInterruptionRequested', lambda: bool(requested))
    monkeypatch.setattr(worker, 'terminate', lambda: pytest.fail('Forced thread termination'))
    window.cancel_optimization()
    assert requested == [True]
    assert not window.ui.pushButton_launch_optimization.isEnabled()
    with pytest.raises(main.OptimizationCancelled):
        worker.optimization_callback(worker.config.initial_guess)
    worker.run()
    monkeypatch.setattr(worker, 'isRunning', lambda: False)
    worker.finished.emit()
    assert errors == []
    assert 'cancelled' in window.ui.textEdit_output_of_optimization.toPlainText()
    assert window.ui.pushButton_launch_optimization.isEnabled()


def test_real_thread_cancellation_returns_to_ready(optimization_window):
    import threading
    import time

    main, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)
    window.launch_optimization()
    worker = started[0]
    entered_solver = threading.Event()
    finished = []

    def wait_for_cancellation(function, initial_guess, callback, **kwargs):
        entered_solver.set()
        for _ in range(200):
            callback(initial_guess)
            time.sleep(0.005)
        raise AssertionError("Cancellation did not reach the solver callback")

    worker.config = replace(worker.config, local_optimizer=wait_for_cancellation)
    worker.finished.connect(lambda: finished.append(True))
    main.QThread.start(worker)
    try:
        assert entered_solver.wait(timeout=2)
        window.cancel_optimization()
        deadline = time.monotonic() + 3
        while not finished and time.monotonic() < deadline:
            main.QApplication.processEvents()
            time.sleep(0.005)
        assert finished == [True]
        assert errors == []
        assert window.ui.pushButton_launch_optimization.text() == 'Start optimization'
        assert 'cancelled' in window.ui.textEdit_output_of_optimization.toPlainText()
    finally:
        worker.requestInterruption()
        assert worker.wait(3000)


def test_saved_results_reload_unequal_experiments(optimization_window, tmp_path, monkeypatch):
    main, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)
    window.experimental_times.append(np.array([10., 11.]))
    window.experimental_temperatures.append(np.array([380., 390.]))
    window.experimental_extents.append(np.array([.4, .7]))
    window.experimental_rates.append(np.array([.04, .05]))
    for singular, plural in [('time', 'times'), ('temperature', 'temperatures'),
                             ('extent', 'extents'), ('rate', 'rates')]:
        setattr(window, 'experimental_' + singular, np.concatenate(getattr(window, 'experimental_' + plural)))
    window.selected_shortened_file_paths.append('second.csv')
    window.entries_dict_local_optimization['maxiter'].setText('2')
    window.entries_dict_local_optimization['disp'].setCurrentText('No')
    window.launch_optimization()
    started[0].run()
    started[0].finished.emit()
    assert errors == []
    path = next((tmp_path / 'results').glob('*.txt'))
    window.selected_full_results_file_paths = [str(path)]
    window.ui.listView_result_files.setModel(main.QStringListModel([path.name]))
    window.ui.listView_result_files.setCurrentIndex(window.ui.listView_result_files.model().index(0))
    calls = []
    simulate = main.km.compute_extent_and_rate

    def record_simulation(times, temperatures, **kwargs):
        calls.append((times.copy(), temperatures.copy(), kwargs['initial_extent']))
        return simulate(times, temperatures, **kwargs)

    monkeypatch.setattr(main.km, 'compute_extent_and_rate', record_simulation)
    window.display_selected_result_file()
    assert errors == []
    assert len(calls) == 2
    for index, (times, temperatures, initial_extent) in enumerate(calls):
        np.testing.assert_array_equal(times, window.experimental_times[index])
        np.testing.assert_array_equal(temperatures, window.experimental_temperatures[index])
        assert initial_extent == window.experimental_extents[index][0]


def test_result_write_failure_is_reported_and_controls_recover(optimization_window, tmp_path):
    _, window, started, errors = optimization_window
    configure_optimization(window, with_vitrification=False)
    window.entries_dict_local_optimization['maxiter'].setText('1')
    window.entries_dict_local_optimization['disp'].setCurrentText('No')
    (tmp_path / 'results').write_text('This is a file, not a directory.')
    window.launch_optimization()
    started[0].run()
    started[0].finished.emit()
    assert len(errors) == 1
    assert window.results is not None
    assert window.ui.pushButton_launch_optimization.text() == 'Start optimization'
