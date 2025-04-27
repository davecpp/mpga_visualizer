#!/usr/bin/env python3
"""
Runner module for the MPGA GUI application.
Handles running the MultiParametricGA executable in a separate process.
"""

import os
import platform
import tempfile
import json
from PyQt5.QtCore import QThread, pyqtSignal, QProcess

class MPGARunner(QThread):
    """Thread to run the MultiParametricGA executable"""
    progress_update = pyqtSignal(str)
    progress_value = pyqtSignal(int)
    finished_with_result = pyqtSignal(bool, str, str)
    
    def __init__(self, executable_path=None, input_file=None, output_file=None, 
                 config_file=None, focus=None, max_iterations=200):
        """
        Initialize the runner.
        
        Args:
            executable_path (str): Path to the MPGA executable
            input_file (str): Path to the input file
            output_file (str): Path to the output file
            config_file (str): Path to the configuration file
            focus (str): Focus mode (e.g., "WireLength", "Thermal", etc.)
            max_iterations (int): Maximum number of iterations for progress calculation
        """
        super().__init__()
        
        # Set default executable path based on platform if not provided
        if executable_path is None:
            if platform.system() == "Windows":
                self.executable = "MultiParametricGA.exe"
            else:
                self.executable = "./MultiParametricGA"
        else:
            self.executable = executable_path
            
        self.input_file = input_file
        self.output_file = output_file
        self.config_file = config_file
        self.focus = focus
        self.process = None
        self.max_iterations = max_iterations
        self.temp_files = []  # List to track temporary files for cleanup
        
    def create_temp_config_file(self, config_data):
        """
        Create a temporary configuration file.
        
        Args:
            config_data (dict): Configuration data
            
        Returns:
            str: Path to the temporary file or None if creation failed
        """
        try:
            fd, temp_file = tempfile.mkstemp(suffix='.json')
            with os.fdopen(fd, 'w') as f:
                json.dump(config_data, f, indent=4)
            
            # Track the file for later cleanup
            self.temp_files.append(temp_file)
            return temp_file
        except Exception as e:
            self.progress_update.emit(f"Error creating temporary config file: {str(e)}")
            return None
        
    def run(self):
        """Run the optimization process"""
        try:
            # Validate required parameters
            if not self.input_file or not self.output_file:
                self.progress_update.emit("Error: Input and output files must be specified")
                self.finished_with_result.emit(False, "Input and output files must be specified", None)
                return
                
            # Build command
            cmd = [self.executable, f"--input={self.input_file}", f"--output={self.output_file}"]
            
            if self.config_file:
                cmd.append(f"--config={self.config_file}")
                
            if self.focus:
                cmd.append(f"--focus={self.focus}")
                
            # Add verbose flag for more output
            cmd.append("--verbose")
            
            self.progress_update.emit(f"Running command: {' '.join(cmd)}")
            
            # Use QProcess to run the executable
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            
            self.process.start(cmd[0], cmd[1:])
            
            # Check if process started successfully
            if not self.process.waitForStarted(3000):
                self.progress_update.emit("Error: Process failed to start")
                self.finished_with_result.emit(False, "Process failed to start", None)
                return
                
            # Wait for process to finish
            while self.process.state() != QProcess.NotRunning:
                self.process.waitForFinished(100)
                QThread.msleep(50)  # Small delay to prevent high CPU usage
                
            # Check exit code
            exit_code = self.process.exitCode()
            
            if exit_code == 0:
                if os.path.exists(self.output_file):
                    self.progress_update.emit(f"Optimization completed successfully. Output saved to {self.output_file}")
                    self.finished_with_result.emit(True, "", self.output_file)
                else:
                    self.progress_update.emit("Warning: Process completed but output file not found")
                    self.finished_with_result.emit(False, "Output file not found", None)
            else:
                error_output = bytes(self.process.readAllStandardError()).decode('utf-8', errors='ignore')
                self.progress_update.emit(f"Process exited with code {exit_code}")
                self.finished_with_result.emit(False, f"Exit code: {exit_code}\n{error_output}", None)
                
        except Exception as e:
            self.progress_update.emit(f"Error running optimization: {str(e)}")
            self.finished_with_result.emit(False, str(e), None)
        finally:
            # Clean up temporary files
            self.cleanup_temp_files()
            
    def handle_stdout(self):
        """Handle standard output from the process"""
        if not self.process:
            return
            
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode('utf-8', errors='ignore')
        self.progress_update.emit(text.strip())
        
        # Try to parse progress information if available
        try:
            lines = text.strip().split('\n')
            for line in lines:
                if "Iteration" in line and "Avg Fitness" in line:
                    parts = line.split(',')
                    if len(parts) >= 1:
                        iter_part = parts[0].strip()
                        iter_num = int(iter_part.split(' ')[1])
                        # Calculate progress percentage
                        progress = min(int(iter_num / self.max_iterations * 100), 99)
                        self.progress_value.emit(progress)
        except:
            pass
            
    def handle_stderr(self):
        """Handle standard error from the process"""
        if not self.process:
            return
            
        data = self.process.readAllStandardError()
        text = bytes(data).decode('utf-8', errors='ignore')
        self.progress_update.emit(f"Error: {text.strip()}")
        
    def stop(self):
        """Stop the optimization process"""
        if self.process and self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()
                
        # Clean up temporary files
        self.cleanup_temp_files()
                
    def cleanup_temp_files(self):
        """Clean up any temporary files created during the process"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Error cleaning up temporary file {temp_file}: {e}")
                
        # Clear the list
        self.temp_files = []
