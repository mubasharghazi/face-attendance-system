"""
Face Recognition Attendance System
Main application entry point.

This is a desktop application for automated attendance marking using
facial recognition technology with a professional GUI interface.

Author: Face Attendance System
Version: 1.0.0
"""

import sys
import os
import configparser
import tkinter as tk
from tkinter import messagebox

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from gui.main_window import MainWindow
from utils.logger import logger


def load_config(config_path='config.ini'):
    """
    Load application configuration from config file.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        ConfigParser object
    """
    config = configparser.ConfigParser()
    
    if os.path.exists(config_path):
        config.read(config_path)
    else:
        logger.warning(f"Config file not found: {config_path}")
        # Create default config
        config['CAMERA'] = {
            'camera_index': '0',
            'frame_width': '640',
            'frame_height': '480',
            'fps': '30'
        }
        config['RECOGNITION'] = {
            'tolerance': '0.6',
            'model': 'hog',
            'process_every_n_frames': '2'
        }
        config['DATABASE'] = {
            'db_path': 'data/database/attendance.db'
        }
        config['PATHS'] = {
            'student_images': 'data/student_images',
            'exports': 'exports',
            'logs': 'logs'
        }
        config['GUI'] = {
            'theme': 'light',
            'window_width': '1200',
            'window_height': '800'
        }
        config['ADMIN'] = {
            'username': 'admin',
            'password_hash': '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'
        }
        
        # Save default config
        with open(config_path, 'w') as f:
            config.write(f)
        logger.info(f"Created default config file: {config_path}")
    
    return config


def create_directories(config):
    """
    Create necessary directories if they don't exist.
    
    Args:
        config: ConfigParser object
    """
    directories = [
        config.get('PATHS', 'student_images', fallback='data/student_images'),
        config.get('PATHS', 'exports', fallback='exports'),
        config.get('PATHS', 'logs', fallback='logs'),
        os.path.dirname(config.get('DATABASE', 'db_path', fallback='data/database/attendance.db'))
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")


def check_dependencies():
    """
    Check if all required dependencies are installed.
    
    Returns:
        Tuple of (success, missing_modules)
    """
    required_modules = [
        'cv2',
        'face_recognition',
        'numpy',
        'pandas',
        'PIL',
        'openpyxl'
    ]
    
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    return len(missing) == 0, missing


def show_startup_error(title, message):
    """
    Show error message box at startup.
    
    Args:
        title: Error title
        message: Error message
    """
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, message)
    root.destroy()


def main():
    """Main application entry point."""
    try:
        logger.info("=" * 60)
        logger.info("Face Recognition Attendance System - Starting")
        logger.info("Version: 1.0.0")
        logger.info("=" * 60)
        
        # Check dependencies
        logger.info("Checking dependencies...")
        deps_ok, missing = check_dependencies()
        
        if not deps_ok:
            error_msg = (
                "Missing required dependencies:\n\n"
                f"{', '.join(missing)}\n\n"
                "Please install them using:\n"
                "pip install -r requirements.txt"
            )
            logger.error(f"Missing dependencies: {missing}")
            show_startup_error("Missing Dependencies", error_msg)
            return 1
        
        logger.info("All dependencies found.")
        
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        logger.info("Configuration loaded successfully.")
        
        # Create directories
        logger.info("Creating necessary directories...")
        create_directories(config)
        logger.info("Directories created/verified.")
        
        # Create main window
        logger.info("Initializing GUI...")
        root = tk.Tk()
        app = MainWindow(root, config)
        
        logger.info("Application started successfully.")
        logger.info("=" * 60)
        
        # Start main loop
        root.mainloop()
        
        logger.info("Application closed normally.")
        return 0
        
    except Exception as e:
        logger.exception("Fatal error during startup:")
        error_msg = (
            f"An error occurred during startup:\n\n"
            f"{str(e)}\n\n"
            "Please check the log file for details."
        )
        show_startup_error("Startup Error", error_msg)
        return 1


if __name__ == "__main__":
    sys.exit(main())
