#!/usr/bin/env python3
"""
Visualizer module for the MPGA GUI application.
Enhanced with interactive features like zoom, pan, and grid toggle.
"""

import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.widgets import RectangleSelector
import traceback

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QLineEdit, QPushButton, QCheckBox, QMessageBox,
                            QSlider, QLabel, QComboBox, QSplitter, QToolBar,
                            QAction, QFileDialog, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QCursor

from core.data_loader import load_geojson


class MPGAZoomableCanvas(FigureCanvas):
    """Enhanced canvas for matplotlib figures with zoom and pan capabilities"""
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        # Disable automatic layout adjustments
        self.fig.set_tight_layout(False)
        self.fig.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.1)
        
        super(MPGAZoomableCanvas, self).__init__(self.fig)
        self.setParent(parent)
        
        # Set size policy for canvas
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()
        
        # Setup mouse event tracking
        self.dragging = False
        self.dragging_view = False
        self.last_mouse_pos = None
        self.selected_index = None
        
        # Grid parameters
        self.show_grid = True
        self.grid_size = 1  # Default grid size
        
        # Save initial figure size
        self.initial_width, self.initial_height = self.fig.get_size_inches()
        
        # Connect event handlers using direct matplotlib events
        self.mpl_connect('button_press_event', self.on_click)
        self.mpl_connect('button_release_event', self.on_release)
        self.mpl_connect('motion_notify_event', self.on_motion)
        self.mpl_connect('scroll_event', self.on_scroll)
        self.mpl_connect('key_press_event', self.on_key)
        
    def on_click(self, event):
        """Handle mouse click event"""
        if event.inaxes != self.axes:
            return
            
        # Save mouse position in screen coordinates
        self.last_mouse_pos = (event.x, event.y)
        self.dragging_view = True
        
    def on_release(self, event):
        """Handle mouse release event"""
        self.dragging_view = False
        
    def on_motion(self, event):
        """Handle mouse motion for panning the view"""
        if event.x is None or event.y is None or self.last_mouse_pos is None:
            return
            
        # Calculate movement in screen pixels
        dx = event.x - self.last_mouse_pos[0]
        dy = event.y - self.last_mouse_pos[1]
        self.last_mouse_pos = (event.x, event.y)
        
        if self.dragging_view:
            # Convert screen pixels to data coordinates
            xlim = self.axes.get_xlim()
            ylim = self.axes.get_ylim()
            
            # Calculate scaling factor based on figure size
            scale = (xlim[1] - xlim[0]) / self.fig.bbox.width
            
            # Apply pan offset (negative to move in the direction of mouse movement)
            dx_data = -dx * scale
            dy_data = -dy * scale
            
            # Update plot limits
            self.axes.set_xlim(xlim[0] + dx_data, xlim[1] + dx_data)
            self.axes.set_ylim(ylim[0] + dy_data, ylim[1] + dy_data)
            
            # Draw without updating layout
            self.draw_maintain_view()
    
    def on_scroll(self, event):
        """Handle mouse scroll for zooming"""
        # Set zoom factor
        base_scale = 1.2
        
        # Get current view limits
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        
        # Get mouse position in data coordinates
        xdata = event.xdata
        ydata = event.ydata
        
        if xdata is None or ydata is None:
            return
            
        # Determine zoom direction
        scale_factor = 1 / base_scale if event.button == 'up' else base_scale
        
        # Calculate new view dimensions
        new_width = (xlim[1] - xlim[0]) * scale_factor
        new_height = (ylim[1] - ylim[0]) * scale_factor
        
        # Calculate relative position of mouse in view
        relx = (xdata - xlim[0]) / (xlim[1] - xlim[0])
        rely = (ydata - ylim[0]) / (ylim[1] - ylim[0])
        
        # Calculate new view limits, keeping mouse position fixed
        new_xlim = [xdata - relx * new_width, xdata + (1 - relx) * new_width]
        new_ylim = [ydata - rely * new_height, ydata + (1 - rely) * new_height]
        
        # Apply new view limits
        self.axes.set_xlim(new_xlim)
        self.axes.set_ylim(new_ylim)
        
        # Draw without updating layout
        self.draw_maintain_view()
        
    def on_key(self, event):
        """Handle key press events for grid adjustment"""
        if event.key == '[':
            # Decrease grid size
            self.grid_size = max(0.5, self.grid_size - 0.5)
            self.update_grid()
        elif event.key == ']':
            # Increase grid size
            self.grid_size += 0.5
            self.update_grid()
            
    def update_grid(self):
        """Update grid with current settings"""
        if self.show_grid:
            # Get current view limits
            xlim = self.axes.get_xlim()
            ylim = self.axes.get_ylim()
            
            # Clear previous grid
            self.axes.grid(False)
            
            # Calculate grid lines
            step = self.grid_size
            xmin, xmax = xlim
            ymin, ymax = ylim
            
            # Remove existing grid lines if any
            for line in self.axes.get_lines():
                if line.get_color() == 'lightgray':
                    line.remove()
                    
            # Draw vertical grid lines
            for x in range(int(xmin - step), int(xmax + step), int(step)):
                self.axes.axvline(x, color='lightgray', linewidth=0.5, zorder=0)
                
            # Draw horizontal grid lines
            for y in range(int(ymin - step), int(ymax + step), int(step)):
                self.axes.axhline(y, color='lightgray', linewidth=0.5, zorder=0)
        else:
            # Just remove the grid
            self.axes.grid(False)
            
            # Remove existing grid lines if any
            for line in self.axes.get_lines():
                if line.get_color() == 'lightgray':
                    line.remove()
        
        # Redraw without changing layout
        self.draw_maintain_view()
        
    def draw_maintain_view(self):
        """Draw canvas without changing the view or layout"""
        # Save current limits
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        
        # Save figure size
        fig_width, fig_height = self.fig.get_size_inches()
        
        # Draw the figure
        self.draw()
        
        # Restore limits
        self.axes.set_xlim(xlim)
        self.axes.set_ylim(ylim)
        
        # Restore figure size
        self.fig.set_size_inches(fig_width, fig_height)

