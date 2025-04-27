#!/usr/bin/env python3
"""
Main Window for the MPGA GUI application.
Main application window that integrates all widgets.
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QTabWidget, QVBoxLayout,
                            QAction, QMenu, QToolBar, QStatusBar, QMessageBox,
                            QFileDialog, QDialog, QLabel, QComboBox, QPushButton,
                            QHBoxLayout, QFormLayout, QApplication, QSizePolicy)
from PyQt5.QtCore import Qt, QSettings, QSize, QTimer, QByteArray
from PyQt5.QtGui import QIcon, QPalette, QColor

from ui.config_widget import MPGAConfigWidget
from ui.run_widget import MPGARunWidget
from ui.visualizer import MPGAVisualizerWidget
from ui.comparison_widget import MPGAComparisonWidget
from utils.constants import APP_NAME, APP_VERSION, APP_ORGANIZATION, APP_DOMAIN, COLOR_SCHEMES


class ThemeDialog(QDialog):
    """Dialog for selecting application theme"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Select Theme")
        self.resize(300, 150)
        
        layout = QVBoxLayout(self)
        
        # Theme selector
        form_layout = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(COLOR_SCHEMES.keys()))
        
        # Get current theme
        settings = QSettings(APP_ORGANIZATION, APP_NAME)
        current_theme = settings.value("theme", "dark")
        self.theme_combo.setCurrentText(current_theme)
        
        form_layout.addRow("Theme:", self.theme_combo)
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def get_selected_theme(self):
        """Get the selected theme"""
        return self.theme_combo.currentText()


