# -*- coding: utf-8 -*-
"""
This script is used to define the graphical interface and its main functions.

@author: alan.tabore
"""
   
    
import sys
import os
import traceback

# Get the absolute path of the 'Kinopt' folder
kinopt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Add the 'Kinopt' folder to the Python path
sys.path.append(kinopt_path)

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QComboBox, QLabel, QLineEdit
from PyQt5.QtCore import QStringListModel, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
from kinopt_interface import Ui_MainWindow

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


import data_extraction
import isoconversional_methods as icm
import kinetic_models as km
import optimization as opt 

import scipy
import numpy as np
import time as time_module
import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect data extraction elements
        self.ui.pushButton_add_files.clicked.connect(self.browse_files)
        self.ui.pushButton_clear_all_files.clicked.connect(self.clear_files)
        self.ui.pushButton_extract_data.clicked.connect(self.extract_data)
        
        # Connect isoconversional analysis elements
        self.selected_isoconversional_method = ''
        self.ui.comboBox_isoconversional_analysis_methods.addItems(get_functions_for_isoconversional_method())
        self.ui.comboBox_isoconversional_analysis_methods.setCurrentIndex(-1)
        self.ui.comboBox_isoconversional_analysis_methods.currentIndexChanged.connect(self.update_isoconversional_formLayout)
        self.ui.pushButton_autofill_isoconversional.clicked.connect(self.autofill_isoconversional_analysis_parameters)
        self.ui.pushButton_clear_isoconversional.clicked.connect(self.clear_isoconversional_formLayout_and_combobox)
        self.ui.pushButton_launch_isoconversional_analysis.clicked.connect(self.launch_isoconversional_analysis)
        
        # Connect results viewer elements
        self.ui.pushButton_load_result_files.clicked.connect(self.load_results_files)
        self.ui.pushButton_clear_result_files.clicked.connect(self.clear_results_files)
        self.ui.pushButton_display_result_files.clicked.connect(self.display_selected_result_file)
        
        # Connect models and parameters elements
        self.selected_rate = ''
        self.selected_vitrification = ''
        self.selected_coupling_law = ''
        self.selected_tg_law = ''
        self.line_edit_dict_rate_model = {}
        self.line_edit_dict_vitrification_model = {}
        self.line_edit_dict_coupling_law = {}
        self.line_edit_dict_tg_law = {}
        self.rate_parameters_experimental = []
        self.rate_parameters_to_optimize = []
        self.vitrification_parameters_experimental = []
        self.vitrification_parameters_to_optimize = []
        self.coupling_law_parameters_experimental = []
        self.coupling_law_parameters_to_optimize = []
        self.tg_law_parameters_experimental = []
        self.tg_law_parameters_to_optimize = []
        rate_laws, vitrification_laws, coupling_laws, tg_laws = get_functions_for_kinetics()
        self.ui.comboBox_rate_model.addItems(rate_laws)
        self.ui.comboBox_rate_model.setCurrentIndex(-1)
        self.ui.comboBox_rate_model.activated.connect(self.update_rate_formLayout)
        self.ui.comboBox_vitrification_model.addItems(vitrification_laws)
        self.ui.comboBox_vitrification_model.setCurrentIndex(-1)
        self.ui.comboBox_vitrification_model.activated.connect(self.update_vitrification_formLayout)
        self.ui.comboBox_coupling_law.addItems(coupling_laws)
        self.ui.comboBox_coupling_law.setCurrentIndex(-1)
        self.ui.comboBox_coupling_law.activated.connect(self.update_coupling_formLayout)
        self.ui.comboBox_tg_law.addItems(tg_laws)
        self.ui.comboBox_tg_law.setCurrentIndex(-1)
        self.ui.comboBox_tg_law.activated.connect(self.update_tg_formLayout)
        
        self.ui.pushButton_clear_models_and_parameters.clicked.connect(self.clear_models_and_parameters_forms_and_combobox)
        self.ui.pushButton_autofill_models_and_parameters.clicked.connect(self.autofill_models_parameters)
        
        # Connect optimization parameters elements
        self.selected_global_optimization = ''
        self.selected_local_optimization = ''
        self.selected_cost_function = ''
        self.labels_dict_global_optimization = {}
        self.entries_dict_global_optimization = {}
        self.labels_dict_local_optimization = {}
        self.entries_dict_local_optimization = {}
        self.labels_dict_cost_function = {}
        self.entries_dict_cost_function = {}
        global_optimization_methods, local_optimization_methods, rss_methods = get_functions_for_optimization()
        self.ui.comboBox_global_optimization_methods.addItems(global_optimization_methods)
        self.ui.comboBox_global_optimization_methods.setCurrentIndex(-1)
        self.ui.comboBox_global_optimization_methods.activated.connect(self.update_global_optimization_gridLayout)
        self.ui.comboBox_local_optimization_methods.addItems(local_optimization_methods)
        self.ui.comboBox_local_optimization_methods.setCurrentIndex(-1)
        self.ui.comboBox_local_optimization_methods.activated.connect(self.update_local_optimization_gridLayout)
        self.ui.comboBox_cost_functions.addItems(rss_methods)
        self.ui.comboBox_cost_functions.setCurrentIndex(-1)
        self.ui.comboBox_cost_functions.activated.connect(self.update_cost_functions_formLayout)
        
        self.ui.pushButton_clear_optimization.clicked.connect(self.clear_optimization_grids_and_combobox)
        self.ui.pushButton_autofill_optimization.clicked.connect(self.autofill_optimization_parameters)
        self.ui.pushButton_launch_optimization.clicked.connect(self.launch_optimization)
        
        # Create a Matplotlib figure and canvas to plot the rate from extracted data
        self.figure_data_extraction_rate = Figure()
        self.canvas_data_extraction_rate = FigureCanvas(self.figure_data_extraction_rate)
        self.ax_data_extraction_rate = self.figure_data_extraction_rate.add_subplot(111)
        self.ui.verticalLayout_data_extraction_rate.addWidget(self.canvas_data_extraction_rate)
        self.ui.verticalLayout_data_extraction_rate.addWidget(NavigationToolbar(self.canvas_data_extraction_rate, self))
        
        # Create a Matplotlib figure and canvas to plot the extent from extracted data
        self.figure_data_extraction_extent = Figure()
        self.canvas_data_extraction_extent = FigureCanvas(self.figure_data_extraction_extent)
        self.ax_data_extraction_extent = self.figure_data_extraction_extent.add_subplot(111)
        self.ui.verticalLayout_data_extraction_extent.addWidget(self.canvas_data_extraction_extent)
        self.ui.verticalLayout_data_extraction_extent.addWidget(NavigationToolbar(self.canvas_data_extraction_extent,self))
        
        # Create a Matplotlib figure and canvas to plot the temperature from extracted data
        self.figure_data_extraction_temperature = Figure()
        self.canvas_data_extraction_temperature = FigureCanvas(self.figure_data_extraction_temperature)
        self.ax_data_extraction_temperature = self.figure_data_extraction_temperature.add_subplot(111)
        self.ui.verticalLayout_data_extraction_temperature.addWidget(self.canvas_data_extraction_temperature)
        self.ui.verticalLayout_data_extraction_temperature.addWidget(NavigationToolbar(self.canvas_data_extraction_temperature,self))
        
        self.ui.pushButton_data_extraction_rate.clicked.connect(self.show_extracted_rate)
        self.ui.pushButton_data_extraction_extent.clicked.connect(self.show_extracted_extent)
        self.ui.pushButton_data_extraction_temperature.clicked.connect(self.show_extracted_temperature)

        # Create a Matplotlib figure and canvas to plot the evolution of activation energy from isoconversional analysis
        self.figure_isoconversional_analysis = Figure()
        self.canvas_isoconversional_analysis = FigureCanvas(self.figure_isoconversional_analysis)
        self.ax_isoconversional_analysis = self.figure_isoconversional_analysis.add_subplot(111)
        self.ui.verticalLayout_isoconversional_analysis.addWidget(self.canvas_isoconversional_analysis)
        self.ui.verticalLayout_isoconversional_analysis.addWidget(NavigationToolbar(self.canvas_isoconversional_analysis,self))
        
        # Create a Matplotlib figure and canvas to plot the rate during optimization
        self.figure_optimization = Figure()
        self.canvas_optimization = FigureCanvas(self.figure_optimization)
        self.ax_optimization = self.figure_optimization.add_subplot(111)
        self.ui.verticalLayout_optimization.addWidget(self.canvas_optimization)
        self.ui.verticalLayout_optimization.addWidget(NavigationToolbar(self.canvas_optimization,self))
        
        # Create a Matplotlib figure and canvas to plot the rate from result file
        self.figure_results_viewer_rate = Figure()
        self.canvas_results_viewer_rate = FigureCanvas(self.figure_results_viewer_rate)
        self.ax_results_viewer_rate = self.figure_results_viewer_rate.add_subplot(111)
        self.ui.verticalLayout_results_viewer_rate.addWidget(self.canvas_results_viewer_rate)
        self.ui.verticalLayout_results_viewer_rate.addWidget(NavigationToolbar(self.canvas_results_viewer_rate, self))
        
        # Create a Matplotlib figure and canvas to plot the extent from result file
        self.figure_results_viewer_extent = Figure()
        self.canvas_results_viewer_extent = FigureCanvas(self.figure_results_viewer_extent)
        self.ax_results_viewer_extent = self.figure_results_viewer_extent.add_subplot(111)
        self.ui.verticalLayout_results_viewer_extent.addWidget(self.canvas_results_viewer_extent)
        self.ui.verticalLayout_results_viewer_extent.addWidget(NavigationToolbar(self.canvas_results_viewer_extent,self))
        
        # Create a Matplotlib figure and canvas to plot the temperature from result file
        self.figure_results_viewer_temperature = Figure()
        self.canvas_results_viewer_temperature = FigureCanvas(self.figure_results_viewer_temperature)
        self.ax_results_viewer_temperature = self.figure_results_viewer_temperature.add_subplot(111)
        self.ui.verticalLayout_results_viewer_temperature.addWidget(self.canvas_results_viewer_temperature)
        self.ui.verticalLayout_results_viewer_temperature.addWidget(NavigationToolbar(self.canvas_results_viewer_temperature,self))
        
        self.ui.pushButton_results_viewer_rate.clicked.connect(self.show_extracted_result_rate)
        self.ui.pushButton_results_viewer_extent.clicked.connect(self.show_extracted_result_extent)
        self.ui.pushButton_results_viewer_temperature.clicked.connect(self.show_extracted_result_temperature)
        
        
    def browse_files(self):
        """Open a file dialog to browse and select multiple files. Update the file paths list widget."""
        try:
            # Open a file dialog to select files
            file_paths, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Files",
                "",
                "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
            )
            if file_paths:
                # Clear the data extraction plots in case previous files were extracted
                self.clear_data_extraction_plots()
                
                # Update listView background in white to indicate no extraction was performed
                self.ui.listView_files.viewport().setStyleSheet("background-color: white")
                
                # Create a string list model to hold the filenames
                string_list_model = QStringListModel()
    
                # Populate the model with shortened filenames
                string_list_model.setStringList([os.path.basename(fp) for fp in file_paths])
                
                # Save the shortened filenames
                self.selected_shortened_file_paths = [os.path.basename(fp) for fp in file_paths]
    
                # Set the model for the list view
                self.ui.listView_files.setModel(string_list_model)
    
                # Store the full file paths in an instance variable
                self.selected_full_file_paths = file_paths
        except Exception as e:
            # Handle other exceptions with a generic error message
            QMessageBox.critical(self,"Error", f"An error occurred: {str(e)}")
            traceback.print_exc()
            
    def clear_files(self):
        """Clear all the files in the listView_files object."""
        # Create an empty string list model to empty the listView
        string_list_model = QStringListModel()
        # Set the model for the list view with the empty list
        self.ui.listView_files.setModel(string_list_model)
        # Empty the full file paths list
        self.selected_full_file_paths = None
        # Empty the shortened file paths list
        self.selected_shortened_file_paths = None
        # Reset the bool to indicate successful extraction
        self.successful_extraction = None
        
        # Update listView background in white to indicate no extraction was performed
        self.ui.listView_files.viewport().setStyleSheet("background-color: white")
        
        self.clear_data_extraction_plots()
        
    def extract_data(self):
        """Extract data from selected files and update GUI elements based on extraction results."""
        try:
            # Get the selected file paths
            file_paths_list = self.selected_full_file_paths

            # Check if no files have been selected
            if not file_paths_list:
                # Show a warning message using PySide2
                QMessageBox.warning(
                    self, "No File Selected", "Please select a file before extracting.")
                return
    
            # Get the delimiter entry from the line edit field
            delimiter_entry = self.ui.lineEdit_delimiter.text()
            if delimiter_entry == "":
                delimiter_entry = ","
            elif delimiter_entry.lower() == "tab" or delimiter_entry == "\\t":
                delimiter_entry = "\t"
    
            # Get the value of the file_has_header_var (Int variable indicating if files have headers)
            has_header_entry = self.ui.checkBox_file_has_headers.isChecked()
            
            # Get the number of lines to skip from the line edit field and convert to integer
            number_of_lines_to_skip = int(self.ui.lineEdit_number_of_lines_to_skip.text())
                
            # Launch the extraction process with provided parameters
            self.successful_extraction, message, time_array, temp_array, rate_array, extent_array = launch_extraction(
                file_paths_list,
                delimiter=delimiter_entry,
                has_header=has_header_entry,
                skip_lines=number_of_lines_to_skip
            )
            
            self.ax_data_extraction_rate.clear()
            self.ax_data_extraction_extent.clear()
            self.ax_data_extraction_temperature.clear()
            
            
            # Check if the extraction was successful
            if self.successful_extraction:
                # Update experimental data arrays in the class instance
                self.experimental_time = time_array
                self.experimental_temperature = temp_array
                self.experimental_rate = rate_array
                self.experimental_extent = extent_array
    
                # Update listView background in green to indicate a successful extraction
                self.ui.listView_files.viewport().setStyleSheet("background-color: #C8FFC8")
                
                QMessageBox.information(self, "Extraction Successful", f"Successful extraction! \n {message}")
    
               
                self.ax_optimization.clear()
                # Create lists with data separated by files
                self.experimental_times = []
                self.experimental_temperatures = []
                self.experimental_rates = []
                self.experimental_extents = []
                for index, filepath in enumerate(self.selected_full_file_paths):
                    time, temperature, rate, extent = data_extraction.extract_dsc_data_single_file(
                        filepath, delimiter=delimiter_entry, has_header=has_header_entry, skip_lines=number_of_lines_to_skip)
                    self.experimental_times.append(time)
                    self.experimental_temperatures.append(temperature)
                    self.experimental_rates.append(rate)
                    self.experimental_extents.append(extent)
                    
                    self.ax_data_extraction_rate.plot(time,rate,label=f'{self.selected_shortened_file_paths[index]}')
                    self.ax_data_extraction_extent.plot(time,extent,label=f'{self.selected_shortened_file_paths[index]}')
                    self.ax_data_extraction_temperature.plot(time,temperature,label=f'{self.selected_shortened_file_paths[index]}')
                    
                self.ax_data_extraction_rate.legend()
                self.ax_data_extraction_extent.legend()
                self.ax_data_extraction_temperature.legend()
                
                self.ax_data_extraction_rate.set_ylabel("Rate (s-1)")
                self.ax_data_extraction_rate.set_xlabel("Time (s)")
                self.ax_data_extraction_extent.set_ylabel("Extent")
                self.ax_data_extraction_extent.set_xlabel("Time (s)")
                self.ax_data_extraction_temperature.set_ylabel("Temperature (K)")
                self.ax_data_extraction_temperature.set_xlabel("Time (s)")
                
                self.canvas_data_extraction_rate.draw_idle()
                self.canvas_data_extraction_extent.draw_idle()
                self.canvas_data_extraction_temperature.draw_idle()
                
                self.ui.tabWidget_visualization.setCurrentIndex(0)
                

            else:
                # Update listView background in green to indicate a failed extraction
                self.ui.listView_files.viewport().setStyleSheet("background-color: #FFC8C8")

                QMessageBox.critical(self, "Extraction Failed", f"Extraction failed! \n {message}")
                
        except AttributeError as e:
            if str(e) == "'MainWindow' object has no attribute 'selected_full_file_paths'":
                # Handle the specific AttributeError and display a customized error message
                QMessageBox.critical(self, "Error", "Please select a file.")
            else:
                # Handle other AttributeErrors (if any) differently
                print(e)
                traceback.print_exc()
                QMessageBox.critical(self, "Error", f"An AttributeError occurred: {str(e)}")
        except Exception as e:
            # Handle other exceptions with a generic error message
            QMessageBox.critical(
                self, "Error", f"An error occurred: {str(e)}")
            traceback.print_exc()
            
    def clear_data_extraction_plots(self):
        self.ax_data_extraction_rate.clear()
        self.ax_data_extraction_extent.clear()
        self.ax_data_extraction_temperature.clear()
        
        self.canvas_data_extraction_rate.draw_idle()
        self.canvas_data_extraction_extent.draw_idle()
        self.canvas_data_extraction_temperature.draw_idle()
        
    def show_extracted_rate(self):
        self.ui.stackedWidget_data_extraction.setCurrentWidget(self.ui.page_data_extraction_rate)
        
    def show_extracted_extent(self):
        self.ui.stackedWidget_data_extraction.setCurrentWidget(self.ui.page_data_extraction_extent)
    
    def show_extracted_temperature(self):
        self.ui.stackedWidget_data_extraction.setCurrentWidget(self.ui.page_data_extraction_temperature)
        
    def update_isoconversional_formLayout(self):
        # Clear parameter entry boxes
        for i in reversed(range(self.ui.formLayout_isoconversional_analysis.count())):
            widget = self.ui.formLayout_isoconversional_analysis.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Get the selected model
        self.selected_isoconversional_method = self.ui.comboBox_isoconversional_analysis_methods.currentText()

        # Get parameters for the selected model
        isoconversional_method_parameters = get_parameters_for_isoconversional_method(self.selected_isoconversional_method)
        
        # Lists to store the experimental parameters and parameters to optimize
        self.isoconversional_method_parameters_experimental = []
        self.isoconversional_method_parameters_to_give = []
        
        # List of values to match against
        experimental_param_values = ["conv_lists", "time_lists", "temperature_lists", "rate_lists"]
        
        self.line_edit_dict_isoconversional_analysis = {}
        # Create line edit entities for each parameter
        for parameter in isoconversional_method_parameters:
            if parameter in experimental_param_values:
                # Adding the experimental parameters to the list
                if parameter != "optional_parameters":
                    self.isoconversional_method_parameters_experimental.append(parameter)
            else:
                # Adding the parameters to optimize to the list
                self.isoconversional_method_parameters_to_give.append(parameter)
                line_edit = QLineEdit()
                self.line_edit_dict_isoconversional_analysis[parameter] = line_edit
                self.ui.formLayout_isoconversional_analysis.addRow(parameter+":",line_edit)
        

    def clear_isoconversional_formLayout_and_combobox(self):
        # Clear parameter entry boxes
        for i in reversed(range(self.ui.formLayout_isoconversional_analysis.count())):
            widget = self.ui.formLayout_isoconversional_analysis.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.ui.comboBox_isoconversional_analysis_methods.setCurrentIndex(-1)
        # Lists to store the experimental parameters and parameters to optimize
        self.isoconversional_method_parameters_experimental = []
        self.isoconversional_method_parameters_to_give = []
        self.selected_isoconversional_method = ''
        
                
    def get_isoconversional_method_args(self):
        # Get arguments from parameter entry boxes
        isoconversional_method_args = []
        for i in range(self.ui.formLayout_isoconversional_analysis.count()):
            widget = self.ui.formLayout_isoconversional_analysis.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                if widget.text() == "":
                    QMessageBox.critical(self, "Error", "Please fill all the values for the isoconversional law.")
                    return
                isoconversional_method_args.append(float(widget.text()))

        return tuple(isoconversional_method_args)
    
    def autofill_isoconversional_analysis_parameters(self):
        try:
            for key, line_edit in self.line_edit_dict_isoconversional_analysis.items():
                if key == "min_conv":
                    line_edit.setText("0.1")
                elif key == "max_conv":
                    line_edit.setText("0.9")
                elif key == "initial_guess":
                    line_edit.setText("50000")
                elif key == "number_of_points":
                    line_edit.setText("100")
                else:
                    QMessageBox.critical(self, "Error", f"An error occurred:\nThe parameter {key} doesn't have a default value.\nPlease modify the 'autofill_isoconversional_analysis_parameters' function.", QMessageBox.Icon.Critical)
        except Exception as e:
            # Handle other exceptions with a generic error message
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            traceback.print_exc() 
            
    def launch_isoconversional_analysis(self):
        try:
            if not hasattr(self, 'successful_extraction') or not self.successful_extraction:
                QMessageBox.critical(self, "Error", "Please, make sure you extracted the data successfully.")
                return
            # Obtain isoconversional_method and related parameters
            if self.selected_isoconversional_method == '':
                QMessageBox.critical(self, "Error", "Please select an isoconversional method")
                return
            # Get the selected isoconversional method from the module icm
            isoconversional_method = getattr(icm, self.selected_isoconversional_method)

            # Retrieve the associated experimental parameters
            experimental_args_for_isoconversional_analysis = self.get_associated_experimental_parameters(
                self.isoconversional_method_parameters_experimental)
            
            # Retrieve the isoconversional method arguments
            isoconversional_method_args = self.get_isoconversional_method_args()
            if isoconversional_method_args == None:
                return

            # Perform the isoconversional analysis
            isoconversional_analysis_result = isoconversional_method(
                *experimental_args_for_isoconversional_analysis, *isoconversional_method_args)

            # Plot the results
            self.ax_isoconversional_analysis.clear()
            self.ax_isoconversional_analysis.plot(isoconversional_analysis_result[0], isoconversional_analysis_result[1])
            self.ax_isoconversional_analysis.set_xlabel("Conversion")
            self.ax_isoconversional_analysis.set_ylabel(r"$E_a$ (J/mol)")
            self.ax_isoconversional_analysis.set_title(f"Evolution of Ea obtained with \n{self.selected_isoconversional_method}")
            self.figure_isoconversional_analysis.tight_layout()
            self.canvas_isoconversional_analysis.draw_idle()
            
            self.ui.tabWidget_visualization.setCurrentIndex(1)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def update_rate_formLayout(self, event):
        """
        Update the entry boxes for rate parameters based on the selected rate model.

        Args:
            event (Event): The event that triggers the update.
        """
        self.clear_optimization_grids_and_combobox()
        # Clear formLayout
        for i in reversed(range(self.ui.formLayout_rate.count())):
            widget = self.ui.formLayout_rate.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Get the selected model
        self.selected_rate = self.ui.comboBox_rate_model.currentText()

        # Get parameters for the selected model
        rate_parameters = get_parameters_for_rate(self.selected_rate)

        # Lists to store the experimental parameters and parameters to optimize
        self.rate_parameters_experimental = []
        self.rate_parameters_to_optimize = []

        # List of values to match against
        experimental_param_values = ['T', 'extent', 'Tg', 'optional_parameters']
        
        # Dictionnary to store the graphical entities for the formLayout
        self.line_edit_dict_rate_model = {}
        
        for parameter in rate_parameters:
            if parameter in experimental_param_values:
                # Adding the experimental parameters to the list
                if parameter != "optional_parameters":
                    self.rate_parameters_experimental.append(parameter)
            else:
                # Adding the parameters to optimize to the list
                self.rate_parameters_to_optimize.append(parameter)
                line_edit = QLineEdit()
                self.line_edit_dict_rate_model[parameter] = line_edit
                self.ui.formLayout_rate.addRow(parameter+":",line_edit)

        
            
    def update_vitrification_formLayout(self, event):
        """
        Update the entry boxes for rate parameters based on the selected rate model.

        Args:
            event (Event): The event that triggers the update.
        """
        self.clear_optimization_grids_and_combobox()
        # Clear formLayout
        for i in reversed(range(self.ui.formLayout_vitrification.count())):
            widget = self.ui.formLayout_vitrification.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Get the selected model
        self.selected_vitrification = self.ui.comboBox_vitrification_model.currentText()

        # Get parameters for the selected model
        vitrification_parameters = get_parameters_for_vitrification(self.selected_vitrification)

        # Lists to store the experimental parameters and parameters to optimize
        self.vitrification_parameters_experimental = []
        self.vitrification_parameters_to_optimize = []

        # List of values to match against
        experimental_param_values = ['T', 'extent', 'extent_at_gel', 'Tg', 'optional_parameters']
        
        # Dictionnary to store the graphical entities for the formLayout
        self.line_edit_dict_vitrification_model = {}
        
        for parameter in vitrification_parameters:
            if parameter in experimental_param_values:
                # Adding the experimental parameters to the list
                if parameter != "optional_parameters":
                    self.vitrification_parameters_experimental.append(parameter)
            else:
                # Adding the parameters to optimize to the list
                self.vitrification_parameters_to_optimize.append(parameter)
                line_edit = QLineEdit()
                self.line_edit_dict_vitrification_model[parameter] = line_edit
                self.ui.formLayout_vitrification.addRow(parameter+":",line_edit)

        
        
    def update_coupling_formLayout(self, event):
        """
        Update the entry boxes for rate parameters based on the selected rate model.

        Args:
            event (Event): The event that triggers the update.
        """
        self.clear_optimization_grids_and_combobox()
        # Clear formLayout
        for i in reversed(range(self.ui.formLayout_coupling_law.count())):
            widget = self.ui.formLayout_coupling_law.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Get the selected model
        self.selected_coupling_law = self.ui.comboBox_coupling_law.currentText()

        # Get parameters for the selected model
        coupling_law_parameters = get_parameters_for_coupling(self.selected_coupling_law)

        # Lists to store the experimental parameters and parameters to optimize
        self.coupling_law_parameters_experimental = []
        self.coupling_law_parameters_to_optimize = []

        # List of values to match against
        experimental_param_values = ['T', 'extent', 'kc', 'kv', 'experimental_parameters', 'extent_at_gel', 'optional_parameters']
        
        # Dictionnary to store the graphical entities for the formLayout
        self.line_edit_dict_coupling_law = {}
        
        for parameter in coupling_law_parameters:
            if parameter in experimental_param_values:
                # Adding the experimental parameters to the list
                if parameter != "optional_parameters":
                    self.coupling_law_parameters_experimental.append(parameter)
            else:
                # Adding the parameters to optimize to the list
                self.coupling_law_parameters_to_optimize.append(parameter)
                line_edit = QLineEdit()
                self.line_edit_dict_coupling_law[parameter] = line_edit
                self.ui.formLayout_coupling_law.addRow(parameter+":",line_edit)

        
        
    def update_tg_formLayout(self, event):
        """
        Update the entry boxes for rate parameters based on the selected rate model.

        Args:
            event (Event): The event that triggers the update.
        """
        self.clear_optimization_grids_and_combobox()
        # Clear formLayout
        for i in reversed(range(self.ui.formLayout_tg.count())):
            widget = self.ui.formLayout_tg.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Get the selected model
        self.selected_tg_law = self.ui.comboBox_tg_law.currentText()

        # Get parameters for the selected model
        tg_law_parameters = get_parameters_for_tg(self.selected_tg_law)

        # Lists to store the experimental parameters and parameters to optimize
        self.tg_law_parameters_experimental = []
        self.tg_law_parameters_to_optimize = []

        # List of values to match against
        experimental_param_values = ['T', 'extent', 'Tg']
        
        # Dictionnary to store the graphical entities for the formLayout
        self.line_edit_dict_tg_law = {}
        
        for parameter in tg_law_parameters:
            if parameter in experimental_param_values:
                # Adding the experimental parameters to the list
                if parameter != "optional_parameters":
                    self.tg_law_parameters_experimental.append(parameter)
            else:
                # Adding the parameters to optimize to the list
                self.tg_law_parameters_to_optimize.append(parameter)
                line_edit = QLineEdit()
                self.line_edit_dict_tg_law[parameter] = line_edit
                self.ui.formLayout_tg.addRow(parameter+":",line_edit)
        

    def clear_models_and_parameters_forms_and_combobox(self):
        """
        Clear all formLayouts and reset comboboxes and dictionaries storing line edits and parameters.
        
        Clears the rate, vitrification, coupling law, and tg formLayouts from all their widgets.
        Resets corresponding comboboxes and lists storing experimental parameters and parameters to optimize.
        
        Returns:
        - None
        """
        # Clear the rate formLayout from all its widgets
        for i in reversed(range(self.ui.formLayout_rate.count())):
            widget = self.ui.formLayout_rate.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        # Reset the coupling law combobox
        self.ui.comboBox_rate_model.setCurrentIndex(-1)
        
        self.line_edit_dict_rate_model = {}
        self.rate_parameters_experimental = []
        self.rate_parameters_to_optimize = []
        self.selected_rate = ''
        
        # Clear the vitrification formLayout from all its widgets
        for i in reversed(range(self.ui.formLayout_vitrification.count())):
            widget = self.ui.formLayout_vitrification.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        # Reset the vitrification model combobox        
        self.ui.comboBox_vitrification_model.setCurrentIndex(-1)
        # Lists to store the experimental parameters and parameters to optimize
        self.line_edit_dict_vitrification_model = {}
        self.vitrification_parameters_experimental = []
        self.vitrification_parameters_to_optimize = []
        self.selected_vitrification = ''
        
        # Clear the coupling formLayout from all its widgets
        for i in reversed(range(self.ui.formLayout_coupling_law.count())):
            widget = self.ui.formLayout_coupling_law.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        # Reset the coupling law combobox
        self.ui.comboBox_coupling_law.setCurrentIndex(-1)
        
        self.line_edit_dict_coupling_law = {}
        self.coupling_law_parameters_experimental = []
        self.coupling_law_parameters_to_optimize = []
        self.selected_coupling_law = ''
        
        # Clear the tg formLayout from all its widgets
        for i in reversed(range(self.ui.formLayout_tg.count())):
            widget = self.ui.formLayout_tg.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        # Reset the tg law combobox
        self.ui.comboBox_tg_law.setCurrentIndex(-1)
        # Lists to store the experimental parameters and parameters to optimize
        self.line_edit_dict_tg_law = {}
        self.tg_law_parameters_experimental = []
        self.tg_law_parameters_to_optimize = []
        self.selected_tg_law = ''
        
        
    def autofill_models_parameters(self):
        """
        Autofill parameters in line edits for rate, vitrification, and coupling law models.
    
        Parameters:
        - self: The object instance.
    
        Returns:
        - None
        """
        try :
            for dict in [self.line_edit_dict_rate_model, self.line_edit_dict_vitrification_model, self.line_edit_dict_coupling_law]:
                for key,line_edit in dict.items():
                    if key in ["A", "A1", "A2"]:
                        line_edit.setText("1e8")
                    elif key in ["E", "Ea", "E1", "E2"]:
                        line_edit.setText("50000")
                    elif key in ["m", "n"]:
                        line_edit.setText("2")
                    elif key in ["Ad"]:
                        line_edit.setText("1")                  
                    elif key in ["C","C1", "C2"]:
                        line_edit.setText("50")
                    else:
                        QMessageBox.critical(self,"Error", f" An error occurred:\n The parameter {key} does'nt have a default value.\n Please modify the 'autofill_parameters' function in GUI.py.")
        except Exception as e:
            # Handle other exceptions with a generic error message
            QMessageBox.critical(self,"Error", f"An error occurred: {str(e)}")
            traceback.print_exc()   
    
    def update_global_optimization_gridLayout(self):
        """
        Update the global optimization grid layout based on selected optimization method.
    
        Retrieves parameters for the selected optimization method and creates corresponding input widgets
        in the grid layout for global optimization.
    
        Parameters:
        - self: The object instance.
    
        Returns:
        - None
        """
        try:
            if self.ui.comboBox_rate_model.currentText() == "":
                self.ui.comboBox_global_optimization_methods.setCurrentIndex(-1)
                QMessageBox.critical(self, 'Error', 'Please, select a rate law')
                traceback.print_exc()
                return
    
            # Clear parameter entry boxes
            for i in reversed(range(self.ui.gridLayout_global_optimization.count())):
                widget = self.ui.gridLayout_global_optimization.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
    
            # Get the selected optimization method from the combobox
            self.selected_global_optimization = self.ui.comboBox_global_optimization_methods.currentText()
    
            # Get dictionary of parameters for the selected optimization method
            global_optimization_method_parameters = get_parameters_for_optimization(self.selected_global_optimization)
    
            self.labels_dict_global_optimization = {}
            self.entries_dict_global_optimization = {}
    
            row = 0
            for key, value_info in global_optimization_method_parameters.items():
                value_type = value_info["type"]
                if value_type == float or value_type == int:
                    label = QLabel(key)
                    line_edit = QLineEdit()
                    self.labels_dict_global_optimization[key] = label
                    self.entries_dict_global_optimization[key] = line_edit
                    self.ui.gridLayout_global_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_global_optimization.addWidget(line_edit, row, 1)
                    row += 1
                elif value_type == bool:
                    label = QLabel(key)
                    combobox = QComboBox()
                    combobox.addItems(["Yes", "No"])
                    if key == "vectorized":
                        combobox.setCurrentIndex(1)
                    self.labels_dict_global_optimization[key] = label
                    self.entries_dict_global_optimization[key] = combobox
                    self.ui.gridLayout_global_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_global_optimization.addWidget(combobox, row, 1)
                    row += 1
                elif value_type == list:
                    label = QLabel(key)
                    combobox = QComboBox()
                    if key == "jac":
                        combobox.addItems(["None", "2-point", "3-point", "cs"])
                    else:
                        QMessageBox.critical(self, "Unsupported Key", f"The key '{key}' is not handled by the program.")
                    self.labels_dict_global_optimization[key] = label
                    self.entries_dict_global_optimization[key] = combobox
                    self.ui.gridLayout_global_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_global_optimization.addWidget(combobox, row, 1)
                    row += 1
                elif value_type == "sequence":
                    # Create a first line to indicate min and max values
                    min_label = QLabel("min")
                    max_label = QLabel("max")
                    self.labels_dict_global_optimization["min"] = min_label
                    self.labels_dict_global_optimization["max"] = max_label
                    self.ui.gridLayout_global_optimization.addWidget(min_label, row, 1)
                    self.ui.gridLayout_global_optimization.addWidget(max_label, row, 2)
                    row += 1
                    # Merge dict to get all the parameters to optimize
                    parameters_to_optimize = self.line_edit_dict_rate_model | self.line_edit_dict_vitrification_model | self.line_edit_dict_coupling_law
                    for parameter in parameters_to_optimize.keys():
                        label = QLabel(parameter)
                        line_edit_min = QLineEdit()
                        line_edit_max = QLineEdit()
                        self.labels_dict_global_optimization[parameter] = label
                        self.entries_dict_global_optimization["min" + parameter] = line_edit_min
                        self.entries_dict_global_optimization["max" + parameter] = line_edit_max
                        self.ui.gridLayout_global_optimization.addWidget(label, row, 0)
                        self.ui.gridLayout_global_optimization.addWidget(line_edit_min, row, 1)
                        self.ui.gridLayout_global_optimization.addWidget(line_edit_max, row, 2)
                        row += 1
                elif value_type == "init":
                    label = QLabel(key)
                    combobox = QComboBox()
                    combobox.addItems(["latinhypercube", "sobol", "halton", "random"])
                    self.labels_dict_global_optimization[key] = label
                    self.entries_dict_global_optimization[key] = combobox
                    self.ui.gridLayout_global_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_global_optimization.addWidget(combobox, row, 1)
                    row += 1
                elif value_type == "updating":
                    label = QLabel(key)
                    combobox = QComboBox()
                    combobox.addItems(["immediate", "deferred"])
                    self.labels_dict_global_optimization[key] = label
                    self.entries_dict_global_optimization[key] = combobox
                    self.ui.gridLayout_global_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_global_optimization.addWidget(combobox, row, 1)
                    row += 1
                elif value_type == "sampling_method":
                    label = QLabel(key)
                    combobox = QComboBox()
                    combobox.addItems(["simplicial", "halton", "sobol"])
                    self.labels_dict_global_optimization[key] = label
                    self.entries_dict_global_optimization[key] = combobox
                    self.ui.gridLayout_global_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_global_optimization.addWidget(combobox, row, 1)
                    row += 1
                elif value_type == "strategy":
                    label = QLabel(key)
                    combobox = QComboBox()
                    combobox.addItems(["best1bin",
                                       "best1exp",
                                       "rand1bin",
                                       "rand1exp",
                                       "rand2bin",
                                       "rand2exp",
                                       "randtobest1bin",
                                       "randtobest1exp",
                                       "currenttobest1bin",
                                       "currenttobest1exp",
                                       "best2exp",
                                       "best2bin"])
                    self.labels_dict_global_optimization[key] = label
                    self.entries_dict_global_optimization[key] = combobox
                    self.ui.gridLayout_global_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_global_optimization.addWidget(combobox, row, 1)
                    row += 1
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            traceback.print_exc()
            
    def update_local_optimization_gridLayout(self):
        """
        Update the local optimization grid layout based on selected optimization method.
    
        Retrieves parameters for the selected optimization method and creates corresponding input widgets
        in the grid layout for local optimization.
    
        Parameters:
        - self: The object instance.
    
        Returns:
        - None
        """
        try:
            if self.ui.comboBox_rate_model.currentText() == "":
                QMessageBox.critical(self, "Error", "Please, select a rate law")
                self.ui.comboBox_local_optimization_methods.setCurrentIndex(-1)
                return
            
            # Clear parameter entry boxes
            for i in reversed(range(self.ui.gridLayout_local_optimization.count())):
                widget = self.ui.gridLayout_local_optimization.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
            
            # Get the selected optimization method from the combobox
            self.selected_local_optimization = self.ui.comboBox_local_optimization_methods.currentText()
            
            # Get dictionary of parameters for the selected optimization method
            local_optimization_method_parameters = get_parameters_for_optimization(self.selected_local_optimization)
            
            self.labels_dict_local_optimization = {}
            self.entries_dict_local_optimization = {}
            
            row = 0
            for key, value_info in local_optimization_method_parameters.items():
                value_type = value_info["type"]
                if value_type == float or value_type == int:
                    label = QLabel(key)
                    line_edit = QLineEdit()
                    self.labels_dict_local_optimization[key] = label
                    self.entries_dict_local_optimization[key] = line_edit
                    self.ui.gridLayout_local_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_local_optimization.addWidget(line_edit, row, 1)
                    row += 1
                elif value_type == bool:
                    label = QLabel(key)
                    combobox = QComboBox()
                    combobox.addItems(["Yes", "No"])
                    if key == "vectorized":
                        combobox.setCurrentIndex(1)
                    self.labels_dict_local_optimization[key] = label
                    self.entries_dict_local_optimization[key] = combobox
                    self.ui.gridLayout_local_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_local_optimization.addWidget(combobox, row, 1)
                    row += 1
                elif value_type == list:
                    label = QLabel(key)
                    combobox = QComboBox()
                    if key == "jac":
                        combobox.addItems(["None", "2-point", "3-point", "cs"])
                    else:
                        QMessageBox.critical(self, "Unsupported Key", f"The key '{key}' is not handled by the program.")
                    self.labels_dict_local_optimization[key] = label
                    self.entries_dict_local_optimization[key] = combobox
                    self.ui.gridLayout_local_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_local_optimization.addWidget(combobox, row, 1)
                    row += 1
                elif value_type == "sequence":
                    # Create a first line to indicate min and max values
                    min_label = QLabel("min")
                    max_label = QLabel("max")
                    self.labels_dict_local_optimization["min"] = min_label
                    self.labels_dict_local_optimization["max"] = max_label
                    self.ui.gridLayout_local_optimization.addWidget(min_label, row, 1)
                    self.ui.gridLayout_local_optimization.addWidget(max_label, row, 2)
                    row += 1
                    # Merge dict to get all the parameters to optimize
                    parameters_to_optimize = self.line_edit_dict_rate_model | self.line_edit_dict_vitrification_model | self.line_edit_dict_coupling_law
                    for parameter in parameters_to_optimize.keys():
                        label = QLabel(parameter)
                        line_edit_min = QLineEdit()
                        line_edit_max = QLineEdit()
                        self.labels_dict_local_optimization[parameter] = label
                        self.entries_dict_local_optimization["min" + parameter] = line_edit_min
                        self.entries_dict_local_optimization["max" + parameter] = line_edit_max
                        self.ui.gridLayout_local_optimization.addWidget(label, row, 0)
                        self.ui.gridLayout_local_optimization.addWidget(line_edit_min, row, 1)
                        self.ui.gridLayout_local_optimization.addWidget(line_edit_max, row, 2)
                        row += 1
                elif value_type == "init":
                    label = QLabel(key)
                    combobox = QComboBox()
                    combobox.addItems(["latinhypercube", "sobol", "halton", "random"])
                    self.labels_dict_local_optimization[key] = label
                    self.entries_dict_local_optimization[key] = combobox
                    self.ui.gridLayout_local_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_local_optimization.addWidget(combobox, row, 1)
                    row += 1
                elif value_type == "updating":
                    label = QLabel(key)
                    combobox = QComboBox()
                    combobox.addItems(["immediate", "deferred"])
                    self.labels_dict_local_optimization[key] = label
                    self.entries_dict_local_optimization[key] = combobox
                    self.ui.gridLayout_local_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_local_optimization.addWidget(combobox, row, 1)
                    row += 1
                elif value_type == "sampling_method":
                    label = QLabel(key)
                    combobox = QComboBox()
                    combobox.addItems(["simplicial", "halton", "sobol"])
                    self.labels_dict_local_optimization[key] = label
                    self.entries_dict_local_optimization[key] = combobox
                    self.ui.gridLayout_local_optimization.addWidget(label, row, 0)
                    self.ui.gridLayout_local_optimization.addWidget(combobox, row, 1)
                    row += 1
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def update_cost_functions_formLayout(self):
        if self.ui.comboBox_cost_functions.currentText() == "":
            QMessageBox.critical(self,"Error", "Please, select a rate law")
            self.ui.comboBox_cost_functions.setCurrentIndex(-1)
            return
        
        # Clear parameter entry boxes
        for i in reversed(range(self.ui.gridLayout_cost_functions.count())):
            widget = self.ui.gridLayout_cost_functions.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Get the selected optimization method from the combobox
        self.selected_cost_function = self.ui.comboBox_cost_functions.currentText()
        
        # Get dictionary of parameters for the selected optimization method
        cost_function_parameters = get_parameters_for_rss(self.selected_cost_function)
        
        # Lists to store the experimental parameters and input parameters
        self.cost_function_parameters_experimental = []
        self.cost_function_parameters_input = []
        
        # List of values to match against
        experimental_param_values = ['T', 'extent', 'Tg']
        
        
        # Dictionnary to store the graphical entities for the formLayout
        self.labels_dict_cost_function = {}
        self.entries_dict_cost_function = {}
        
        row = 0            
        for parameter in cost_function_parameters:
            if parameter in experimental_param_values:
                # Adding the experimental parameters to the list
                if parameter != "optional_parameters":
                    self.cost_function_parameters_experimental.append(parameter)
            else:
                self.cost_function_parameters_input.append(parameter)
                label = QLabel(parameter)
                line_edit = QLineEdit()
                self.labels_dict_cost_function[parameter] = label
                self.entries_dict_cost_function[parameter] = line_edit
                self.ui.gridLayout_cost_functions.addWidget(label,row,0)
                self.ui.gridLayout_cost_functions.addWidget(line_edit,row,1)
                row = row + 1
    
    def clear_optimization_grids_and_combobox(self):
        # Clear parameter entry boxes    
        for i in reversed(range(self.ui.gridLayout_global_optimization.count())):
            widget = self.ui.gridLayout_global_optimization.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.labels_dict_global_optimization = {}
        self.entries_dict_global_optimization = {}
        self.ui.comboBox_global_optimization_methods.setCurrentIndex(-1)
        self.selected_global_optimization = ''
        
        # Clear parameter entry boxes
        for i in reversed(range(self.ui.gridLayout_local_optimization.count())):
            widget = self.ui.gridLayout_local_optimization.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.labels_dict_local_optimization = {}
        self.entries_dict_local_optimization = {}
        self.ui.comboBox_local_optimization_methods.setCurrentIndex(-1)
        self.selected_local_optimization = ''
        
        # Clear parameter entry boxes
        for i in reversed(range(self.ui.gridLayout_cost_functions.count())):
            widget = self.ui.gridLayout_cost_functions.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.labels_dict_cost_function = {}
        self.entries_dict_cost_function = {}
        self.cost_function_parameters_experimental = []
        self.cost_function_parameters_input = []
        self.ui.comboBox_cost_functions.setCurrentIndex(-1)
        self.selected_cost_function = ''
        

    def autofill_optimization_parameters(self):
        try :
            for dict in [self.entries_dict_global_optimization, self.entries_dict_local_optimization, self.entries_dict_cost_function]:
                for key,object in dict.items():
                    if key in ["minA", "minA1", "minA2"]:
                        object.setText("1")
                    elif key in ["minAd"]:
                       object.setText("1e-20")    
                    elif key in ["maxA", "maxA1", "maxA2", "maxAd"]:
                       object.setText("1e20")
                    elif key in ["minE", "minEa", "minE1", "minE2"]:
                        object.setText("1000")
                    elif key in ["maxE", "maxEa", "maxE1", "maxE2"]:
                        object.setText("350000")
                    elif key in ["minm", "minn"]:
                        object.setText("0.1")
                    elif key in ["maxm", "maxn"]:
                        object.setText("20")
                    elif key in ["minC","minC1", "minC2"]:
                        object.setText("1")
                    elif key in ["maxC","maxC1", "maxC2"]:
                        object.setText("350")
                    elif key in ["disp", "return_all", "adaptive","polish"]:
                        object.setCurrentText("Yes")
                    elif key in ["vectorized"]:
                        object.setCurrentText("No")
                    elif key in ["sampling_method"]:
                        object.setCurrentText("simplicial")
                    elif key in ["init"]:
                        object.setCurrentText("latinhypercube")
                    elif key in ["updating"]:
                        object.setCurrentText("")
                    elif key in ["strategy"]:
                        object.setCurrentText("best1bin")
                    elif key in ["maxiter","iters","niters","niter"]:
                        object.setText("1200")
                    elif key in ["n"]:
                        object.setText("500")
                    elif key in ["workers"]:
                        object.setText("4")
                    elif key in ["maxfev", "maxfun", "norm", "eps", "maxls", "iprint", "maxcor","T","stepsize","interval","niter_success","target_accept_rate","stepwise_factor","popsize","mutation","recombination"]:
                        object.setText("")
                    elif key in ["tol","atol","xatol", "xrtol", "xtol", "fatol", "ftol", "gtol"]:
                        object.setText("1e-15")
                    elif key in ["extent_limit"]:
                        object.setText("0.707")
                    elif key in ["amplification_factor"]:
                        object.setText("10")
                    elif key in ["fraction_to_amplify"]:
                        object.setText("0.5")
                    elif key in ["jac"]:
                        object.setCurrentText("None")
                    elif key in ["bounds"]:
                        pass       
                    else:
                        QMessageBox.critical(self,"Error", f" An error occurred:\n The parameter {key} does'nt have a default value.\n Please modify the 'autofill_parameters' function in main.py.")
        except Exception as e:
            # Handle other exceptions with a generic error message
            QMessageBox.critical(self,"Error", f"An error occurred: {str(e)}")
            traceback.print_exc()
            
    def get_global_optimization_args_dict(self,selected_optimization_method):
        reference_dict = get_parameters_for_optimization(selected_optimization_method)
        to_return_dict = {}
        try:
            for key, value_info in reference_dict.items():
                value_type = value_info["type"]
                optional = value_info["optional"]
                if value_type == int:
                    if self.entries_dict_global_optimization[key].text() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    if self.entries_dict_global_optimization[key].text() != '':
                        to_return_dict[key] = int(self.entries_dict_global_optimization[key].text())
                elif value_type == float:
                    if self.entries_dict_global_optimization[key].text() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    if self.entries_dict_global_optimization[key].text() != '':
                        to_return_dict[key] = float(self.entries_dict_global_optimization[key].text()) 
                elif value_type == bool:
                    if self.entries_dict_global_optimization[key].currentText() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    if self.entries_dict_global_optimization[key].currentText() == "Yes":
                        to_return_dict[key] = True
                    elif self.entries_dict_global_optimization[key].currentText() == "No":
                        to_return_dict[key] = False
                    else:
                        raise ValueError(f"Parameter '{key}' is a boolean and should be 'Yes' or 'No' but its value is currently '{self.entries_dict_global_optimization[key].currentText()}'")
                elif value_type == list:                     
                    if self.entries_dict_global_optimization[key].currentText() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    to_return_dict[key] = self.entries_dict_global_optimization[key].currentText()
                elif value_type == "sequence":
                    # Merge dict to get all the parameters to optimize
                    parameters_to_optimize = self.line_edit_dict_rate_model | self.line_edit_dict_vitrification_model | self.line_edit_dict_coupling_law
                    bounds = []
                    if not optional:
                        for parameter in parameters_to_optimize.keys():
                            min_param = self.entries_dict_global_optimization["min" + parameter].text()
                            max_param = self.entries_dict_global_optimization["max" + parameter].text()
                            if min_param == '' or max_param =='':
                                raise ValueError(f"Parameters '{key}' are mandatory for optimization method '{selected_optimization_method}'")
                            else:
                                min_param = float(min_param)
                                max_param = float(max_param)
                            bounds.append((min_param, max_param))
                    else:
                        for parameter in parameters_to_optimize.keys():
                            min_param = float(self.entries_dict_global_optimization["min" + parameter].text())
                            max_param = float(self.entries_dict_global_optimization["max" + parameter].text())
                            bounds.append((min_param, max_param))
                    to_return_dict[key] = bounds
                elif value_type == "init":
                    if self.entries_dict_global_optimization[key].currentText() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    to_return_dict[key] = self.entries_dict_global_optimization[key].currentText()
                elif value_type == "updating":
                    if self.entries_dict_global_optimization[key].currentText() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    to_return_dict[key] = self.entries_dict_global_optimization[key].currentText()               
                elif value_type == "sampling_method":
                    if self.entries_dict_global_optimization[key].currentText() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    to_return_dict[key] = self.entries_dict_global_optimization[key].currentText()
                elif value_type == "strategy":
                    if self.entries_dict_global_optimization[key].currentText() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    to_return_dict[key] = self.entries_dict_global_optimization[key].currentText()
                else:
                    # Handle other exceptions with a generic error message
                    raise AttributeError( f" An error occurred:\n The parameter {key} is not handled.\n Please modify the 'get_global_optimization_args_dict' function in main.py.")
                    traceback.print_exc()
            return to_return_dict
        except Exception as e:
            # Handle other exceptions with a generic error message
            QMessageBox.critical(self,"Error", f"An error occurred: {str(e)}")
            traceback.print_exc()   
    
    def get_local_optimization_args_dict(self,selected_optimization_method):
        reference_dict = get_parameters_for_optimization(selected_optimization_method)
        options_dict = {}
        try:
            for key, value_info in reference_dict.items():
                value_type = value_info["type"]
                optional = value_info["optional"]
                if value_type == int:
                    if self.entries_dict_local_optimization[key].text() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    if self.entries_dict_local_optimization[key].text() != '':
                        options_dict[key] = int(self.entries_dict_local_optimization[key].text())
                elif value_type == float:
                    if self.entries_dict_local_optimization[key].text() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    if self.entries_dict_local_optimization[key].text() != '':
                        options_dict[key] = float(self.entries_dict_local_optimization[key].text())
                elif value_type == bool:
                    if self.entries_dict_local_optimization[key].currentText() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    if self.entries_dict_local_optimization[key].currentText() == "Yes":
                        options_dict[key] = True
                    elif self.entries_dict_local_optimization[key].currentText() == "No":
                        options_dict[key] = False
                    else:
                        raise ValueError(f"Parameter '{key}' is a boolean and should be 'Yes' or 'No' but its value is currently '{self.entries_dict_local_optimization[key].currentText()}'")
                elif value_type == list:
                    if self.entries_dict_local_optimization[key].currentText() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")               
                    options_dict[key] = self.entries_dict_local_optimization[key].currentText()
                elif value_type == "sequence":
                    # Merge dict to get all the parameters to optimize
                    parameters_to_optimize = self.line_edit_dict_rate_model | self.line_edit_dict_vitrification_model | self.line_edit_dict_coupling_law
                    bounds = []
                    if not optional:
                        for parameter in parameters_to_optimize.keys():
                            min_param = self.entries_dict_local_optimization["min" + parameter].text()
                            max_param = self.entries_dict_local_optimization["max" + parameter].text()
                            if min_param == '' or max_param =='':
                                raise ValueError(f"Parameters '{key}' are mandatory for optimization method '{selected_optimization_method}'")
                            else:
                                min_param = float(min_param)
                                max_param = float(max_param)
                            bounds.append((min_param, max_param))
                    else:
                        for parameter in parameters_to_optimize.keys():
                            min_param = float(self.entries_dict_local_optimization["min" + parameter].text())
                            max_param = float(self.entries_dict_local_optimization["max" + parameter].text())
                            bounds.append((min_param, max_param))
                    options_dict[key] = bounds
                elif value_type == "init":
                    if self.entries_dict_local_optimization[key].currentText() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")                    
                    options_dict[key] = self.entries_dict_local_optimization[key].currentText()
                elif value_type == "updating":
                    if self.entries_dict_local_optimization[key].currentText() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    options_dict[key] = self.entries_dict_local_optimization[key].currentText()               
                elif value_type == "sampling_method":
                    if self.entries_dict_local_optimization[key].currentText() == '' and not optional:
                        raise ValueError(f"The parameter '{key}' must be provided for optimization method '{selected_optimization_method}'")
                    options_dict[key] = self.entries_dict_local_optimization[key].currentText()
                else:
                    # Handle other exceptions with a generic error message
                    raise AttributeError( f" An error occurred:\n The parameter {key} is not handled.\n Please modify the 'get_local_optimization_args_dict' function in main.py.")
                    traceback.print_exc()
                    
            main_args_dict_for_local_optimization = {"jac": None, "hess": None, "hessp": None, "bounds": None,"constraints": (), "tol": None, "callback": None}
            keys_to_remove_from_option_dict = []
            for key, value in options_dict.items():
                if key in main_args_dict_for_local_optimization.keys():
                    main_args_dict_for_local_optimization[key] = options_dict[key]
                    keys_to_remove_from_option_dict.append(key)
            for key in keys_to_remove_from_option_dict:
                del options_dict[key]
            main_args_dict_for_local_optimization['options'] = options_dict  
            return main_args_dict_for_local_optimization
        except Exception as e:
            # Handle other exceptions with a generic error message
            QMessageBox.critical(self,"Error", f"An error occurred: {str(e)}")
            traceback.print_exc()   

    def launch_optimization(self):
        """
        Launch the optimization process.
    
        This function checks the necessary conditions for optimization, assigns necessary parameters,
        and starts the optimization process in a separate thread.
    
        Parameters:
        - self: The object instance.
    
        Returns:
        - None
        """
        try:
            # =============================================================================
            # Check before launching optimization            
            # =============================================================================
            # Check that data was successfully extracted
            if not hasattr(self, 'successful_extraction') or not self.successful_extraction:
                QMessageBox.critical(self, "Error", "Please, make sure you extracted the data successfully.")
                return
            # Check that there's a model to optimize
            if self.selected_rate == '' and self.selected_vitrification == '':
                QMessageBox.critical(self, "Error", "Please, make sure you at least selected a rate model or a vitrification model to optimize.")
                return
            # Check that there's a coupling law if both rate and vitrification models are selected
            if self.selected_rate != '' and self.selected_vitrification != '':
                if self.selected_coupling_law == '':
                    QMessageBox.critical(self, "Error", "Please, make sure you selected the coupling law between rate model and vitrification model")
                    return
            # Check that Tg is selected if necessary
            if any("Tg" in lst for lst in [self.rate_parameters_experimental, self.vitrification_parameters_experimental, self.coupling_law_parameters_experimental]):
                if self.selected_tg_law == '':
                    QMessageBox.critical(self, "Error", "The current optimization requires the computation of the Tg. \nPlease select a Tg model in the 'Models and parameters section.")
                    return
            # Check that an optimization is selected
            if self.selected_global_optimization == '' and self.selected_local_optimization == '':
                QMessageBox.critical(self, "Error", "Please, make sure you at least selected a global or local optimization method.")
                return
            # Check that a cost function is selected
            if self.selected_cost_function == '':
                QMessageBox.critical(self, "Error", "Please, make sure you selected a cost function")
                return
            # =============================================================================
            # Function and args attribution            
            # =============================================================================
            self.initial_guess = np.array([])
            self.results = None
            self.ui.progressBar.setValue(0)
            if self.selected_rate != '':
                self.rate_law = getattr(km, self.selected_rate)
                self.experimental_args_for_rate = self.get_associated_experimental_parameters(self.rate_parameters_experimental)
                self.number_of_parameters_to_optimize_for_rate = len(self.line_edit_dict_rate_model)
                try:
                    self.initial_guess = np.append(self.initial_guess, [float(line_edit.text()) for line_edit in self.line_edit_dict_rate_model.values()])
                except ValueError:
                    QMessageBox.critical(self, "Error", "Please, indicate an initial guess for the rate law.\n(In the 'Models and parameters' section of the 'Optimiztion' dock)")
                    return                    
            else:
                self.rate_law = None
                self.experimental_args_for_rate = None
                self.number_of_parameters_to_optimize_for_rate = 0
            
            if self.selected_vitrification != '':
                self.vitrification_law = getattr(km, self.selected_vitrification)
                self.experimental_args_for_vitrification = self.get_associated_experimental_parameters(self.vitrification_parameters_experimental)
                self.number_of_parameters_to_optimize_for_vitrification = len(self.line_edit_dict_vitrification_model)
                try:
                    self.initial_guess = np.append(self.initial_guess, [float(line_edit.text()) for line_edit in self.line_edit_dict_vitrification_model.values()])
                except ValueError:
                    QMessageBox.critical(self, "Error", "Please, indicate an initial guess for the vitrification law.\n(In the 'Models and parameters' section of the 'Optimiztion' dock)")
                    return
            else:
                self.vitrification_law = None
                self.experimental_args_for_vitrification = None
                self.number_of_parameters_to_optimize_for_vitrification = 0
            if self.selected_coupling_law != '':
                self.coupling_law = getattr(km, self.selected_coupling_law)
                self.experimental_args_for_coupling = self.get_associated_experimental_parameters(self.coupling_law_parameters_experimental)
                try:
                    self.initial_guess = np.append(self.initial_guess, [float(line_edit.text()) for line_edit in self.line_edit_dict_coupling_law.values()])
                except ValueError:
                    QMessageBox.critical(self, "Error", "Please, indicate an initial guess for the coupling law.\n(In the 'Models and parameters' section of the 'Optimiztion' dock)")
                    return
            else:
                self.coupling_law = None
                self.experimental_args_for_coupling = None
            if self.selected_tg_law != '':
                self.tg_law = getattr(km, self.selected_tg_law)
                self.experimental_args_for_tg = self.get_associated_experimental_parameters(self.tg_law_parameters_experimental)
                self.tg_args = np.array([])
                self.tg_args = np.append(self.tg_args, tuple([float(line_edit.text()) for line_edit in self.line_edit_dict_vitrification_model.values()]))
            else:
                self.tg_law = None
                self.experimental_args_for_tg = None
                self.tg_args = None            
            if self.selected_global_optimization != '':
                self.global_optimization = getattr(scipy.optimize, self.selected_global_optimization)
                
                self.global_optimization_args_dict = self.get_global_optimization_args_dict(self.selected_global_optimization)
                
            else:
                self.global_optimization = None
                self.global_optimization_args_dict = None
            if self.selected_local_optimization != '':
                self.local_optimization = getattr(scipy.optimize, 'minimize')
                
                self.local_optimization_args_dict = self.get_local_optimization_args_dict(self.selected_local_optimization)
                
                self.local_optimization_args_dict['method'] = self.selected_local_optimization
            else:
                self.local_optimization = None
                self.local_optimization_args_dict = None
            if self.selected_cost_function != '':
                self.cost_function = getattr(opt, self.selected_cost_function)
                self.experimental_args_for_cost_function = self.get_associated_experimental_parameters(self.cost_function_parameters_experimental)
                self.cost_function_args = tuple([float(line_edit.text()) for line_edit in self.entries_dict_cost_function.values()])
            else:
                self.cost_function = None
                self.cost_function_args = None
            
            # Check if the maximum number of iterations is an argument of the selected optimization methods
            self.max_iter = "default"
            keys_to_check_for_iterations = ["maxiter","niter","n"]
            if self.global_optimization:
                for key in keys_to_check_for_iterations:
                    if key in self.global_optimization_args_dict.keys():
                        self.max_iter = self.global_optimization_args_dict[key]
            else:
                for key in keys_to_check_for_iterations:
                    if key in self.local_optimization_args_dict['options'].keys():
                        self.max_iter = self.local_optimization_args_dict['options'][key]

            
            self.ui.textEdit_output_of_optimization.clear()
            
            # =============================================================================
            # Start a thread to perform optimization without blocking the GUI         
            # =============================================================================
            self.optimization_thread = OptimizationThread(self.cost_function,
                                                          self.initial_guess,
                                                          self.selected_global_optimization,
                                                          self.global_optimization,
                                                          self.global_optimization_args_dict,
                                                          self.selected_local_optimization,
                                                          self.local_optimization,
                                                          self.local_optimization_args_dict,
                                                          self.experimental_rate, 
                                                          self.rate_law, 
                                                          self.experimental_args_for_rate, 
                                                          self.number_of_parameters_to_optimize_for_rate, 
                                                          self.vitrification_law, 
                                                          self.experimental_args_for_vitrification, 
                                                          self.number_of_parameters_to_optimize_for_vitrification, 
                                                          self.coupling_law, 
                                                          self.experimental_args_for_coupling, 
                                                          self.tg_law, 
                                                          self.experimental_args_for_tg, 
                                                          self.tg_args, 
                                                          self.cost_function_args,                                                          
                                                          self.experimental_args_for_cost_function,
                                                          self.max_iter
                                                          )
            self.ui.pushButton_launch_optimization.setEnabled(False)
            self.optimization_thread.start()
            self.optimization_thread.update_progress_bar_signal.connect(self.update_progress_bar)
            self.optimization_thread.update_graph_signal.connect(self.update_graph)
            self.optimization_thread.end_of_optimization.connect(self.update_GUI_at_end_of_optimization)
            self.optimization_thread.error_in_optimization_thread.connect(self.display_error_in_optimization_thread)
        except Exception as e:
            # Handle other exceptions with a generic error message
            traceback.print_exc() 
            QMessageBox.critical(self,"Error", f"An error occurred: {str(e)}")
            return
            
    def update_progress_bar(self,progress):
        """
        Update the progress bar with the given progress value.
    
        Parameters
        ----------
        self : object
            The object instance.
        progress : int
            The value indicating the progress of the optimization process.
    
        Returns
        -------
        None
        """
        self.ui.progressBar.setValue(progress)
        
    def update_graph(self,increment,estimated_remaining_seconds,x,*args,**kwargs):
        """
        Update the graph and output of the optimization process.
    
        Parameters
        ----------
        self : object
            The object instance.
        increment : int
            The current increment of the optimization process.
        estimated_remaining_seconds : int
            The estimated remaining time for the optimization process.
        x : Any
            Current optimization parameters.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.
    
        Returns
        -------
        None
        """
        increment_info = f"Increment: {increment}\nCurrent x: {x}\n"
        increment_info += '\n'.join([f"- {arg}" for arg in args])
        increment_info += '\n'
        increment_info += '\n'.join([f"- {key}: {value}" for key, value in kwargs.items()])
        increment_info += '\n'
        self.ui.textEdit_output_of_optimization.insertPlainText(increment_info)
        self.ui.textEdit_output_of_optimization.moveCursor(QTextCursor.End)
        
        # Convert remaining seconds to hours, minutes, and seconds
        remaining_hours, remaining_seconds = divmod(estimated_remaining_seconds, 3600)
        remaining_minutes, remaining_seconds = divmod(remaining_seconds, 60)
        remaining_time_str = "{:02}hours:{:02}min:{:02}s".format(int(remaining_hours), int(remaining_minutes), int(remaining_seconds))
        self.ui.label_remaing_time.setText(f"Remaining time: {remaining_time_str}")
        
        rate_opti = opt.model(x,
                              self.rate_law,
                              self.experimental_args_for_rate,
                              self.number_of_parameters_to_optimize_for_rate,
                              self.vitrification_law,
                              self.experimental_args_for_vitrification,
                              self.number_of_parameters_to_optimize_for_vitrification,
                              self.coupling_law,
                              self.experimental_args_for_coupling,
                              self.tg_law,
                              self.experimental_args_for_tg,
                              self.tg_args)
        
        # The result of the "opt.model" function contained in "rate_opti" are an aggregation of the rates contained in all the files.
        # Since we want to display a curve for each, we split the data thanks to "range_of_plot"
        range_of_plot = [0, 0]
        self.ax_optimization.clear()
        self.ax_optimization.set_title(f'Optimization at increment:{increment}')
        self.ax_optimization.set_xlabel("Time (s)")
        self.ax_optimization.set_ylabel("Rate (s-1)")
        
        for index, filepath in enumerate(self.selected_shortened_file_paths):
            # Extend the plot range according to the number of experimental points
            range_of_plot[1] = range_of_plot[1] + len(self.experimental_times[index])
            # Plot the experimental rate with respect to time
            curve1 = self.ax_optimization.plot(self.experimental_times[index], self.experimental_rates[index], label=f"Experimental rate for {self.selected_shortened_file_paths[index]}", alpha=0.8)
            # Get the color of curve1 so that experimental and optimized rate have the same color
            color_of_first_curve = curve1[0].get_color()
            # Plot the optimized rate with respect to time
            self.ax_optimization.plot(self.experimental_times[index], rate_opti[range_of_plot[0]:range_of_plot[1]], label=f"Model rate for {self.selected_shortened_file_paths[index]}", linestyle='dashed', color=color_of_first_curve, linewidth=2)
            # Modify the initial range of plot so that it corresponds to the initial index of next file data in "rate_opti" 
            range_of_plot[0] = range_of_plot[0] + len(self.experimental_times[index])

        self.ax_optimization.legend()
        self.canvas_optimization.draw_idle()
        
        self.ui.tabWidget_visualization.setCurrentIndex(2)
    
    def update_GUI_at_end_of_optimization(self,results):
        try:
            self.optimization_thread.terminate()
            self.ui.pushButton_launch_optimization.setEnabled(True)
            self.ui.progressBar.setValue(100)
            self.ui.label_remaing_time.setText("Remaining time: (No optimization runnning)")
            
            self.results = results
            print("final x used for plot:", self.results.x)
            rate_opti = opt.model(self.results.x,
                                  self.rate_law,
                                  self.experimental_args_for_rate,
                                  self.number_of_parameters_to_optimize_for_rate,
                                  self.vitrification_law,
                                  self.experimental_args_for_vitrification,
                                  self.number_of_parameters_to_optimize_for_vitrification,
                                  self.coupling_law,
                                  self.experimental_args_for_coupling,
                                  self.tg_law,
                                  self.experimental_args_for_tg,
                                  self.tg_args)
            
            dif = rate_opti-self.experimental_rate
            self.mean_rss = np.dot(dif, dif)/len(dif)
            
            # Update output textEdit widget with
            summary_info = self.get_summary_info()
            self.ui.textEdit_output_of_optimization.insertPlainText(summary_info)
            
            current_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            src_dir = os.path.dirname(os.path.realpath(__file__))
            results_dir = os.path.join(src_dir, "..", "results")
            filename = f"{current_date}_results_of_optimization.txt"
            file_path = os.path.join(results_dir, filename)
            
            # Create the 'results' folder if it doesn't exist
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            with open(file_path, 'w') as file:
                file.write(summary_info)
            
            # The result of the "opt.model" function contained in "rate_opti" are an aggregation of the rates contained in all the files.
            # Since we want to display a curve for each, we split the data thanks to "range_of_plot"
            range_of_plot = [0, 0]
            
            self.ax_optimization.clear()
            self.ax_optimization.set_title('Final result of optimization')
            self.ax_optimization.set_xlabel("Time (s)")
            self.ax_optimization.set_ylabel("Rate (s-1)")
            
            for index, filepath in enumerate(self.selected_shortened_file_paths):
                # Extend the plot range according to the number of experimental points
                range_of_plot[1] = range_of_plot[1] + len(self.experimental_times[index])
                # Plot the experimental rate with respect to time
                curve1 = self.ax_optimization.plot(self.experimental_times[index], self.experimental_rates[index], label=f"Experimental rate for {self.selected_shortened_file_paths[index]}", alpha=0.8)
                # Get the color of curve1 so that experimental and optimized rate have the same color
                color_of_first_curve = curve1[0].get_color()
                # Plot the optimized rate with respect to time
                self.ax_optimization.plot(self.experimental_times[index], rate_opti[range_of_plot[0]:range_of_plot[1]], label=f"Model rate for {self.selected_shortened_file_paths[index]}", linestyle='dashed', color=color_of_first_curve, linewidth=2)
                # Modify the initial range of plot so that it corresponds to the initial index of next file data in "rate_opti" 
                range_of_plot[0] = range_of_plot[0] + len(self.experimental_times[index])
    
            self.ax_optimization.legend()
            self.canvas_optimization.draw_idle()
            self.ui.tabWidget_visualization.setCurrentIndex(2)
        except Exception as e:
            # Handle other exceptions with a generic error message
            QMessageBox.critical(self,"Error", f"An error occurred: {str(e)}")
            
    def display_error_in_optimization_thread(self,error_message):
        """
        Display the error that happened in the optimization thread.
        
        Parameters
        ----------
        error_message : TypeError
           Error message returned by the optimization thread.
        
        Returns
        -------
        None
        """
        print("error detected in optimization thread")
        self.optimization_thread.terminate()
        # Handle other exceptions with a generic error message
        self.ui.pushButton_launch_optimization.setEnabled(True)
        QMessageBox.critical(self,"Error", f"An error occurred: {str(error_message)}")
        traceback.print_exc() 
            
                
    def get_associated_experimental_parameters(self, labels_of_experimental_arguments):
        """
        Retrieve the associated experimental parameters based on provided labels.
        
        Parameters
        ----------
        labels_of_experimental_arguments : list
            List of labels for experimental parameters.
        
        Returns
        -------
        tuple
            Tuple of experimental parameter values.
        """
        # Check that data was extracted successfully
        if not self.successful_extraction:
            QMessageBox.critical(self, "Error", "Please, make sure you extracted the data successfully.")
            return    
        
        experimental_args = []
        for label in labels_of_experimental_arguments:
            if label == "T":
                experimental_args.append(self.experimental_temperature)
            elif label == "time":
                experimental_args.append(self.experimental_time)
            elif label == "rate":
                experimental_args.append(self.experimental_rate)
            elif label == "extent":
                experimental_args.append(self.experimental_extent)
            elif label == "time_lists":
                experimental_args.append(self.experimental_times)
            elif label == "temperature_lists":
                experimental_args.append(self.experimental_temperatures)
            elif label == "rate_lists":
                experimental_args.append(self.experimental_rates)
            elif label == "conv_lists":
                experimental_args.append(self.experimental_extents)
    
        return tuple(experimental_args)
    
    def get_summary_info(self):
        summary_info = '================ Files ================\n'
        summary_info += "Files used for optimization:\n"
        summary_info += '\n'.join([f"- {file}" for file in self.selected_shortened_file_paths])
        summary_info += '\n\n'
    
        # Rate section
        if self.selected_rate:
            summary_info += '================ Rate ================\n'
            summary_info += f"Rate law: {self.selected_rate}\n"
            summary_info += f"Experimental parameters for rate computation: {self.rate_parameters_experimental}\n"
            summary_info += "Rate parameters initial guess:\n"
            if self.line_edit_dict_rate_model:
                summary_info += '\n'.join([f"- {key}: {line_edit.text()}" for key, line_edit in self.line_edit_dict_rate_model.items()])
            else:
                summary_info += '- None: None\n'   
            summary_info += '\n\n'
    
        # Vitrification section
        if self.selected_vitrification:
            summary_info += '================ Vitrification ================\n'
            summary_info += f"Vitrification law: {self.selected_vitrification}\n"
            summary_info += f"Experimental parameters for vitrification computation: {self.vitrification_parameters_experimental}\n"
            summary_info += "Vitrification parameters initial guess:\n"
            if self.line_edit_dict_vitrification_model:    
                summary_info += '\n'.join([f"- {key}: {line_edit.text()}" for key, line_edit in self.line_edit_dict_vitrification_model.items()])
            else:
                summary_info += '- None: None\n'  
            summary_info += '\n\n'
    
        # Coupling section
        if self.selected_coupling_law:
            summary_info += '================ Coupling ================\n'
            summary_info += f"Coupling law: {self.selected_coupling_law}\n"
            summary_info += f"Experimental parameters for coupling law: {self.coupling_law_parameters_experimental}\n"
            summary_info += "Coupling parameters initial guess:\n"
            if self.line_edit_dict_coupling_law:
                summary_info += '\n'.join([f"- {key}: {line_edit.text()}" for key, line_edit in self.line_edit_dict_coupling_law.items()])
            else:
                summary_info += '- None: None\n'   
            summary_info += '\n\n'
    
        # Tg section
        if self.selected_tg_law:
            summary_info += '================ Tg ================\n'
            summary_info += f"Tg law: {self.selected_tg_law}\n"
            summary_info += f"Experimental parameters for Tg computation: {self.tg_law_parameters_experimental}\n"
            summary_info += "Tg parameters:\n"
            if self.line_edit_dict_tg_law:
                summary_info += '\n'.join([f"- {key}: {line_edit.text()}" for key, line_edit in self.line_edit_dict_tg_law.items()])
            else:
                summary_info += '- None: None\n'  
            summary_info += '\n\n'
    
        # Optimization section
        summary_info += '================ Optimization ================\n'
        if self.selected_global_optimization:
            summary_info += f"Global optimization method: {self.selected_global_optimization}\n"
            summary_info += "Parameters for global optimization:\n"
            summary_info += '\n'.join([f"- {key}: {value}" for key, value in self.global_optimization_args_dict.items()])
            summary_info += '\n\n'
        if self.selected_local_optimization:
            summary_info += f"Local optimization method: {self.selected_local_optimization}\n"
            summary_info += "Parameters for local optimization:\n"
            summary_info += '\n'.join([f"- {key}: {value}" for key, value in self.local_optimization_args_dict.items()])
            summary_info += '\n\n'
    
        # Cost function section
        summary_info += '================ Cost Function ================\n'
        summary_info += f"Cost function: {self.selected_cost_function}\n"
        summary_info += f"Experimental parameters for cost function computation: {self.cost_function_parameters_experimental}\n"
        summary_info += f"Cost function parameters: {self.cost_function_args}\n"
        if self.entries_dict_cost_function:    
            summary_info += '\n'.join([f"- {key}: {line_edit.text()}" for key, line_edit in self.entries_dict_cost_function.items()])
    
        # Results section
        if hasattr(self, 'results'):
            summary_info += '\n================ Results ================\n'
            if self.selected_rate:
                summary_info += "Rate optimization results:\n"
                summary_info += '\n'.join([f"- {key}: {self.results.x[index]}" for index, key in enumerate(self.line_edit_dict_rate_model)])
                summary_info += '\n\n'
            if self.selected_vitrification:
                summary_info += "Vitrification optimization results:\n"
                summary_info += '\n'.join([f"- {key}: {self.results.x[self.number_of_parameters_to_optimize_for_rate + index]}" for index, key in enumerate(self.line_edit_dict_vitrification_model)])
                summary_info += '\n\n'
            if self.selected_coupling_law:
                summary_info += "Coupling optimization results:\n"
                summary_info += '\n'.join([f"- {key}: {self.results.x[self.number_of_parameters_to_optimize_for_rate + self.number_of_parameters_to_optimize_for_vitrification + index]}" for index, key in enumerate(self.line_edit_dict_coupling_law)])
                summary_info += '\n'
            summary_info += f"Final cost function value: {self.results.fun}\n"
            if self.mean_rss:
                summary_info += f"Final mean RSS value: {self.mean_rss}\n"
            summary_info += "Scipy final output:\n"
            summary_info += f"{self.results}\n"
        
        # Data section
        summary_info += '================ Data used for optimization ================\n'
        

        data_rows = []
        headers = ["Time", "Temperature", "Rate", "Extent"]
        
        # Construct the header row
        header_row = "\t".join([f"{header}{i+1}" for i in range(len(self.experimental_times)) for header in headers ])
        data_rows.append(header_row)
        
        # Combine experimental data into a single NumPy array
        experimental_data = np.array([self.experimental_times, self.experimental_temperatures, self.experimental_rates, self.experimental_extents])
        
        # Transpose the data
        experimental_data = np.transpose(experimental_data)
        
        # Construct the data rows
        for row_values in experimental_data:
            concatenated_row = np.concatenate(row_values)
            data_rows.append("\t".join(map(str, concatenated_row)))
        
        data_section = "\n".join(data_rows)
        summary_info += data_section
        
        return summary_info

    def load_results_files(self):
        """Open a file dialog to browse and select multiple results files. Update the results file paths list widget."""
        try:
            # Open a file dialog to select files
            results_file_paths, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Files",
                "",
                "Text Files (*.txt);;All Files (*)"
            )
            if results_file_paths:
                # Clear the data extraction plots in case previous files were extracted
                self.clear_results_viewer_plots()
                
                # Update listView background in white to indicate no extraction was performed
                self.ui.listView_result_files.viewport().setStyleSheet("background-color: white")
                
                # Create a string list model to hold the filenames
                string_list_model = QStringListModel()
    
                # Populate the model with shortened filenames
                string_list_model.setStringList([os.path.basename(fp) for fp in results_file_paths])
                
                # Save the shortened filenames
                self.selected_shortened_results_file_paths = [os.path.basename(fp) for fp in results_file_paths]
    
                # Set the model for the list view
                self.ui.listView_result_files.setModel(string_list_model)
    
                # Store the full file paths in an instance variable
                self.selected_full_results_file_paths = results_file_paths
        except Exception as e:
            # Handle other exceptions with a generic error message
            QMessageBox.critical(self,"Error", f"An error occurred: {str(e)}")
            traceback.print_exc()
            
    def clear_results_files(self):
        """Clear all the files in the listView_files object."""
        # Create an empty string list model to empty the listView
        string_list_model = QStringListModel()
        # Set the model for the list view with the empty list
        self.ui.listView_result_files.setModel(string_list_model)
        # Empty the full file paths list
        self.selected_full_results_file_paths = None
        # Empty the shortened file paths list
        self.selected_shortened_results_file_paths = None
        # Reset the bool to indicate successful extraction
        self.successful_results_extraction = None
        
        # Update listView background in white to indicate no extraction was performed
        self.ui.listView_result_files.viewport().setStyleSheet("background-color: white")
        
        self.clear_results_viewer_plots()
        
    def display_selected_result_file(self):
        """Extract data from selected files and update GUI elements based on extraction results."""
        try:
            # Get the selected file paths
            selected_index = self.ui.listView_result_files.currentIndex()
            if selected_index.isValid():
                row = selected_index.row()
                self.selected_result_file = self.selected_full_results_file_paths[row]
            else:
                QMessageBox.warning(self, "No File Selected", "Please select a result file before extracting.")
                return
    
            
            # Launch the extraction process with provided parameters
            with open(self.selected_result_file, 'r') as file:
                result_summary_info = file.read()
                self.ui.textEdit_result_file_content.setText(result_summary_info)
                
                # Define variables to store the extracted information
                files = []
                rate_info = {}
                vitrification_info = {}
                coupling_info = {}
                tg_info = {}
                results_experimental_times = []
                results_experimental_temperatures = []
                results_experimental_extents = []
                results_experimental_rates = []
                
                # Split the summary info by sections
                sections = result_summary_info.split('================ ')
                
                rate_info = {"law": None,"experimental_parameters": None,"initial_guess": {'None':'None'}}   
                vitrification_info = {"law": None,"experimental_parameters": None,"initial_guess": {'None':'None'}} 
                coupling_info = {"law": None,"experimental_parameters": None,"initial_guess": {'None':'None'}} 
                tg_info = {"law": None,"experimental_parameters": None,"parameters": {'None':'None'}} 
                
                # Iterate over sections to extract information
                for section in sections:
                    lines = section.strip().split('\n')
                    if "Files ==" in section:
                        files = [line.split('- ')[1].strip() for line in lines[2:]]
                    elif "Rate ==" in section:
                        rate_info = {
                            "law": getattr(km,lines[1].split(": ")[1]),
                            "experimental_parameters": lines[2].split(": ")[1],
                            "initial_guess": {line.split(": ")[0].strip('- '): line.split(": ")[1] for line in lines[4:]}
                        }
                    elif "Vitrification ==" in section:
                        vitrification_info = {
                            "law": getattr(km,lines[1].split(": ")[1]),
                            "experimental_parameters": lines[2].split(": ")[1],
                            "initial_guess": {line.split(": ")[0].strip('- '): line.split(": ")[1] for line in lines[4:]}
                        }
                    elif "Coupling ==" in section:
                        coupling_info = {
                            "law": getattr(km,lines[1].split(": ")[1]),
                            "experimental_parameters": lines[2].split(": ")[1],
                            "initial_guess": {line.split(": ")[0].strip('- '): line.split(": ")[1] for line in lines[4:]}
                        }
                    elif "Tg ==" in section:
                        tg_info = {
                            "law": getattr(km,lines[1].split(": ")[1]),
                            "experimental_parameters": lines[2].split(": ")[1],
                            "parameters": {line.split(": ")[0].strip('- '): line.split(": ")[1] for line in lines[4:]}
                        }

                    elif "Results ==" in section:
                        if 'None' not in rate_info["initial_guess"]:
                            start_rate_index = lines.index("Rate optimization results:")+1
                            end_rate_index = start_rate_index + len(rate_info["initial_guess"])
                            rate_args = [float(line.split(": ")[1]) for line in lines[start_rate_index:end_rate_index]]
                        else:
                            rate_args = None
                        if 'None' not in vitrification_info["initial_guess"]:
                            start_vitrification_index = lines.index("Vitrification optimization results:")+1
                            end_vitrification_index = start_vitrification_index + len(vitrification_info["initial_guess"])
                            vitrification_args = [float(line.split(": ")[1]) for line in lines[start_vitrification_index:end_vitrification_index]]
                        else:
                            vitrification_args = None
                        if 'None' not in coupling_info["initial_guess"]:
                            start_coupling_index = lines.index("Coupling optimization results:")+1
                            end_coupling_index = start_coupling_index + len(coupling_info["initial_guess"])
                            coupling_args = [float(line.split(": ")[1]) for line in lines[start_coupling_index:end_coupling_index]]
                        else:
                            coupling_args = None
                        if 'None' not in tg_info["parameters"]:
                            tg_args = [float(value) for value in tg_info["parameters"].values()]
                        else:
                            tg_args = None
                            
                       
                    elif "Data used for optimization ==" in section:
                        data_lines = [line.split("\t") for line in lines[1:] if line]
                        data = np.array(data_lines[1:],dtype=float)
                        
                        # Determine the indices of columns to select
                        total_number_of_columns = data.shape[1]
                        
                        time_indices = np.arange(0, total_number_of_columns, step=4)
                        results_experimental_times = data[:,time_indices]
                        
                        temperature_indices = np.arange(1, total_number_of_columns, step=4)
                        results_experimental_temperatures = data[:,temperature_indices]
                        
                        rate_indices = np.arange(2, total_number_of_columns, step=4)
                        results_experimental_rates = data[:,rate_indices]
                        
                        extent_indices = np.arange(3, total_number_of_columns, step=4)
                        results_experimental_extents = data[:,extent_indices]
                                
            # Clear axes in the visualization widget
            self.ax_results_viewer_rate.clear()
            self.ax_results_viewer_extent.clear()
            self.ax_results_viewer_temperature.clear()
            
            

                
            for i in range(results_experimental_times.shape[1]):
                extent, rate, _,_,_ = km.compute_extent_and_rate(results_experimental_times[:,i],
                                                            results_experimental_temperatures[:,i],
                                                            rate_law = rate_info["law"],
                                                            rate_law_args=rate_args,
                                                            vitrification_law=vitrification_info["law"],
                                                            vitrification_law_args=vitrification_args,
                                                            tg_law=tg_info["law"],
                                                            tg_law_args=tg_args,
                                                            coupling_law=coupling_info["law"],
                                                            coupling_law_args=coupling_args,
                                                            initial_extent=results_experimental_extents[i][0])
                
                curve1 = self.ax_results_viewer_rate.plot(results_experimental_times[:,i],results_experimental_rates[:,i],label=f'Experimental {files[i]}')
                self.ax_results_viewer_extent.plot(results_experimental_times[:,i],results_experimental_extents[:,i],label=f'Experimental {files[i]}')
                self.ax_results_viewer_temperature.plot(results_experimental_times[:,i],results_experimental_temperatures[:,i],label=f'Experimental {files[i]}')
                
                color_of_first_curve = curve1[0].get_color()
                
                self.ax_results_viewer_rate.plot(results_experimental_times[:,i],rate,label=f'Model {files[i]}', linestyle='dashed', color=color_of_first_curve, linewidth=2)
                self.ax_results_viewer_extent.plot(results_experimental_times[:,i],extent,label=f'Model {files[i]}', linestyle='dashed', color=color_of_first_curve, linewidth=2)
                self.ax_results_viewer_temperature.plot(results_experimental_times[:,i],results_experimental_temperatures[:,i],label=f'Experimental {files[i]}', linestyle='dashed', color=color_of_first_curve, linewidth=2)
                
                
            self.ax_results_viewer_rate.legend()
            self.ax_results_viewer_extent.legend()
            self.ax_results_viewer_temperature.legend()
            
            self.ax_results_viewer_rate.set_ylabel("Rate (s-1)")
            self.ax_results_viewer_rate.set_xlabel("Time (s)")
            self.ax_results_viewer_extent.set_ylabel("Extent")
            self.ax_results_viewer_extent.set_xlabel("Time (s)")
            self.ax_results_viewer_temperature.set_ylabel("Temperature (K)")
            self.ax_results_viewer_temperature.set_xlabel("Time (s)")
            
            self.canvas_results_viewer_rate.draw_idle()
            self.canvas_results_viewer_extent.draw_idle()
            self.canvas_results_viewer_temperature.draw_idle()
            
            self.ui.tabWidget_visualization.setCurrentIndex(3)
                
                
        except AttributeError as e:
            if str(e) == "'MainWindow' object has no attribute 'selected_full_file_paths'":
                # Handle the specific AttributeError and display a customized error message
                QMessageBox.critical(self, "Error", "Please select a file.")
            else:
                # Handle other AttributeErrors (if any) differently
                print(e)
                traceback.print_exc()
                QMessageBox.critical(self, "Error", f"An AttributeError occurred: {str(e)}")
        except Exception as e:
            # Handle other exceptions with a generic error message
            QMessageBox.critical(
                self, "Error", f"An error occurred: {str(e)}")
            traceback.print_exc()
            
    def clear_results_viewer_plots(self):
        self.ax_results_viewer_rate.clear()
        self.ax_results_viewer_extent.clear()
        self.ax_results_viewer_temperature.clear()
        
        self.canvas_results_viewer_rate.draw_idle()
        self.canvas_results_viewer_extent.draw_idle()
        self.canvas_results_viewer_temperature.draw_idle()
        
    def show_extracted_result_rate(self):
        self.ui.stackedWidget_results_viewer.setCurrentWidget(self.ui.page_results_viewer_rate)
        
    def show_extracted_result_extent(self):
        self.ui.stackedWidget_results_viewer.setCurrentWidget(self.ui.page_results_viewer_extent)
    
    def show_extracted_result_temperature(self):
        self.ui.stackedWidget_results_viewer.setCurrentWidget(self.ui.page_results_viewer_temperature)
     
        
        
