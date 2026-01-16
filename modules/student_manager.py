"""
Student Manager Module
Handles student CRUD operations.
"""

import os
from typing import Optional, List, Dict, Any
from database.db_manager import DatabaseManager
from utils.validators import (
    validate_student_id, validate_name, validate_email,
    validate_department, validate_batch
)


class StudentManager:
    """Manages student-related operations."""
    
    def __init__(self, db_manager: DatabaseManager, image_dir: str):
        """
        Initialize student manager.
        
        Args:
            db_manager: Database manager instance
            image_dir: Directory for storing student images
        """
        self.db = db_manager
        self.image_dir = image_dir
        os.makedirs(image_dir, exist_ok=True)
    
    def register_student(self, student_id: str, name: str, face_encoding: Any,
                        email: Optional[str] = None, department: Optional[str] = None,
                        batch: Optional[str] = None, photo_path: Optional[str] = None) -> tuple[bool, str]:
        """
        Register a new student.
        
        Args:
            student_id: Unique student ID
            name: Student name
            face_encoding: Face encoding array
            email: Student email (optional)
            department: Student department (optional)
            batch: Student batch (optional)
            photo_path: Path to student photo (optional)
        
        Returns:
            Tuple of (success, message)
        """
        # Validate inputs
        is_valid, error = validate_student_id(student_id)
        if not is_valid:
            return False, error
        
        is_valid, error = validate_name(name)
        if not is_valid:
            return False, error
        
        is_valid, error = validate_email(email or "")
        if not is_valid:
            return False, error
        
        is_valid, error = validate_department(department or "")
        if not is_valid:
            return False, error
        
        is_valid, error = validate_batch(batch or "")
        if not is_valid:
            return False, error
        
        # Check if student already exists
        if self.db.student_exists(student_id):
            return False, f"Student ID '{student_id}' already exists."
        
        # Add to database
        success = self.db.add_student(
            student_id=student_id.strip(),
            name=name.strip(),
            face_encoding=face_encoding,
            email=email.strip() if email else None,
            department=department.strip() if department else None,
            batch=batch.strip() if batch else None,
            photo_path=photo_path
        )
        
        if success:
            return True, "Student registered successfully."
        else:
            return False, "Failed to register student. Please try again."
    
    def get_student(self, student_id: str) -> Optional[Dict]:
        """
        Get student by ID.
        
        Args:
            student_id: Student ID
        
        Returns:
            Student data or None
        """
        return self.db.get_student(student_id)
    
    def get_all_students(self) -> List[Dict]:
        """
        Get all registered students.
        
        Returns:
            List of student dictionaries
        """
        return self.db.get_all_students()
    
    def update_student(self, student_id: str, name: Optional[str] = None,
                      email: Optional[str] = None, department: Optional[str] = None,
                      batch: Optional[str] = None) -> tuple[bool, str]:
        """
        Update student information.
        
        Args:
            student_id: Student ID
            name: New name (optional)
            email: New email (optional)
            department: New department (optional)
            batch: New batch (optional)
        
        Returns:
            Tuple of (success, message)
        """
        # Check if student exists
        if not self.db.student_exists(student_id):
            return False, "Student not found."
        
        # Validate inputs
        if name is not None:
            is_valid, error = validate_name(name)
            if not is_valid:
                return False, error
        
        if email is not None:
            is_valid, error = validate_email(email)
            if not is_valid:
                return False, error
        
        if department is not None:
            is_valid, error = validate_department(department)
            if not is_valid:
                return False, error
        
        if batch is not None:
            is_valid, error = validate_batch(batch)
            if not is_valid:
                return False, error
        
        # Update
        success = self.db.update_student(
            student_id=student_id,
            name=name.strip() if name else None,
            email=email.strip() if email else None,
            department=department.strip() if department else None,
            batch=batch.strip() if batch else None
        )
        
        if success:
            return True, "Student updated successfully."
        else:
            return False, "Failed to update student."
    
    def delete_student(self, student_id: str) -> tuple[bool, str]:
        """
        Delete a student.
        
        Args:
            student_id: Student ID
        
        Returns:
            Tuple of (success, message)
        """
        if not self.db.student_exists(student_id):
            return False, "Student not found."
        
        # Get student to delete photo
        student = self.db.get_student(student_id)
        
        # Delete from database
        success = self.db.delete_student(student_id)
        
        if success:
            # Delete photo file if exists
            if student and student.get('photo_path'):
                try:
                    if os.path.exists(student['photo_path']):
                        os.remove(student['photo_path'])
                except Exception as e:
                    print(f"Error deleting photo: {e}")
            
            return True, "Student deleted successfully."
        else:
            return False, "Failed to delete student."
    
    def search_students(self, search_term: str) -> List[Dict]:
        """
        Search students by name, ID, or department.
        
        Args:
            search_term: Search keyword
        
        Returns:
            List of matching students
        """
        return self.db.search_students(search_term)
    
    def get_student_count(self) -> int:
        """
        Get total number of registered students.
        
        Returns:
            Student count
        """
        return self.db.get_total_students()
    
    def get_departments(self) -> List[str]:
        """
        Get list of all departments.
        
        Returns:
            List of department names
        """
        return self.db.get_departments()
    
    def get_batches(self) -> List[str]:
        """
        Get list of all batches.
        
        Returns:
            List of batch names
        """
        return self.db.get_batches()
    
    def get_student_image_path(self, student_id: str) -> str:
        """
        Get the image path for a student.
        
        Args:
            student_id: Student ID
        
        Returns:
            Path where student image should be stored
        """
        return os.path.join(self.image_dir, f"{student_id}.jpg")
    
    def save_student_photo(self, student_id: str, image_data) -> Optional[str]:
        """
        Save student photo to disk.
        
        Args:
            student_id: Student ID
            image_data: Image data (cv2 image or PIL Image)
        
        Returns:
            Path to saved image or None if failed
        """
        try:
            import cv2
            photo_path = self.get_student_image_path(student_id)
            
            # Save image
            cv2.imwrite(photo_path, image_data)
            
            return photo_path
        except Exception as e:
            print(f"Error saving photo: {e}")
            return None
