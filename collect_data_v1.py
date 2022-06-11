# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 15:28:02 2022

@author: 21255
"""

import sys
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow, QWidget, QSlider, \
                            QComboBox, QLabel, QLineEdit, QToolButton, QFileDialog, QMessageBox, \
                            QAction, QCheckBox, QGridLayout, QSplitter, QFrame, QMenu
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QFont
from PyQt5.QtGui import QIcon
from superqt import QRangeSlider
from PyQt5.QtCore import Qt, QThread, QTimer
from superqt import QRangeSlider

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
matplotlib.rcParams["toolbar"] = "toolmanager"

import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
from time import sleep
from math import ceil
from random import uniform
import psutil

from instrument_drivers.tektronix.Keithley_2450 import Keithley2450
from instrument_drivers.tektronix.Keithley_2400 import Keithley2400
from instrument_drivers.tektronix.Keithley_2502 import Keithley2502
from instrument_drivers.stanford_research.SR830 import SR830
from instrument_drivers.tektronix.Keithley_6221 import Keithley6221
from instrument_drivers.tektronix.Keithley_2182 import Keithley2182
import qcodes as qc
from instrument_drivers.Bluefors.Probe import Probe

import qdarkstyle
from qdarkstyle.dark.palette import DarkPalette
from qdarkstyle.light.palette import LightPalette

#在初始化output，run循环，和画图 的时候用到了loop_num = 4


class QLabel(QLabel):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setFont(QFont('Book Antiqua', 10))
        
class QLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont('Book Antiqua', 10))
        
class QPushButton(QPushButton):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setFont(QFont('Book Antiqua', 10))

class QComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setFont(QFont('Book Antiqua', 10))
    def wheelEvent(self, QWheelEvent):
        pass

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=800):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        
        
class MyToolbar(NavigationToolbar):
  def __init__(self, canvas, parent):
    super().__init__(canvas, parent)
    self.current_dir = os.getcwd().replace('\\','/') + '/'
    
    self.auto_X_button = QToolButton(checkable = True)
    self.auto_X_button.setIcon(QIcon(self.current_dir + 'X.png'))
    self.auto_X_button.setChecked(True)
    
    self.auto_Y_button = QToolButton(checkable = True)
    self.auto_Y_button.setIcon(QIcon(self.current_dir + 'Y.png'))
    self.auto_Y_button.setChecked(True)
    
    self.addWidget(self.auto_X_button)
    self.addWidget(self.auto_Y_button)
    
        

        
        
class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.current_dir = os.getcwd().replace('\\','/') + '/'
        print(self.current_dir)
        
        self.loop_num = 4
        self.read_num = 6
        
        self.loop_info = [{} for i in range(self.loop_num)]
        self.loop_params = [{} for i in range(self.loop_num)]
        self.read_info = [{} for i in range(self.read_num)]
        self.read_params = [{} for i in range(self.read_num)]
        
        self.onlyDouble = QDoubleValidator()
        self.onlyPositiveDouble = QDoubleValidator(bottom = 0)
        self.onlyPositiveInt = QIntValidator(bottom = 0)
        
        self.save_folder = 'C:/'
        
        self.source_meter_list = ['None', 'K2400', 'K2450', 'K2502', 'K6221', 'K2182', 'SR830', 'SR865']
        self.address_list = ['None'] + ['GPIB0::{}::INSTR'.format(str(i)) for i in range(30)]
        self.order_list = ['0123', '0132', '0213', '0231', '0312', '0321', 
                           '1023', '1032', '1203', '1230', '1302', '1320', 
                           '2013', '2031', '2103', '2130', '2301', '2310', 
                           '3012', '3021', '3102', '3120', '3201', '3210']
        
        self.collect_data_thread = CollectDataThread()
        
        hline = [QFrame() for i in range(self.loop_num)]
        
        string_label_list = [QLabel('Loop {}: '.format(str(i)), self) for i in range(self.loop_num)]
        self.string_edit_list = [QLineEdit() for i in range(self.loop_num)]
        
        address_label_list = [QLabel('GPIB Address: ', self) for i in range(self.loop_num)]
        self.combo_address_list = [QComboBox() for i in range(self.loop_num)]
        
        type_label_list = [QLabel('Meter Type: ', self) for i in range(self.loop_num)]
        self.combo_type_list = [QComboBox() for i in range(self.loop_num)]
        
        start_point_label_list = [QLabel('Start: ', self) for i in range(self.loop_num)]
        self.start_point_edit_list = [QLineEdit() for i in range(self.loop_num)]
        
        end_point_label_list = [QLabel('End: ', self) for i in range(self.loop_num)]
        self.end_point_edit_list = [QLineEdit() for i in range(self.loop_num)]
        
        number_of_points_label_list = [QLabel('Number of points: ', self) for i in range(self.loop_num)]
        self.number_of_points_edit_list = [QLineEdit() for i in range(self.loop_num)]
        
        step_label_list = [QLabel('Interval: ', self) for i in range(self.loop_num)]
        self.step_indicator_list = [QLabel('', self) for i in range(self.loop_num)]
        
        self.current_value_label_list = [QLabel('', self) for i in range(self.loop_num)]
        
        internal_delay_label_list = [QLabel('Internal delay (s): ', self) for i in range(self.loop_num)]
        self.internal_delay_edit_list = [QLineEdit() for i in range(self.loop_num)]
        
        internal_step_label_list = [QLabel('Internal step: ', self) for i in range(self.loop_num)]
        self.internal_step_edit_list = [QLineEdit() for i in range(self.loop_num)]
        
        wait_time_label_list = [QLabel('Wait time(s): ', self) for i in range(self.loop_num)]
        self.wait_time_edit_list = [QLineEdit() for i in range(self.loop_num)]
        
        
        hbox_1 = [QHBoxLayout() for i in range(self.loop_num)]
        hbox_2 = [QHBoxLayout() for i in range(self.loop_num)]
        hbox_3 = [QHBoxLayout() for i in range(self.loop_num)]
        
        for i in range(self.loop_num):
            hbox_1[i].addStretch(1)
            hbox_1[i].addWidget(string_label_list[i])
            hbox_1[i].addWidget(self.string_edit_list[i])
            self.string_edit_list[i].setFixedWidth(100)
            hbox_1[i].addStretch(1)
            
            hbox_1[i].addWidget(address_label_list[i])
            hbox_1[i].addWidget(self.combo_address_list[i])
            self.combo_address_list[i].addItems(self.address_list)
            hbox_1[i].addStretch(1)
            
            hbox_1[i].addWidget(type_label_list[i])
            hbox_1[i].addWidget(self.combo_type_list[i])
            self.combo_type_list[i].addItems(self.source_meter_list)
            hbox_1[i].addStretch(1)
            
            hbox_2[i].addWidget(start_point_label_list[i])
            hbox_2[i].addWidget(self.start_point_edit_list[i])
            self.start_point_edit_list[i].setFixedWidth(70)
            self.start_point_edit_list[i].setValidator(self.onlyDouble)
            hbox_2[i].addStretch(1)
            
            hbox_2[i].addWidget(end_point_label_list[i])
            hbox_2[i].addWidget(self.end_point_edit_list[i])
            self.end_point_edit_list[i].setFixedWidth(70)
            self.end_point_edit_list[i].setValidator(self.onlyDouble)
            hbox_2[i].addStretch(1)
            
            hbox_2[i].addWidget(number_of_points_label_list[i])
            hbox_2[i].addWidget(self.number_of_points_edit_list[i])
            self.number_of_points_edit_list[i].setFixedWidth(70)
            self.number_of_points_edit_list[i].setValidator(self.onlyPositiveInt)
            self.number_of_points_edit_list[i].textChanged.connect(self.refresh_interval)
            hbox_2[i].addStretch(1)
            
            hbox_2[i].addWidget(step_label_list[i])
            hbox_2[i].addWidget(self.step_indicator_list[i])
            self.step_indicator_list[i].setFixedWidth(80)
            
            hbox_2[i].addWidget(self.current_value_label_list[i])
            self.current_value_label_list[i].setFixedWidth(70)
            
            hbox_3[i].addStretch(1)
            hbox_3[i].addWidget(internal_delay_label_list[i])
            hbox_3[i].addWidget(self.internal_delay_edit_list[i])
            self.internal_delay_edit_list[i].setFixedWidth(60)
            self.internal_delay_edit_list[i].setValidator(self.onlyPositiveDouble)
            hbox_3[i].addStretch(1)
            
            hbox_3[i].addStretch(1)
            hbox_3[i].addWidget(internal_step_label_list[i])
            hbox_3[i].addWidget(self.internal_step_edit_list[i])
            self.internal_step_edit_list[i].setFixedWidth(60)
            self.internal_step_edit_list[i].setValidator(self.onlyPositiveDouble)
            hbox_3[i].addStretch(1)
            
            
            hbox_3[i].addWidget(wait_time_label_list[i])
            hbox_3[i].addWidget(self.wait_time_edit_list[i])
            self.wait_time_edit_list[i].setFixedWidth(60)
            self.wait_time_edit_list[i].setValidator(self.onlyPositiveDouble)
            hbox_3[i].addStretch(1)
        
        vbox_small = [QVBoxLayout() for i in range(self.loop_num)]
        for i in range(self.loop_num):
            vbox_small[i].addLayout(hbox_1[i])
            vbox_small[i].addLayout(hbox_2[i])
            vbox_small[i].addLayout(hbox_3[i])
            vbox_small[i].addWidget(hline[i])
            hline[i].setFrameShape(QFrame.HLine)
            
        update_button = QPushButton('Update', self)
        update_button.setFixedWidth(70)
        update_button.clicked.connect(self.update_delay_step_wait)
        
        up_order_label = QLabel('Up Order: ', self)
        self.up_order_combo = QComboBox()
        self.up_order_combo.setFixedWidth(70)
        self.up_order_combo.addItems(self.order_list)
        self.up_order_combo.setCurrentText('0123')
        
        
        down_order_label = QLabel('Down Order: ', self)
        self.down_order_combo = QComboBox()
        self.down_order_combo.setFixedWidth(70)
        self.down_order_combo.addItems(self.order_list)
        self.down_order_combo.setCurrentText('3210')
        
        hbox_update = QHBoxLayout()
        hbox_update.addStretch(1)
        hbox_update.addWidget(update_button)
        hbox_update.addStretch(1)
        hbox_update.addWidget(up_order_label)
        hbox_update.addWidget(self.up_order_combo)
        hbox_update.addStretch(1)
        hbox_update.addWidget(down_order_label)
        hbox_update.addWidget(self.down_order_combo)
        hbox_update.addStretch(1)
        
        hline_update = QFrame()
        hline_update.setFrameShape(QFrame.HLine)
        
            
        read_label_label = QLabel('Label', self)
        address_label = QLabel('Address', self)
        type_label = QLabel('Meter Type', self)
        prefactor_label = QLabel('Prefactor', self)
        reading_label = QLabel('Reading', self)
        display_1d_label = QLabel('1D Display', self)
        display_2d_label = QLabel('2D Display', self)
        
        self.read_label_list = [QLineEdit() for i in range(self.read_num)] 
        self.combo_address_read_list = [QComboBox() for i in range(self.read_num)]
        self.combo_type_read_list = [QComboBox() for i in range(self.read_num)]
        self.prefactor_edit_list = [QLineEdit() for i in range(self.read_num)]    
        self.reading_list = [QLabel('0', self) for i in range(self.read_num)]
        self.display_1d_checkbox_list = [QCheckBox(self) for i in range(self.read_num)]
        self.display_2d_checkbox_list = [QCheckBox(self) for i in range(self.read_num)]
        self.previous_checked_2d_checkbox_num = 0
        
        
        reading_grid = QGridLayout()
        
        reading_grid.addWidget(read_label_label, 0, 0, Qt.AlignCenter)
        reading_grid.addWidget(address_label, 0, 1, Qt.AlignCenter)
        reading_grid.addWidget(type_label, 0, 2, Qt.AlignCenter)
        reading_grid.addWidget(prefactor_label, 0, 3, Qt.AlignCenter)
        reading_grid.addWidget(reading_label, 0, 4, Qt.AlignCenter)
        reading_grid.addWidget(display_1d_label, 0, 5, Qt.AlignCenter)
        reading_grid.addWidget(display_2d_label, 0, 6, Qt.AlignCenter)
        
        for i in range(self.read_num):
            reading_grid.addWidget(self.read_label_list[i], i + 1, 0, Qt.AlignCenter)
            self.read_label_list[i].setFixedWidth(60)
            
            reading_grid.addWidget(self.combo_address_read_list[i], i + 1, 1, Qt.AlignCenter )
            self.combo_address_read_list[i].addItems(self.address_list)
            
            reading_grid.addWidget(self.combo_type_read_list[i], i + 1, 2, Qt.AlignCenter )
            self.combo_type_read_list[i].addItems(self.source_meter_list)
            
            reading_grid.addWidget(self.prefactor_edit_list[i], i + 1, 3, Qt.AlignCenter )
            self.prefactor_edit_list[i].setFixedWidth(60)
            self.prefactor_edit_list[i].setValidator(self.onlyDouble)
            self.prefactor_edit_list[i].setText('1')
            
            reading_grid.addWidget(self.reading_list[i], i + 1, 4, Qt.AlignCenter )
            
            reading_grid.addWidget(self.display_1d_checkbox_list[i], i + 1, 5, Qt.AlignCenter)
            
            reading_grid.addWidget(self.display_2d_checkbox_list[i], i + 1, 6, Qt.AlignCenter)
            self.display_2d_checkbox_list[i].stateChanged.connect(self.change_2d_display_state)
            
        hbox_reading = QHBoxLayout()
        hbox_reading.addStretch(1)
        hbox_reading.addLayout(reading_grid)
        hbox_reading.addStretch(1)
        
        save_path_button = QPushButton('Folder: ', self)
        save_path_button.setIcon(QIcon(self.current_dir + 'openfile.png'))
        save_path_button.setFixedWidth(100)
        save_path_button.clicked.connect(self.save_path_setting)
        self.save_path_edit = QLineEdit()
        self.save_path_edit.setText('C:/Jingxu')
        save_file_label = QLabel('File Name: ', self)
        self.save_file_edit = QLineEdit()
        
        
        hbox_save_path = QHBoxLayout()
        hbox_save_path.addWidget(save_path_button)
        hbox_save_path.addWidget(self.save_path_edit)
        
        hbox_save_file = QHBoxLayout()
        hbox_save_file.addWidget(save_file_label)
        hbox_save_file.addWidget(self.save_file_edit)
        
        vbox_save_data = QVBoxLayout()
        vbox_save_data.addLayout(hbox_save_path)
        vbox_save_data.addLayout(hbox_save_file)
        
        self.start_button = QPushButton(QIcon(self.current_dir + 'start.png'), '')
        self.start_button.setCheckable(True)
        self.start_button.setFixedWidth(50)
        self.start_button.setToolTip('Start')
        self.start_button.clicked.connect(self.check_for_run)
        
        self.pause_button = QPushButton(QIcon(self.current_dir + 'pause.png'), '')
        self.pause_button.setCheckable(True)
        self.pause_button.setFixedWidth(50)
        self.pause_button.setToolTip('Pause')
        self.pause_button.clicked.connect(self.check_for_pause)
        
        self.stop_button = QPushButton(QIcon(self.current_dir + 'stop.png'), '')
        self.stop_button.setFixedWidth(50)
        self.stop_button.setToolTip('Stop')
        
        self.emergency_button = QPushButton(QIcon(self.current_dir + 'emergency.png'), '')
        self.emergency_button.setFixedWidth(50)
        self.emergency_button.setToolTip('Emergency stop')
        self.emergency_button.clicked.connect(self.emergency_stop)
        self.emergency_button.setAutoRepeat(True)
        self.emergency_button.setAutoRepeatInterval(1000)
        
        
        hbox_run = QHBoxLayout()
        hbox_run.addWidget(self.start_button)
        hbox_run.addWidget(self.pause_button)
        hbox_run.addWidget(self.stop_button)
        hbox_run.addWidget(self.emergency_button)
        
        vbox_left = QVBoxLayout()
        vbox_left.addStretch(1)
        for i in range(self.loop_num):
            vbox_left.addLayout(vbox_small[i])
            vbox_left.addStretch(1)
        
        vbox_left.addLayout(hbox_update)
        vbox_left.addWidget(hline_update)
        vbox_left.addStretch(1)
        vbox_left.addLayout(hbox_reading)
        vbox_left.addStretch(1)
        vbox_left.addLayout(vbox_save_data)
        vbox_left.addStretch(1)
        vbox_left.addLayout(hbox_run)
        
        
        
        self.canvas_1 = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas_1.fig.tight_layout(pad = 0)
        self.canvas_2 = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas_2.fig.tight_layout(pad = 0)
        
        
        # self.isPlot = False
        
        self.toolbar_matplotlib_1 = MyToolbar(self.canvas_1, self)
        self.toolbar_matplotlib_2 = MyToolbar(self.canvas_2, self)
        
        self.update_2d_thread = Update2DThread(toolbar = self.toolbar_matplotlib_2, canvas = self.canvas_2)
        
        self.set_range_high_edit = QLineEdit()
        self.set_range_high_edit.setFixedWidth(70)
        self.set_range_high_edit.setValidator(self.onlyDouble)
        self.set_range_high_edit.textChanged.connect(self.change_range)
        
        self.slider_range = [0, 1000]
        self.v_ratio = [0, 1]
        self.slider = QRangeSlider(Qt.Vertical)
        self.slider.setFocusPolicy(Qt.StrongFocus)
        self.slider.setMaximum(self.slider_range[1])
        self.slider.setMinimum(self.slider_range[0])
        self.slider.setValue([0, 1000])
        # self.slider.valueChanged[tuple].connect(self.change_contrast)
        
        
        self.set_range_low_edit = QLineEdit()
        self.set_range_low_edit.setFixedWidth(70)
        self.set_range_low_edit.setValidator(self.onlyDouble)
        self.set_range_low_edit.textChanged.connect(self.change_range)
        
        cmap_list = ['seismic', 'autumn', 'bwr', 'cool', 'hot', 'jet', 'rainbow', 'viridis', 'plasma', 'winter']
        
        self.combo_cmap = QComboBox()
        self.combo_cmap.addItems(cmap_list)
        self.combo_cmap.activated[str].connect(self.change_cmap)
        
        vbox_figure_1 = QVBoxLayout()
        vbox_figure_1.addWidget(self.toolbar_matplotlib_1)
        vbox_figure_1.addWidget(self.canvas_1)
        # vbox_figure_1.addLayout(hbox_leftTool)
        
        widget_figure_1 = QWidget()
        widget_figure_1.setLayout(vbox_figure_1)
        
        vbox_figure_2 = QtWidgets.QVBoxLayout()
        vbox_figure_2.addWidget(self.toolbar_matplotlib_2)
        vbox_figure_2.addWidget(self.canvas_2)
        
        vbox_slider = QVBoxLayout()
        vbox_slider.addWidget(self.set_range_high_edit, 0, Qt.AlignHCenter)
        vbox_slider.addWidget(self.slider, 0, Qt.AlignHCenter)
        vbox_slider.addWidget(self.set_range_low_edit, 0, Qt.AlignHCenter)
        vbox_slider.addWidget(self.combo_cmap)
        
        hbox_right_bottom = QHBoxLayout()
        hbox_right_bottom.addLayout(vbox_figure_2)
        hbox_right_bottom.addLayout(vbox_slider)
        
        widget_figure_2 = QWidget()
        widget_figure_2.setLayout(hbox_right_bottom)
        
        splitter_right = QSplitter(Qt.Vertical)
        splitter_right.addWidget(widget_figure_1)
        splitter_right.addWidget(widget_figure_2)
        
        
        widget_left = QWidget()
        widget_left.setLayout(vbox_left)
        widget_left.setFixedWidth(800)        
        
        hbox_main = QHBoxLayout()
        hbox_main.addWidget(widget_left)
        hbox_main.addWidget(splitter_right)
        
        self.plot_timer = QTimer()
        self.plot_timer.timeout.connect(self.update_draw)
        
            
            
        self.central_widget = QWidget()
            
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)
        self.layout.addLayout(hbox_main)
        
        self.resize(1600, 800)
        self.move( 0, 0)
        
        self.setStyleSheet(qdarkstyle._load_stylesheet(qt_api='pyqt5', palette = LightPalette))
        self.slider.setStyleSheet(QSS)
        
        self.show()
        
    def check_for_run(self):
        if self.start_button.isChecked():
            if not self.collect_data_thread.is_running and not self.collect_data_thread.is_pause:
                self.generate_for_run()
            if self.collect_data_thread.is_pause:
                self.collect_data_thread.is_pause = False
                self.pause_button.setChecked(False)
                
        if not self.start_button.isChecked():
            if self.collect_data_thread.is_running:
                self.start_button.setChecked(True)
                
    def check_for_pause(self):
        if self.pause_button.isChecked():
            if self.collect_data_thread.is_running:
                self.collect_data_thread.is_pause = True
                self.pause_button.setChecked(True)
                self.start_button.setChecked(False)
            else:
                self.pause_button.setChecked(False)
                
        if not self.pause_button.isChecked():
            if self.collect_data_thread.is_pause:
                self.pause_button.setChecked(True)
                
    def emergency_stop(self):
        if self.emergency_button.isDown():
            print('isDown')
            if self.collect_data_thread.is_running:
                print('stopping')
                self.collect_data_thread.is_stop = True
                self.collect_data_thread.go_zero()
                print('Emergency stopped')
        
                
        
        
    def generate_for_run(self):
        self.plot_timer.stop()
        self.check_and_create_folder()
        header_to_write = 'Probe' + '\t'
        for i in range(self.loop_num):
            self.loop_info[i]['Address'] = self.combo_address_list[i].currentText()
            self.loop_info[i]['MeterType'] = self.combo_type_list[i].currentText()
            header_to_write += self.string_edit_list[i].text() + '\t'
            try:
                self.loop_params[i]['StartPoint'] = float(self.start_point_edit_list[i].text())
                self.loop_params[i]['EndPoint'] = float(self.end_point_edit_list[i].text())
                self.loop_params[i]['NumberOfPoints'] = int(self.number_of_points_edit_list[i].text())
            except:
                self.loop_params[i]['StartPoint'] = 0
                self.loop_params[i]['EndPoint'] = 0
                self.loop_params[i]['NumberOfPoints'] = 1
                
                self.loop_info[i]['Address'] = 'None'
                self.loop_info[i]['MeterType'] = 'None'
            
            try:
                self.loop_params[i]['InternalDelay'] = float(self.internal_delay_edit_list[i].text())
            except:
                self.loop_params[i]['InternalDelay'] = 0.1
            try:
                self.loop_params[i]['InternalStep'] = float(self.internal_step_edit_list[i].text())
            except:
                self.loop_params[i]['InternalStep'] = 0.1
            try:
                self.loop_params[i]['WaitTime'] = float(self.wait_time_edit_list[i].text())
            except:
                self.loop_params[i]['WaitTime'] = 0
                # print('Generate information error')
                # return False
        for i in range(self.loop_num):
            for j in range(i + 1, self.loop_num):
                print(self.loop_info[i]['Address'])
                if self.loop_info[i]['Address'] == 'None':
                    break
                if self.loop_info[j]['Address'] == self.loop_info[i]['Address']:
                    print('Address Conflict!')
                    return
            
        for i in range(self.read_num):
            self.read_info[i]['Address'] = self.combo_address_read_list[i].currentText()
            self.read_info[i]['MeterType'] = self.combo_type_read_list[i].currentText()
            header_to_write += self.read_label_list[i].text() + '\t'
            
            try:
                self.read_params[i]['Prefactor'] = float(self.prefactor_edit_list[i].text())
            except:
                self.read_params[i]['Prefactor'] = 1
        
        with open(self.save_file_name, 'w') as file:
            file.write((header_to_write + "\n"))
            
        up_order = self.up_order_combo.currentText()
        down_order = self.down_order_combo.currentText()
        
        self.collect_data_thread = CollectDataThread(True, 
                                                     self.loop_num, self.loop_info, self.loop_params,
                                                     self.read_num, self.read_info, self.read_params,
                                                     self.save_file_name, up_order, down_order)
        
        sleep(5)
        self.collect_data_thread.start()
        
        if not self.collect_data_thread.error:
            self.plot_timer.start(100)
            sleep(1)
            self.update_2d_thread.plot_2D = True
            self.update_2d_thread.start()
            
    
    
    def update_delay_step_wait(self):
        if self.collect_data_thread.is_running and not self.collect_data_thread.is_stop:
            for i in range(self.loop_num):
                try:
                    self.collect_data_thread.loop_instruments[i]._INTER_DELAY = float(self.internal_delay_edit_list[i].text())
                except: pass
                try:
                    self.collect_data_thread.loop_instruments[i]._STEP = float(self.internal_step_edit_list[i].text())
                except: pass
                try:
                    self.loop_params[i]['WaitTime'] = float(self.wait_time_edit_list[i].text())
                except: pass
            try:
                self.collect_data_thread.down_order = self.down_order_combo.currentText()
            except: pass
                    

        
    def refresh_interval(self):
        for i in range(self.loop_num):
            try:
                start = float(self.start_point_edit_list[i].text())
                end = float(self.end_point_edit_list[i].text())
                diff = end - start
                NoP = int(self.number_of_points_edit_list[i].text()) - 1
                if NoP <= 0:
                    self.number_of_points_edit_list[i].setText('1')
                    self.step_indicator_list[i].setText('0')
                else:
                    self.step_indicator_list[i].setText(str(diff / NoP)[:8])
            except Exception as e:
                self.step_indicator_list[i].setText('')
                # print(e)
                # print('refresh_inteval error')
        
    def save_path_setting(self):     
        fname = QFileDialog.getExistingDirectory(self, 'Set saving folder', self.save_folder)
        if len(fname) != 0:
            self.save_folder = fname
            self.save_path_edit.setText(fname)
            
    def check_and_create_folder(self):
        self.save_folder = self.save_path_edit.text()
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
        if self.save_folder[-1] != '/':
            self.save_folder += '/'
        self.save_file_name = self.save_folder + datetime.now().strftime("%Y%m%d-%H%M%S") + ' ' + \
                              self.save_file_edit.text() + '.txt'
                    
                    
    def change_2d_display_state(self):
        checked_box_num_list = []
        for i in range(0, self.read_num):
            if self.display_2d_checkbox_list[i].isChecked():
                checked_box_num_list.append(i)
        for num in checked_box_num_list:
            if num != self.previous_checked_2d_checkbox_num:
                self.previous_checked_2d_checkbox_num = num
                break
        if len(checked_box_num_list) > 1:
            for i in range(0, self.read_num):
                self.display_2d_checkbox_list[i].setChecked(False)
            self.display_2d_checkbox_list[num].setChecked(True)
            
    def update_draw(self):
        try:
        
            value_list = self.collect_data_thread.value_list
            index = self.collect_data_thread.index
            self.data_collected = self.collect_data_thread.data_collected
            
            x_axis = value_list[-1]
            y_axis = value_list[-2]
            if self.collect_data_thread.loop_info[-1]['MeterType'] == 'K2502': #2502 negative output, so we change back here
                x_axis = -x_axis
            if self.collect_data_thread.loop_info[-2]['MeterType'] == 'K2502': #2502 negative output, so we change back here
                y_axis = -y_axis
                
                
            x_index = index[-1]
            
            xlim = self.canvas_1.axes.get_xlim()
            ylim = self.canvas_1.axes.get_ylim()
            self.canvas_1.axes.cla()
            
            for i in range(self.read_num):
                if self.display_1d_checkbox_list[i].isChecked():
                    self.canvas_1.axes.plot(x_axis[:x_index], self.data_collected[index[0], index[1], index[2], :x_index, i])
                    if not self.toolbar_matplotlib_1.auto_X_button.isChecked():
                        self.canvas_1.axes.set_xlim(xlim)
                    if not self.toolbar_matplotlib_1.auto_Y_button.isChecked():
                        self.canvas_1.axes.set_ylim(ylim)
            self.canvas_1.draw()
            
            
            
            y_index = index[-2] + 2
            self.update_2d_thread.x_axis = x_axis
            self.update_2d_thread.y_axis = y_axis[:y_index]
            
            for i in range(self.read_num):
                if self.display_2d_checkbox_list[i].isChecked():
                    self.data_2D = self.data_collected[index[0], index[1], :y_index, :, i]
                    self.change_contrast(self.data_2D)
                    self.update_2d_thread.data = self.data_2D
                    break                               #break because there is only 1 (maximun) 2d plot
            
            if not self.display_2d_checkbox_list[i].isChecked():                   # if there is no 2d plot checked        
                self.update_2d_thread.data = np.zeros(1)
                    
            if not self.collect_data_thread.is_running:
                self.start_button.setChecked(False)
                self.pause_button.setChecked(False)
            else:
                for i in range(self.loop_num):
                    self.current_value_label_list[i].setText(str(self.collect_data_thread.loop_instruments[i]._VALUE)[:7])
                for i in range(self.read_num):
                    self.reading_list[i].setText(str(self.collect_data_thread.read_instruments[i]._OUTPUT * self.read_params[i]['Prefactor'])[:5])
                if psutil.swap_memory().free/1024/1024 < 100: # free committed memory < 100M
                    self.collected_data_thread.is_stop = True
                    self.update_2d_thread.plot_2D = False
                    self.collect_data_thread.go_zero()
                    print('Out of memory')
        except Exception as e:
            print('Plot 1D error', e)
            
    def change_range(self):
        pass
        
        
    def change_contrast(self, data_show):
        try:
            v_start = float(self.set_range_low_edit.text())
        except:
            v_start = np.min(data_show)
        try:
            v_end = float(self.set_range_high_edit.text())
        except:
            v_end = np.max(data_show)
            
        v_diff = v_end - v_start
            
        total_range = self.slider_range[1] - self.slider_range[0]
        value = self.slider.value()
        v_ratio = [(value[0] - self.slider_range[0]) / total_range,
                   (value[1] - self.slider_range[0]) / total_range]
        
        vmin = v_start + v_diff * v_ratio[0]
        vmax = v_start + v_diff * v_ratio[1]
        
        # print(vmin, vmax)
        
        # self.cbar_label = self.cbar.ax.get_ylabel()
        self.update_2d_thread.cmap = self.combo_cmap.currentText()
        self.update_2d_thread.vmin = vmin
        self.update_2d_thread.vmax = vmax
        pass
    
    def change_cmap(self):
        pass
        


class Update2DThread(QThread):
    def __init__(self, toolbar, canvas):
        super().__init__()
        self.toolbar = toolbar
        self.canvas = canvas
        self.data = np.zeros((3, 3))
        self.x_axis = np.linspace(0, 1, 3)
        self.y_axis = np.linspace(0, 1, 3)
        self.vmin = 0
        self.vmax = 1
        self.xlim = (0, 1)
        self.ylim = (0, 1)
        self.cmap = 'seismic'
        self.plot_2D = False
        self.isPlot = False
        
    def run(self):
        while self.plot_2D:
            try:
                X, Y = np.meshgrid(self.x_axis, self.y_axis)
                if self.data.shape[0] != X.shape[0] or self.data.shape[1] != X.shape[1]:
                    self.canvas.axes.cla()
                    self.canvas.draw()
                    sleep(1)
                    continue
                
                xlim = self.canvas.axes.get_xlim()
                ylim = self.canvas.axes.get_ylim()
                self.canvas.axes.cla()
                
                if self.isPlot:
                    self.cbar.remove()
                im = self.canvas.axes.pcolormesh(X, Y, self.data, shading = 'auto', cmap = self.cmap)
                self.cbar = self.canvas.fig.colorbar(im)
                # self.cbar.mappable.set_cmap(self.cmap)
                self.cbar.mappable.set_clim(self.vmin, self.vmax)
                if not self.toolbar.auto_X_button.isChecked():
                    self.canvas.axes.set_xlim(xlim)
                if not self.toolbar.auto_Y_button.isChecked():
                    self.canvas.axes.set_ylim(ylim)
                self.isPlot = True
                self.canvas.draw()
                
                sleep(0.5)
            except Exception as e:
                print('Plot 2D error', e)
                sleep(1)
            
        
        
        
        
        
class CollectDataThread(QThread):
    def __init__(self, flag = False, 
                 loop_num = [], loop_info = [], loop_params = [], 
                 read_num = [], read_info = [], read_params = [],
                 filename = [], up_order = [], down_order = []):
        super().__init__()
        self.is_running = False
        self.is_pause = False
        self.is_stop = False
        self.error = True
        if not flag:
            return
        
        self.loop_num = loop_num
        self.loop_info = loop_info
        self.loop_instruments = []
        self.loop_params = loop_params
        
        self.read_num = read_num
        self.read_info = read_info
        self.read_instruments = []
        self.read_params = read_params
        
        self.value_list = [[] for i in range(self.loop_num)]
        self.value = np.zeros(self.loop_num)
        self.index = np.zeros(self.loop_num, dtype = int)
        
        self.filename = filename
        
        self.up_order = up_order
        self.down_order = down_order
        
        self.probe = Probe('Probe', address = '192.168.0.30')
        
        self.error = False
        
        self.initialize_instruments()
            
    def initialize_instruments(self):
        try:
            for i in range(self.loop_num):
                if self.loop_info[i]['MeterType'] == 'None' or self.loop_info[i]['Address'] == 'None':
                    self.loop_instruments.append(EMPTY())
                if self.loop_info[i]['MeterType'] == 'K2400':
                    # self.loop_instruments.append(TEST)
                    self.loop_instruments.append(Keithley2400(str(i), self.loop_info[i]['Address']))
                elif self.loop_info[i]['MeterType'] == 'K2450':
                    self.loop_instruments.append(Keithley2450(str(i), self.loop_info[i]['Address']))
                elif self.loop_info[i]['MeterType'] == 'K2502':
                    self.loop_instruments.append(Keithley2502(str(i), self.loop_info[i]['Address']))
                elif self.loop_info[i]['MeterType'] == 'K6221':
                    self.loop_instruments.append(Keithley6221(str(i), self.loop_info[i]['Address']))
                elif self.loop_info[i]['MeterType'] == 'SR830':
                    self.loop_instruments.append(SR830(str(i), self.loop_info[i]['Address'], autorange = False))
                    
                self.loop_instruments[i]._STEP = self.loop_params[i]['InternalStep']
                self.loop_instruments[i]._INTER_DELAY = self.loop_params[i]['InternalDelay']
                self.value_list[i] = np.linspace(self.loop_params[i]['StartPoint'], self.loop_params[i]['EndPoint'], self.loop_params[i]['NumberOfPoints'])
            
                if self.loop_info[i]['MeterType'] == 'K2502': #K2502 negtive output
                    self.value_list[i] = -self.value_list[i]
            self.error = False
        
        except Exception as e:
            self.error = True
            print(e)
            print('Initalization Loop Failed. ' + self.loop_info[i]['Address'])
            
        try:
            for i in range(self.read_num):
                if self.read_info[i]['MeterType'] == 'None' or self.read_info[i]['Address'] == 'None':
                    self.read_instruments.append(EMPTY())
                if self.read_info[i]['MeterType'] == 'K2400':
                    self.read_instruments.append(Keithley2400(str(i + self.loop_num), self.read_info[i]['Address']))
                elif self.read_info[i]['MeterType'] == 'K2450':
                    self.read_instruments.append(Keithley2450(str(i + self.loop_num), self.read_info[i]['Address']))
                elif self.read_info[i]['MeterType'] == 'K2502':
                    self.read_instruments.append(Keithley2502(str(i + self.loop_num), self.read_info[i]['Address']))
                elif self.read_info[i]['MeterType'] == 'K6221':
                    self.read_instruments.append(Keithley6221(str(i + self.loop_num), self.read_info[i]['Address']))
                elif self.read_info[i]['MeterType'] == 'K2182':
                    self.read_instruments.append(Keithley2182(str(i + self.loop_num), self.read_info[i]['Address']))
                elif self.read_info[i]['MeterType'] == 'SR830':
                    self.read_instruments.append(SR830(str(i + self.loop_num), self.read_info[i]['Address'], autorange = False))
                    
                    
        except Exception as e:
            self.error = True
            print(e)
            print('Initalization Read Failed. ' + self.read_info[i]['Address'])
            
        self.data_collected = np.zeros([self.loop_params[0]['NumberOfPoints'], self.loop_params[1]['NumberOfPoints'],
                                        self.loop_params[2]['NumberOfPoints'], self.loop_params[3]['NumberOfPoints'],
                                        self.read_num])
            
            
    def run(self):
        try:
            if self.error:
                print('Error! Start failed')
                return #正式运行必须要有这个
            
            for i in range(self.loop_num): #check is K2502 error
                if self.loop_info[i]['MeterType'] == 'K2502':
                    if self.value_list[i][0] != -self.loop_params[i]['StartPoint'] or self.value_list[i][-1] != -self.loop_params[i]['EndPoint']:
                        self.error = True
                        print('K2502 negative output error!')
                        return
            
            self.is_running = True     
            
            self.previous_value = np.zeros(self.loop_num)
            count = 0
            
            up_list = []
            for i in range(self.loop_num):
                up_list.append(int(self.up_order[i]))
            
            for i in up_list:
                self.check_pause_and_stop()
                if self.is_stop: return
                self.value[i] = self.value_list[i][0]
                self.loop_instruments[i].set_volt(0, self.value[i])
                self.previous_value[i] = self.value[i]
                sleep(self.loop_params[i]['WaitTime'])
                
            for self.index[0] in range(len(self.value_list[0])):
                self.check_pause_and_stop()
                if self.is_stop: return
                print(self.value_list[0], self.index[0])
                self.value[0] = self.value_list[0][self.index[0]]
                self.loop_instruments[0].set_volt(self.previous_value[0], self.value[0])
                self.previous_value[0] = self.value[0]
                sleep(self.loop_params[0]['WaitTime'])
                    
                for self.index[1] in range(len(self.value_list[1])):
                    self.check_pause_and_stop()
                    if self.is_stop: return
                    self.value[1] = self.value_list[1][self.index[1]]
                    self.loop_instruments[1].set_volt(self.previous_value[1], self.value[1])
                    self.previous_value[1] = self.value[1]
                    sleep(self.loop_params[1]['WaitTime'])
                    
                    for self.index[2] in range(len(self.value_list[2])):
                        self.check_pause_and_stop()
                        if self.is_stop: return
                        self.index[3] = 0 #For 1d plot usage
                        self.value[2] = self.value_list[2][self.index[2]]
                        self.loop_instruments[2].set_volt(self.previous_value[2], self.value[2])
                        self.previous_value[2] = self.value[2]
                        sleep(self.loop_params[2]['WaitTime'])
                            
                        for self.index[3] in range(len(self.value_list[3])):
                            self.check_pause_and_stop()
                            if self.is_stop: return
                            self.value[3] = self.value_list[3][self.index[3]]
                            self.loop_instruments[3].set_volt(self.previous_value[3], self.value[3])
                            self.previous_value[3] = self.value[3]
                            sleep(self.loop_params[3]['WaitTime'])
                            
                            for i in range(self.read_num):
                                if self.read_info[i]['MeterType'] == 'K6221':
                                    self.read_instruments[i]._OUTPUT = self.read_instruments[i].delta_read()
                                else:
                                   self.read_instruments[i]._OUTPUT = self.read_instruments[i].volt()
                                self.data_collected[self.index[0], self.index[1], self.index[2], self.index[3], i] = self.read_instruments[i]._OUTPUT * self.read_params[i]['Prefactor']
                            
                            # data_for_write = [self.probe.temperature()]
                            data_for_write = []
                            data_for_write += [self.value[i] for i in range(self.loop_num)]
                            data_for_write += list(self.data_collected[self.index[0], self.index[1], self.index[2], self.index[3], :])
                            
                            with open(self.filename, 'a') as file:
                                file.write(("\t".join(map(str, data_for_write))+"\n"))
                                
                            count += 1
                            if count == self.loop_params[0]['NumberOfPoints'] * self.loop_params[1]['NumberOfPoints'] * \
                                        self.loop_params[2]['NumberOfPoints'] * self.loop_params[3]['NumberOfPoints']:
                                print('Scan finished')
                                self.is_stop = True
                                self.go_zero()
                                print('All set to zero')
                                return
                        
                        self.check_pause_and_stop()
                        if self.is_stop: return
                        self.loop_instruments[3].set_volt(self.value[3], self.value_list[3][0])
                        self.previous_value[3] = self.value_list[3][0]
                    
                    self.check_pause_and_stop()
                    if self.is_stop: return 
                    self.loop_instruments[2].set_volt(self.value[2], self.value_list[2][0])
                    self.previous_value[2] = self.value_list[2][0]
                   
                self.check_pause_and_stop()    
                if self.is_stop: return
                self.loop_instruments[1].set_volt(self.value[1], self.value_list[1][0])
                self.previous_value[1] = self.value_list[1][0]
                
        except Exception as e:
            print('Collecting data error: ', e)
            self.go_zero()
    
    def check_pause_and_stop(self):
        while True:
            if self.is_stop:
                break
            if not self.is_pause:
                break
            else:
                sleep(0.1)
    
    
    def go_zero(self):
        if self.is_running:
            self.loop_instruments[3]._STOP = True
            self.loop_instruments[2]._STOP = True
            self.loop_instruments[1]._STOP = True
            self.loop_instruments[0]._STOP = True
            
            sleep(np.max([self.loop_params[3]['InternalDelay'], self.loop_params[2]['InternalDelay'],
                          self.loop_params[1]['InternalDelay'], self.loop_params[0]['InternalDelay']]))
            sleep(1)
            
            self.loop_instruments[3]._STOP = False
            self.loop_instruments[2]._STOP = False
            self.loop_instruments[1]._STOP = False
            self.loop_instruments[0]._STOP = False
            
            down_list = []
            for i in range(self.loop_num):
                down_list.append(int(self.down_order[i]))
            
            for i in down_list:
                self.loop_instruments[i].set_volt(self.loop_instruments[i]._VALUE, 0)

            
            self.is_running = False
            self.is_pause = False
            self.is_stop = False
            
            qc.Instrument.close_all()
        
            
            

class EMPTY:
    _STEP = 0.1
    _INTER_DELAY = 0.1
    _STOP = False
    _VALUE = 0
    _OUTPUT = 0
    def __init__(self):
        super().__init__()
        pass
    
    def set_volt(self, v_1, v_2):
        v_vals = np.linspace(v_1, v_2, abs(round((v_2-v_1)/self._STEP)) + 1)
        if len(v_vals) < 2:
            v_vals = [v_1, v_2]
        # print(v_vals)
        for self._VALUE in v_vals[1:]:
            if self._STOP:
                self._STOP = False
                break
            print(self._VALUE)
            sleep(self._INTER_DELAY)
        
        
    def volt(self):
        OUTPUT = uniform(-1, 1)
        return OUTPUT
        
    
    
    
    
QSS = """
QSlider{
 background-color: none;
}

QSlider::add-page:vertical {
  background: none;
  border: none;
}

QRangeSlider {
      qproperty-barColor: #9FCBFF;
}
"""
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()
        
        