class OptimizationThread(QThread):
    end_of_optimization = pyqtSignal(scipy.optimize.OptimizeResult)
    update_progress_bar_signal = pyqtSignal(int)
    update_graph_signal = pyqtSignal(int,float,np.ndarray,object,object)
    error_in_optimization_thread = pyqtSignal(Exception)
    def __init__(self, cost_function, initial_guess, selected_global_optimization, global_optimization, global_optimization_args_dict, selected_local_optimization, local_optimization, local_optimization_args_dict, experimental_rate, rate_law, experimental_args_for_rate, number_of_parameters_to_optimize_for_rate, vitrification_law, experimental_args_for_vitrification, number_of_parameters_to_optimize_for_vitrification, coupling_law, experimental_args_for_coupling, tg_law, experimental_args_for_tg, tg_args, cost_function_args,experimental_args_for_cost_function, max_iter):
        super().__init__()
        self.cost_function = cost_function
        self.initial_guess = initial_guess
        self.selected_global_optimization = selected_global_optimization
        self.global_optimization = global_optimization
        self.global_optimization_args_dict = global_optimization_args_dict
        self.selected_local_optimization = selected_local_optimization
        self.local_optimization = local_optimization
        self.local_optimization_args_dict = local_optimization_args_dict
        self.experimental_rate = experimental_rate
        self.rate_law = rate_law
        self.experimental_args_for_rate = experimental_args_for_rate
        self.number_of_parameters_to_optimize_for_rate = number_of_parameters_to_optimize_for_rate
        self.vitrification_law = vitrification_law
        self.experimental_args_for_vitrification = experimental_args_for_vitrification
        self.number_of_parameters_to_optimize_for_vitrification = number_of_parameters_to_optimize_for_vitrification
        self.coupling_law = coupling_law
        self.experimental_args_for_coupling = experimental_args_for_coupling
        self.tg_law = tg_law
        self.experimental_args_for_tg = experimental_args_for_tg
        self.tg_args = tg_args
        self.cost_function_args = cost_function_args
        self.experimental_args_for_cost_function = experimental_args_for_cost_function
        self.max_iter = max_iter
        self.start_time = None
        self.next_iteration_for_GUI_updtate = 1 
        self.time_between_GUI_update = 1 # in seconds
        self.xmin_bashinhopping = None
        self.fmin_bashinhopping = None
        
    def run(self):
        try:
            if self.selected_global_optimization != '':
                    self.global_optimization_args_dict['callback'] = self.optimization_callback   
            if self.selected_local_optimization != '':        
                    if self.global_optimization == None:
                        self.local_optimization_args_dict['callback'] = self.optimization_callback
                        
            # Initialize a self.count variable that will be used to display a progress bar
            self.count = 0
            
            # Initialize a self.count
            self.start_time = time_module.time()
            
            if self.selected_global_optimization == 'basinhopping':
                if self.selected_local_optimization == '':
                    # If no local minimization method is selected the default local minimization is used
                    # However, the arguments for local minimization still need to be given, hence the creation of the args dict
                    self.local_optimization_args_dict = {}
                self.local_optimization_args_dict['args'] = (self.experimental_rate,
                                                            self.rate_law,
                                                            self.experimental_args_for_rate,
                                                            self.number_of_parameters_to_optimize_for_rate,
                                                            self.vitrification_law,
                                                            self.experimental_args_for_vitrification,
                                                            self.number_of_parameters_to_optimize_for_vitrification,
                                                            self.coupling_law,
                                                            self.experimental_args_for_coupling,
                                                            self.tg_law,
                                                            self.experimental_args_for_tg,
                                                            self.tg_args,
                                                            *self.experimental_args_for_cost_function,
                                                            *self.cost_function_args)
                self.global_optimization_args_dict['minimizer_kwargs'] = self.local_optimization_args_dict
                self.result = self.global_optimization(self.cost_function,
                                                    self.initial_guess,
                                                    **self.global_optimization_args_dict)
                self.result.x = self.xmin_bashinhopping
                self.result.fun = self.fmin_bashinhopping
            
            elif self.selected_global_optimization == 'differential_evolution':
                self.global_optimization_args_dict['args'] = (self.experimental_rate,
                                                            self.rate_law,
                                                            self.experimental_args_for_rate,
                                                            self.number_of_parameters_to_optimize_for_rate,
                                                            self.vitrification_law,
                                                            self.experimental_args_for_vitrification,
                                                            self.number_of_parameters_to_optimize_for_vitrification,
                                                            self.coupling_law,
                                                            self.experimental_args_for_coupling,
                                                            self.tg_law,
                                                            self.experimental_args_for_tg,
                                                            self.tg_args,
                                                            *self.experimental_args_for_cost_function,
                                                            *self.cost_function_args)
                self.bounds = self.global_optimization_args_dict['bounds']
                self.global_optimization_args_dict.pop('bounds')
                self.result = self.global_optimization(self.cost_function,
                                                    self.bounds,
                                                    **self.global_optimization_args_dict)
                
            elif self.selected_global_optimization == 'shgo':                
                self.global_optimization_args_dict['args'] = (self.experimental_rate,
                                                            self.rate_law,
                                                            self.experimental_args_for_rate,
                                                            self.number_of_parameters_to_optimize_for_rate,
                                                            self.vitrification_law,
                                                            self.experimental_args_for_vitrification,
                                                            self.number_of_parameters_to_optimize_for_vitrification,
                                                            self.coupling_law,
                                                            self.experimental_args_for_coupling,
                                                            self.tg_law,
                                                            self.experimental_args_for_tg,
                                                            self.tg_args,
                                                            *self.experimental_args_for_cost_function,
                                                            *self.cost_function_args)
                
                
                
                self.global_optimization_args_dict['minimizer_kwargs'] = self.local_optimization_args_dict
                
                self.bounds = self.global_optimization_args_dict['bounds']
                self.global_optimization_args_dict.pop('bounds')                    
                self.result = self.global_optimization(self.cost_function,
                                                    self.bounds,
                                                    **self.global_optimization_args_dict)
            elif self.selected_global_optimization == '':
                self.local_optimization_args_dict['args'] = (self.experimental_rate,
                                                            self.rate_law,
                                                            self.experimental_args_for_rate,
                                                            self.number_of_parameters_to_optimize_for_rate,
                                                            self.vitrification_law,
                                                            self.experimental_args_for_vitrification,
                                                            self.number_of_parameters_to_optimize_for_vitrification,
                                                            self.coupling_law,
                                                            self.experimental_args_for_coupling,
                                                            self.tg_law,
                                                            self.experimental_args_for_tg,
                                                            self.tg_args,
                                                            *self.experimental_args_for_cost_function,
                                                            *self.cost_function_args)
                self.result = self.local_optimization(self.cost_function,
                                                    self.initial_guess,
                                                    **self.local_optimization_args_dict)
            
            self.end_of_optimization.emit(self.result)
            
        except Exception as e:
            # Handle other exceptions with a generic error message
            traceback.print_exc()
            self.error_in_optimization_thread.emit(e)
            return
           
            
    def optimization_callback(self, xk, *args,**kwargs):
        print(self.count)
        self.count = self.count + 1
        progress = (self.count / self.max_iter) * 100
        self.update_progress_bar_signal.emit(int(progress))
        
        
        if self.selected_global_optimization == 'basinhopping':
            if self.count == 1:
                self.xmin_bashinhopping = xk
                self.fmin_bashinhopping = args[0]
                kwargs["x_min_basinhopping_all_iterations"] = xk
                kwargs["f_min_basinhopping_all_iterations"] = self.fmin_bashinhopping
            else:
                if self.fmin_bashinhopping > args[0]:
                    self.xmin_bashinhopping = xk
                    self.fmin_bashinhopping = args[0]
                    kwargs["x_min_basinhopping_all_iterations"] = xk
                    kwargs["f_min_basinhopping_all_iterations"] = self.fmin_bashinhopping
        
        if self.selected_global_optimization == 'differential_evolution':
            kwargs["convergence"] = args
            args = None
            
        if self.count == self.next_iteration_for_GUI_updtate:
            elapsed_time = time_module.time() - self.start_time
            time_per_iteration = elapsed_time/self.count
            iteration_per_time = 1 / time_per_iteration
            if int(iteration_per_time)<1:
                self.next_iteration_for_GUI_updtate = self.count + 1     
            else:
                self.next_iteration_for_GUI_updtate = self.count + int(iteration_per_time * self.time_between_GUI_update) 
            estimated_remaining_time = time_per_iteration * (self.max_iter-self.count)
            
            self.update_graph_signal.emit(self.count,estimated_remaining_time,xk,args,kwargs)
            
            print(self.next_iteration_for_GUI_updtate)
            print(estimated_remaining_time)
        
        
        
        
        
        
        
        
        
