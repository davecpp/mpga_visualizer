#!/usr/bin/env python3
"""
Configuration widget module for the MPGA GUI application.
Provides a UI for configuring optimization parameters.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QTabWidget, QGroupBox, QLabel, QLineEdit, 
                            QPushButton, QCheckBox, QComboBox, QSpinBox,
                            QDoubleSpinBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal

from utils.constants import DEFAULT_CONFIG, FILE_FILTERS
from core.data_loader import load_config, save_config

class MPGAConfigWidget(QWidget):
    """Widget for configuring the optimization parameters"""
    
    # Signal emitted when configuration changes
    config_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_config = DEFAULT_CONFIG.copy()
        self.setupUI()
        self.load_config_to_ui()
        
    def setupUI(self):
        """Set up the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create tabs for different config sections
        self.tabs = QTabWidget()
        
        # GA tab
        ga_tab = QWidget()
        ga_layout = QFormLayout(ga_tab)
        
        # Population settings
        self.pop_size = QSpinBox()
        self.pop_size.setRange(10, 1000)
        self.pop_size.setSingleStep(10)
        self.pop_size.valueChanged.connect(self.on_value_changed)
        ga_layout.addRow("Population Size:", self.pop_size)
        
        self.max_iterations = QSpinBox()
        self.max_iterations.setRange(10, 1000)
        self.max_iterations.setSingleStep(10)
        self.max_iterations.valueChanged.connect(self.on_value_changed)
        ga_layout.addRow("Max Iterations:", self.max_iterations)
        
        self.convergence_threshold = QDoubleSpinBox()
        self.convergence_threshold.setRange(0.0001, 0.1)
        self.convergence_threshold.setSingleStep(0.001)
        self.convergence_threshold.setDecimals(4)
        self.convergence_threshold.valueChanged.connect(self.on_value_changed)
        ga_layout.addRow("Convergence Threshold:", self.convergence_threshold)
        
        self.filter_coefficient = QDoubleSpinBox()
        self.filter_coefficient.setRange(0.1, 0.9)
        self.filter_coefficient.setSingleStep(0.05)
        self.filter_coefficient.setDecimals(2)
        self.filter_coefficient.valueChanged.connect(self.on_value_changed)
        ga_layout.addRow("Filter Coefficient:", self.filter_coefficient)
        
        self.mutation_probability = QDoubleSpinBox()
        self.mutation_probability.setRange(0.01, 0.5)
        self.mutation_probability.setSingleStep(0.01)
        self.mutation_probability.setDecimals(2)
        self.mutation_probability.valueChanged.connect(self.on_value_changed)
        ga_layout.addRow("Mutation Probability:", self.mutation_probability)
        
        # Specialized populations
        self.use_specialized_pops = QCheckBox()
        self.use_specialized_pops.stateChanged.connect(self.on_value_changed)
        ga_layout.addRow("Use Specialized Populations:", self.use_specialized_pops)
        
        self.specialized_evolutions = QSpinBox()
        self.specialized_evolutions.setRange(5, 100)
        self.specialized_evolutions.setSingleStep(5)
        self.specialized_evolutions.valueChanged.connect(self.on_value_changed)
        ga_layout.addRow("Specialized Evolutions:", self.specialized_evolutions)
        
        self.specialized_best_percentage = QDoubleSpinBox()
        self.specialized_best_percentage.setRange(0.05, 0.5)
        self.specialized_best_percentage.setSingleStep(0.05)
        self.specialized_best_percentage.setDecimals(2)
        self.specialized_best_percentage.valueChanged.connect(self.on_value_changed)
        ga_layout.addRow("Specialized Best %:", self.specialized_best_percentage)
        
        self.specialized_random_percentage = QDoubleSpinBox()
        self.specialized_random_percentage.setRange(0.01, 0.2)
        self.specialized_random_percentage.setSingleStep(0.01)
        self.specialized_random_percentage.setDecimals(2)
        self.specialized_random_percentage.valueChanged.connect(self.on_value_changed)
        ga_layout.addRow("Specialized Random %:", self.specialized_random_percentage)
        
        # DRC settings
        self.drc_filter_percentage = QDoubleSpinBox()
        self.drc_filter_percentage.setRange(0.05, 0.3)
        self.drc_filter_percentage.setSingleStep(0.05)
        self.drc_filter_percentage.setDecimals(2)
        self.drc_filter_percentage.valueChanged.connect(self.on_value_changed)
        ga_layout.addRow("DRC Filter %:", self.drc_filter_percentage)
        
        self.drc_check_interval = QSpinBox()
        self.drc_check_interval.setRange(1, 50)
        self.drc_check_interval.setSingleStep(1)
        self.drc_check_interval.valueChanged.connect(self.on_value_changed)
        ga_layout.addRow("DRC Check Interval:", self.drc_check_interval)
        
        # Fitness tab
        fitness_tab = QWidget()
        fitness_layout = QVBoxLayout(fitness_tab)
        
        # Weights group
        weights_group = QGroupBox("Fitness Weights")
        weights_layout = QFormLayout(weights_group)
        
        self.weight_wire_length = QDoubleSpinBox()
        self.weight_wire_length.setRange(0.0, 5.0)
        self.weight_wire_length.setSingleStep(0.1)
        self.weight_wire_length.setDecimals(1)
        self.weight_wire_length.valueChanged.connect(self.on_value_changed)
        weights_layout.addRow("Wire Length:", self.weight_wire_length)
        
        self.weight_thermal = QDoubleSpinBox()
        self.weight_thermal.setRange(0.0, 5.0)
        self.weight_thermal.setSingleStep(0.1)
        self.weight_thermal.setDecimals(1)
        self.weight_thermal.valueChanged.connect(self.on_value_changed)
        weights_layout.addRow("Thermal:", self.weight_thermal)
        
        self.weight_drc = QDoubleSpinBox()
        self.weight_drc.setRange(0.0, 5.0)
        self.weight_drc.setSingleStep(0.1)
        self.weight_drc.setDecimals(1)
        self.weight_drc.valueChanged.connect(self.on_value_changed)
        weights_layout.addRow("DRC:", self.weight_drc)
        
        self.weight_power = QDoubleSpinBox()
        self.weight_power.setRange(0.0, 5.0)
        self.weight_power.setSingleStep(0.1)
        self.weight_power.setDecimals(1)
        self.weight_power.valueChanged.connect(self.on_value_changed)
        weights_layout.addRow("Power:", self.weight_power)
        
        self.weight_parasitic = QDoubleSpinBox()
        self.weight_parasitic.setRange(0.0, 5.0)
        self.weight_parasitic.setSingleStep(0.1)
        self.weight_parasitic.setDecimals(1)
        self.weight_parasitic.valueChanged.connect(self.on_value_changed)
        weights_layout.addRow("Parasitic:", self.weight_parasitic)
        
        fitness_layout.addWidget(weights_group)
        
        # Thermal model group
        thermal_group = QGroupBox("Thermal Model")
        thermal_layout = QFormLayout(thermal_group)
        
        self.thermal_max_temp = QDoubleSpinBox()
        self.thermal_max_temp.setRange(50.0, 200.0)
        self.thermal_max_temp.setSingleStep(5.0)
        self.thermal_max_temp.setDecimals(1)
        self.thermal_max_temp.valueChanged.connect(self.on_value_changed)
        thermal_layout.addRow("Max Allowed Temp:", self.thermal_max_temp)
        
        self.thermal_ambient_temp = QDoubleSpinBox()
        self.thermal_ambient_temp.setRange(10.0, 40.0)
        self.thermal_ambient_temp.setSingleStep(1.0)
        self.thermal_ambient_temp.setDecimals(1)
        self.thermal_ambient_temp.valueChanged.connect(self.on_value_changed)
        thermal_layout.addRow("Ambient Temp:", self.thermal_ambient_temp)
        
        self.thermal_conductivity = QDoubleSpinBox()
        self.thermal_conductivity.setRange(50.0, 500.0)
        self.thermal_conductivity.setSingleStep(10.0)
        self.thermal_conductivity.setDecimals(1)
        self.thermal_conductivity.valueChanged.connect(self.on_value_changed)
        thermal_layout.addRow("Thermal Conductivity:", self.thermal_conductivity)
        
        self.thermal_power_density = QDoubleSpinBox()
        self.thermal_power_density.setRange(0.01, 1.0)
        self.thermal_power_density.setSingleStep(0.01)
        self.thermal_power_density.setDecimals(2)
        self.thermal_power_density.valueChanged.connect(self.on_value_changed)
        thermal_layout.addRow("Power Density:", self.thermal_power_density)
        
        fitness_layout.addWidget(thermal_group)
        
        # Power model group
        power_group = QGroupBox("Power Model")
        power_layout = QFormLayout(power_group)
        
        self.power_cell_power = QDoubleSpinBox()
        self.power_cell_power.setRange(0.01, 1.0)
        self.power_cell_power.setSingleStep(0.01)
        self.power_cell_power.setDecimals(2)
        self.power_cell_power.valueChanged.connect(self.on_value_changed)
        power_layout.addRow("Cell Power:", self.power_cell_power)
        
        self.power_wire_capacitance = QDoubleSpinBox()
        self.power_wire_capacitance.setRange(0.001, 0.1)
        self.power_wire_capacitance.setSingleStep(0.001)
        self.power_wire_capacitance.setDecimals(3)
        self.power_wire_capacitance.valueChanged.connect(self.on_value_changed)
        power_layout.addRow("Wire Capacitance:", self.power_wire_capacitance)
        
        self.power_voltage_factor = QDoubleSpinBox()
        self.power_voltage_factor.setRange(0.1, 2.0)
        self.power_voltage_factor.setSingleStep(0.1)
        self.power_voltage_factor.setDecimals(1)
        self.power_voltage_factor.valueChanged.connect(self.on_value_changed)
        power_layout.addRow("Voltage Factor:", self.power_voltage_factor)
        
        self.power_frequency = QDoubleSpinBox()
        self.power_frequency.setRange(0.1, 10.0)
        self.power_frequency.setSingleStep(0.1)
        self.power_frequency.setDecimals(1)
        self.power_frequency.valueChanged.connect(self.on_value_changed)
        power_layout.addRow("Frequency:", self.power_frequency)
        
        self.power_leakage_factor = QDoubleSpinBox()
        self.power_leakage_factor.setRange(0.01, 0.5)
        self.power_leakage_factor.setSingleStep(0.01)
        self.power_leakage_factor.setDecimals(2)
        self.power_leakage_factor.valueChanged.connect(self.on_value_changed)
        power_layout.addRow("Leakage Factor:", self.power_leakage_factor)
        
        fitness_layout.addWidget(power_group)
        
        # DRC tab
        drc_tab = QWidget()
        drc_layout = QFormLayout(drc_tab)
        
        self.drc_min_distance = QSpinBox()
        self.drc_min_distance.setRange(1, 10)
        self.drc_min_distance.setSingleStep(1)
        self.drc_min_distance.valueChanged.connect(self.on_value_changed)
        drc_layout.addRow("Min Distance:", self.drc_min_distance)
        
        self.drc_overlap_penalty = QDoubleSpinBox()
        self.drc_overlap_penalty.setRange(1.0, 50.0)
        self.drc_overlap_penalty.setSingleStep(1.0)
        self.drc_overlap_penalty.setDecimals(1)
        self.drc_overlap_penalty.valueChanged.connect(self.on_value_changed)
        drc_layout.addRow("Overlap Penalty:", self.drc_overlap_penalty)
        
        self.drc_distance_penalty = QDoubleSpinBox()
        self.drc_distance_penalty.setRange(1.0, 20.0)
        self.drc_distance_penalty.setSingleStep(0.5)
        self.drc_distance_penalty.setDecimals(1)
        self.drc_distance_penalty.valueChanged.connect(self.on_value_changed)
        drc_layout.addRow("Distance Penalty:", self.drc_distance_penalty)
        
        # Add tabs
        self.tabs.addTab(ga_tab, "Genetic Algorithm")
        self.tabs.addTab(fitness_tab, "Fitness Parameters")
        self.tabs.addTab(drc_tab, "DRC Parameters")
        
        # Add the tabs to the main layout
        main_layout.addWidget(self.tabs)
        
        # Add configuration file controls
        file_layout = QHBoxLayout()
        
        self.load_config_btn = QPushButton("Load Config...")
        self.load_config_btn.clicked.connect(self.load_config_from_file)
        
        self.save_config_btn = QPushButton("Save Config...")
        self.save_config_btn.clicked.connect(self.save_config_to_file)
        
        self.reset_defaults_btn = QPushButton("Reset to Defaults")
        self.reset_defaults_btn.clicked.connect(self.reset_to_defaults)
        
        file_layout.addWidget(self.load_config_btn)
        file_layout.addWidget(self.save_config_btn)
        file_layout.addWidget(self.reset_defaults_btn)
        
        main_layout.addLayout(file_layout)
        
    def load_config_to_ui(self):
        """Load current configuration values to UI controls"""
        # GA parameters
        ga = self.current_config.get('ga', {})
        self.pop_size.setValue(ga.get('population_size', 100))
        self.max_iterations.setValue(ga.get('max_iterations', 200))
        self.convergence_threshold.setValue(ga.get('convergence_threshold', 0.001))
        self.filter_coefficient.setValue(ga.get('filter_coefficient', 0.4))
        self.mutation_probability.setValue(ga.get('mutation_probability', 0.1))
        self.drc_filter_percentage.setValue(ga.get('drc_filter_percentage', 0.1))
        self.drc_check_interval.setValue(ga.get('drc_check_interval', 10))
        self.use_specialized_pops.setChecked(ga.get('use_specialized_populations', True))
        self.specialized_evolutions.setValue(ga.get('specialized_evolutions', 20))
        self.specialized_best_percentage.setValue(ga.get('specialized_best_percentage', 0.2))
        self.specialized_random_percentage.setValue(ga.get('specialized_random_percentage', 0.05))
        
        # Fitness weights
        weights = self.current_config.get('fitness', {}).get('weights', {})
        self.weight_wire_length.setValue(weights.get('wire_length', 1.0))
        self.weight_thermal.setValue(weights.get('thermal', 0.5))
        self.weight_drc.setValue(weights.get('drc', 2.0))
        self.weight_power.setValue(weights.get('power', 0.3))
        self.weight_parasitic.setValue(weights.get('parasitic', 0.2))
        
        # Thermal parameters
        thermal = self.current_config.get('fitness', {}).get('thermal', {})
        self.thermal_max_temp.setValue(thermal.get('max_allowed_temp', 100.0))
        self.thermal_ambient_temp.setValue(thermal.get('ambient_temp', 25.0))
        self.thermal_conductivity.setValue(thermal.get('thermal_conductivity', 150.0))
        self.thermal_power_density.setValue(thermal.get('power_density', 0.1))
        
        # Power parameters
        power = self.current_config.get('fitness', {}).get('power', {})
        self.power_cell_power.setValue(power.get('cell_power', 0.1))
        self.power_wire_capacitance.setValue(power.get('wire_capacitance', 0.02))
        self.power_voltage_factor.setValue(power.get('voltage_factor', 1.0))
        self.power_frequency.setValue(power.get('frequency', 1.0))
        self.power_leakage_factor.setValue(power.get('leakage_factor', 0.05))
        
        # DRC parameters
        drc = self.current_config.get('drc', {})
        self.drc_min_distance.setValue(drc.get('min_distance', 2))
        self.drc_overlap_penalty.setValue(drc.get('overlap_penalty', 10.0))
        self.drc_distance_penalty.setValue(drc.get('distance_penalty', 5.0))
        
    def update_config_from_ui(self):
        """Update configuration from UI controls"""
        # GA parameters
        self.current_config['ga'] = {
            'population_size': self.pop_size.value(),
            'max_iterations': self.max_iterations.value(),
            'convergence_threshold': self.convergence_threshold.value(),
            'filter_coefficient': self.filter_coefficient.value(),
            'mutation_probability': self.mutation_probability.value(),
            'drc_filter_percentage': self.drc_filter_percentage.value(),
            'drc_check_interval': self.drc_check_interval.value(),
            'use_specialized_populations': self.use_specialized_pops.isChecked(),
            'specialized_evolutions': self.specialized_evolutions.value(),
            'specialized_best_percentage': self.specialized_best_percentage.value(),
            'specialized_random_percentage': self.specialized_random_percentage.value()
        }
        
        # Fitness parameters
        if 'fitness' not in self.current_config:
            self.current_config['fitness'] = {}
            
        self.current_config['fitness']['weights'] = {
            'wire_length': self.weight_wire_length.value(),
            'thermal': self.weight_thermal.value(),
            'drc': self.weight_drc.value(),
            'power': self.weight_power.value(),
            'parasitic': self.weight_parasitic.value()
        }
        
        self.current_config['fitness']['thermal'] = {
            'max_allowed_temp': self.thermal_max_temp.value(),
            'ambient_temp': self.thermal_ambient_temp.value(),
            'thermal_conductivity': self.thermal_conductivity.value(),
            'power_density': self.thermal_power_density.value()
        }
        
        self.current_config['fitness']['power'] = {
            'cell_power': self.power_cell_power.value(),
            'wire_capacitance': self.power_wire_capacitance.value(),
            'voltage_factor': self.power_voltage_factor.value(),
            'frequency': self.power_frequency.value(),
            'leakage_factor': self.power_leakage_factor.value()
        }
        
        # DRC parameters
        self.current_config['drc'] = {
            'min_distance': self.drc_min_distance.value(),
            'overlap_penalty': self.drc_overlap_penalty.value(),
            'distance_penalty': self.drc_distance_penalty.value()
        }
        
        # Emit signal that config has changed
        self.config_changed.emit(self.current_config)
        
        return self.current_config
        
    def on_value_changed(self):
        """Handler for value changes in UI controls"""
        # Only update if not currently loading config
        if hasattr(self, 'loading_config') and self.loading_config:
            return
        self.update_config_from_ui()
        
    def load_config_from_file(self):
        """Load configuration from a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Configuration File", "", FILE_FILTERS["config"])
            
        if file_path:
            config = load_config(file_path)
            if config:
                # Set flag to prevent multiple updates while loading
                self.loading_config = True
                
                self.current_config = config
                self.load_config_to_ui()
                
                # Clear flag
                self.loading_config = False
                
                # Emit signal that config has changed
                self.config_changed.emit(self.current_config)
                
                QMessageBox.information(self, "Success", f"Configuration loaded from {file_path}")
            else:
                QMessageBox.warning(self, "Error", f"Failed to load configuration from {file_path}")
                
    def save_config_to_file(self):
        """Save configuration to a file"""
        self.update_config_from_ui()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration File", "", FILE_FILTERS["config"])
            
        if file_path:
            success = save_config(self.current_config, file_path)
            if success:
                QMessageBox.information(self, "Success", f"Configuration saved to {file_path}")
            else:
                QMessageBox.warning(self, "Error", f"Failed to save configuration to {file_path}")
                
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Reset Configuration")
        msg_box.setText("Are you sure you want to reset all configuration values to defaults?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            # Set flag to prevent multiple updates while loading
            self.loading_config = True
            
            self.current_config = DEFAULT_CONFIG.copy()
            self.load_config_to_ui()
            
            # Clear flag
            self.loading_config = False
            
            # Emit signal that config has changed
            self.config_changed.emit(self.current_config)
        
    def get_config(self):
        """Get current configuration"""
        return self.update_config_from_ui()
