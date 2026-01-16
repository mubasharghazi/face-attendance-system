"""
Attendance Manager Module
Handles attendance operations.
"""

from datetime import datetime, date
from typing import Optional, List, Dict
from database.db_manager import DatabaseManager


class AttendanceManager:
    """Manages attendance-related operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize attendance manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def mark_attendance(self, student_id: str, status: str = 'Present') -> tuple[bool, str]:
        """
        Mark attendance for a student.
        
        Args:
            student_id: Student ID
            status: Attendance status (default 'Present')
        
        Returns:
            Tuple of (success, message)
        """
        # Check if student exists
        if not self.db.student_exists(student_id):
            return False, "Student not found."
        
        # Check if already marked today
        if self.db.is_attendance_marked(student_id):
            return False, "Attendance already marked for today."
        
        # Mark attendance
        success = self.db.mark_attendance(student_id, status=status)
        
        if success:
            student = self.db.get_student(student_id)
            student_name = student['name'] if student else student_id
            return True, f"Attendance marked for {student_name}."
        else:
            return False, "Failed to mark attendance."
    
    def is_attendance_marked_today(self, student_id: str) -> bool:
        """
        Check if attendance is marked for student today.
        
        Args:
            student_id: Student ID
        
        Returns:
            True if attendance is marked
        """
        return self.db.is_attendance_marked(student_id)
    
    def get_todays_attendance(self) -> List[Dict]:
        """
        Get all attendance records for today.
        
        Returns:
            List of attendance records
        """
        return self.db.get_attendance_by_date()
    
    def get_attendance_by_date(self, date_str: str) -> List[Dict]:
        """
        Get attendance for a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
        
        Returns:
            List of attendance records
        """
        return self.db.get_attendance_by_date(date_str)
    
    def get_student_attendance_history(self, student_id: str,
                                      start_date: Optional[str] = None,
                                      end_date: Optional[str] = None) -> List[Dict]:
        """
        Get attendance history for a student.
        
        Args:
            student_id: Student ID
            start_date: Start date (optional)
            end_date: End date (optional)
        
        Returns:
            List of attendance records
        """
        return self.db.get_attendance_by_student(student_id, start_date, end_date)
    
    def get_attendance_statistics(self, date_str: Optional[str] = None) -> Dict[str, int]:
        """
        Get attendance statistics for a date.
        
        Args:
            date_str: Date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            Dictionary with statistics
        """
        total_students = self.db.get_total_students()
        present_count = self.db.get_present_count(date_str)
        absent_count = total_students - present_count
        
        attendance_percentage = 0.0
        if total_students > 0:
            attendance_percentage = (present_count / total_students) * 100
        
        return {
            'total_students': total_students,
            'present': present_count,
            'absent': absent_count,
            'percentage': round(attendance_percentage, 2)
        }
    
    def get_recent_attendance(self, limit: int = 10) -> List[Dict]:
        """
        Get recent attendance records.
        
        Args:
            limit: Number of records to retrieve
        
        Returns:
            List of recent attendance records
        """
        return self.db.get_recent_attendance(limit)
    
    def get_attendance_by_date_range(self, start_date: str, end_date: str,
                                    department: Optional[str] = None,
                                    batch: Optional[str] = None) -> List[Dict]:
        """
        Get attendance for a date range with filters.
        
        Args:
            start_date: Start date
            end_date: End date
            department: Department filter (optional)
            batch: Batch filter (optional)
        
        Returns:
            List of attendance records
        """
        return self.db.get_attendance_by_date_range(start_date, end_date, department, batch)
    
    def calculate_student_attendance_percentage(self, student_id: str,
                                               start_date: Optional[str] = None,
                                               end_date: Optional[str] = None) -> float:
        """
        Calculate attendance percentage for a student.
        
        Args:
            student_id: Student ID
            start_date: Start date (optional)
            end_date: End date (optional)
        
        Returns:
            Attendance percentage
        """
        attendance_records = self.db.get_attendance_by_student(student_id, start_date, end_date)
        
        if not attendance_records:
            return 0.0
        
        present_count = sum(1 for record in attendance_records if record['status'] == 'Present')
        total_days = len(attendance_records)
        
        if total_days == 0:
            return 0.0
        
        return round((present_count / total_days) * 100, 2)
    
    def get_defaulters(self, threshold: float = 75.0,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> List[Dict]:
        """
        Get students with attendance below threshold.
        
        Args:
            threshold: Minimum attendance percentage
            start_date: Start date (optional)
            end_date: End date (optional)
        
        Returns:
            List of students with low attendance
        """
        students = self.db.get_all_students()
        defaulters = []
        
        for student in students:
            percentage = self.calculate_student_attendance_percentage(
                student['student_id'], start_date, end_date
            )
            
            if percentage < threshold:
                defaulters.append({
                    'student_id': student['student_id'],
                    'name': student['name'],
                    'department': student['department'],
                    'batch': student['batch'],
                    'attendance_percentage': percentage
                })
        
        # Sort by attendance percentage
        defaulters.sort(key=lambda x: x['attendance_percentage'])
        
        return defaulters
    
    def manual_attendance_entry(self, student_id: str, date_str: str,
                               time_str: str, status: str = 'Present') -> tuple[bool, str]:
        """
        Manually enter attendance for a student.
        
        Args:
            student_id: Student ID
            date_str: Date in YYYY-MM-DD format
            time_str: Time in HH:MM:SS format
            status: Attendance status
        
        Returns:
            Tuple of (success, message)
        """
        # Check if student exists
        if not self.db.student_exists(student_id):
            return False, "Student not found."
        
        # Mark attendance
        success = self.db.mark_attendance(student_id, date_str, time_str, status)
        
        if success:
            return True, "Attendance recorded successfully."
        else:
            return False, "Attendance already exists for this date or failed to record."