def launch_extraction(file_paths, delimiter=',', has_header=False, skip_lines=0):
    """
    Launch the data extraction process and processes warning and info messages.
    
    Parameters
    ----------
    file_paths : list
        List of file paths to input txt or csv files containing DSC data.
    delimiter : str, optional
        Delimiter used in the input files. Default is ','.
    has_header : bool, optional
        Whether the input files have headers. Default is False.
    skip_lines : int, optional
        Number of lines to skip at the beginning of each file. Default is 0.
    
    Returns
    -------
    tuple
        A tuple containing:
            - boolean: Indicates whether the extraction was successful (True) or not (False).
            - str: String containing any warning or info messages.
            - numpy.ndarray: Time data.
            - numpy.ndarray: Temperature data.
            - numpy.ndarray: Rate of reaction data.
            - numpy.ndarray: Extent of reaction data.
    """
    # Capture standard output to capture warning and info messages
    from io import StringIO
    import sys

    old_stdout = sys.stdout
    new_stdout = StringIO()
    sys.stdout = new_stdout

    # Call the extract_dsc_data_multiple_files function
    time, temperature, rate_of_reaction, extent_of_reaction = data_extraction.extract_dsc_data_multiple_files(
        file_paths, delimiter, has_header, skip_lines)

    # Restore standard output
    sys.stdout = old_stdout

    # Get the captured output
    captured_output = new_stdout.getvalue()

    # Check for warnings or info messages
    if "Error" in captured_output:
        return False, captured_output, time, temperature, rate_of_reaction, extent_of_reaction
    elif "Info" in captured_output:
        return True, captured_output, time, temperature, rate_of_reaction, extent_of_reaction
    else:
        return True, "", time, temperature, rate_of_reaction, extent_of_reaction
    
