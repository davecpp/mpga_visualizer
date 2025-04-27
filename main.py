#!/usr/bin/env python3
"""
Main entry point for the MPGA GUI application.
"""

import sys
import os
import platform
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings

from ui.main_window import MPGAMainWindow
from utils.constants import APP_NAME, APP_ORGANIZATION


def setup_environment():
    """Set up the application environment"""
    # Add current directory to path if needed
    if '' not in sys.path:
        sys.path.insert(0, '')
        
    # Set up application settings
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, os.path.expanduser("~/.config/mpga"))
    
    # Handle platform-specific setup
    if platform.system() == "Windows":
        # Set up high DPI support on Windows
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    elif platform.system() == "Darwin":  # macOS
        # Add any macOS-specific settings
        pass
    else:  # Linux and others
        # Add any Linux-specific settings
        pass
        
    # Make sure necessary directories exist
    os.makedirs(os.path.expanduser("~/.config/mpga"), exist_ok=True)
    
    # Create directories for the application structure if they don't exist
    for dir_name in ['core', 'ui', 'utils']:
        os.makedirs(dir_name, exist_ok=True)


def main():
    """Main entry point for the application"""
    # Set up environment
    setup_environment()
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ORGANIZATION)
    
    # Set application style
    app.setStyle('Fusion')  # Use Fusion style for consistent look across platforms
    
    # Create and show the main window
    main_window = MPGAMainWindow()
    main_window.show()
    
    # Run the application
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
