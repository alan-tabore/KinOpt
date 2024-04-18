# -*- coding: utf-8 -*-
"""
ui file used for the graphical interface.

@author: alan.tabore
"""

# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'kinopt_interfaceUnzdHi.ui'
##
## Created by: Qt User Interface Compiler version 5.14.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PyQt5.QtWidgets import *

from ressources import ressources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1181, 911)
        icon = QIcon()
        icon.addFile(u":/Logos/Logos/logo_no_background_with_outline.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setIconSize(QSize(40, 40))
        self.actionKinOpt_documentation = QAction(MainWindow)
        self.actionKinOpt_documentation.setObjectName(u"actionKinOpt_documentation")
        self.actionScipy_documentation = QAction(MainWindow)
        self.actionScipy_documentation.setObjectName(u"actionScipy_documentation")
        self.actionData_extraction = QAction(MainWindow)
        self.actionData_extraction.setObjectName(u"actionData_extraction")
        self.actionData_extraction.setCheckable(True)
        self.actionData_extraction.setChecked(True)
        self.actionIsoconversional_analysis = QAction(MainWindow)
        self.actionIsoconversional_analysis.setObjectName(u"actionIsoconversional_analysis")
        self.actionIsoconversional_analysis.setCheckable(True)
        self.actionIsoconversional_analysis.setChecked(True)
        self.actionOptimization = QAction(MainWindow)
        self.actionOptimization.setObjectName(u"actionOptimization")
        self.actionOptimization.setCheckable(True)
        self.actionOptimization.setChecked(True)
        self.actionDocumentation = QAction(MainWindow)
        self.actionDocumentation.setObjectName(u"actionDocumentation")
        self.actionDocumentation.setCheckable(True)
        self.actionResults_viewer = QAction(MainWindow)
        self.actionResults_viewer.setObjectName(u"actionResults_viewer")
        self.actionResults_viewer.setCheckable(True)
        self.actionResults_viewer.setChecked(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_6 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.widget_output_of_optimization = QWidget(self.centralwidget)
        self.widget_output_of_optimization.setObjectName(u"widget_output_of_optimization")
        self.verticalLayout_7 = QVBoxLayout(self.widget_output_of_optimization)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.widget_output_of_optimization_window_title = QWidget(self.widget_output_of_optimization)
        self.widget_output_of_optimization_window_title.setObjectName(u"widget_output_of_optimization_window_title")
        self.horizontalLayout_7 = QHBoxLayout(self.widget_output_of_optimization_window_title)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalSpacer_output_of_optimization = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_output_of_optimization)

        self.label_output_of_optimization = QLabel(self.widget_output_of_optimization_window_title)
        self.label_output_of_optimization.setObjectName(u"label_output_of_optimization")
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.label_output_of_optimization.setFont(font)

        self.horizontalLayout_7.addWidget(self.label_output_of_optimization)

        self.horizontalSpacer_output_of_optimization_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_output_of_optimization_2)


        self.verticalLayout_7.addWidget(self.widget_output_of_optimization_window_title)

        self.textEdit_output_of_optimization = QTextEdit(self.widget_output_of_optimization)
        self.textEdit_output_of_optimization.setObjectName(u"textEdit_output_of_optimization")
        self.textEdit_output_of_optimization.setEnabled(True)
        self.textEdit_output_of_optimization.setMinimumSize(QSize(0, 150))
        self.textEdit_output_of_optimization.setReadOnly(True)

        self.verticalLayout_7.addWidget(self.textEdit_output_of_optimization)

        self.progressBar = QProgressBar(self.widget_output_of_optimization)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setOrientation(Qt.Horizontal)
        self.progressBar.setInvertedAppearance(False)

        self.verticalLayout_7.addWidget(self.progressBar)

        self.label_remaing_time = QLabel(self.widget_output_of_optimization)
        self.label_remaing_time.setObjectName(u"label_remaing_time")

        self.verticalLayout_7.addWidget(self.label_remaing_time)


        self.verticalLayout_6.addWidget(self.widget_output_of_optimization)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_6.addWidget(self.line)

        self.widget_visualization = QWidget(self.centralwidget)
        self.widget_visualization.setObjectName(u"widget_visualization")
        self.verticalLayout_8 = QVBoxLayout(self.widget_visualization)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.widget_visualization_window_title = QWidget(self.widget_visualization)
        self.widget_visualization_window_title.setObjectName(u"widget_visualization_window_title")
        self.horizontalLayout_9 = QHBoxLayout(self.widget_visualization_window_title)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalSpacer_visualization = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_visualization)

        self.label_visualization = QLabel(self.widget_visualization_window_title)
        self.label_visualization.setObjectName(u"label_visualization")
        self.label_visualization.setFont(font)

        self.horizontalLayout_9.addWidget(self.label_visualization)

        self.horizontalSpacer_visualization_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_visualization_2)


        self.verticalLayout_8.addWidget(self.widget_visualization_window_title)

        self.tabWidget_visualization = QTabWidget(self.widget_visualization)
        self.tabWidget_visualization.setObjectName(u"tabWidget_visualization")
        self.tabWidget_visualization.setMinimumSize(QSize(400, 400))
        self.tabWidget_visualization.setTabShape(QTabWidget.Rounded)
        self.tabWidget_visualization.setMovable(False)
        self.tab_data_extraction_visualization = QWidget()
        self.tab_data_extraction_visualization.setObjectName(u"tab_data_extraction_visualization")
        self.verticalLayout_data_extraction_visualization = QVBoxLayout(self.tab_data_extraction_visualization)
        self.verticalLayout_data_extraction_visualization.setObjectName(u"verticalLayout_data_extraction_visualization")
        self.stackedWidget_data_extraction = QStackedWidget(self.tab_data_extraction_visualization)
        self.stackedWidget_data_extraction.setObjectName(u"stackedWidget_data_extraction")
        self.stackedWidget_data_extraction.setMinimumSize(QSize(0, 0))
        self.stackedWidget_data_extraction.setFrameShape(QFrame.NoFrame)
        self.page_data_extraction_rate = QWidget()
        self.page_data_extraction_rate.setObjectName(u"page_data_extraction_rate")
        self.verticalLayout_data_extraction_rate = QVBoxLayout(self.page_data_extraction_rate)
        self.verticalLayout_data_extraction_rate.setObjectName(u"verticalLayout_data_extraction_rate")
        self.stackedWidget_data_extraction.addWidget(self.page_data_extraction_rate)
        self.page_data_extraction_extent = QWidget()
        self.page_data_extraction_extent.setObjectName(u"page_data_extraction_extent")
        self.verticalLayout_data_extraction_extent = QVBoxLayout(self.page_data_extraction_extent)
        self.verticalLayout_data_extraction_extent.setObjectName(u"verticalLayout_data_extraction_extent")
        self.stackedWidget_data_extraction.addWidget(self.page_data_extraction_extent)
        self.page_data_extraction_temperature = QWidget()
        self.page_data_extraction_temperature.setObjectName(u"page_data_extraction_temperature")
        self.verticalLayout_data_extraction_temperature = QVBoxLayout(self.page_data_extraction_temperature)
        self.verticalLayout_data_extraction_temperature.setObjectName(u"verticalLayout_data_extraction_temperature")
        self.stackedWidget_data_extraction.addWidget(self.page_data_extraction_temperature)

        self.verticalLayout_data_extraction_visualization.addWidget(self.stackedWidget_data_extraction)

        self.widget_buttons_selection_data_extraction = QWidget(self.tab_data_extraction_visualization)
        self.widget_buttons_selection_data_extraction.setObjectName(u"widget_buttons_selection_data_extraction")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_buttons_selection_data_extraction)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_data_extraction_rate = QPushButton(self.widget_buttons_selection_data_extraction)
        self.pushButton_data_extraction_rate.setObjectName(u"pushButton_data_extraction_rate")

        self.horizontalLayout_2.addWidget(self.pushButton_data_extraction_rate)

        self.pushButton_data_extraction_extent = QPushButton(self.widget_buttons_selection_data_extraction)
        self.pushButton_data_extraction_extent.setObjectName(u"pushButton_data_extraction_extent")

        self.horizontalLayout_2.addWidget(self.pushButton_data_extraction_extent)

        self.pushButton_data_extraction_temperature = QPushButton(self.widget_buttons_selection_data_extraction)
        self.pushButton_data_extraction_temperature.setObjectName(u"pushButton_data_extraction_temperature")

        self.horizontalLayout_2.addWidget(self.pushButton_data_extraction_temperature)


        self.verticalLayout_data_extraction_visualization.addWidget(self.widget_buttons_selection_data_extraction)

        self.tabWidget_visualization.addTab(self.tab_data_extraction_visualization, "")
        self.tab_isoconversional_analysis_visualization = QWidget()
        self.tab_isoconversional_analysis_visualization.setObjectName(u"tab_isoconversional_analysis_visualization")
        self.verticalLayout_16 = QVBoxLayout(self.tab_isoconversional_analysis_visualization)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.widget_isoconversional_analysis_visualization = QWidget(self.tab_isoconversional_analysis_visualization)
        self.widget_isoconversional_analysis_visualization.setObjectName(u"widget_isoconversional_analysis_visualization")
        self.widget_isoconversional_analysis_visualization.setMinimumSize(QSize(0, 0))
        self.verticalLayout_isoconversional_analysis = QVBoxLayout(self.widget_isoconversional_analysis_visualization)
        self.verticalLayout_isoconversional_analysis.setObjectName(u"verticalLayout_isoconversional_analysis")

        self.verticalLayout_16.addWidget(self.widget_isoconversional_analysis_visualization)

        self.tabWidget_visualization.addTab(self.tab_isoconversional_analysis_visualization, "")
        self.tab_optimization_visualization = QWidget()
        self.tab_optimization_visualization.setObjectName(u"tab_optimization_visualization")
        self.verticalLayout_17 = QVBoxLayout(self.tab_optimization_visualization)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.widget_optimization_visualization = QWidget(self.tab_optimization_visualization)
        self.widget_optimization_visualization.setObjectName(u"widget_optimization_visualization")
        self.widget_optimization_visualization.setMinimumSize(QSize(0, 0))
        self.verticalLayout_optimization = QVBoxLayout(self.widget_optimization_visualization)
        self.verticalLayout_optimization.setObjectName(u"verticalLayout_optimization")

        self.verticalLayout_17.addWidget(self.widget_optimization_visualization)

        self.tabWidget_visualization.addTab(self.tab_optimization_visualization, "")
        self.tab_results_viewer_visualization = QWidget()
        self.tab_results_viewer_visualization.setObjectName(u"tab_results_viewer_visualization")
        self.verticalLayout_15 = QVBoxLayout(self.tab_results_viewer_visualization)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.stackedWidget_results_viewer = QStackedWidget(self.tab_results_viewer_visualization)
        self.stackedWidget_results_viewer.setObjectName(u"stackedWidget_results_viewer")
        self.page_results_viewer_rate = QWidget()
        self.page_results_viewer_rate.setObjectName(u"page_results_viewer_rate")
        self.verticalLayout_results_viewer_rate = QVBoxLayout(self.page_results_viewer_rate)
        self.verticalLayout_results_viewer_rate.setObjectName(u"verticalLayout_results_viewer_rate")
        self.stackedWidget_results_viewer.addWidget(self.page_results_viewer_rate)
        self.page_results_viewer_extent = QWidget()
        self.page_results_viewer_extent.setObjectName(u"page_results_viewer_extent")
        self.verticalLayout_results_viewer_extent = QVBoxLayout(self.page_results_viewer_extent)
        self.verticalLayout_results_viewer_extent.setObjectName(u"verticalLayout_results_viewer_extent")
        self.stackedWidget_results_viewer.addWidget(self.page_results_viewer_extent)
        self.page_results_viewer_temperature = QWidget()
        self.page_results_viewer_temperature.setObjectName(u"page_results_viewer_temperature")
        self.verticalLayout_results_viewer_temperature = QVBoxLayout(self.page_results_viewer_temperature)
        self.verticalLayout_results_viewer_temperature.setObjectName(u"verticalLayout_results_viewer_temperature")
        self.stackedWidget_results_viewer.addWidget(self.page_results_viewer_temperature)

        self.verticalLayout_15.addWidget(self.stackedWidget_results_viewer)

        self.widget_buttons_selection_results_viewer = QWidget(self.tab_results_viewer_visualization)
        self.widget_buttons_selection_results_viewer.setObjectName(u"widget_buttons_selection_results_viewer")
        self.horizontalLayout_11 = QHBoxLayout(self.widget_buttons_selection_results_viewer)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.pushButton_results_viewer_rate = QPushButton(self.widget_buttons_selection_results_viewer)
        self.pushButton_results_viewer_rate.setObjectName(u"pushButton_results_viewer_rate")

        self.horizontalLayout_11.addWidget(self.pushButton_results_viewer_rate)

        self.pushButton_results_viewer_extent = QPushButton(self.widget_buttons_selection_results_viewer)
        self.pushButton_results_viewer_extent.setObjectName(u"pushButton_results_viewer_extent")

        self.horizontalLayout_11.addWidget(self.pushButton_results_viewer_extent)

        self.pushButton_results_viewer_temperature = QPushButton(self.widget_buttons_selection_results_viewer)
        self.pushButton_results_viewer_temperature.setObjectName(u"pushButton_results_viewer_temperature")

        self.horizontalLayout_11.addWidget(self.pushButton_results_viewer_temperature)


        self.verticalLayout_15.addWidget(self.widget_buttons_selection_results_viewer)

        self.tabWidget_visualization.addTab(self.tab_results_viewer_visualization, "")

        self.verticalLayout_8.addWidget(self.tabWidget_visualization)


        self.verticalLayout_6.addWidget(self.widget_visualization)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidgetData_extraction = QDockWidget(MainWindow)
        self.dockWidgetData_extraction.setObjectName(u"dockWidgetData_extraction")
        self.dockWidgetData_extraction.setMinimumSize(QSize(352, 281))
        self.dockWidgetData_extraction.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.dockWidgetOpenFileContents = QWidget()
        self.dockWidgetOpenFileContents.setObjectName(u"dockWidgetOpenFileContents")
        self.verticalLayout_9 = QVBoxLayout(self.dockWidgetOpenFileContents)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.widget_table_view_files = QWidget(self.dockWidgetOpenFileContents)
        self.widget_table_view_files.setObjectName(u"widget_table_view_files")
        self.horizontalLayout_5 = QHBoxLayout(self.widget_table_view_files)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.listView_files = QListView(self.widget_table_view_files)
        self.listView_files.setObjectName(u"listView_files")
        self.listView_files.setDragEnabled(False)
        self.listView_files.setDragDropOverwriteMode(False)
        self.listView_files.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.listView_files.setAlternatingRowColors(False)
        self.listView_files.setSelectionMode(QAbstractItemView.MultiSelection)

        self.horizontalLayout_5.addWidget(self.listView_files)

        self.widget_button_files = QWidget(self.widget_table_view_files)
        self.widget_button_files.setObjectName(u"widget_button_files")
        self.verticalLayout_11 = QVBoxLayout(self.widget_button_files)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalSpacer_data_extraction_1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_data_extraction_1)

        self.pushButton_add_files = QPushButton(self.widget_button_files)
        self.pushButton_add_files.setObjectName(u"pushButton_add_files")
        icon1 = QIcon()
        icon1.addFile(u":/Icons/Icons/folder.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_add_files.setIcon(icon1)
        self.pushButton_add_files.setIconSize(QSize(30, 30))

        self.verticalLayout_11.addWidget(self.pushButton_add_files)

        self.pushButton_clear_all_files = QPushButton(self.widget_button_files)
        self.pushButton_clear_all_files.setObjectName(u"pushButton_clear_all_files")
        icon2 = QIcon()
        icon2.addFile(u":/Icons/Icons/file_clean.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_clear_all_files.setIcon(icon2)
        self.pushButton_clear_all_files.setIconSize(QSize(30, 30))

        self.verticalLayout_11.addWidget(self.pushButton_clear_all_files)

        self.verticalSpacer_data_extraction_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_data_extraction_2)


        self.horizontalLayout_5.addWidget(self.widget_button_files)


        self.verticalLayout_9.addWidget(self.widget_table_view_files)

        self.widget_data_extraction = QWidget(self.dockWidgetOpenFileContents)
        self.widget_data_extraction.setObjectName(u"widget_data_extraction")
        self.widget_data_extraction.setMaximumSize(QSize(16777215, 140))
        self.horizontalLayout_6 = QHBoxLayout(self.widget_data_extraction)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.widget_data_extraction_options = QWidget(self.widget_data_extraction)
        self.widget_data_extraction_options.setObjectName(u"widget_data_extraction_options")
        self.formLayout = QFormLayout(self.widget_data_extraction_options)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.label_numbers_of_lines_to_skip = QLabel(self.widget_data_extraction_options)
        self.label_numbers_of_lines_to_skip.setObjectName(u"label_numbers_of_lines_to_skip")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_numbers_of_lines_to_skip)

        self.label_delimiter = QLabel(self.widget_data_extraction_options)
        self.label_delimiter.setObjectName(u"label_delimiter")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_delimiter)

        self.checkBox_file_has_headers = QCheckBox(self.widget_data_extraction_options)
        self.checkBox_file_has_headers.setObjectName(u"checkBox_file_has_headers")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.checkBox_file_has_headers)

        self.lineEdit_number_of_lines_to_skip = QLineEdit(self.widget_data_extraction_options)
        self.lineEdit_number_of_lines_to_skip.setObjectName(u"lineEdit_number_of_lines_to_skip")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.lineEdit_number_of_lines_to_skip)

        self.lineEdit_delimiter = QLineEdit(self.widget_data_extraction_options)
        self.lineEdit_delimiter.setObjectName(u"lineEdit_delimiter")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.lineEdit_delimiter)


        self.horizontalLayout_6.addWidget(self.widget_data_extraction_options)

        self.widget_data_extraction_buttons = QWidget(self.widget_data_extraction)
        self.widget_data_extraction_buttons.setObjectName(u"widget_data_extraction_buttons")
        self.verticalLayout_10 = QVBoxLayout(self.widget_data_extraction_buttons)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_4)

        self.pushButton_extract_data = QPushButton(self.widget_data_extraction_buttons)
        self.pushButton_extract_data.setObjectName(u"pushButton_extract_data")
        icon3 = QIcon()
        icon3.addFile(u":/Icons/Icons/analyzing.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_extract_data.setIcon(icon3)
        self.pushButton_extract_data.setIconSize(QSize(30, 30))

        self.verticalLayout_10.addWidget(self.pushButton_extract_data)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_5)


        self.horizontalLayout_6.addWidget(self.widget_data_extraction_buttons)


        self.verticalLayout_9.addWidget(self.widget_data_extraction)

        self.dockWidgetData_extraction.setWidget(self.dockWidgetOpenFileContents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidgetData_extraction)
        self.dockWidgetIsoconversionalAnalysis = QDockWidget(MainWindow)
        self.dockWidgetIsoconversionalAnalysis.setObjectName(u"dockWidgetIsoconversionalAnalysis")
        self.dockWidgetIsoconversionalAnalysis.setMinimumSize(QSize(359, 173))
        self.dockWidgetContents_IsoconversionalAnalysis = QWidget()
        self.dockWidgetContents_IsoconversionalAnalysis.setObjectName(u"dockWidgetContents_IsoconversionalAnalysis")
        self.verticalLayout_12 = QVBoxLayout(self.dockWidgetContents_IsoconversionalAnalysis)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.widget_IsoconversionalAnalysisMethods = QWidget(self.dockWidgetContents_IsoconversionalAnalysis)
        self.widget_IsoconversionalAnalysisMethods.setObjectName(u"widget_IsoconversionalAnalysisMethods")
        self.isoconversional_method_layout = QVBoxLayout(self.widget_IsoconversionalAnalysisMethods)
        self.isoconversional_method_layout.setObjectName(u"isoconversional_method_layout")
        self.label_IsoconversionalAnalysisMethods = QLabel(self.widget_IsoconversionalAnalysisMethods)
        self.label_IsoconversionalAnalysisMethods.setObjectName(u"label_IsoconversionalAnalysisMethods")

        self.isoconversional_method_layout.addWidget(self.label_IsoconversionalAnalysisMethods)

        self.comboBox_isoconversional_analysis_methods = QComboBox(self.widget_IsoconversionalAnalysisMethods)
        self.comboBox_isoconversional_analysis_methods.setObjectName(u"comboBox_isoconversional_analysis_methods")

        self.isoconversional_method_layout.addWidget(self.comboBox_isoconversional_analysis_methods)

        self.formLayout_isoconversional_analysis = QFormLayout()
        self.formLayout_isoconversional_analysis.setObjectName(u"formLayout_isoconversional_analysis")

        self.isoconversional_method_layout.addLayout(self.formLayout_isoconversional_analysis)


        self.verticalLayout_12.addWidget(self.widget_IsoconversionalAnalysisMethods)

        self.widget_IsoconversionalAnalysisButtons = QWidget(self.dockWidgetContents_IsoconversionalAnalysis)
        self.widget_IsoconversionalAnalysisButtons.setObjectName(u"widget_IsoconversionalAnalysisButtons")
        self.horizontalLayout_8 = QHBoxLayout(self.widget_IsoconversionalAnalysisButtons)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.pushButton_autofill_isoconversional = QPushButton(self.widget_IsoconversionalAnalysisButtons)
        self.pushButton_autofill_isoconversional.setObjectName(u"pushButton_autofill_isoconversional")

        self.horizontalLayout_8.addWidget(self.pushButton_autofill_isoconversional)

        self.pushButton_clear_isoconversional = QPushButton(self.widget_IsoconversionalAnalysisButtons)
        self.pushButton_clear_isoconversional.setObjectName(u"pushButton_clear_isoconversional")

        self.horizontalLayout_8.addWidget(self.pushButton_clear_isoconversional)

        self.pushButton_launch_isoconversional_analysis = QPushButton(self.widget_IsoconversionalAnalysisButtons)
        self.pushButton_launch_isoconversional_analysis.setObjectName(u"pushButton_launch_isoconversional_analysis")

        self.horizontalLayout_8.addWidget(self.pushButton_launch_isoconversional_analysis)


        self.verticalLayout_12.addWidget(self.widget_IsoconversionalAnalysisButtons)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_12.addItem(self.verticalSpacer_3)

        self.dockWidgetIsoconversionalAnalysis.setWidget(self.dockWidgetContents_IsoconversionalAnalysis)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidgetIsoconversionalAnalysis)
        self.dockWidgetOptimization = QDockWidget(MainWindow)
        self.dockWidgetOptimization.setObjectName(u"dockWidgetOptimization")
        self.dockWidgetOptimization.setMinimumSize(QSize(110, 192))
        self.dockWidgetContents_Optimization = QWidget()
        self.dockWidgetContents_Optimization.setObjectName(u"dockWidgetContents_Optimization")
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents_Optimization)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.toolBox_models_and_optimization_parameters = QToolBox(self.dockWidgetContents_Optimization)
        self.toolBox_models_and_optimization_parameters.setObjectName(u"toolBox_models_and_optimization_parameters")
        self.toolBox_models_and_optimization_parameters.setFrameShape(QFrame.NoFrame)
        self.page_models_and_parameters = QWidget()
        self.page_models_and_parameters.setObjectName(u"page_models_and_parameters")
        self.page_models_and_parameters.setGeometry(QRect(0, 0, 271, 747))
        self.verticalLayout_2 = QVBoxLayout(self.page_models_and_parameters)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea_models_and_parameters = QScrollArea(self.page_models_and_parameters)
        self.scrollArea_models_and_parameters.setObjectName(u"scrollArea_models_and_parameters")
        self.scrollArea_models_and_parameters.setMinimumSize(QSize(0, 0))
        self.scrollArea_models_and_parameters.setWidgetResizable(True)
        self.scrollAreaWidgetContents_models_and_parameters = QWidget()
        self.scrollAreaWidgetContents_models_and_parameters.setObjectName(u"scrollAreaWidgetContents_models_and_parameters")
        self.scrollAreaWidgetContents_models_and_parameters.setEnabled(True)
        self.scrollAreaWidgetContents_models_and_parameters.setGeometry(QRect(0, 0, 251, 680))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents_models_and_parameters)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_rate_model = QLabel(self.scrollAreaWidgetContents_models_and_parameters)
        self.label_rate_model.setObjectName(u"label_rate_model")

        self.verticalLayout_3.addWidget(self.label_rate_model)

        self.comboBox_rate_model = QComboBox(self.scrollAreaWidgetContents_models_and_parameters)
        self.comboBox_rate_model.setObjectName(u"comboBox_rate_model")

        self.verticalLayout_3.addWidget(self.comboBox_rate_model)

        self.formLayout_rate = QFormLayout()
        self.formLayout_rate.setObjectName(u"formLayout_rate")

        self.verticalLayout_3.addLayout(self.formLayout_rate)

        self.label_vitrification_model = QLabel(self.scrollAreaWidgetContents_models_and_parameters)
        self.label_vitrification_model.setObjectName(u"label_vitrification_model")

        self.verticalLayout_3.addWidget(self.label_vitrification_model)

        self.comboBox_vitrification_model = QComboBox(self.scrollAreaWidgetContents_models_and_parameters)
        self.comboBox_vitrification_model.setObjectName(u"comboBox_vitrification_model")

        self.verticalLayout_3.addWidget(self.comboBox_vitrification_model)

        self.formLayout_vitrification = QFormLayout()
        self.formLayout_vitrification.setObjectName(u"formLayout_vitrification")

        self.verticalLayout_3.addLayout(self.formLayout_vitrification)

        self.label_coupling_law = QLabel(self.scrollAreaWidgetContents_models_and_parameters)
        self.label_coupling_law.setObjectName(u"label_coupling_law")

        self.verticalLayout_3.addWidget(self.label_coupling_law)

        self.comboBox_coupling_law = QComboBox(self.scrollAreaWidgetContents_models_and_parameters)
        self.comboBox_coupling_law.setObjectName(u"comboBox_coupling_law")

        self.verticalLayout_3.addWidget(self.comboBox_coupling_law)

        self.formLayout_coupling_law = QFormLayout()
        self.formLayout_coupling_law.setObjectName(u"formLayout_coupling_law")

        self.verticalLayout_3.addLayout(self.formLayout_coupling_law)

        self.label_tg_law = QLabel(self.scrollAreaWidgetContents_models_and_parameters)
        self.label_tg_law.setObjectName(u"label_tg_law")

        self.verticalLayout_3.addWidget(self.label_tg_law)

        self.comboBox_tg_law = QComboBox(self.scrollAreaWidgetContents_models_and_parameters)
        self.comboBox_tg_law.setObjectName(u"comboBox_tg_law")

        self.verticalLayout_3.addWidget(self.comboBox_tg_law)

        self.formLayout_tg = QFormLayout()
        self.formLayout_tg.setObjectName(u"formLayout_tg")

        self.verticalLayout_3.addLayout(self.formLayout_tg)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.scrollArea_models_and_parameters.setWidget(self.scrollAreaWidgetContents_models_and_parameters)

        self.verticalLayout_2.addWidget(self.scrollArea_models_and_parameters)

        self.widget_models_and_parameters_buttons = QWidget(self.page_models_and_parameters)
        self.widget_models_and_parameters_buttons.setObjectName(u"widget_models_and_parameters_buttons")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_models_and_parameters_buttons)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pushButton_autofill_models_and_parameters = QPushButton(self.widget_models_and_parameters_buttons)
        self.pushButton_autofill_models_and_parameters.setObjectName(u"pushButton_autofill_models_and_parameters")

        self.horizontalLayout_3.addWidget(self.pushButton_autofill_models_and_parameters)

        self.pushButton_clear_models_and_parameters = QPushButton(self.widget_models_and_parameters_buttons)
        self.pushButton_clear_models_and_parameters.setObjectName(u"pushButton_clear_models_and_parameters")

        self.horizontalLayout_3.addWidget(self.pushButton_clear_models_and_parameters)


        self.verticalLayout_2.addWidget(self.widget_models_and_parameters_buttons)

        self.toolBox_models_and_optimization_parameters.addItem(self.page_models_and_parameters, u"Models and parameters")
        self.page_optimization_methods_and_parameters = QWidget()
        self.page_optimization_methods_and_parameters.setObjectName(u"page_optimization_methods_and_parameters")
        self.page_optimization_methods_and_parameters.setGeometry(QRect(0, 0, 271, 747))
        self.verticalLayout_5 = QVBoxLayout(self.page_optimization_methods_and_parameters)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.scrollArea_optimization_methods = QScrollArea(self.page_optimization_methods_and_parameters)
        self.scrollArea_optimization_methods.setObjectName(u"scrollArea_optimization_methods")
        self.scrollArea_optimization_methods.setMinimumSize(QSize(0, 195))
        self.scrollArea_optimization_methods.setFrameShape(QFrame.StyledPanel)
        self.scrollArea_optimization_methods.setWidgetResizable(True)
        self.scrollAreaWidgetContents_optimization_methods = QWidget()
        self.scrollAreaWidgetContents_optimization_methods.setObjectName(u"scrollAreaWidgetContents_optimization_methods")
        self.scrollAreaWidgetContents_optimization_methods.setGeometry(QRect(0, 0, 251, 680))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents_optimization_methods)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_global_optimization_methods = QLabel(self.scrollAreaWidgetContents_optimization_methods)
        self.label_global_optimization_methods.setObjectName(u"label_global_optimization_methods")
        self.label_global_optimization_methods.setMaximumSize(QSize(16777215, 13))

        self.verticalLayout_4.addWidget(self.label_global_optimization_methods)

        self.comboBox_global_optimization_methods = QComboBox(self.scrollAreaWidgetContents_optimization_methods)
        self.comboBox_global_optimization_methods.setObjectName(u"comboBox_global_optimization_methods")

        self.verticalLayout_4.addWidget(self.comboBox_global_optimization_methods)

        self.gridLayout_global_optimization = QGridLayout()
        self.gridLayout_global_optimization.setObjectName(u"gridLayout_global_optimization")

        self.verticalLayout_4.addLayout(self.gridLayout_global_optimization)

        self.label_local_optimization_methods = QLabel(self.scrollAreaWidgetContents_optimization_methods)
        self.label_local_optimization_methods.setObjectName(u"label_local_optimization_methods")
        self.label_local_optimization_methods.setMaximumSize(QSize(16777215, 13))

        self.verticalLayout_4.addWidget(self.label_local_optimization_methods)

        self.comboBox_local_optimization_methods = QComboBox(self.scrollAreaWidgetContents_optimization_methods)
        self.comboBox_local_optimization_methods.setObjectName(u"comboBox_local_optimization_methods")

        self.verticalLayout_4.addWidget(self.comboBox_local_optimization_methods)

        self.gridLayout_local_optimization = QGridLayout()
        self.gridLayout_local_optimization.setObjectName(u"gridLayout_local_optimization")

        self.verticalLayout_4.addLayout(self.gridLayout_local_optimization)

        self.label_cost_functions = QLabel(self.scrollAreaWidgetContents_optimization_methods)
        self.label_cost_functions.setObjectName(u"label_cost_functions")
        self.label_cost_functions.setMaximumSize(QSize(16777215, 13))

        self.verticalLayout_4.addWidget(self.label_cost_functions)

        self.comboBox_cost_functions = QComboBox(self.scrollAreaWidgetContents_optimization_methods)
        self.comboBox_cost_functions.setObjectName(u"comboBox_cost_functions")

        self.verticalLayout_4.addWidget(self.comboBox_cost_functions)

        self.gridLayout_cost_functions = QGridLayout()
        self.gridLayout_cost_functions.setObjectName(u"gridLayout_cost_functions")

        self.verticalLayout_4.addLayout(self.gridLayout_cost_functions)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.scrollArea_optimization_methods.setWidget(self.scrollAreaWidgetContents_optimization_methods)

        self.verticalLayout_5.addWidget(self.scrollArea_optimization_methods)

        self.widget_optimization_methods_buttons = QWidget(self.page_optimization_methods_and_parameters)
        self.widget_optimization_methods_buttons.setObjectName(u"widget_optimization_methods_buttons")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_optimization_methods_buttons)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.pushButton_autofill_optimization = QPushButton(self.widget_optimization_methods_buttons)
        self.pushButton_autofill_optimization.setObjectName(u"pushButton_autofill_optimization")

        self.horizontalLayout_4.addWidget(self.pushButton_autofill_optimization)

        self.pushButton_clear_optimization = QPushButton(self.widget_optimization_methods_buttons)
        self.pushButton_clear_optimization.setObjectName(u"pushButton_clear_optimization")

        self.horizontalLayout_4.addWidget(self.pushButton_clear_optimization)


        self.verticalLayout_5.addWidget(self.widget_optimization_methods_buttons)

        self.toolBox_models_and_optimization_parameters.addItem(self.page_optimization_methods_and_parameters, u"Optimization method and parameters")

        self.verticalLayout.addWidget(self.toolBox_models_and_optimization_parameters)

        self.pushButton_launch_optimization = QPushButton(self.dockWidgetContents_Optimization)
        self.pushButton_launch_optimization.setObjectName(u"pushButton_launch_optimization")

        self.verticalLayout.addWidget(self.pushButton_launch_optimization)

        self.dockWidgetOptimization.setWidget(self.dockWidgetContents_Optimization)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidgetOptimization)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1181, 21))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuView = QMenu(self.menuBar)
        self.menuView.setObjectName(u"menuView")
        self.menuPanes = QMenu(self.menuView)
        self.menuPanes.setObjectName(u"menuPanes")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menuBar)
        self.dockWidgetResultsViewer = QDockWidget(MainWindow)
        self.dockWidgetResultsViewer.setObjectName(u"dockWidgetResultsViewer")
        self.dockWidgetResultsViewer.setEnabled(True)
        self.dockWidgetContents_ResultsViewer = QWidget()
        self.dockWidgetContents_ResultsViewer.setObjectName(u"dockWidgetContents_ResultsViewer")
        self.verticalLayout_13 = QVBoxLayout(self.dockWidgetContents_ResultsViewer)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.widget_result_files = QWidget(self.dockWidgetContents_ResultsViewer)
        self.widget_result_files.setObjectName(u"widget_result_files")
        self.horizontalLayout = QHBoxLayout(self.widget_result_files)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.listView_result_files = QListView(self.widget_result_files)
        self.listView_result_files.setObjectName(u"listView_result_files")
        self.listView_result_files.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout.addWidget(self.listView_result_files)

        self.widget_results_viewer_buttons = QWidget(self.widget_result_files)
        self.widget_results_viewer_buttons.setObjectName(u"widget_results_viewer_buttons")
        self.verticalLayout_22 = QVBoxLayout(self.widget_results_viewer_buttons)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.pushButton_load_result_files = QPushButton(self.widget_results_viewer_buttons)
        self.pushButton_load_result_files.setObjectName(u"pushButton_load_result_files")
        self.pushButton_load_result_files.setIcon(icon1)
        self.pushButton_load_result_files.setIconSize(QSize(30, 30))

        self.verticalLayout_22.addWidget(self.pushButton_load_result_files)

        self.pushButton_clear_result_files = QPushButton(self.widget_results_viewer_buttons)
        self.pushButton_clear_result_files.setObjectName(u"pushButton_clear_result_files")
        self.pushButton_clear_result_files.setIcon(icon2)
        self.pushButton_clear_result_files.setIconSize(QSize(30, 30))

        self.verticalLayout_22.addWidget(self.pushButton_clear_result_files)

        self.pushButton_display_result_files = QPushButton(self.widget_results_viewer_buttons)
        self.pushButton_display_result_files.setObjectName(u"pushButton_display_result_files")
        icon4 = QIcon()
        icon4.addFile(u":/Icons/Icons/line-chart.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_display_result_files.setIcon(icon4)
        self.pushButton_display_result_files.setIconSize(QSize(30, 30))

        self.verticalLayout_22.addWidget(self.pushButton_display_result_files)


        self.horizontalLayout.addWidget(self.widget_results_viewer_buttons)


        self.verticalLayout_13.addWidget(self.widget_result_files)

        self.widget_result_file_content = QWidget(self.dockWidgetContents_ResultsViewer)
        self.widget_result_file_content.setObjectName(u"widget_result_file_content")
        self.verticalLayout_14 = QVBoxLayout(self.widget_result_file_content)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.label_result_file = QLabel(self.widget_result_file_content)
        self.label_result_file.setObjectName(u"label_result_file")
        font1 = QFont()
        font1.setBold(True)
        font1.setWeight(75)
        self.label_result_file.setFont(font1)

        self.verticalLayout_14.addWidget(self.label_result_file)

        self.textEdit_result_file_content = QTextEdit(self.widget_result_file_content)
        self.textEdit_result_file_content.setObjectName(u"textEdit_result_file_content")
        self.textEdit_result_file_content.setReadOnly(True)

        self.verticalLayout_14.addWidget(self.textEdit_result_file_content)


        self.verticalLayout_13.addWidget(self.widget_result_file_content)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_13.addItem(self.verticalSpacer_6)

        self.dockWidgetResultsViewer.setWidget(self.dockWidgetContents_ResultsViewer)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidgetResultsViewer)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuView.addAction(self.menuPanes.menuAction())
        self.menuPanes.addAction(self.actionData_extraction)
        self.menuPanes.addAction(self.actionIsoconversional_analysis)
        self.menuPanes.addAction(self.actionOptimization)
        self.menuPanes.addAction(self.actionResults_viewer)

        self.retranslateUi(MainWindow)
        self.actionData_extraction.toggled.connect(self.dockWidgetData_extraction.setVisible)
        self.actionOptimization.toggled.connect(self.dockWidgetOptimization.setVisible)
        self.actionIsoconversional_analysis.toggled.connect(self.dockWidgetIsoconversionalAnalysis.setVisible)
        self.pushButton_launch_isoconversional_analysis.clicked.connect(self.widget_isoconversional_analysis_visualization.setFocus)
        self.pushButton_extract_data.clicked.connect(self.stackedWidget_data_extraction.setFocus)
        self.pushButton_launch_optimization.clicked.connect(self.widget_optimization_visualization.setFocus)

        self.tabWidget_visualization.setCurrentIndex(0)
        self.stackedWidget_data_extraction.setCurrentIndex(2)
        self.stackedWidget_results_viewer.setCurrentIndex(0)
        self.toolBox_models_and_optimization_parameters.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"KinOpt", None))
        self.actionKinOpt_documentation.setText(QCoreApplication.translate("MainWindow", u"KinOpt documentation", None))
        self.actionScipy_documentation.setText(QCoreApplication.translate("MainWindow", u"Scipy documentation", None))
        self.actionData_extraction.setText(QCoreApplication.translate("MainWindow", u"Data extraction", None))
        self.actionIsoconversional_analysis.setText(QCoreApplication.translate("MainWindow", u"Isoconversional analysis", None))
        self.actionOptimization.setText(QCoreApplication.translate("MainWindow", u"Optimization", None))
        self.actionDocumentation.setText(QCoreApplication.translate("MainWindow", u"Documentation", None))
        self.actionResults_viewer.setText(QCoreApplication.translate("MainWindow", u"Results viewer", None))
        self.label_output_of_optimization.setText(QCoreApplication.translate("MainWindow", u"Output of optimization", None))
        self.label_remaing_time.setText(QCoreApplication.translate("MainWindow", u"Estimated remaining time: (No optimization running)", None))
        self.label_visualization.setText(QCoreApplication.translate("MainWindow", u"Visualization", None))
        self.pushButton_data_extraction_rate.setText(QCoreApplication.translate("MainWindow", u"Rate", None))
        self.pushButton_data_extraction_extent.setText(QCoreApplication.translate("MainWindow", u"Extent", None))
        self.pushButton_data_extraction_temperature.setText(QCoreApplication.translate("MainWindow", u"Temperature", None))
        self.tabWidget_visualization.setTabText(self.tabWidget_visualization.indexOf(self.tab_data_extraction_visualization), QCoreApplication.translate("MainWindow", u"Data extraction", None))
        self.tabWidget_visualization.setTabText(self.tabWidget_visualization.indexOf(self.tab_isoconversional_analysis_visualization), QCoreApplication.translate("MainWindow", u"Isoconversional analysis", None))
        self.tabWidget_visualization.setTabText(self.tabWidget_visualization.indexOf(self.tab_optimization_visualization), QCoreApplication.translate("MainWindow", u"Optimization", None))
        self.pushButton_results_viewer_rate.setText(QCoreApplication.translate("MainWindow", u"Rate", None))
        self.pushButton_results_viewer_extent.setText(QCoreApplication.translate("MainWindow", u"Extent", None))
        self.pushButton_results_viewer_temperature.setText(QCoreApplication.translate("MainWindow", u"Temperature", None))
        self.tabWidget_visualization.setTabText(self.tabWidget_visualization.indexOf(self.tab_results_viewer_visualization), QCoreApplication.translate("MainWindow", u"Result file", None))