# =============================================================================
# Function for isoconversional analysis parameters
# =============================================================================

def get_functions_for_isoconversional_method():
    # Get the isoconversional analysis methods from the isoconversional method module
    isoconversional_methods = []
    for element in dir(icm):
        if callable(getattr(icm, element)):
            if element[:24] == "isoconversional_analysis":
                isoconversional_methods.append(element)
    return isoconversional_methods


def get_parameters_for_isoconversional_method(isoconversional_method_name):
    # Get the parameters for a specified function in the isoconversional method module
    module = icm
    function = getattr(module, isoconversional_method_name, None)
    if function is not None:
        arguments = function.__code__.co_varnames[:function.__code__.co_argcount]
        return arguments
    return []
# =============================================================================
# Function for model parameters
# =============================================================================

def get_functions_for_kinetics():
    """
    Get the functions related to kinetics from the kinetic module.
    
    Returns
    -------
    tuple
        A tuple containing four lists:
        - rate_laws (list): List of functions related to rate laws.
        - vitrification_laws (list): List of functions related to vitrification laws.
        - tg_laws (list): List of functions related to tg laws.
        - coupling_laws (list): List of functions related to coupling laws.
    """
    rate_laws = []
    vitrification_laws = []
    tg_laws = []
    coupling_laws = []

    for element in dir(km):
        if callable(getattr(km, element)):
            if element[:4] == "rate":
                rate_laws.append(element)
            elif element[:13] == "vitrification":
                vitrification_laws.append(element)            
            elif element[:8] == "coupling":
                coupling_laws.append(element)
            elif element[:2] == "tg":
                tg_laws.append(element)
    return rate_laws, vitrification_laws, coupling_laws, tg_laws