class MPGAVisualizerWidget(QWidget):
    """Enhanced widget for visualizing placement results"""
    
    # Add a signal to indicate when a new file is loaded
    file_loaded = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Initialize instance variables
        self.current_data = None
        self.show_connections = True
        self.show_grid = True
        self.show_labels = True
        self.thermal_view = True
        self.color_map_name = "hot"
        self.selected_cells = []
        self.selection_mode = False
        self.cbar = None
        self.thermal_norm = None
        
        # Set up the UI
        self.setupUI()
        
    def setupUI(self):
        """Set up the user interface"""
        # Use QVBoxLayout with fixed margins
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)  # Fixed spacing between elements
        
        # Create a toolbar for visualization options
        toolbar = QToolBar("Visualization Tools")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setFixedHeight(40)  # Fix toolbar height
        
        # Add actions to toolbar
        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(self.zoom_in_action)
        
        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(self.zoom_out_action)
        
        self.reset_view_action = QAction("Reset View", self)
        self.reset_view_action.triggered.connect(self.reset_view)
        toolbar.addAction(self.reset_view_action)
        
        toolbar.addSeparator()
        
        self.toggle_grid_action = QAction("Toggle Grid", self)
        self.toggle_grid_action.setCheckable(True)
        self.toggle_grid_action.setChecked(self.show_grid)
        self.toggle_grid_action.triggered.connect(self.toggle_grid)
        toolbar.addAction(self.toggle_grid_action)
        
        self.toggle_labels_action = QAction("Toggle Labels", self)
        self.toggle_labels_action.setCheckable(True)
        self.toggle_labels_action.setChecked(self.show_labels)
        self.toggle_labels_action.triggered.connect(self.toggle_labels)
        toolbar.addAction(self.toggle_labels_action)
        
        self.toggle_connections_action = QAction("Toggle Connections", self)
        self.toggle_connections_action.setCheckable(True)
        self.toggle_connections_action.setChecked(self.show_connections)
        self.toggle_connections_action.triggered.connect(self.toggle_connections)
        toolbar.addAction(self.toggle_connections_action)
        
        toolbar.addSeparator()
        
        self.toggle_thermal_action = QAction("Thermal View", self)
        self.toggle_thermal_action.setCheckable(True)
        self.toggle_thermal_action.setChecked(self.thermal_view)
        self.toggle_thermal_action.triggered.connect(self.toggle_thermal_view)
        toolbar.addAction(self.toggle_thermal_action)
        
        # Colormap selector
        toolbar.addWidget(QLabel("Colormap:"))
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(["hot", "viridis", "plasma", "inferno", "magma", "coolwarm"])
        self.colormap_combo.setCurrentText(self.color_map_name)
        self.colormap_combo.currentTextChanged.connect(self.change_colormap)
        toolbar.addWidget(self.colormap_combo)
        
        toolbar.addSeparator()
        
        self.save_image_action = QAction("Save Image", self)
        self.save_image_action.triggered.connect(self.save_current_view)
        toolbar.addAction(self.save_image_action)
        
        layout.addWidget(toolbar)
        
        # File controls with fixed height
        file_group = QGroupBox("Placement File")
        file_group.setFixedHeight(80)  # Fix height
        file_layout = QHBoxLayout(file_group)
        file_layout.setContentsMargins(10, 10, 10, 10)
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(self.browse_btn)
        
        layout.addWidget(file_group)
        
        # Create a fixed container for the matplotlib canvas
        canvas_container = QWidget()
        canvas_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)
        
        # Create the matplotlib navigation toolbar
        self.canvas = MPGAZoomableCanvas(self, width=8, height=6)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Disable automatic layout adjustments
        self.canvas.fig.set_tight_layout(False)
        self.canvas.fig.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.1)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setFixedHeight(35)  # Fix navigation toolbar height
        
        # Hide unnecessary buttons from the default navigation toolbar
        unwanted_buttons = ["Subplots", "Customize"]
        for action in self.toolbar.actions():
            if action.text() in unwanted_buttons:
                action.setVisible(False)
        
        # Add toolbar and canvas to container
        canvas_layout.addWidget(self.toolbar)
        canvas_layout.addWidget(self.canvas, 1)  # Canvas takes all remaining space
        
        # Add canvas container to main layout with explicit centering
        hlayout = QHBoxLayout()
        hlayout.addStretch(1)  # Add stretch on left
        hlayout.addWidget(canvas_container)
        hlayout.addStretch(1)  # Add stretch on right
        layout.addLayout(hlayout, 1)  # This layout takes all available space
        
        # Status bar at the bottom for showing cell info with fixed height
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(5, 5, 5, 5)
        self.status_label = QLabel("Ready")
        self.status_label.setFixedHeight(25)
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)
        
        # Connect events for showing cell info
        self.canvas.mpl_connect('motion_notify_event', self.show_cell_info)
      
    def browse_file(self):
        """Browse for a placement file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Placement File", "", "GeoJSON Files (*.geojson);;All Files (*.*)")
        
        if file_path:
            self.file_path.setText(file_path)
            self.load_and_visualize(file_path)
            
    def load_and_visualize(self, file_path):
        """Load and visualize a placement file"""
        data = load_geojson(file_path)
        if data:
            self.current_data = data
            self.visualize_placement()
            # Emit signal that file was loaded
            self.file_loaded.emit(file_path)
        else:
            QMessageBox.warning(self, "Error", f"Failed to load file: {file_path}")
            
    def visualize_placement(self):
        """Visualize placement data on the canvas"""
        if not self.current_data:
            return
            
        # Save current view limits if they exist
        if hasattr(self.canvas, 'axes') and self.canvas.axes:
            old_xlim = self.canvas.axes.get_xlim()
            old_ylim = self.canvas.axes.get_ylim()
            had_previous_view = True
        else:
            had_previous_view = False
        
        # Block signals to prevent layout recalculations
        self.blockSignals(True)
        
        # Save the figure's position and size
        fig_width, fig_height = self.canvas.fig.get_size_inches()
        
        # Disable automatic layout adjustments
        self.canvas.fig.set_tight_layout(False)
        self.canvas.fig.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.1)
        
        # Clear the axes but keep the figure
        self.canvas.axes.clear()
        
        # If there was a colorbar, remove it
        if hasattr(self, 'cbar') and self.cbar:
            try:
                self.cbar.remove()
            except:
                pass
            self.cbar = None
        
        try:
            # Create cell visualizations
            cell_patches, thermal_values = self.create_cell_patches(self.current_data)
            
            # Create connections if enabled
            if self.show_connections:
                connection_segments = self.create_connection_lines(self.current_data)
                
                # Draw connections first (so they're behind cells)
                for line, weight in connection_segments:
                    self.canvas.axes.add_line(line)
            
            # Draw cells
            for polygon, label, x, y, area in cell_patches:
                self.canvas.axes.add_patch(polygon)
                
                # Add cell label if it has one and labels are enabled
                if self.show_labels and label and area > 1.5:
                    # Scale font with cell size
                    font_size = max(6, min(10, area / 5))
                    
                    self.canvas.axes.text(x, y, label, 
                                        ha='center', va='center', 
                                        fontsize=font_size, 
                                        fontweight='bold', 
                                        color='white')
                    
            # Set plot limits based on field size or previous view
            field = self.current_data.get('metadata', {}).get('field', {})
            rows = field.get('rows', 20)
            cols = field.get('cols', 20)
            
            # Restore previous view if it existed, otherwise set default view
            if had_previous_view:
                self.canvas.axes.set_xlim(old_xlim)
                self.canvas.axes.set_ylim(old_ylim)
            else:
                self.canvas.axes.set_xlim(-1, cols + 1)
                self.canvas.axes.set_ylim(-1, rows + 1)
            
            # Make sure aspect ratio remains equal regardless of window size
            self.canvas.axes.set_aspect('equal')
            
            # Set title and labels
            self.canvas.axes.set_title('IC Placement Visualization', fontsize=16)
            self.canvas.axes.set_xlabel('X Coordinate', fontsize=12)
            self.canvas.axes.set_ylabel('Y Coordinate', fontsize=12)
            
            # Create a fixed position axes for colorbar
            if len(thermal_values) > 0:
                if not hasattr(self, 'cbar_ax') or self.cbar_ax not in self.canvas.fig.axes:
                    self.cbar_ax = self.canvas.fig.add_axes([0.88, 0.1, 0.03, 0.8])
                else:
                    self.cbar_ax.clear()
                
                # Create colorbar in the fixed position
                sm = ScalarMappable(cmap=plt.get_cmap(self.color_map_name), norm=self.thermal_norm)
                sm.set_array([])
                self.cbar = self.canvas.fig.colorbar(sm, cax=self.cbar_ax, label='Thermal Value')
            
            # Update the grid
            self.canvas.show_grid = self.show_grid
            self.canvas.update_grid()
            
            # Restore figure size
            self.canvas.fig.set_size_inches(fig_width, fig_height)
            
        except Exception as e:
            QMessageBox.warning(self, "Visualization Error", f"Error visualizing placement: {str(e)}")
            traceback.print_exc()
        finally:
            # Unblock signals
            self.blockSignals(False)
    
    def create_cell_patches(self, data):
        """Create matplotlib patches for cells"""
        patches_list = []
        thermal_values = []
        
        # Find cell features
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
                    thermal_values.append(thermal_value)
                    label = feature.get('properties', {}).get('name', '')
                    
                    try:
                        xy = np.array(coords)
                        
                        # Skip cells with no coordinates
                        if xy.size == 0:
                            continue
                            
                        # Calculate centroid and area for label positioning and sizing
                        x = np.mean([p[0] for p in xy])
                        y = np.mean([p[1] for p in xy])
                        
                        # Calculate area
                        xmin, ymin = xy.min(axis=0)
                        xmax, ymax = xy.max(axis=0)
                        width = xmax - xmin
                        height = ymax - ymin
                        area = width * height
                        
                        # Create the polygon patch
                        polygon = patches.Polygon(
                            xy, closed=True, fill=True,
                            facecolor='red', alpha=0.7,  # Will be updated later
                            edgecolor='black', linewidth=0.8
                        )
                        
                        patches_list.append((polygon, label, x, y, area))
                    except Exception as e:
                        print(f"Error processing cell: {e}")
                        continue
        
        # Normalize thermal values for coloring
        if thermal_values:
            self.thermal_norm = Normalize(min(thermal_values), max(thermal_values))
            
            # Apply colors based on thermal values
            cmap = plt.get_cmap(self.color_map_name)
            for i, (polygon, _, _, _, _) in enumerate(patches_list):
                if i < len(thermal_values):
                    if self.thermal_view:
                        color = cmap(self.thermal_norm(thermal_values[i]))
                        polygon.set_facecolor(color)
                    else:
                        # Use a simpler coloring scheme when not in thermal view
                        polygon.set_facecolor('lightblue')
                        polygon.set_alpha(0.7)
        else:
            self.thermal_norm = Normalize(0, 1)
            
        return patches_list, thermal_values
        
    def create_connection_lines(self, data):
        """Create matplotlib lines for connections"""
        segments = []
        weights = []
        
        # Find connection features
        for feature in data.get('features', []):
            if feature.get('properties', {}).get('type') == 'connection':
                geometry = feature.get('geometry', {})
                if geometry.get('type') == 'LineString':
                    coords = geometry.get('coordinates', [])
                    if len(coords) >= 2:
                        weight = feature.get('properties', {}).get('weight', 0)
                        weights.append(weight)
                        segments.append((coords[0], coords[1]))
        
        # Normalize weights
        if weights:
            weight_norm = Normalize(min(weights), max(weights))
        else:
            weight_norm = Normalize(0, 1)
            
        # Create line segments
        line_segments = []
        for i, (start, end) in enumerate(segments):
            if i < len(weights):
                # Scale line width with weight
                line_width = 0.5 + 3 * weight_norm(weights[i])
                
                # Create orthogonal lines (with right angles)
                # Instead of direct diagonal, use two segments: horizontal then vertical
                x1, y1 = start
                x2, y2 = end
                
                # Create the horizontal segment
                line1 = plt.Line2D(
                    [x1, x2], [y1, y1],
                    linewidth=line_width, color='blue', alpha=0.4
                )
                
                # Create the vertical segment
                line2 = plt.Line2D(
                    [x2, x2], [y1, y2],
                    linewidth=line_width, color='blue', alpha=0.4
                )
                
                line_segments.append((line1, weights[i]))
                line_segments.append((line2, weights[i]))
                
        return line_segments               

    def toggle_connections(self):
        """Toggle connection visibility"""
        self.show_connections = self.toggle_connections_action.isChecked()
        self.refresh_visualization()
        
    def toggle_grid(self):
        """Toggle grid visibility"""
        self.show_grid = self.toggle_grid_action.isChecked()
        
        if hasattr(self.canvas, 'axes') and self.canvas.axes:
            # Update the canvas grid setting
            self.canvas.show_grid = self.show_grid
            
            # Update the grid
            self.canvas.update_grid()
      
    def toggle_labels(self):
        """Toggle label visibility"""
        self.show_labels = self.toggle_labels_action.isChecked()
        self.refresh_visualization()
        
    def toggle_thermal_view(self):
        """Toggle between thermal view and regular view"""
        self.thermal_view = self.toggle_thermal_action.isChecked()
        self.refresh_visualization()
        
    def change_colormap(self, cmap_name):
        """Change the colormap used for thermal visualization"""
        self.color_map_name = cmap_name
        self.refresh_visualization()       
    
    def refresh_visualization(self):
        """Refresh the visualization with current settings, maintaining the current view"""
        # Only refresh if we have data
        if self.current_data:
            self.visualize_placement()            
        
    def zoom_in(self):
        """Zoom in on the visualization"""
        xlim = self.canvas.axes.get_xlim()
        ylim = self.canvas.axes.get_ylim()
        
        # Calculate center point
        xcenter = (xlim[0] + xlim[1]) / 2
        ycenter = (ylim[0] + ylim[1]) / 2
        
        # Calculate new limits (zoom in by 20%)
        xrange = (xlim[1] - xlim[0]) * 0.8
        yrange = (ylim[1] - ylim[0]) * 0.8
        
        # Set new limits
        self.canvas.axes.set_xlim(xcenter - xrange / 2, xcenter + xrange / 2)
        self.canvas.axes.set_ylim(ycenter - yrange / 2, ycenter + yrange / 2)
        
        self.canvas.draw()
        
    def zoom_out(self):
        """Zoom out on the visualization"""
        xlim = self.canvas.axes.get_xlim()
        ylim = self.canvas.axes.get_ylim()
        
        # Calculate center point
        xcenter = (xlim[0] + xlim[1]) / 2
        ycenter = (ylim[0] + ylim[1]) / 2
        
        # Calculate new limits (zoom out by 20%)
        xrange = (xlim[1] - xlim[0]) * 1.2
        yrange = (ylim[1] - ylim[0]) * 1.2
        
        # Set new limits
        self.canvas.axes.set_xlim(xcenter - xrange / 2, xcenter + xrange / 2)
        self.canvas.axes.set_ylim(ycenter - yrange / 2, ycenter + yrange / 2)
        
        self.canvas.draw()
        
    def reset_view(self):
        """Reset the view to show all cells"""
        if self.current_data:
            field = self.current_data.get('metadata', {}).get('field', {})
            rows = field.get('rows', 20)
            cols = field.get('cols', 20)
            
            self.canvas.axes.set_xlim(-1, cols + 1)
            self.canvas.axes.set_ylim(-1, rows + 1)
            self.canvas.draw()
        
    def resizeEvent(self, event):
        """Handle resize event to prevent layout shifts"""
        super().resizeEvent(event)
        
        # If we have data and canvas, update visualization without changing layout
        if hasattr(self, 'current_data') and self.current_data and hasattr(self, 'canvas'):
            # Save figure size
            fig_width, fig_height = self.canvas.fig.get_size_inches()
            
            # Recalculate canvas size if needed
            self.canvas.fig.tight_layout()
            
            # Restore size
            self.canvas.fig.set_size_inches(fig_width, fig_height)
            
            # Update canvas
            self.canvas.draw()
            
    def show_cell_info(self, event):
        """Show cell information on mouse hover"""
        if event.inaxes == self.canvas.axes and hasattr(self, 'current_data') and self.current_data:
            x, y = event.xdata, event.ydata
            
            # Find the cell at the cursor position
            for feature in self.current_data.get('features', []):
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
                            
                        if self.point_in_polygon(x, y, coords):
                            # Found the cell at cursor position
                            properties = feature.get('properties', {})
                            name = properties.get('name', 'Unknown')
                            cell_id = properties.get('id', 'Unknown')
                            thermal = properties.get('thermal_value', 0)
                            power = properties.get('power_density', 0)
                            
                            info_text = f"Cell: {name} (ID: {cell_id}) - Thermal: {thermal:.2f}, Power: {power:.2f}"
                            self.status_label.setText(info_text)
                            return
                            
            # No cell found at cursor position
            self.status_label.setText("Ready")
            
    def point_in_polygon(self, x, y, polygon):
        """Check if a point is inside a polygon using ray casting algorithm"""
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
            
        return inside
        
    def save_current_view(self):
        """Save the current view as an image"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "PNG Files (*.png);;PDF Files (*.pdf);;SVG Files (*.svg);;All Files (*.*)")
            
        if file_path:
            self.canvas.fig.savefig(file_path, dpi=300, bbox_inches='tight')
            QMessageBox.information(self, "Success", f"Image saved to {file_path}")
            
    def show_metrics(self):
        """Show metrics for the current placement"""
        if not self.current_data:
            QMessageBox.warning(self, "Error", "No placement data loaded")
            return
            
        try:
            # Extract metrics
            metadata = self.current_data.get('metadata', {})
            cell_count = metadata.get('cell_count', 0)
            connection_count = metadata.get('connection_count', 0)
            total_weight = metadata.get('total_connection_weight', 0)
            
            # Calculate average connection length
            total_length = 0
            conn_count = 0
            for feature in self.current_data.get('features', []):
                if feature.get('properties', {}).get('type') == 'connection':
                    coords = feature.get('geometry', {}).get('coordinates', [])
                    if len(coords) >= 2:
                        x1, y1 = coords[0]
                        x2, y2 = coords[1]
                        length = abs(x2 - x1) + abs(y2 - y1)
                        weight = feature.get('properties', {}).get('weight', 1)
                        total_length += length * weight
                        conn_count += 1
            
            avg_length = total_length / conn_count if conn_count > 0 else 0
            
            # Calculate thermal metrics
            high_thermal_cells = []
            for feature in self.current_data.get('features', []):
                if feature.get('properties', {}).get('type') != 'connection':
                    thermal_value = feature.get('properties', {}).get('thermal_value', 0)
                    if thermal_value > 0.7:
                        geometry = feature.get('geometry', {})
                        coords_data = geometry.get('coordinates', [])
                        if coords_data:
                            # Get valid coordinates
                            coords = []
                            if len(coords_data) == 1 and isinstance(coords_data[0], list):
                                if coords_data[0] and isinstance(coords_data[0][0], list):
                                    coords = coords_data[0]
                            else:
                                coords = coords_data
                                
                            if coords:
                                # Calculate centroid
                                centroid_x = sum(c[0] for c in coords) / len(coords)
                                centroid_y = sum(c[1] for c in coords) / len(coords)
                                high_thermal_cells.append((centroid_x, centroid_y))
            
            # Calculate average distance between high thermal cells
            thermal_distances = []
            for i in range(len(high_thermal_cells)):
                for j in range(i+1, len(high_thermal_cells)):
                    x1, y1 = high_thermal_cells[i]
                    x2, y2 = high_thermal_cells[j]
                    distance = abs(x2 - x1) + abs(y2 - y1)
                    thermal_distances.append(distance)
                    
            thermal_clustering = sum(thermal_distances) / len(thermal_distances) if thermal_distances else 0
            
            # Create metrics message
            metrics_text = f"""
            <h3>Placement Metrics</h3>
            <table>
                <tr><td><b>Cells:</b></td><td>{cell_count}</td></tr>
                <tr><td><b>Connections:</b></td><td>{connection_count}</td></tr>
                <tr><td><b>Total Connection Weight:</b></td><td>{total_weight:.2f}</td></tr>
                <tr><td><b>Average Connection Length:</b></td><td>{avg_length:.2f}</td></tr>
                <tr><td><b>Thermal Clustering:</b></td><td>{thermal_clustering:.2f}</td></tr>
            </table>
            
            <p>Lower thermal clustering indicates better separation of high-temperature components.</p>
            """
            
            QMessageBox.information(self, "Placement Metrics", metrics_text)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error calculating metrics: {str(e)}")
