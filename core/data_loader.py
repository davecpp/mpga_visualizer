#!/usr/bin/env python3
"""
Data loading module for the MPGA GUI application.
Handles loading and parsing of input files.
"""

import json
import os
import traceback

def load_geojson(file_path):
    """
    Load a GeoJSON file containing placement data.
    
    Args:
        file_path (str): Path to the GeoJSON file
        
    Returns:
        dict: Parsed GeoJSON data or None if loading fails
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading GeoJSON: {e}")
        traceback.print_exc()
        return None

def load_config(file_path):
    """
    Load a configuration file in JSON format.
    
    Args:
        file_path (str): Path to the configuration file
        
    Returns:
        dict: Parsed configuration or None if loading fails
    """
    try:
        with open(file_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        traceback.print_exc()
        return None
        
def save_config(config, file_path):
    """
    Save configuration to a JSON file.
    
    Args:
        config (dict): Configuration to save
        file_path (str): Path to save the configuration file
        
    Returns:
        bool: True if saving was successful, False otherwise
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        traceback.print_exc()
        return False
        
def convert_scheme_to_input(scheme_data, output_path):
    """
    Convert a scheme file to a format suitable for the MPGA optimizer.
    
    Args:
        scheme_data (dict): Parsed scheme data
        output_path (str): Path to save the converted file
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        # Process the scheme data to create input for optimizer
        # (Implementation depends on the exact format requirements)
        
        # For now, just pass through the data
        with open(output_path, 'w') as f:
            json.dump(scheme_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error converting scheme: {e}")
        traceback.print_exc()
        return False
        
def load_output_data(file_path):
    """
    Load output data from the optimizer.
    
    Args:
        file_path (str): Path to the output file
        
    Returns:
        dict: Parsed output data or None if loading fails
    """
    return load_geojson(file_path)  # For now, same as loading GeoJSON