def get_parameters_for_rate(rate_name):
    """
    Get the parameters for a specified kinetic law in the kinetic module.
    
    Parameters
    ----------
    rate_name : str
        The name of the function in the kinetic module.
    
    Returns
    -------
    list or None
        The list of parameters for the specified function if found, otherwise None.
    """
    module = km
    function = getattr(module, rate_name, None)
    if function is not None:
        arguments = function.__code__.co_varnames[:function.__code__.co_argcount]
    return arguments


def get_parameters_for_vitrification(vitrification_name):
    """
    Get the parameters for a specified vitrifiaction law in the kinetic module.
    
    Parameters
    ----------
    vitrification_name : str
        The name of the function in the kinetic module.
    
    Returns
    -------
    list or None
        The list of parameters for the specified function if found, otherwise None.
    """
    module = km
    function = getattr(module, vitrification_name, None)
    if function is not None:
        arguments = function.__code__.co_varnames[:function.__code__.co_argcount]
    return arguments


def get_parameters_for_coupling(coupling_name):
    """
    Get the parameters for a specified coupling law in the kinetic module.
    
    Parameters
    ----------
    coupling_name : str
        The name of the function in the kinetic module.
    
    Returns
    -------
    list or None
        The list of parameters for the specified function if found, otherwise None.
    """
    module = km
    function = getattr(module, coupling_name, None)
    if function is not None:
        arguments = function.__code__.co_varnames[:function.__code__.co_argcount]
    return arguments


