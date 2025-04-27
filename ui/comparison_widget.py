#!/usr/bin/env python3
"""
Comparison widget module for the MPGA GUI application.
Allows comparing multiple placement results.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QPushButton, QListWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView, QFileDialog,
                            QMessageBox, QGroupBox, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal

from core.data_loader import load_geojson
from utils.constants import FILE_FILTERS


class MPGAMplCanvas(FigureCanvas):
    """Canvas for matplotlib figures"""
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        
        super(MPGAMplCanvas, self).__init__(self.fig)
        self.setParent(parent)
        
        # Configure figure
        self.fig.tight_layout()


class MPGAComparisonWidget(QWidget):
    """Widget for comparing multiple placement results"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Initialize variables before setupUI is called
        self.placements = []  # List of (file_path, name, data) tuples
        self.color_map_name = "hot"  # Default colormap
        self.comparison_running = False

        self.setupUI()
        self.placements = []  # List of (file_path, name, data) tuples
        self.color_map_name = "hot"  # Default colormap
        
    def setupUI(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Controls layout
        ctrl_layout = QGridLayout()
        
        # Placement list
        list_group = QGroupBox("Placements to Compare")
        list_layout = QVBoxLayout(list_group)
        self.placement_list = QListWidget()
        self.placement_list.setMinimumHeight(100)
        list_layout.addWidget(self.placement_list)
        
        # Buttons for list management
        list_btn_layout = QHBoxLayout()
        self.add_placement_btn = QPushButton("Add Placement")
        self.add_placement_btn.clicked.connect(self.add_placement)
        self.remove_placement_btn = QPushButton("Remove Selected")
        self.remove_placement_btn.clicked.connect(self.remove_placement)
        self.clear_placements_btn = QPushButton("Clear All")
        self.clear_placements_btn.clicked.connect(self.clear_placements)
        list_btn_layout.addWidget(self.add_placement_btn)
        list_btn_layout.addWidget(self.remove_placement_btn)
        list_btn_layout.addWidget(self.clear_placements_btn)
        list_layout.addLayout(list_btn_layout)
        
        # Comparison controls
        compare_group = QGroupBox("Comparison Settings")
        compare_layout = QVBoxLayout(compare_group)
        
        # Colormap selector
        colormap_layout = QHBoxLayout()
        colormap_layout.addWidget(QLabel("Colormap:"))
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(["hot", "viridis", "plasma", "inferno", "magma", "coolwarm"])
        self.colormap_combo.setCurrentText(self.color_map_name)
        self.colormap_combo.currentTextChanged.connect(self.change_colormap)
        colormap_layout.addWidget(self.colormap_combo)
        compare_layout.addLayout(colormap_layout)
        
        # Comparison action
        self.compare_btn = QPushButton("Compare Placements")
        self.compare_btn.clicked.connect(self.run_comparison)
        self.compare_btn.setEnabled(False)
        compare_layout.addWidget(self.compare_btn)
        
        # Save comparison action
        self.save_comparison_btn = QPushButton("Save Comparison")
        self.save_comparison_btn.clicked.connect(self.save_comparison)
        self.save_comparison_btn.setEnabled(False)
        compare_layout.addWidget(self.save_comparison_btn)
        
        # Add groups to control layout
        ctrl_layout.addWidget(list_group, 0, 0, 1, 3)
        ctrl_layout.addWidget(compare_group, 0, 3, 1, 1)
        
        # Canvas area
        self.canvas_container = QVBoxLayout()
        
        self.canvas = MPGAMplCanvas(self, width=10, height=8)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.canvas_container.addWidget(self.toolbar)
        self.canvas_container.addWidget(self.canvas)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setMinimumHeight(150)
        
        # Add all layouts to main layout
        layout.addLayout(ctrl_layout)
        layout.addLayout(self.canvas_container, 3)
        layout.addWidget(self.results_table, 1)
        
    def add_placement(self, file_path=None):
        """
        Add a placement file to the comparison
        
        Args:
            file_path (str, optional): Path to placement file. If None, a file dialog will be shown.
        """
        if file_path is None:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Placement File", "", FILE_FILTERS["geojson"])
                
        if file_path and os.path.exists(file_path):
            # Check if this file is already in the list
            for existing_path, _, _ in self.placements:
                if os.path.samefile(file_path, existing_path):
                    QMessageBox.warning(self, "Warning", "This file is already in the comparison list.")
                    return
            
            # Get a name for this placement
            name = os.path.basename(file_path)
            name, _ = os.path.splitext(name)
            
            # Load the data
            data = load_geojson(file_path)
            if data:
                # Add to internal list
                self.placements.append((file_path, name, data))
                
                # Add to UI list
                self.placement_list.addItem(name)
                
                # Enable comparison if we have at least 2 placements
                self.compare_btn.setEnabled(len(self.placements) >= 2)
            else:
                QMessageBox.warning(self, "Error", f"Failed to load file: {file_path}")               

    def remove_placement(self):
        """Remove selected placement from the comparison"""
        current_row = self.placement_list.currentRow()
        if current_row >= 0:
            # Remove from internal list
            self.placements.pop(current_row)
            
            # Remove from UI list
            self.placement_list.takeItem(current_row)
            
            # Enable/disable comparison based on number of placements
            self.compare_btn.setEnabled(len(self.placements) >= 2)
            
    def clear_placements(self):
        """Clear all placements"""
        self.placements.clear()
        self.placement_list.clear()
        self.compare_btn.setEnabled(False)
        self.save_comparison_btn.setEnabled(False)
        
    def change_colormap(self, cmap_name):
        """Change the colormap for thermal view"""
        self.color_map_name = cmap_name
        if hasattr(self, 'comparison_running') and self.comparison_running:
            self.run_comparison()
            
    def run_comparison(self):
        """Run the comparison visualization"""
        if len(self.placements) < 2:
            QMessageBox.warning(self, "Error", "Need at least 2 placements to compare")
            return
            
        try:
            # Set flag to indicate comparison is running
            self.comparison_running = True
            
            # Clear previous plot
            self.canvas.fig.clear()
            
            # Determine grid layout for subplots
            n_plots = len(self.placements)
            n_cols = min(2, n_plots)
            n_rows = (n_plots + n_cols - 1) // n_cols
            
            # Create grid of subplots
            axs = self.canvas.fig.subplots(n_rows, n_cols)
            if n_rows * n_cols == 1:
                axs = np.array([axs])
            axs = axs.flatten()
            
            # Create a shared colormap
            cmap = plt.get_cmap(self.color_map_name)
            
            # Find global min/max thermal values
            all_thermal_values = []
            for _, _, data in self.placements:
                for feature in data.get('features', []):
                    if feature.get('properties', {}).get('type') != 'connection':
                        thermal_value = feature.get('properties', {}).get('thermal_value', 0)
                        if thermal_value is not None:
                            all_thermal_values.append(thermal_value)
            
            thermal_norm = Normalize(min(all_thermal_values) if all_thermal_values else 0, 
                                    max(all_thermal_values) if all_thermal_values else 1)
            
            # Find global min/max connection weights
            all_weights = []
            for _, _, data in self.placements:
                for feature in data.get('features', []):
                    if feature.get('properties', {}).get('type') == 'connection':
                        weight = feature.get('properties', {}).get('weight', 0)
                        if weight is not None:
                            all_weights.append(weight)
            
            if all_weights:
                weight_norm = Normalize(min(all_weights), max(all_weights))
            else:
                weight_norm = Normalize(0, 1)
                
            # Extract metrics for all placements
            metrics = []
            for _, name, data in self.placements:
                # Basic metrics
                metadata = data.get('metadata', {})
                metric = {
                    'name': name,
                    'cell_count': metadata.get('cell_count', 0),
                    'connection_count': metadata.get('connection_count', 0),
                    'total_weight': metadata.get('total_connection_weight', 0),
                }
                
                # Calculate average connection length
                total_length = 0
                conn_count = 0
                for feature in data.get('features', []):
                    if feature.get('properties', {}).get('type') == 'connection':
                        coords = feature.get('geometry', {}).get('coordinates', [])
                        if len(coords) >= 2:
                            try:
                                x1, y1 = coords[0]
                                x2, y2 = coords[1]
                                length = abs(x2 - x1) + abs(y2 - y1)
                                weight = feature.get('properties', {}).get('weight', 1)
                                total_length += length * weight
                                conn_count += 1
                            except (IndexError, TypeError):
                                continue
                
                metric['avg_length'] = total_length / conn_count if conn_count > 0 else 0
                
                # Calculate thermal clustering
                high_thermal_cells = []
                for feature in data.get('features', []):
                    if feature.get('properties', {}).get('type') != 'connection':
                        thermal_value = feature.get('properties', {}).get('thermal_value', 0)
                        if thermal_value > 0.7:  # Threshold for "high thermal"
                            geometry = feature.get('geometry', {})
                            if geometry.get('type') != 'Polygon':
                                continue
                                
                            # Get coordinates safely
                            coords_data = geometry.get('coordinates', [])
                            if not coords_data:
                                continue
                                
                            # Handle different coordinate formats
                            coords = []
                            if len(coords_data) == 1 and isinstance(coords_data[0], list):
                                if coords_data[0] and isinstance(coords_data[0][0], list):
                                    coords = coords_data[0]
                            else:
                                coords = coords_data
                                
                            # Skip empty coordinates
                            if not coords:
                                continue
                                
                            try:
                                # Calculate centroid
                                centroid_x = sum(c[0] for c in coords) / len(coords)
                                centroid_y = sum(c[1] for c in coords) / len(coords)
                                high_thermal_cells.append((centroid_x, centroid_y))
                            except (TypeError, ZeroDivisionError):
                                continue
                
                # Calculate average distance between high thermal cells
                thermal_distances = []
                for i in range(len(high_thermal_cells)):
                    for j in range(i+1, len(high_thermal_cells)):
                        x1, y1 = high_thermal_cells[i]
                        x2, y2 = high_thermal_cells[j]
                        distance = abs(x2 - x1) + abs(y2 - y1)
                        thermal_distances.append(distance)
                
                metric['thermal_clustering'] = sum(thermal_distances) / len(thermal_distances) if thermal_distances else 0
                metric['high_thermal_count'] = len(high_thermal_cells)
                metrics.append(metric)
            
            # Plot each placement in its subplot
            for i, ((file_path, name, data), ax) in enumerate(zip(self.placements, axs)):
                # Create cell patches
                cell_patches = []
                for feature in data.get('features', []):
                    if feature.get('properties', {}).get('type') != 'connection':
                        geometry = feature.get('geometry', {})
                        if geometry.get('type') == 'Polygon':
                            coords_data = geometry.get('coordinates', [])
                            if not coords_data:
                                continue
                                
                            # Handle both coordinate formats
                            coords = []
                            if len(coords_data) == 1 and isinstance(coords_data[0], list):
                                if coords_data[0] and isinstance(coords_data[0][0], list):
                                    coords = coords_data[0]
                            else:
                                coords = coords_data
                                
                            # Skip empty coordinates
                            if not coords:
                                continue
                                
                            thermal_value = feature.get('properties', {}).get('thermal_value', 0)
                            label = feature.get('properties', {}).get('name', '')
                            
                            try:
                                xy = np.array(coords)
                                
                                # Skip empty coordinates
                                if xy.size == 0:
                                    continue
                                    
                                # Create polygon patch with color based on thermal value
                                color = cmap(thermal_norm(thermal_value))
                                polygon = plt.Polygon(
                                    xy, closed=True, fill=True,
                                    facecolor=color, alpha=0.7,
                                    edgecolor='black', linewidth=0.5
                                )
                                
                                cell_patches.append((polygon, label, xy))
                            except Exception as e:
                                print(f"Error processing cell in comparison: {e}")
                                continue
                
                # Create connection lines
                connection_lines = []
                for feature in data.get('features', []):
                    if feature.get('properties', {}).get('type') == 'connection':
                        geometry = feature.get('geometry', {})
                        if geometry.get('type') == 'LineString':
                            coords = geometry.get('coordinates', [])
                            if len(coords) >= 2:
                                weight = feature.get('properties', {}).get('weight', 0)
                                try:
                                    # Create line with width based on weight
                                    line_width = 0.5 + 3 * weight_norm(weight)
                                    line = plt.Line2D(
                                        [coords[0][0], coords[1][0]],
                                        [coords[0][1], coords[1][1]],
                                        linewidth=line_width, color='blue', alpha=0.4
                                    )
                                    connection_lines.append(line)
                                except Exception as e:
                                    print(f"Error creating connection line: {e}")
                                    continue
                
                # Draw connections first
                for line in connection_lines:
                    ax.add_line(line)
                    
                # Draw cells
                for polygon, label, xy in cell_patches:
                    ax.add_patch(polygon)
                    
                    # Calculate area for font size scaling
                    xmin, ymin = xy.min(axis=0)
                    xmax, ymax = xy.max(axis=0)
                    width = xmax - xmin
                    height = ymax - ymin
                    area = width * height
                    
                    # Only add text if cell is large enough
                    if area > 1.5 and label:
                        # Calculate centroid for text position
                        x = np.mean([p[0] for p in xy])
                        y = np.mean([p[1] for p in xy])
                        
                        # Scale font with cell size
                        font_size = max(4, min(9, area / 5))
                        
                        ax.text(x, y, label,
                               ha='center', va='center',
                               fontsize=font_size, fontweight='bold', color='white')
                
                # Set plot limits based on field size
                field = data.get('metadata', {}).get('field', {})
                rows = field.get('rows', 20)
                cols = field.get('cols', 20)
                
                ax.set_xlim(-1, cols + 1)
                ax.set_ylim(-1, rows + 1)
                
                # Formatting
                ax.set_aspect('equal')
                ax.grid(True, linestyle='--', alpha=0.3)
                ax.set_title(name, fontsize=12)
                
                # Add axes labels only on the bottom and left
                if i >= len(self.placements) - n_cols:  # Bottom row
                    ax.set_xlabel('X', fontsize=10)
                if i % n_cols == 0:  # Leftmost column
                    ax.set_ylabel('Y', fontsize=10)
            
            # Hide any unused subplots
            for i in range(len(self.placements), len(axs)):
                axs[i].set_visible(False)
                
            # Add a colorbar for the thermal values
            sm = ScalarMappable(cmap=cmap, norm=thermal_norm)
            sm.set_array([])
            self.canvas.fig.colorbar(sm, ax=axs, label='Thermal Value')
            
            # Adjust layout
            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
            # Update the results table
            self.update_metrics_table(metrics)
            
            # Enable save button
            self.save_comparison_btn.setEnabled(True)
            
            # Clear the flag
            self.comparison_running = False
            
        except Exception as e:
            import traceback
            QMessageBox.warning(self, "Comparison Error", f"Error creating comparison: {str(e)}")
            traceback.print_exc()
            self.comparison_running = False
            
    def update_metrics_table(self, metrics):
        """Update the metrics table with comparison results"""
        # Set up table
        self.results_table.clear()
        self.results_table.setRowCount(len(metrics))
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Placement", "Cells", "Connections", "Avg Length", "High Thermal Cells", "Thermal Clustering"
        ])
        
        # Fill table
        for i, metric in enumerate(metrics):
            self.results_table.setItem(i, 0, QTableWidgetItem(metric['name']))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(metric['cell_count'])))
            self.results_table.setItem(i, 2, QTableWidgetItem(str(metric['connection_count'])))
            self.results_table.setItem(i, 3, QTableWidgetItem(f"{metric['avg_length']:.2f}"))
            self.results_table.setItem(i, 4, QTableWidgetItem(str(metric['high_thermal_count'])))
            self.results_table.setItem(i, 5, QTableWidgetItem(f"{metric['thermal_clustering']:.2f}"))
            
        # Set colors based on values (lower is better for length and thermal clustering)
        if len(metrics) > 1:
            # Find best (min) values
            min_length = min(metric['avg_length'] for metric in metrics)
            min_thermal = min(metric['thermal_clustering'] for metric in metrics)
            
            # Highlight best values
            for i, metric in enumerate(metrics):
                # Highlight best average length
                if metric['avg_length'] == min_length:
                    self.results_table.item(i, 3).setBackground(Qt.green)
                    
                # Highlight best thermal clustering
                if metric['thermal_clustering'] == min_thermal:
                    self.results_table.item(i, 5).setBackground(Qt.green)
            
        # Adjust column widths
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 6):
            self.results_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
            
    def save_comparison(self):
        """Save the comparison visualization"""
        if not hasattr(self, 'canvas') or not self.canvas:
            QMessageBox.warning(self, "Error", "No comparison to save")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Comparison", "", FILE_FILTERS["image"])
            
        if file_path:
            try:
                self.canvas.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Success", f"Comparison saved to: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save comparison: {str(e)}")