class MPGAMainWindow(QMainWindow):
    """Main window for the MPGA GUI application"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(900, 700)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create tabs widget with fixed size policy for each tab
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)  # Position tabs at the top
        self.tabs.setDocumentMode(True)  # More compact display mode
        
        # Prevent size changes when switching tabs
        self.tabs.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widgets
        self.run_widget = MPGARunWidget(self)
        self.config_widget = MPGAConfigWidget(self)
        self.visualizer_widget = MPGAVisualizerWidget(self)
        self.comparison_widget = MPGAComparisonWidget(self)
        
        # Set size policy for each tab widget
        for widget in [self.run_widget, self.config_widget, self.visualizer_widget, self.comparison_widget]:
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add tabs
        self.tabs.addTab(self.run_widget, "Run Optimization")
        self.tabs.addTab(self.config_widget, "Configuration")
        self.tabs.addTab(self.visualizer_widget, "Visualize Results")
        self.tabs.addTab(self.comparison_widget, "Compare Results")
        
        # Connect tab change handler
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Main layout
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabs)
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Set up menu bar
        self.setup_menu()
        
        # Set up toolbar
        self.setup_toolbar()
        
        # Connect signals and slots
        self.connect_signals()
        
        # Load application settings
        self.load_settings()
        
        # Apply theme
        self.apply_theme()
        
    def setup_menu(self):
        """Set up the application menu bar"""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        # File -> Open Input Scheme
        self.open_action = QAction("&Open Input Scheme...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.run_widget.browse_input)
        file_menu.addAction(self.open_action)
        
        # File -> Load Configuration
        self.load_config_action = QAction("Load &Configuration...", self)
        self.load_config_action.setShortcut("Ctrl+L")
        self.load_config_action.triggered.connect(self.config_widget.load_config_from_file)
        file_menu.addAction(self.load_config_action)
        
        # File -> Save Configuration
        self.save_config_action = QAction("&Save Configuration...", self)
        self.save_config_action.setShortcut("Ctrl+S")
        self.save_config_action.triggered.connect(self.config_widget.save_config_to_file)
        file_menu.addAction(self.save_config_action)
        
        file_menu.addSeparator()
        
        # File -> Open Results
        self.open_results_action = QAction("Open Results File...", self)
        self.open_results_action.setShortcut("Ctrl+R")
        self.open_results_action.triggered.connect(self.open_results)
        file_menu.addAction(self.open_results_action)
        
        file_menu.addSeparator()
        
        # File -> Exit
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        
        # Edit -> Preferences
        self.preferences_action = QAction("&Preferences...", self)
        self.preferences_action.triggered.connect(self.show_preferences)
        edit_menu.addAction(self.preferences_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("&View")
        
        # View -> Run Tab
        self.run_tab_action = QAction("&Run Tab", self)
        self.run_tab_action.setShortcut("Ctrl+1")
        self.run_tab_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction(self.run_tab_action)
        
        # View -> Configuration Tab
        self.config_tab_action = QAction("&Configuration Tab", self)
        self.config_tab_action.setShortcut("Ctrl+2")
        self.config_tab_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        view_menu.addAction(self.config_tab_action)
        
        # View -> Visualizer Tab
        self.visualizer_tab_action = QAction("&Visualizer Tab", self)
        self.visualizer_tab_action.setShortcut("Ctrl+3")
        self.visualizer_tab_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        view_menu.addAction(self.visualizer_tab_action)
        
        # View -> Comparison Tab
        self.comparison_tab_action = QAction("&Comparison Tab", self)
        self.comparison_tab_action.setShortcut("Ctrl+4")
        self.comparison_tab_action.triggered.connect(lambda: self.tabs.setCurrentIndex(3))
        view_menu.addAction(self.comparison_tab_action)
        
        view_menu.addSeparator()
        
        # View -> Reset Layout
        self.reset_layout_action = QAction("Reset &Layout", self)
        self.reset_layout_action.triggered.connect(self.reset_layout)
        view_menu.addAction(self.reset_layout_action)
        
        # View -> Change Theme
        self.change_theme_action = QAction("Change &Theme...", self)
        self.change_theme_action.triggered.connect(self.change_theme)
        view_menu.addAction(self.change_theme_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        # Help -> About
        self.about_action = QAction("&About", self)
        self.about_action.triggered.connect(self.show_about)
        help_menu.addAction(self.about_action)
        
    def setup_toolbar(self):
        """Set up the application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Add Run Optimization action
        run_action = QAction("Run Optimization", self)
        run_action.triggered.connect(lambda: self.run_widget.run_optimization())
        toolbar.addAction(run_action)
        
        # Add View Results action
        view_action = QAction("View Results", self)
        view_action.triggered.connect(lambda: self.tabs.setCurrentWidget(self.visualizer_widget))
        toolbar.addAction(view_action)
        
        # Add Compare Results action
        compare_action = QAction("Compare Results", self)
        compare_action.triggered.connect(lambda: self.tabs.setCurrentWidget(self.comparison_widget))
        toolbar.addAction(compare_action)
        
        # Add Config action
        config_action = QAction("Configuration", self)
        config_action.triggered.connect(lambda: self.tabs.setCurrentWidget(self.config_widget))
        toolbar.addAction(config_action)
        
    def connect_signals(self):
        """Connect signals and slots between widgets"""
        # When config changes in config_widget, update the run_widget
        self.config_widget.config_changed.connect(self.config_changed)
        
        # When run completes, show visualization
        self.run_widget.run_completed.connect(self.show_visualization)
        
    def load_settings(self):
        """Load application settings"""
        settings = QSettings(APP_ORGANIZATION, APP_NAME)
        
        # Window geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
        # Window state
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
            
        # Last tab index
        last_tab = settings.value("lastTab", 0, type=int)
        if 0 <= last_tab < self.tabs.count():
            self.tabs.setCurrentIndex(last_tab)
        
    def save_settings(self):
        """Save application settings"""
        settings = QSettings(APP_ORGANIZATION, APP_NAME)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("lastTab", self.tabs.currentIndex())
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Save settings
        self.save_settings()
        event.accept()
        
    def apply_theme(self):
        """Apply the current theme to the application"""
        settings = QSettings(APP_ORGANIZATION, APP_NAME)
        theme_name = settings.value("theme", "dark")
        
        if theme_name in COLOR_SCHEMES:
            theme = COLOR_SCHEMES[theme_name]
            
            # Create palette
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(*theme["window"]))
            palette.setColor(QPalette.WindowText, QColor(*theme["window_text"]))
            palette.setColor(QPalette.Base, QColor(*theme["base"]))
            palette.setColor(QPalette.AlternateBase, QColor(*theme["alt_base"]))
            palette.setColor(QPalette.ToolTipBase, QColor(*theme["tooltip_base"]))
            palette.setColor(QPalette.ToolTipText, QColor(*theme["tooltip_text"]))
            palette.setColor(QPalette.Text, QColor(*theme["text"]))
            palette.setColor(QPalette.Button, QColor(*theme["button"]))
            palette.setColor(QPalette.ButtonText, QColor(*theme["button_text"]))
            palette.setColor(QPalette.BrightText, QColor(*theme["bright_text"]))
            palette.setColor(QPalette.Link, QColor(*theme["link"]))
            palette.setColor(QPalette.Highlight, QColor(*theme["highlight"]))
            palette.setColor(QPalette.HighlightedText, QColor(*theme["highlighted_text"]))
            
            # Apply the palette
            QApplication.setPalette(palette)
        
    def show_preferences(self):
        """Show preferences dialog"""
        self.change_theme()
        
    def change_theme(self):
        """Show theme selection dialog"""
        dialog = ThemeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            theme_name = dialog.get_selected_theme()
            
            # Save the setting
            settings = QSettings(APP_ORGANIZATION, APP_NAME)
            settings.setValue("theme", theme_name)
            
            # Apply the theme
            self.apply_theme()
            
            # Notify user
            self.statusBar().showMessage(f"Theme changed to {theme_name}", 3000)
        
    def reset_layout(self):
        """Reset window layout to default"""
        settings = QSettings(APP_ORGANIZATION, APP_NAME)
        settings.remove("geometry")
        settings.remove("windowState")
        
        # Reset window size and position
        self.resize(900, 700)
        self.move(100, 100)
        
        # Reset toolbar and dock widgets
        self.restoreState(QByteArray())
        
        # Notify user
        self.statusBar().showMessage("Layout reset to default", 3000)
        
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
        <h2>{APP_NAME} v{APP_VERSION}</h2>
        <p>A GUI for running and visualizing integrated circuit placement optimization.</p>
        <p>This application provides:</p>
        <ul>
            <li>Configuration management for optimization parameters</li>
            <li>A simple interface for running optimization jobs</li>
            <li>Interactive visualization of placement results</li>
            <li>Comparison tools for multiple placement strategies</li>
        </ul>
        """
        
        QMessageBox.about(self, "About", about_text)
        
    def get_active_config(self):
        """Get the active configuration from the config widget"""
        return self.config_widget.get_config()
        
    def config_changed(self, config):
        """Handle configuration changes"""
        # Just update the status for now
        self.statusBar().showMessage("Configuration updated", 3000)
        
    def open_results(self):
        """Open a results file for visualization"""
        from utils.constants import FILE_FILTERS
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Results File", "", FILE_FILTERS["geojson"])
            
        if file_path:
            self.show_visualization(file_path)
            
    def show_visualization(self, file_path):
        """Show visualization for a results file"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", f"File not found: {file_path}")
            return
            
        # Switch to visualizer tab
        self.tabs.setCurrentWidget(self.visualizer_widget)
        
        # Load the file in the visualizer
        self.visualizer_widget.load_and_visualize(file_path)
        
        # Update status
        self.statusBar().showMessage(f"Loaded: {file_path}", 3000)
        
    def add_to_comparison(self, file_path):
        """Add a file to the comparison"""
        # Switch to comparison tab
        self.tabs.setCurrentWidget(self.comparison_widget)
        
        # Add the file
        self.comparison_widget.add_placement(file_path)
        
    def on_tab_changed(self, index):
        """Handle tab change event"""
        # Get current widget
        current_widget = self.tabs.widget(index)
        
        # Block layout updates
        self.blockSignals(True)
        
        # Update geometry but keep layout stable
        current_widget.updateGeometry()
        
        # Unblock layout updates
        self.blockSignals(False)
        
        # If current tab is visualizer, need to update canvas
        if index == 2 and hasattr(self.visualizer_widget, 'canvas'):
            # Use QTimer for delayed update after tab is fully rendered
            QTimer.singleShot(100, self.visualizer_widget.refresh_visualization)
