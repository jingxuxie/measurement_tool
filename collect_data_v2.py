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
                            QAction, QCheckBox, QGridLayout, QSplitter, QFrame, QMenu, QProgressBar
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QFont
from PyQt5.QtGui import QIcon
from superqt import QRangeSlider
from PyQt5.QtCore import Qt, QThread, QTimer

import pyqtgraph as pg
pg.setConfigOption('imageAxisOrder', 'row-major')
pg.setConfigOption('useNumba', True)

import numpy as np
import os
from datetime import datetime
from time import sleep, time
from random import uniform

from instrument_drivers.tektronix.Keithley_2450 import Keithley2450
from instrument_drivers.tektronix.Keithley_2400 import Keithley2400
from instrument_drivers.tektronix.Keithley_2502_Src_1 import Keithley2502_Src_1
from instrument_drivers.tektronix.Keithley_2502_Src_2 import Keithley2502_Src_2
from instrument_drivers.stanford_research.SR830 import SR830
from instrument_drivers.tektronix.Keithley_6221 import Keithley6221
from instrument_drivers.tektronix.Keithley_2182 import Keithley2182
import qcodes as qc
from instrument_drivers.Bluefors.Probe import Probe

import qdarkstyle
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

        
class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.current_dir = os.getcwd().replace('\\','/') + '/support_files/'
        print(self.current_dir)
        
        self.timer_num = 3
        # self.previous_levels = [0, 1]
        
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
        
        self.source_meter_list = ['None', 'K2400', 'K2450', 'K2502_1', 'K2502_2', 'K6221', 'K2182', 'SR830', 'SR865']
        self.read_meter_list = ['None', 'K2400', 'K2450', 'K2502_1', 'K2502_2', 'K6221', 'K2182', 'SR830 X', 'SR830 Y', 'SR830 R', 'SR830 Theta', 'SR865']
        self.address_list = ['None'] + ['GPIB0::{}::INSTR'.format(str(i)) for i in range(30)]
        self.order_list = ['0123', '0132', '0213', '0231', '0312', '0321', 
                           '1023', '1032', '1203', '1230', '1302', '1320', 
                           '2013', '2031', '2103', '2130', '2301', '2310', 
                           '3012', '3021', '3102', '3120', '3201', '3210']
        
        self.color_list = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        self.collect_data_thread = CollectDataThread()
        
        load_param = QAction('Load Params', self)
        load_param.triggered.connect(self.LoadParams)
        load_param.setIcon(QIcon(self.current_dir+'openfile.png'))
        
        save_param = QAction('Save Params', self)
        save_param.triggered.connect(self.SaveParams)
        save_param.setIcon(QIcon(self.current_dir+'savefile.png'))
        save_param.setShortcut('Ctrl + S')
        
        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(load_param)
        fileMenu.addAction(save_param)
        
        self.params_folder = 'C:/'
        
        
        
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
            self.combo_type_read_list[i].addItems(self.read_meter_list)
            
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
        self.save_path_edit.setText('F:/Temp')
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
        
        self.pbar = QProgressBar(self)
        
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
        vbox_left.addStretch(1)
        vbox_left.addWidget(self.pbar)
        
        pg.setConfigOption('background', '#FAFAFA')
        
        self.pos_label = QLabel('', self)
        self.pos_label.setFixedHeight(15)
        self.pos_label.setFont(QFont('Arial', 8))
        
        self.isPlot = False
        self.crosshair = [pg.InfiniteLine(angle = 90, movable = False),
                          pg.InfiniteLine(angle = 0, movable = False)]

        self.plot_1 = pg.PlotWidget()
        self.plot_1.addLegend()
        self.plot_2_plotitem = pg.PlotItem()
        self.plot_2 = pg.ImageView(view = self.plot_2_plotitem)
        self.plot_2.scene.sigMouseMoved.connect(self.show_pos)
        
        for i in range(2):
            self.plot_2_plotitem.addItem(self.crosshair[i], ignoreBounds=True)
            self.crosshair[i].setZValue(1)
        
        # self.plot_2.setImage(np.array([np.array([uniform(1, -1) for i in range(200)]) for j in range(200)]),
        #                         scale = [0.1, 0.1], levels = [-1, 1])
        
        viewbox = self.plot_2.getView()
        viewbox.setAspectLocked(False)
        viewbox.autoRange(padding = 0)
        viewbox.invertY(False)
        histogram = self.plot_2.ui.histogram
        histogram.vb.setMaximumWidth(0)
        histogram.vb.setMouseEnabled(x = False, y = False)
        histogram.gradient.loadPreset('RdBu_r')
        self.plot_2.ui.roiBtn.hide()
        self.plot_2.ui.menuBtn.hide()
        
        
        # self.update_2d_thread = Update2DThread(canvas = self.plot_2)
        
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
        
        cmap_list = ['RdBu_r', 'RdBu', 'seismic', 'autumn', 'bwr', 'coolwarm', 'hot', 'jet', 'rainbow', 'viridis', 'plasma', 'winter']
        
        self.combo_cmap = QComboBox()
        self.combo_cmap.addItems(cmap_list)
        self.combo_cmap.activated[str].connect(self.change_cmap)
        self.combo_cmap.setFixedWidth(100)

        
        vbox_figure_1 = QVBoxLayout()
        vbox_figure_1.addWidget(self.plot_1)
        
        widget_figure_1 = QWidget()
        widget_figure_1.setLayout(vbox_figure_1)
        
        vbox_figure_2 = QtWidgets.QVBoxLayout()
        vbox_figure_2.addWidget(self.pos_label, 0, Qt.AlignRight)
        vbox_figure_2.addWidget(self.plot_2)
        
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
        
        self.plot_timer = [QTimer() for i in range(self.timer_num)]
        self.plot_timer[0].timeout.connect(self.update_draw_1d)
        self.plot_timer[1].timeout.connect(self.update_draw_2d)
        self.plot_timer[2].timeout.connect(self.update_progress)
        
            
            
        self.central_widget = QWidget()
            
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)
        self.layout.addLayout(hbox_main)
        
        self.resize(1600, 800)
        self.move( 0, 0)
        
        self.setStyleSheet(qdarkstyle._load_stylesheet(qt_api='pyqt5', palette = LightPalette))
        self.slider.setStyleSheet(QSS)
        
        self.show()
        
    def LoadParams(self):
        open_fname = QFileDialog.getOpenFileName(self, 'Load Params',\
                                                 self.params_folder,\
                                                 "params files(*.params)")
        if open_fname[0]:
            self.params_folder = os.path.dirname(open_fname[0])
            with open(open_fname[0]) as file:
                lines = file.readlines()
            for i in range(self.loop_num):
                line = lines[i].split(sep = '\t')
                self.string_edit_list[i].setText(line[0])
                self.combo_address_list[i].setCurrentText(line[1])
                self.combo_type_list[i].setCurrentText(line[2])
                self.start_point_edit_list[i].setText(line[3])
                self.end_point_edit_list[i].setText(line[4])
                self.number_of_points_edit_list[i].setText(line[5])
                self.internal_delay_edit_list[i].setText(line[6])
                self.internal_step_edit_list[i].setText(line[7])
                self.wait_time_edit_list[i].setText(line[8])
            line = lines[self.loop_num + 1].split(sep = '\t')
            self.up_order_combo.setCurrentText(line[0])
            self.down_order_combo.setCurrentText(line[1])
            for i in range(self.read_num):
                line = lines[i + self.loop_num + 1].split(sep = '\t')
                self.read_label_list[i].setText(line[0])
                self.combo_address_read_list[i].setCurrentText(line[1])
                self.combo_type_read_list[i].setCurrentText(line[2])
                self.prefactor_edit_list[i].setText(line[3])
            
                
        pass
    
    def SaveParams(self):
        save_fname = QFileDialog.getSaveFileName(self,'save as',\
                                                     self.params_folder,\
                                                     "Params files(*.params)")
        if save_fname[0]:
            self.params_folder = os.path.dirname(save_fname[0])
            with open(save_fname[0], 'w+') as file:
                for i in range(self.loop_num):
                    file.write(self.string_edit_list[i].text() + '\t')
                    file.write(self.combo_address_list[i].currentText() + '\t')
                    file.write(self.combo_type_list[i].currentText() + '\t')
                    file.write(self.start_point_edit_list[i].text() + '\t')
                    file.write(self.end_point_edit_list[i].text() + '\t')
                    file.write(self.number_of_points_edit_list[i].text() + '\t')
                    file.write(self.internal_delay_edit_list[i].text() + '\t')
                    file.write(self.internal_step_edit_list[i].text() + '\t')
                    file.write(self.wait_time_edit_list[i].text() + '\t')
                    file.write('\n')
                file.write(self.up_order_combo.currentText() + '\t')
                file.write(self.down_order_combo.currentText() + '\t')
                file.write('\n')
                for i in range(self.read_num):
                    file.write(self.read_label_list[i].text() + '\t')
                    file.write(self.combo_address_read_list[i].currentText() + '\t')
                    file.write(self.combo_type_read_list[i].currentText() + '\t')
                    file.write(self.prefactor_edit_list[i].text() + '\t')
                    file.write('\n')
                    
                    
        
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
        for i in range(self.timer_num):
            self.plot_timer[i].stop()
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
                    if self.loop_info[j]['MeterType'] == self.loop_info[i]['MeterType']:
                        print('Address and MeterType Conflict!')
                        return
                    elif self.loop_info[j]['MeterType'][:5] != 'K2502' or self.loop_info[i]['MeterType'][:5] != 'K2502':
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
                
        header_to_write += '2450Current' + '\t'
        
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
            self.plot_timer[0].start(100)
            sleep(1)
            self.plot_timer[1].start(1000)
            self.plot_timer[2].start(1000)
            # self.update_2d_thread.plot_2D = True
            # self.update_2d_thread.start()
            
    
    
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
            
    def update_draw_1d(self):
        try:
            self.value_list = self.collect_data_thread.value_list
            self.index = self.collect_data_thread.index
            self.data_collected = self.collect_data_thread.data_collected
            
            self.x_axis = self.value_list[-1]
            self.y_axis = self.value_list[-2]
            if self.collect_data_thread.loop_info[-1]['MeterType'][:5] == 'K2502': #2502 negative output, so we change back here
                self.x_axis = -self.x_axis
            if self.collect_data_thread.loop_info[-2]['MeterType'][:5] == 'K2502': #2502 negative output, so we change back here
                self.y_axis = -self.y_axis
                
                
            x_index = self.index[-1]
            
            self.plot_1.clear()
            
            for i in range(self.read_num):
                if self.display_1d_checkbox_list[i].isChecked():
                    self.plot_1.plot(self.x_axis[:x_index], self.data_collected[self.index[0], self.index[1], self.index[2], :x_index, i], 
                                     pen = pg.mkPen(color = self.color_list[i], width = 2), 
                                     name = self.read_label_list[i].text())
            
                    
            if not self.collect_data_thread.is_running:
                self.start_button.setChecked(False)
                self.pause_button.setChecked(False)
            else:
                for i in range(self.loop_num):
                    self.current_value_label_list[i].setText(str(self.collect_data_thread.loop_instruments[i]._VALUE)[:7])
                for i in range(self.read_num):
                    self.reading_list[i].setText(str(self.collect_data_thread.read_instruments[i]._OUTPUT * self.read_params[i]['Prefactor'])[:5])
            
        except Exception as e:
            print('Plot 1D error', e)
            
    def update_draw_2d(self):
        try:
            x_axis = self.x_axis
            y_index = self.index[-2] + 2
            y_axis = self.y_axis[:y_index]
            
            for i in range(self.read_num):
                if self.display_2d_checkbox_list[i].isChecked():
                    self.data_2D = self.data_collected[self.index[0], self.index[1], :y_index, :, i]
                    self.change_contrast(self.data_2D)
                    
                    scale_x = (x_axis[-1] - x_axis[0]) / len(x_axis)
                    scale_y = (y_axis[-1] - y_axis[0]) / len(y_axis)
                    
                    # self.plot_2.clear()
                    self.plot_2.setImage(self.data_2D, pos = [x_axis[0], y_axis[0]],
                                          autoRange = False, autoLevels = False,
                                          autoHistogramRange = False,
                                          scale = [scale_x, scale_y], 
                                          levels = [self.vmin, self.vmax],
                                          )
                    self.plot_2.ui.histogram.vb.setLimits(yMin = self.vmin, yMax = self.vmax)
                    self.plot_2.ui.histogram.setHistogramRange(self.vmin, self.vmax)
                    self.plot_2.setColorMap(pg.colormap.get(name = self.combo_cmap.currentText(), 
                                                            source='matplotlib'))
                    self.isPlot = True
                    break  #break because there is only 1 (maximun) 2d plot
                    
            
            
        except Exception as e:
            print('Plot 2D error', e)
            
    def update_progress(self):
        self.pbar.setValue(self.collect_data_thread.progress)
        self.pbar.setFormat(self.collect_data_thread.pbar_text)
            
            
        pass
            
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
        
        self.vmin = v_start + v_diff * v_ratio[0]
        self.vmax = v_start + v_diff * v_ratio[1]
        
        pass
    
    def change_cmap(self):
        pass
    
    def show_pos(self, pos):
        p = self.plot_2_plotitem.vb.mapSceneToView(pos)
        self.crosshair[0].setPos(p.x())
        self.crosshair[1].setPos(p.y())
        string = 'X=' + format(p.x(), '.2e') + ' ' + 'Y=' + format(p.y(), '.2e')
        if self.isPlot:
            y_index = self.index[-2] + 2
            y_axis = self.y_axis[:y_index]
            if np.min(self.x_axis) <= p.x() <= np.max(self.x_axis) and np.min(y_axis) <= p.y() <= np.max(y_axis):
                x_index = (p.x() - self.x_axis[0]) / (self.x_axis[-1] - self.x_axis[0]) * (len(self.x_axis) - 1)
                y_index = (p.y() - y_axis[0]) / (y_axis[-1] - y_axis[0]) * (len(y_axis) - 1)
                x_index = round(x_index)
                y_index = round(y_index)
                z = self.data_2D[y_index, x_index]
                string += '    Z='+ format(z, '.2e')
                # print(p.x(), p.y(), z)
        self.pos_label.setText(string)
        
    
    def closeEvent(self, event):
        reply = QMessageBox.warning(self, "Warning", 'Are you sure to close?',+\
                                    QMessageBox.No | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()



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
        
        self.pbar_text = 'Remaining: calculating......'
        self.progress = 0
        
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
                elif self.loop_info[i]['MeterType'] == 'K2502_1':
                    self.loop_instruments.append(Keithley2502_Src_1(str(i), self.loop_info[i]['Address']))
                elif self.loop_info[i]['MeterType'] == 'K2502_2':
                    self.loop_instruments.append(Keithley2502_Src_2(str(i), self.loop_info[i]['Address']))
                elif self.loop_info[i]['MeterType'] == 'K6221':
                    self.loop_instruments.append(Keithley6221(str(i), self.loop_info[i]['Address']))
                elif self.loop_info[i]['MeterType'] == 'SR830':
                    self.loop_instruments.append(SR830(str(i), self.loop_info[i]['Address'], autorange = False))
                    
                self.loop_instruments[i]._STEP = self.loop_params[i]['InternalStep']
                self.loop_instruments[i]._INTER_DELAY = self.loop_params[i]['InternalDelay']
                self.value_list[i] = np.linspace(self.loop_params[i]['StartPoint'], self.loop_params[i]['EndPoint'], self.loop_params[i]['NumberOfPoints'])
            
                if self.loop_info[i]['MeterType'][:5] == 'K2502': #K2502 negtive output
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
                elif self.read_info[i]['MeterType'] == 'K2502_1':
                    self.read_instruments.append(Keithley2502_Src_1(str(i + self.loop_num), self.read_info[i]['Address']))
                elif self.read_info[i]['MeterType'] == 'K2502_2':
                    self.read_instruments.append(Keithley2502_Src_2(str(i + self.loop_num), self.read_info[i]['Address']))
                elif self.read_info[i]['MeterType'] == 'K6221':
                    self.read_instruments.append(Keithley6221(str(i + self.loop_num), self.read_info[i]['Address']))
                elif self.read_info[i]['MeterType'] == 'K2182':
                    self.read_instruments.append(Keithley2182(str(i + self.loop_num), self.read_info[i]['Address']))
                elif self.read_info[i]['MeterType'][:5] == 'SR830':
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
                qc.Instrument.close_all()
                print('Error! Start failed')
                return #正式运行必须要有这个
            
            # Startup check
            for i in range(self.loop_num): 
                if self.loop_info[i]['MeterType'][:5] == 'K2502': #check is K2502 error
                    if self.value_list[i][0] != -self.loop_params[i]['StartPoint'] or self.value_list[i][-1] != -self.loop_params[i]['EndPoint']:
                        self.error = True
                        print('K2502 negative output error!!!!!!')
                        return
                    if -80 < self.loop_params[i]['StartPoint'] < 80 and -80 < self.loop_params[i]['EndPoint'] < 80:
                        print('K2502 Range OK')
                    else:
                        print('K2502 Out of Range !!!!!!')
                    if self.loop_info[i]['Address'] == 'GPIB0::24::INSTR' or self.loop_info[i]['Address'] == 'GPIB0::23::INSTR':
                        print('K2502 Address OK')
                    else:
                        print('K2502 Address not matched !!!!!!')
                        return
                        
                elif self.loop_info[i]['MeterType'] == 'K2450': # Set 2450 Range
                    if -0.81 < self.loop_params[i]['StartPoint'] < 0.81 and -0.81 < self.loop_params[i]['EndPoint'] < 0.81:
                        print('K2450 Range OK')
                    else:
                        print('K2450 Out of Range !!!!!!')
                        return
                    if self.loop_info[i]['Address'] == 'GPIB0::18::INSTR':
                        print('K2450 Address OK')
                    else:
                        print('K2450 Address not matched !!!!!!')
                        return
                    
                elif self.loop_info[i]['MeterType'] == 'K2400': # Set 2400 Range
                    if -0.81 < self.loop_params[i]['StartPoint'] < 0.81 and -0.81 < self.loop_params[i]['EndPoint'] < 0.81:
                        print('K2400 Range OK')
                    else:
                        print('K2400 Out of Range !!!!!!')
                        return
                    if self.loop_info[i]['Address'] == 'GPIB0::25::INSTR':
                        print('K2400 Address OK')
                    else:
                        print('K2400 Address not matched !!!!!!')
                        return
            
            self.is_running = True     
            
            self.previous_value = np.zeros(self.loop_num)
            total_count = self.loop_params[0]['NumberOfPoints'] * self.loop_params[1]['NumberOfPoints'] * \
                          self.loop_params[2]['NumberOfPoints'] * self.loop_params[3]['NumberOfPoints']
            count = 0
            previous_count = 0
            
            curr = 0
            curr_count = 0
            temperature = 0
            
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
                    
                    # self.value_list[3] += 0.002
                    
                    for self.index[2] in range(len(self.value_list[2])):
                        self.check_pause_and_stop()
                        if self.is_stop: return
                        self.index[3] = 0 #For 1d plot usage
                        self.value[2] = self.value_list[2][self.index[2]]
                        self.loop_instruments[2].set_volt(self.previous_value[2], self.value[2])
                        self.previous_value[2] = self.value[2]
                        sleep(self.loop_params[2]['WaitTime'])
                        
                        # self.value[1] = -4 - 0.002*self.index[2]
                        # self.loop_instruments[1].set_volt(self.previous_value[1], self.value[1])
                        # self.previous_value[1] = self.value[1]
                        # sleep(self.loop_params[2]['WaitTime'])
                        
                        # self.value_list[3] -= 0.002
                        if count == 0:
                            time_stamp = time()
                        else:
                            delta_time = time() - time_stamp
                            time_stamp = time()
                            self.progress = int(count / total_count * 100)
                            time_remaining = delta_time * (total_count - count) / len(self.value_list[3]) / 60
                            hours = int(time_remaining / 60)
                            mins = round(time_remaining - hours * 60)
                            self.pbar_text = 'Remaining: ' + str(hours) + ' hs ' + str(mins) + ' mins'
                        
                        for self.index[3] in range(len(self.value_list[3])):
                            self.check_pause_and_stop()
                            if self.is_stop: return
                            self.value[3] = self.value_list[3][self.index[3]]
                            self.loop_instruments[3].set_volt(self.previous_value[3], self.value[3])
                            self.previous_value[3] = self.value[3]
                            
                            # self.value[2] = -4 - 0.0002*self.index[3]
                            # self.loop_instruments[2].set_volt(self.previous_value[2], self.value[2])
                            # self.previous_value[2] = self.value[2]
                            
                            sleep(self.loop_params[3]['WaitTime'])
                            
                            
                            
                            for i in range(self.read_num):
                                if self.read_info[i]['MeterType'] == 'K6221':
                                    self.read_instruments[i]._OUTPUT = self.read_instruments[i].delta_read()
                                elif self.read_info[i]['MeterType'] == 'SR830 X':
                                    self.read_instruments[i]._OUTPUT = self.read_instruments[i].X()
                                elif self.read_info[i]['MeterType'] == 'SR830 Y':
                                    self.read_instruments[i]._OUTPUT = self.read_instruments[i].Y()
                                elif self.read_info[i]['MeterType'] == 'SR830 R':
                                    self.read_instruments[i]._OUTPUT = self.read_instruments[i].R()
                                elif self.read_info[i]['MeterType'] == 'SR830 Theta':
                                    self.read_instruments[i]._OUTPUT = self.read_instruments[i].P()
                                elif self.read_info[i]['MeterType'] == 'K2450':
                                    self.read_instruments[i]._OUTPUT = self.read_instruments[i].curr()
                                elif self.read_info[i]['MeterType'] == 'K2400':
                                    self.read_instruments[i]._OUTPUT = self.read_instruments[i].curr()
                                elif self.read_info[i]['MeterType'][:5] == 'K2502':
                                    self.read_instruments[i]._OUTPUT = self.read_instruments[i].curr()
                                else:
                                   self.read_instruments[i]._OUTPUT = self.read_instruments[i].volt()
                                self.data_collected[self.index[0], self.index[1], self.index[2], self.index[3], i] = self.read_instruments[i]._OUTPUT * self.read_params[i]['Prefactor']
                            
                            if curr_count < 20:
                                curr_count += 1
                            else:
                                curr_count = 0
                                for i in range(self.loop_num):
                                    if self.loop_info[i]['MeterType'] == 'K2450':
                                        curr = self.loop_instruments[i].curr()
                                # temperature = self.probe.temperature()
                                
                            data_for_write = [temperature]
                            data_for_write += [self.value[i] for i in range(self.loop_num)]
                            data_for_write += list(self.data_collected[self.index[0], self.index[1], self.index[2], self.index[3], :])
                            data_for_write += [curr]
                            
                            # with open(self.filename, 'a') as file:
                            #     file.write(("\t".join(map(str, data_for_write))+"\n"))
                                
                            
                            count += 1
                            if count == total_count:
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

            self.pbar_text = ''
            self.progress = 0

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
        OUTPUT = (uniform(-1, 1))*1e7
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
        
        