def get_parameters_for_tg(tg_name):
    """
    Get the parameters for a specified function in the kinetic module.
    
    Parameters
    ----------
    tg_name : str
        The name of the function in the kinetic module.
    
    Returns
    -------
    list or None
        The list of parameters for the specified function if found, otherwise None.
    """
    module = km
    function = getattr(module, tg_name, None)
    if function is not None:
        arguments = function.__code__.co_varnames[:function.__code__.co_argcount]
    return arguments


# =============================================================================
# Functions for optimization parameters
# =============================================================================

def get_functions_for_optimization():
    """
    Get the parameters for a specified function in the kinetic module.
    
    Parameters
    ----------
    tg_name : str
        The name of the function in the kinetic module.
    
    Returns
    -------
    list or None
        The list of parameters for the specified function if found, otherwise None.
    """
    global_optimization_methods = ["basinhopping", "differential_evolution","shgo"]
    local_optimization_methods = ["Nelder-Mead", "CG", "BFGS", "L-BFGS-B"]
    rss_methods = [element for element in dir(opt) if callable(getattr(opt, element)) and element.startswith("rss")]

    return global_optimization_methods, local_optimization_methods, rss_methods


def get_parameters_for_optimization(optimization_name):
    """
    Get the optimization parameters for a specified optimization method.
    
    This function returns a dictionary containing the parameters and their types for the selected optimization method.
    
    Parameters
    ----------
    optimization_name : str
        The name of the optimization method.
    
    Returns
    -------
    dict
        A dictionary of parameters, their types, and whether they are optional.
    """
    # Define a dictionary with parameters for each optimization method
    optimization_parameters = {
        "Nelder-Mead": {
            "disp": {"type": bool, "optional": True},
            "maxiter": {"type": int, "optional": False},
            "maxfev": {"type": int, "optional": True},
            "return_all": {"type": bool, "optional": True},
            "xatol": {"type": float, "optional": True},
            "fatol": {"type": float, "optional": True},
            "adaptive": {"type": bool, "optional": True},
            "bounds": {"type": "sequence", "optional": True}
        },
        "CG": {
            "disp": {"type": bool, "optional": True},
            "jac": {"type": list, "optional": True},
            "maxiter": {"type": int, "optional": False},
            "gtol": {"type": float, "optional": True},
            "norm": {"type": float, "optional": True},
            "eps": {"type": float, "optional": True},
            "return_all": {"type": bool, "optional": True}
        },
        "BFGS": {
            "disp": {"type": bool, "optional": True},
            "jac": {"type": list, "optional": True},
            "maxiter": {"type": int, "optional": False},
            "gtol": {"type": float, "optional": True},
            "norm": {"type": float, "optional": True},
            "eps": {"type": float, "optional": True},
            "return_all": {"type": bool, "optional": True},
            "xrtol": {"type": float, "optional": True}
        },
        "L-BFGS-B": {
            "disp": {"type": bool, "optional": True},
            "jac": {"type": list, "optional": True},
            "maxcor": {"type": int, "optional": True},
            "maxfun": {"type": int, "optional": True},
            "maxiter": {"type": int, "optional": False},
            "iprint": {"type": int, "optional": True},
            "maxls": {"type": int, "optional": True},
            "ftol": {"type": float, "optional": True},
            "gtol": {"type": float, "optional": True},
            "eps": {"type": float, "optional": True},
            "bounds": {"type": "sequence", "optional": True}
        },
        "basinhopping": {
            "disp": {"type": bool, "optional": True},
            "niter": {"type": int, "optional": False},
            "T": {"type": float, "optional": True},
            "stepsize": {"type": float, "optional": True},
            "interval": {"type": int, "optional": True},
            "niter_success": {"type": int, "optional": True},
            "target_accept_rate": {"type": float, "optional": True},
            "stepwise_factor": {"type": float, "optional": True}
        },
        "differential_evolution": {
            "disp": {"type": bool, "optional": True},
            "strategy": {"type": "strategy", "optional": True},
            "maxiter": {"type": int, "optional": False},
            "popsize": {"type": int, "optional": True},
            "tol": {"type": float, "optional": True},
            "mutation": {"type": float, "optional": True},
            "recombination": {"type": float, "optional": True},
            "polish": {"type": bool, "optional": True},
            "init": {"type": "init", "optional": True},
            "atol": {"type": float, "optional": True},
            "updating": {"type": "updating", "optional": True},
            "workers": {"type": int, "optional": False},
            "vectorized": {"type": bool, "optional": True},
            "bounds": {"type": "sequence", "optional": False}
        },
        "shgo": {
            "n": {"type": int, "optional": False},
            "iters": {"type": int, "optional": False},
            "sampling_method": {"type": "sampling_method", "optional": True},
            "workers": {"type": int, "optional": True},
            "bounds": {"type": "sequence", "optional": False}
        }
    }
    # Check if the optimization method is in the dictionary and return its parameters
    if optimization_name in optimization_parameters:
        return optimization_parameters[optimization_name]
    else:
        # Handle the case where the method is not found
        return {}


