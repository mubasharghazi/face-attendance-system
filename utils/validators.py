"""
Validators Module
Input validation functions for the application.
"""

import re
import os
from typing import Optional


def validate_student_id(student_id: str) -> tuple[bool, Optional[str]]:
    """
    Validate student ID.
    
    Args:
        student_id: Student ID to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not student_id or not student_id.strip():
        return False, "Student ID is required"
    
    if len(student_id.strip()) < 2:
        return False, "Student ID must be at least 2 characters"
    
    if len(student_id.strip()) > 50:
        return False, "Student ID must be less than 50 characters"
    
    # Allow alphanumeric and some special characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', student_id.strip()):
        return False, "Student ID can only contain letters, numbers, hyphens, and underscores"
    
    return True, None


def validate_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate student name.
    
    Args:
        name: Name to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Name is required"
    
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name.strip()) > 100:
        return False, "Name must be less than 100 characters"
    
    # Allow letters, spaces, and common name characters
    if not re.match(r'^[a-zA-Z\s.\'-]+$', name.strip()):
        return False, "Name can only contain letters, spaces, dots, hyphens, and apostrophes"
    
    return True, None


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate email address.
    
    Args:
        email: Email to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email or not email.strip():
        # Email is optional
        return True, None
    
    # Basic email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.strip()):
        return False, "Invalid email format"
    
    return True, None


def validate_department(department: str) -> tuple[bool, Optional[str]]:
    """
    Validate department.
    
    Args:
        department: Department to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not department or not department.strip():
        # Department is optional
        return True, None
    
    if len(department.strip()) > 100:
        return False, "Department must be less than 100 characters"
    
    return True, None


def validate_batch(batch: str) -> tuple[bool, Optional[str]]:
    """
    Validate batch/year.
    
    Args:
        batch: Batch to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not batch or not batch.strip():
        # Batch is optional
        return True, None
    
    if len(batch.strip()) > 50:
        return False, "Batch must be less than 50 characters"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and invalid characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\.\.', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:250] + ext
    
    return filename


def validate_threshold(threshold: float) -> tuple[bool, Optional[str]]:
    """
    Validate recognition threshold.
    
    Args:
        threshold: Threshold value
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        threshold_value = float(threshold)
        if threshold_value < 0.3 or threshold_value > 1.0:
            return False, "Threshold must be between 0.3 and 1.0"
        return True, None
    except (ValueError, TypeError):
        return False, "Threshold must be a number"
