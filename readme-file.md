# MultiParametricGA Optimizer

A sophisticated GUI application for integrated circuit (IC) placement optimization using genetic algorithms.

## Overview

The MultiParametricGA Optimizer provides a comprehensive interface for running and visualizing integrated circuit component placement optimizations. It leverages genetic algorithms with multi-parametric optimization to balance various competing factors such as wire length, thermal distribution, power consumption, and design rule constraints (DRC).

![Application Screenshot](docs/images/app_screenshot.png)

## Features

- **Interactive Configuration**: Tune genetic algorithm parameters, fitness weights, thermal model, power model, and DRC rules
- **Optimization Execution**: Run the optimization engine with real-time progress feedback
- **Advanced Visualization**: View optimized placements with thermal overlay, connection visualization and grid options
- **Comparison Tool**: Compare multiple placement solutions side-by-side with key metrics
- **Theme Support**: Choose between dark, light, and blue themes for the application interface

## Installation

### Prerequisites

- Python 3.6 or higher
- PyQt5
- Matplotlib
- NumPy

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/mpga-optimizer.git
   cd mpga-optimizer
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   - On Windows: `run.bat`
   - On Linux/macOS: `./main.py`

## Usage

### Running an Optimization

1. Select the "Run Optimization" tab
2. Load an input scheme using the "Browse..." button
3. Specify an output file location
4. (Optional) Configure optimization parameters in the "Configuration" tab
5. Click "Run Optimization" and monitor progress
6. Once complete, view the results in the visualization tab

### Configuring Parameters

The "Configuration" tab allows adjusting:

- **Genetic Algorithm Parameters**: Population size, iterations, mutation rate, etc.
- **Fitness Weights**: Importance of wire length, thermal performance, DRC compliance, etc.
- **Thermal Model Parameters**: Ambient temperature, thermal conductivity, etc.
- **Power Model Parameters**: Cell power, wire capacitance, voltage factors, etc.
- **DRC Parameters**: Minimum distance rules, penalty values, etc.

### Visualizing Results

The "Visualize Results" tab provides:

- Color-coded thermal view of the placement
- Connection visualization with width indicating connection weight
- Interactive zoom, pan and grid controls
- Option to save visualizations as images

### Comparing Placements

The "Compare Results" tab enables:

- Side-by-side comparison of multiple placement solutions
- Metrics table showing comparative performance indicators
- Various colormap options for thermal visualization
- Option to save comparison results

## File Formats

### Input Scheme (JSON)

The input scheme contains cell definitions and their connections:

```json
{
    "cells": [
        {
            "id": 0,
            "name": "CPU_Core_1",
            "polygon": [[0,0], [5,0], [5,2], [0,2], [0,0]],
            "thermal_value": 0.72,
            "power_density": 0.26
        },
        ...
    ],
    "connections": [ 
        [0.0, 0.94, 0.21, ...],
        [0.94, 0.0, 0.59, ...],
        ...
    ],
    "field": {
        "rows": 25,
        "cols": 25,
        "allow_fillers": true
    }
}
```

### Output Result (GeoJSON)

Results are saved in GeoJSON format:

```json
{
    "features": [
        {
            "geometry": {
                "coordinates": [...],
                "type": "Polygon"
            },
            "properties": {
                "id": 0,
                "name": "CPU_Core1",
                "power_density": 0.85,
                "thermal_value": 0.95,
                "type": "cell"
            },
            "type": "Feature"
        },
        ...
    ],
    "metadata": {
        "cell_count": 25,
        "connection_count": 109,
        "field": {
            "allow_fillers": true,
            "cols": 20,
            "rows": 20
        },
        "total_connection_weight": 35.5
    },
    "type": "FeatureCollection"
}
```

## Configuration (JSON)

Optimization parameters can be saved/loaded:

```json
{
    "drc": {
        "min_distance": 2,
        "overlap_penalty": 10.0,
        "distance_penalty": 5.0
    },
    "fitness": {
        "power": {...},
        "thermal": {...},
        "weights": {...}
    },
    "ga": {
        "population_size": 100,
        "max_iterations": 200,
        ...
    }
}
```

## Architecture

The application is structured in the following modules:

- **UI Components**: Main window and specialized widgets for configuration, running, visualization and comparison
- **Core Logic**: Data loading/saving and optimization execution
- **Utilities**: Constants, file format definitions, and helper functions

## Development

### Project Structure

```
mpga-optimizer/
├── core/
│   ├── data_loader.py
│   └── runner.py
├── ui/
│   ├── main_window.py
│   ├── run_widget.py
│   ├── config_widget.py
│   ├── visualizer.py
│   └── comparison_widget.py
├── utils/
│   └── constants.py
├── main.py
├── setup.py
└── run.bat
```

### Building from Source

To build the application from source:

```
python setup.py build
```

For development installation:

```
python setup.py develop
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- PyQt5 for providing the GUI framework
- Matplotlib for visualization capabilities
- The genetic algorithm community for optimization techniques