def get_parameters_for_rss(rss_name):
    """
    Get and clean the arguments of a specified function from a module.

    This function retrieves the arguments of a specified function and removes any undesired arguments.

    Parameters
    ----------
        rss_name : str 
            The name of the function to retrieve arguments from.

    Returns
    -------
        list: A list of cleaned arguments.
    """
    module = opt

    # Try to get the specified function from the module
    function = getattr(module, rss_name, None)

    if function is not None:
        # Get the arguments using function's code object
        arguments = function.__code__.co_varnames[1:function.__code__.co_argcount]

        # Define a list of arguments to exclude
        arguments_to_exclude = [
            "x",
            "experimental_rate",
            "rate_law",
            "experimental_args_for_rate",
            "number_of_parameters_to_optimize_for_rate",
            "vitrification",
            "vitrification_law",
            "experimental_args_for_vitrification",
            "number_of_parameters_to_optimize_for_vitrification",
            "coupling_law",
            "experimental_args_for_coupling",
            "tg_law",
            "experimental_args_for_tg",
            "tg_args",
            "rss_to_use_args"
        ]

        # Create a list of cleaned arguments by excluding undesired ones
        clean_arguments = [item for item in arguments if item not in arguments_to_exclude]

        return clean_arguments
    else:
        # Handle the case where the function is not found
        return []


def get_main_args_dict_and_options_dict(main_args_dict, method_dict):
    """
    Update the arguments dictionnary for the scipy.optimize.minimize() function with values existing in the arguments dictionnary of user selected method of optimization.
    
    For example, for the Nelder-Mead method, the arguments 'bounds' is both in the arguments of the main function and in the arguments specific to the method. It would be passed 2 times to the function, resulting in an error or conflict.

    Parameters
    ----------
    main_args_dict : dict
        Dictionnary containing the main arguments for scipy.optimize.minimize().
    method_dict : dict
        Dictionary containing arguments specific to the method of minimization selected by the user.

    Returns
    -------
    None
    """
    keys_to_remove = []

    for key in method_dict:
        if key in main_args_dict:
            main_args_dict[key] = method_dict[key]
            keys_to_remove.append(key)

    for key in keys_to_remove:
        method_dict.pop(key)

    return main_args_dict, method_dict

# =============================================================================
#
# =============================================================================

if __name__ == '__main__':
    # Check if QApplication instance already exists
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

