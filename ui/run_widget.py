#!/usr/bin/env python3
"""
Run Widget for the MPGA GUI application.
Provides interface to run optimization jobs.
"""

import os
import json
import tempfile
#!/usr/bin/env python3
"""
Run Widget for the MPGA GUI application.
Provides interface to run optimization jobs.
"""

import os
import json
import tempfile
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QPushButton, QCheckBox,
                             QComboBox, QProgressBar, QTextEdit, QFileDialog,
                             QMessageBox, QGroupBox, QSplitter, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QProcess, QByteArray
from PyQt5.QtGui import QTextCursor

from core.runner import MPGARunner
from utils.constants import FOCUS_MODES, FILE_FILTERS


class MPGARunWidget(QWidget):
    """Widget for running optimization jobs"""

    # Signal emitted when a run completes successfully
    run_completed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setupUI()
        self.runner = None
        self.config_file = None
        self.auto_view = True
        
    def setupUI(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Input/Output group
        io_group = QGroupBox("Input/Output")
        io_layout = QFormLayout(io_group)
        
        # Input file selection
        input_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setReadOnly(True)
        self.input_path.textChanged.connect(self.update_run_button)
        self.input_browse_btn = QPushButton("Browse...")
        self.input_browse_btn.clicked.connect(self.browse_input)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(self.input_browse_btn)
        io_layout.addRow("Input Scheme:", input_layout)
        
        # Output file selection
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setReadOnly(True)
        self.output_path.textChanged.connect(self.update_run_button)
        self.output_browse_btn = QPushButton("Browse...")
        self.output_browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.output_browse_btn)
        io_layout.addRow("Output File:", output_layout)
        
        # Configuration file selection
        config_layout = QHBoxLayout()
        self.use_config_cb = QCheckBox("Use Configuration File")
        self.use_config_cb.setChecked(False)
        self.use_config_cb.stateChanged.connect(self.toggle_config_file)
        
        self.config_path = QLineEdit()
        self.config_path.setReadOnly(True)
        self.config_path.setEnabled(False)
        
        self.config_browse_btn = QPushButton("Browse...")
        self.config_browse_btn.clicked.connect(self.browse_config)
        self.config_browse_btn.setEnabled(False)
        
        config_layout.addWidget(self.use_config_cb)
        config_layout.addWidget(self.config_path)
        config_layout.addWidget(self.config_browse_btn)
        
        io_layout.addRow(config_layout)
        
        # Focus selection
        focus_layout = QHBoxLayout()
        self.focus_cb = QCheckBox("Use Focus Mode")
        self.focus_cb.setChecked(False)
        self.focus_cb.stateChanged.connect(self.toggle_focus)
        
        self.focus_combo = QComboBox()
        self.focus_combo.addItems(FOCUS_MODES)
        self.focus_combo.setEnabled(False)
        
        focus_layout.addWidget(self.focus_cb)
        focus_layout.addWidget(self.focus_combo)
        
        io_layout.addRow(focus_layout)
        
        # Auto-view results option
        auto_view_layout = QHBoxLayout()
        self.auto_view_cb = QCheckBox("Automatically view results when complete")
        self.auto_view_cb.setChecked(True)
        self.auto_view_cb.stateChanged.connect(self.toggle_auto_view)
        auto_view_layout.addWidget(self.auto_view_cb)
        auto_view_layout.addStretch()
        
        io_layout.addRow(auto_view_layout)
        
        layout.addWidget(io_group)
        
        # Run controls
        run_layout = QHBoxLayout()
        
        self.run_btn = QPushButton("Run Optimization")
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self.run_optimization)
        self.run_btn.setMinimumHeight(40)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_optimization)
        self.stop_btn.setMinimumHeight(40)
        
        run_layout.addWidget(self.run_btn)
        run_layout.addWidget(self.stop_btn)
        
        layout.addLayout(run_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Output log
        log_group = QGroupBox("Execution Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Results actions
        results_layout = QHBoxLayout()
        
        self.view_results_btn = QPushButton("View Results")
        self.view_results_btn.clicked.connect(self.view_results)
        self.view_results_btn.setEnabled(False)
        
        self.compare_results_btn = QPushButton("Add to Comparison")
        self.compare_results_btn.clicked.connect(self.add_to_comparison)
        self.compare_results_btn.setEnabled(False)
        
        self.clear_log_btn = QPushButton("Clear Log")
        self.clear_log_btn.clicked.connect(self.clear_log)
        
        results_layout.addWidget(self.view_results_btn)
        results_layout.addWidget(self.compare_results_btn)
        results_layout.addWidget(self.clear_log_btn)
        
        layout.addLayout(results_layout)
        
    def browse_input(self):
        """Browse for input scheme file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Input Scheme", "", "JSON Files (*.json);;All Files (*.*)")
            
        if file_path:
            self.input_path.setText(file_path)
            
            # Auto-suggest output file name
            if not self.output_path.text():
                dir_path = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                suggested_output = os.path.join(dir_path, f"{base_name}_result.geojson")
                self.output_path.setText(suggested_output)
                
    def browse_output(self):
        """Browse for output file location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Output To", "", "GeoJSON Files (*.geojson);;All Files (*.*)")
            
        if file_path:
            # Add .geojson extension if not present
            if not file_path.lower().endswith(('.geojson')):
                file_path += '.geojson'
            self.output_path.setText(file_path)
            
    def browse_config(self):
        """Browse for configuration file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Configuration File", "", "JSON Files (*.json);;All Files (*.*)")
            
        if file_path:
            self.config_path.setText(file_path)
            self.config_file = file_path
            
    def toggle_config_file(self, state):
        """Toggle configuration file selection"""
        self.config_path.setEnabled(state == Qt.Checked)
        self.config_browse_btn.setEnabled(state == Qt.Checked)
        
        if state != Qt.Checked:
            self.config_path.clear()
            self.config_file = None
            
    def toggle_focus(self, state):
        """Toggle focus mode selection"""
        self.focus_combo.setEnabled(state == Qt.Checked)
        
    def toggle_auto_view(self, state):
        """Toggle auto view results"""
        self.auto_view = state == Qt.Checked
            
    def update_run_button(self):
        """Update the state of the run button"""
        self.run_btn.setEnabled(bool(self.input_path.text()) and bool(self.output_path.text()))
        
    def get_config(self):
        """Get current configuration from parent if available"""
        if hasattr(self.parent, 'get_active_config'):
            return self.parent.get_active_config()
        return None
        
    def run_optimization(self):
        """Run optimization with selected parameters"""
        # Check if files exist
        if not self.input_path.text():
            QMessageBox.warning(self, "Error", "Please select an input file.")
            return
            
        if not self.output_path.text():
            QMessageBox.warning(self, "Error", "Please select an output file.")
            return
            
        # Get configuration
        config_file = None
        if self.use_config_cb.isChecked():
            if self.config_path.text():
                config_file = self.config_path.text()
            else:
                # Get config from parent and save to temporary file
                config = self.get_config()
                if config:
                    fd, temp_file = tempfile.mkstemp(suffix='.json')
                    with os.fdopen(fd, 'w') as f:
                        json.dump(config, f, indent=2)
                    config_file = temp_file
                else:
                    QMessageBox.warning(self, "Error", "No configuration available.")
                    return
                    
        # Get focus mode
        focus = None
        if self.focus_cb.isChecked():
            focus = self.focus_combo.currentText()
            
        # Disable controls
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.input_browse_btn.setEnabled(False)
        self.output_browse_btn.setEnabled(False)
        self.config_browse_btn.setEnabled(False)
        self.use_config_cb.setEnabled(False)
        self.focus_cb.setEnabled(False)
        self.focus_combo.setEnabled(False)
        
        # Clear log
        self.log_text.clear()
        
        # Reset progress bar
        self.progress_bar.setValue(0)
        
        # Create and start the runner
        from utils.constants import get_executable_path
        executable = get_executable_path()
        
        self.runner = MPGARunner(
            executable_path=executable,
            input_file=self.input_path.text(),
            output_file=self.output_path.text(),
            config_file=config_file,
            focus=focus
        )
        
        self.runner.progress_update.connect(self.update_log)
        self.runner.progress_value.connect(self.update_progress)
        self.runner.finished_with_result.connect(self.handle_results)
        
        self.runner.start()
        
        # Add initial log entry
        self.update_log("Starting optimization...")
        
    def stop_optimization(self):
        """Stop the running optimization"""
        if self.runner and self.runner.isRunning():
            reply = QMessageBox.question(
                self, "Confirm Stop",
                "Are you sure you want to stop the optimization?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.update_log("Stopping optimization...")
                self.runner.stop()
                
    def update_log(self, text):
        """Add a message to the log"""
        self.log_text.append(text)
        # Scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
        
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)
        
    def optimization_finished(self):
        """Called when the optimization is finished"""
        # Re-enable controls
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.input_browse_btn.setEnabled(True)
        self.output_browse_btn.setEnabled(True)
        self.config_browse_btn.setEnabled(self.use_config_cb.isChecked())
        self.use_config_cb.setEnabled(True)
        self.focus_cb.setEnabled(True)
        self.focus_combo.setEnabled(self.focus_cb.isChecked())
        
        # Set progress to 100%
        self.progress_bar.setValue(100)
        
    def handle_results(self, success, error_message, output_file):
        """Handle the results of the optimization"""
        # First call optimization_finished to re-enable controls
        self.optimization_finished()
        
        if success:
            self.update_log("Optimization completed successfully!")
            self.view_results_btn.setEnabled(True)
            self.compare_results_btn.setEnabled(True)
            
            if self.auto_view_cb.isChecked():
                # Use a timer to allow the GUI to update first
                QTimer.singleShot(500, self.view_results)
        else:
            self.update_log(f"Optimization failed: {error_message}")
            self.view_results_btn.setEnabled(False)
            self.compare_results_btn.setEnabled(False)
            
    def view_results(self):
        """Signal to the parent to view the results"""
        if not os.path.exists(self.output_path.text()):
            QMessageBox.warning(self, "Error", "Output file does not exist.")
            return
            
        self.run_completed.emit(self.output_path.text())
        
    def add_to_comparison(self):
        """Signal to the parent to add results to comparison"""
        if not os.path.exists(self.output_path.text()):
            QMessageBox.warning(self, "Error", "Output file does not exist.")
            return
            
        if hasattr(self.parent, 'add_to_comparison'):
            self.parent.add_to_comparison(self.output_path.text())
            
    def clear_log(self):
        """Clear the log text"""
        self.log_text.clear()