#if QT_CONFIG(tooltip)
        self.dockWidgetData_extraction.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.dockWidgetData_extraction.setWindowTitle(QCoreApplication.translate("MainWindow", u"Data extraction", None))
#if QT_CONFIG(tooltip)
        self.listView_files.setToolTip(QCoreApplication.translate("MainWindow", u"List of all the files to use.", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_add_files.setText(QCoreApplication.translate("MainWindow", u"Add file(s)", None))
        self.pushButton_clear_all_files.setText(QCoreApplication.translate("MainWindow", u"Clear all files", None))
        self.label_numbers_of_lines_to_skip.setText(QCoreApplication.translate("MainWindow", u"Number of lines to skip:", None))
        self.label_delimiter.setText(QCoreApplication.translate("MainWindow", u"Delimiter:", None))
        self.checkBox_file_has_headers.setText(QCoreApplication.translate("MainWindow", u"File has headers", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_number_of_lines_to_skip.setToolTip(QCoreApplication.translate("MainWindow", u"(If \"file has headers\" is selected, the number of lines to skip must not include the header line.)", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_number_of_lines_to_skip.setText(QCoreApplication.translate("MainWindow", u"0", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_delimiter.setToolTip(QCoreApplication.translate("MainWindow", u"(for tab separator, indicate 'tab' or '\\t')", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_extract_data.setText(QCoreApplication.translate("MainWindow", u"Extract data", None))
        self.dockWidgetIsoconversionalAnalysis.setWindowTitle(QCoreApplication.translate("MainWindow", u"Isoconversional analysis", None))
        self.label_IsoconversionalAnalysisMethods.setText(QCoreApplication.translate("MainWindow", u"Isoconversional methods:", None))
        self.pushButton_autofill_isoconversional.setText(QCoreApplication.translate("MainWindow", u"Autofill", None))
        self.pushButton_clear_isoconversional.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.pushButton_launch_isoconversional_analysis.setText(QCoreApplication.translate("MainWindow", u"Launch Isoconversional analysis", None))
        self.dockWidgetOptimization.setWindowTitle(QCoreApplication.translate("MainWindow", u"Optimization", None))
        self.label_rate_model.setText(QCoreApplication.translate("MainWindow", u"Rate model:", None))
        self.label_vitrification_model.setText(QCoreApplication.translate("MainWindow", u"Vitrification model:", None))
        self.label_coupling_law.setText(QCoreApplication.translate("MainWindow", u"Coupling law:", None))
        self.label_tg_law.setText(QCoreApplication.translate("MainWindow", u"Tg law:", None))
        self.pushButton_autofill_models_and_parameters.setText(QCoreApplication.translate("MainWindow", u"Autofill", None))
        self.pushButton_clear_models_and_parameters.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.toolBox_models_and_optimization_parameters.setItemText(self.toolBox_models_and_optimization_parameters.indexOf(self.page_models_and_parameters), QCoreApplication.translate("MainWindow", u"Models and parameters", None))
        self.label_global_optimization_methods.setText(QCoreApplication.translate("MainWindow", u"Global optimization method:", None))
        self.label_local_optimization_methods.setText(QCoreApplication.translate("MainWindow", u"Local optimization method:", None))
        self.label_cost_functions.setText(QCoreApplication.translate("MainWindow", u"Cost function", None))
        self.pushButton_autofill_optimization.setText(QCoreApplication.translate("MainWindow", u"Autofill", None))
        self.pushButton_clear_optimization.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.toolBox_models_and_optimization_parameters.setItemText(self.toolBox_models_and_optimization_parameters.indexOf(self.page_optimization_methods_and_parameters), QCoreApplication.translate("MainWindow", u"Optimization method and parameters", None))
        self.pushButton_launch_optimization.setText(QCoreApplication.translate("MainWindow", u"Start optimization", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuPanes.setTitle(QCoreApplication.translate("MainWindow", u"Panes", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.dockWidgetResultsViewer.setWindowTitle(QCoreApplication.translate("MainWindow", u"Results viewer", None))
        self.pushButton_load_result_files.setText(QCoreApplication.translate("MainWindow", u"Load result file(s)", None))
        self.pushButton_clear_result_files.setText(QCoreApplication.translate("MainWindow", u"Clear all files", None))
        self.pushButton_display_result_files.setText(QCoreApplication.translate("MainWindow", u"Display selected result file", None))
        self.label_result_file.setText(QCoreApplication.translate("MainWindow", u"Result file:", None))
    # retranslateUi

