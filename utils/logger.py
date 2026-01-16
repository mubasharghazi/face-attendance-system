"""
Logger Configuration Module
Sets up application-wide logging.
"""

import logging
import os
from datetime import datetime


def setup_logger(log_dir: str = 'logs', log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up application logger.
    
    Args:
        log_dir: Directory for log files
        log_level: Logging level
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log filename with date
    log_filename = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Configure logger
    logger = logging.getLogger('FaceAttendance')
    logger.setLevel(log_level)
    
    # Remove existing handlers safely
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logger()
