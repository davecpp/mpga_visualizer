#!/usr/bin/env python3
"""
Constants module for the MPGA GUI application.
Contains application-wide constants and settings.
"""

import os
import platform

# Application information
APP_NAME = "MultiParametricGA Optimizer"
APP_VERSION = "2.0.0"
APP_ORGANIZATION = "MPGA"
APP_DOMAIN = "mpga.org"

# Default configuration
DEFAULT_CONFIG = {
    "ga": {
        "population_size": 100,
        "max_iterations": 200,
        "convergence_threshold": 0.001,
        "filter_coefficient": 0.4,
        "mutation_probability": 0.1,
        "drc_filter_percentage": 0.1,
        "drc_check_interval": 10,
        "use_specialized_populations": True,
        "specialized_evolutions": 20,
        "specialized_best_percentage": 0.2,
        "specialized_random_percentage": 0.05
    },
    "fitness": {
        "weights": {
            "wire_length": 1.0,
            "thermal": 0.5,
            "drc": 2.0,
            "power": 0.3,
            "parasitic": 0.2
        },
        "thermal": {
            "max_allowed_temp": 100.0,
            "ambient_temp": 25.0,
            "thermal_conductivity": 150.0,
            "power_density": 0.1
        },
        "power": {
            "cell_power": 0.1,
            "wire_capacitance": 0.02,
            "voltage_factor": 1.0,
            "frequency": 1.0,
            "leakage_factor": 0.05
        }
    },
    "drc": {
        "min_distance": 2,
        "overlap_penalty": 10.0,
        "distance_penalty": 5.0
    }
}

# Determine executable path based on platform
def get_executable_path():
    """
    Get the platform-specific path to the MPGA executable.
    
    Returns:
        str: Path to the executable
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if platform.system() == "Windows":
        return os.path.join(base_dir, "bin", "MultiParametricGA.exe")
    else:
        return os.path.join(base_dir, "bin", "MultiParametricGA")

# Color schemes
COLOR_SCHEMES = {
    "dark": {
        "window": (53, 53, 53),
        "window_text": (255, 255, 255),
        "base": (25, 25, 25),
        "alt_base": (53, 53, 53),
        "tooltip_base": (255, 255, 255),
        "tooltip_text": (255, 255, 255),
        "text": (255, 255, 255),
        "button": (53, 53, 53),
        "button_text": (255, 255, 255),
        "bright_text": (255, 0, 0),
        "link": (42, 130, 218),
        "highlight": (42, 130, 218),
        "highlighted_text": (255, 255, 255)
    },
    "light": {
        "window": (240, 240, 240),
        "window_text": (0, 0, 0),
        "base": (255, 255, 255),
        "alt_base": (245, 245, 245),
        "tooltip_base": (0, 0, 0),
        "tooltip_text": (255, 255, 255),
        "text": (0, 0, 0),
        "button": (240, 240, 240),
        "button_text": (0, 0, 0),
        "bright_text": (255, 0, 0),
        "link": (0, 0, 255),
        "highlight": (42, 130, 218),
        "highlighted_text": (255, 255, 255)
    },
    "blue": {
        "window": (53, 81, 119),
        "window_text": (255, 255, 255),
        "base": (42, 65, 95),
        "alt_base": (53, 81, 119),
        "tooltip_base": (255, 255, 255),
        "tooltip_text": (0, 0, 0),
        "text": (255, 255, 255),
        "button": (70, 100, 150),
        "button_text": (255, 255, 255),
        "bright_text": (255, 255, 0),
        "link": (130, 200, 255),
        "highlight": (100, 160, 230),
        "highlighted_text": (255, 255, 255)
    }
}

# Focus modes
FOCUS_MODES = ["WireLength", "Thermal", "DRC", "Power", "Mixed"]

# File filters
FILE_FILTERS = {
    "geojson": "GeoJSON Files (*.geojson);;All Files (*.*)",
    "config": "JSON Files (*.json);;All Files (*.*)",
    "all": "All Files (*.*)",
    "image": "PNG Files (*.png);;PDF Files (*.pdf);;SVG Files (*.svg);;All Files (*.*)"
}
