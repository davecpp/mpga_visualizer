#!/usr/bin/env python3
"""
Scheme Generator for MultiParametricGA Optimizer

This script generates input schemes with orthogonal polygons for the MultiParametricGA Optimizer.
It allows customization of the number of objects, field dimensions, and filler settings.
"""

import argparse
import json
import random
import numpy as np
from typing import List, Dict, Tuple, Any

# Constants
MIN_CELL_SIZE = 1
MAX_CELL_SIZE = 5
MIN_THERMAL_VALUE = 0.2
MAX_THERMAL_VALUE = 0.95
MIN_POWER_DENSITY = 0.1
MAX_POWER_DENSITY = 0.85
MIN_CONNECTION_WEIGHT = 0.0
MAX_CONNECTION_WEIGHT = 1.0
CONNECTION_SPARSITY = 0.3  # Probability of zero connection
CELL_TYPES = [
    "CPU_Core", "GPU_Core", "Memory_Controller", "Cache_L1", "Cache_L2",
    "DDR_Controller", "PCIe_Controller", "SATA_Controller", "USB_Controller",
    "Network_Controller", "Audio_Processor", "Video_Encoder", "Video_Decoder",
    "Display_Controller", "GPIO_Controller", "Power_Management", "Clock_Generator",
    "Security_Module", "I2C_Controller", "SPI_Controller", "UART_Controller",
    "AI_Accelerator", "DSP_Unit"
]


def generate_orthogonal_polygon(max_width: int, max_height: int) -> List[List[int]]:
    """
    Generate a random orthogonal polygon (L-shape, T-shape, etc.)
    
    Args:
        max_width: Maximum width of the polygon
        max_height: Maximum height of the polygon
        
    Returns:
        List of coordinate pairs forming a closed polygon
    """
    # Base width and height (at least 1x1)
    base_width = random.randint(MIN_CELL_SIZE, max_width)
    base_height = random.randint(MIN_CELL_SIZE, max_height)
    
    # Start with a rectangle
    polygon = [
        [0, 0],
        [base_width, 0],
        [base_width, base_height],
        [0, base_height],
        [0, 0]  # Close the polygon
    ]
    
    # Decide if we should make an L, T, or other shape
    shape_type = random.choice(["rectangle", "L", "T", "U", "Z"])
    
    if shape_type == "rectangle" or base_width <= 2 or base_height <= 2:
        # Keep it as a rectangle
        return polygon
    
    if shape_type == "L":
        # Create an L shape by removing a section
        cut_width = random.randint(1, base_width - 1)
        cut_height = random.randint(1, base_height - 1)
        
        # Remove the top-right corner to make an L
        polygon = [
            [0, 0],
            [base_width, 0],
            [base_width, base_height - cut_height],
            [base_width - cut_width, base_height - cut_height],
            [base_width - cut_width, base_height],
            [0, base_height],
            [0, 0]  # Close the polygon
        ]
    
    elif shape_type == "T":
        # Create a T shape
        stem_width = random.randint(1, base_width - 2)
        stem_start = random.randint(0, base_width - stem_width)
        
        polygon = [
            [0, 0],
            [base_width, 0],
            [base_width, base_height // 3],
            [stem_start + stem_width, base_height // 3],
            [stem_start + stem_width, base_height],
            [stem_start, base_height],
            [stem_start, base_height // 3],
            [0, base_height // 3],
            [0, 0]  # Close the polygon
        ]
    
    elif shape_type == "U":
        # Create a U shape
        opening_width = random.randint(1, base_width - 2)
        wall_width = random.randint(1, (base_width - opening_width) // 2)
        
        polygon = [
            [0, 0],
            [base_width, 0],
            [base_width, base_height],
            [base_width - wall_width, base_height],
            [base_width - wall_width, base_height // 3],
            [wall_width, base_height // 3],
            [wall_width, base_height],
            [0, base_height],
            [0, 0]  # Close the polygon
        ]
    
    elif shape_type == "Z":
        # Create a Z shape
        indent = random.randint(1, base_width // 2)
        
        polygon = [
            [0, 0],
            [base_width, 0],
            [base_width, base_height // 2],
            [indent, base_height // 2],
            [indent, base_height],
            [0, base_height],
            [0, 0]  # Close the polygon
        ]
    
    return polygon


def generate_cells(num_cells: int, field_rows: int, field_cols: int) -> List[Dict[str, Any]]:
    """
    Generate a list of cells with random properties
    
    Args:
        num_cells: Number of cells to generate
        field_rows: Number of rows in the field
        field_cols: Number of columns in the field
        
    Returns:
        List of cell dictionaries
    """
    cells = []
    
    for i in range(num_cells):
        # Generate cell type and name
        cell_type = random.choice(CELL_TYPES)
        cell_name = f"{cell_type}_{i+1}"
        
        # Generate random size for the polygon (capped by field size)
        max_width = min(MAX_CELL_SIZE, field_cols // 2)  # Ensure it fits in the field
        max_height = min(MAX_CELL_SIZE, field_rows // 2)
        
        # Generate random orthogonal polygon
        polygon = generate_orthogonal_polygon(max_width, max_height)
        
        # Generate random properties
        thermal_value = round(random.uniform(MIN_THERMAL_VALUE, MAX_THERMAL_VALUE), 2)
        power_density = round(random.uniform(MIN_POWER_DENSITY, MAX_POWER_DENSITY), 2)
        
        # Create cell object
        cell = {
            "id": i,
            "name": cell_name,
            "polygon": polygon,
            "thermal_value": thermal_value,
            "power_density": power_density
        }
        
        cells.append(cell)
    
    return cells


def generate_connection_matrix(num_cells: int) -> List[List[float]]:
    """
    Generate a connection matrix between cells
    
    Args:
        num_cells: Number of cells
        
    Returns:
        2D matrix of connection weights
    """
    # Initialize connection matrix with zeros
    conn_matrix = [[0.0 for _ in range(num_cells)] for _ in range(num_cells)]
    
    # Fill the upper triangle with random weights
    for i in range(num_cells):
        for j in range(i+1, num_cells):
            # Decide if these cells should be connected
            if random.random() < CONNECTION_SPARSITY:
                weight = 0.0
            else:
                weight = round(random.uniform(MIN_CONNECTION_WEIGHT, MAX_CONNECTION_WEIGHT), 2)
            
            # Set symmetric connection weights
            conn_matrix[i][j] = weight
            conn_matrix[j][i] = weight
    
    return conn_matrix


def generate_scheme(num_cells: int, rows: int, cols: int, allow_fillers: bool) -> Dict[str, Any]:
    """
    Generate a complete scheme with cells, connections, and field properties
    
    Args:
        num_cells: Number of cells to generate
        rows: Number of rows in the field
        cols: Number of columns in the field
        allow_fillers: Whether to allow filler cells
        
    Returns:
        Complete scheme dictionary
    """
    # Generate cells
    cells = generate_cells(num_cells, rows, cols)
    
    # Generate connection matrix
    connections = generate_connection_matrix(num_cells)
    
    # Create the field definition
    field = {
        "rows": rows,
        "cols": cols,
        "allow_fillers": allow_fillers
    }
    
    # Build the complete scheme
    scheme = {
        "cells": cells,
        "connections": connections,
        "field": field
    }
    
    return scheme


def save_scheme(scheme: Dict[str, Any], output_file: str) -> None:
    """
    Save the generated scheme to a JSON file
    
    Args:
        scheme: The scheme to save
        output_file: Path to the output file
    """
    with open(output_file, 'w') as f:
        json.dump(scheme, f, indent=4)
    
    print(f"Scheme saved to {output_file}")


def main():
    """Main entry point for the scheme generator"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate input schemes for MultiParametricGA Optimizer')
    parser.add_argument('--num_cells', type=int, default=20, help='Number of cells to generate')
    parser.add_argument('--rows', type=int, default=25, help='Number of rows in the field')
    parser.add_argument('--cols', type=int, default=25, help='Number of columns in the field')
    parser.add_argument('--allow_fillers', action='store_true', help='Allow filler cells')
    parser.add_argument('--output', type=str, default='scheme.json', help='Output file path')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)
    
    # Generate scheme
    scheme = generate_scheme(args.num_cells, args.rows, args.cols, args.allow_fillers)
    
    # Save to file
    save_scheme(scheme, args.output)


if __name__ == "__main__":
    main()
