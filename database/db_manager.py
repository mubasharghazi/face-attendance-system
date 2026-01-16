"""
Database Manager Module
Handles all database operations for the Face Attendance System.
"""

import sqlite3
import pickle
import os
from contextlib import contextmanager
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime


class DatabaseManager:
    """Manages database operations with connection pooling and error handling."""
    
    def __init__(self, db_path: str):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database and tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        # Execute schema
        with self.get_connection() as conn:
            conn.executescript(schema)
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    # Student Operations
    
    def add_student(self, student_id: str, name: str, face_encoding: Any,
                   email: Optional[str] = None, department: Optional[str] = None,
                   batch: Optional[str] = None, photo_path: Optional[str] = None) -> bool:
        """
        Add a new student to the database.
        
        Args:
            student_id: Unique student identifier
            name: Student name
            face_encoding: Face encoding array (numpy array)
            email: Student email (optional)
            department: Student department (optional)
            batch: Student batch/year (optional)
            photo_path: Path to student photo (optional)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Serialize face encoding
            encoding_blob = pickle.dumps(face_encoding)
            
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO students (student_id, name, email, department, batch, 
                                        face_encoding, photo_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (student_id, name, email, department, batch, encoding_blob, photo_path))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Duplicate student_id
            return False
        except Exception as e:
            print(f"Error adding student: {e}")
            return False
    
    def get_student(self, student_id: str) -> Optional[Dict]:
        """
        Retrieve student by ID.
        
        Args:
            student_id: Student identifier
        
        Returns:
            Dict with student data or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT id, student_id, name, email, department, batch,
                           face_encoding, photo_path, registration_date
                    FROM students WHERE student_id = ?
                """, (student_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': row['id'],
                        'student_id': row['student_id'],
                        'name': row['name'],
                        'email': row['email'],
                        'department': row['department'],
                        'batch': row['batch'],
                        'face_encoding': pickle.loads(row['face_encoding']),
                        'photo_path': row['photo_path'],
                        'registration_date': row['registration_date']
                    }
                return None
        except Exception as e:
            print(f"Error getting student: {e}")
            return None
    
    def get_all_students(self) -> List[Dict]:
        """
        Retrieve all students.
        
        Returns:
            List of student dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT id, student_id, name, email, department, batch,
                           face_encoding, photo_path, registration_date
                    FROM students ORDER BY name
                """)
                rows = cursor.fetchall()
                
                students = []
                for row in rows:
                    students.append({
                        'id': row['id'],
                        'student_id': row['student_id'],
                        'name': row['name'],
                        'email': row['email'],
                        'department': row['department'],
                        'batch': row['batch'],
                        'face_encoding': pickle.loads(row['face_encoding']),
                        'photo_path': row['photo_path'],
                        'registration_date': row['registration_date']
                    })
                return students
        except Exception as e:
            print(f"Error getting all students: {e}")
            return []
    
    def update_student(self, student_id: str, name: Optional[str] = None,
                      email: Optional[str] = None, department: Optional[str] = None,
                      batch: Optional[str] = None) -> bool:
        """
        Update student information.
        
        Args:
            student_id: Student identifier
            name: New name (optional)
            email: New email (optional)
            department: New department (optional)
            batch: New batch (optional)
        
        Returns:
            bool: True if successful
        """
        try:
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if email is not None:
                updates.append("email = ?")
                params.append(email)
            if department is not None:
                updates.append("department = ?")
                params.append(department)
            if batch is not None:
                updates.append("batch = ?")
                params.append(batch)
            
            if not updates:
                return True
            
            params.append(student_id)
            query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = ?"
            
            with self.get_connection() as conn:
                conn.execute(query, params)
                conn.commit()
            return True
        except Exception as e:
            print(f"Error updating student: {e}")
            return False
    
    def delete_student(self, student_id: str) -> bool:
        """
        Delete a student and their attendance records.
        
        Args:
            student_id: Student identifier
        
        Returns:
            bool: True if successful
        """
        try:
            with self.get_connection() as conn:
                # Delete attendance records first
                conn.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
                # Delete student
                conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting student: {e}")
            return False
    
    def student_exists(self, student_id: str) -> bool:
        """
        Check if student exists.
        
        Args:
            student_id: Student identifier
        
        Returns:
            bool: True if student exists
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) as count FROM students WHERE student_id = ?",
                    (student_id,)
                )
                row = cursor.fetchone()
                return row['count'] > 0
        except Exception as e:
            print(f"Error checking student existence: {e}")
            return False
    
    # Attendance Operations
    
    def mark_attendance(self, student_id: str, date: Optional[str] = None,
                       time: Optional[str] = None, status: str = 'Present') -> bool:
        """
        Mark attendance for a student.
        
        Args:
            student_id: Student identifier
            date: Date in YYYY-MM-DD format (defaults to today)
            time: Time in HH:MM:SS format (defaults to now)
            status: Attendance status (default 'Present')
        
        Returns:
            bool: True if successful, False if already marked
        """
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            if time is None:
                time = datetime.now().strftime('%H:%M:%S')
            
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO attendance (student_id, date, time, status)
                    VALUES (?, ?, ?, ?)
                """, (student_id, date, time, status))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Already marked for today
            return False
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return False
    
    def is_attendance_marked(self, student_id: str, date: Optional[str] = None) -> bool:
        """
        Check if attendance is already marked for a student on a date.
        
        Args:
            student_id: Student identifier
            date: Date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            bool: True if attendance is marked
        """
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) as count FROM attendance
                    WHERE student_id = ? AND date = ?
                """, (student_id, date))
                row = cursor.fetchone()
                return row['count'] > 0
        except Exception as e:
            print(f"Error checking attendance: {e}")
            return False
    
    def get_attendance_by_date(self, date: Optional[str] = None) -> List[Dict]:
        """
        Get all attendance records for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            List of attendance records with student info
        """
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT a.id, a.student_id, s.name, a.date, a.time, 
                           a.date || ' ' || a.time as time, a.status,
                           s.department, s.batch
                    FROM attendance a
                    JOIN students s ON a.student_id = s.student_id
                    WHERE a.date = ?
                    ORDER BY a.time DESC
                """, (date,))
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting attendance by date: {e}")
            return []
    
    def get_attendance_by_student(self, student_id: str, 
                                 start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> List[Dict]:
        """
        Get attendance records for a specific student.
        
        Args:
            student_id: Student identifier
            start_date: Start date (optional)
            end_date: End date (optional)
        
        Returns:
            List of attendance records
        """
        try:
            query = """
                SELECT a.id, a.student_id, s.name, a.date, a.time,
                       a.date || ' ' || a.time as time, a.status
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.student_id = ?
            """
            params = [student_id]
            
            if start_date:
                query += " AND a.date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND a.date <= ?"
                params.append(end_date)
            
            query += " ORDER BY a.date DESC, a.time DESC"
            
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting attendance by student: {e}")
            return []
    
    def get_attendance_by_date_range(self, start_date: str, end_date: str,
                                    department: Optional[str] = None,
                                    batch: Optional[str] = None) -> List[Dict]:
        """
        Get attendance records for a date range with optional filters.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            department: Filter by department (optional)
            batch: Filter by batch (optional)
        
        Returns:
            List of attendance records
        """
        try:
            query = """
                SELECT a.id, a.student_id, s.name, a.date, a.time,
                       a.date || ' ' || a.time as time, a.status,
                       s.department, s.batch
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.date BETWEEN ? AND ?
            """
            params = [start_date, end_date]
            
            if department:
                query += " AND s.department = ?"
                params.append(department)
            if batch:
                query += " AND s.batch = ?"
                params.append(batch)
            
            query += " ORDER BY a.date DESC, a.time DESC"
            
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting attendance by date range: {e}")
            return []
    
    # Statistics Operations
    
    def get_total_students(self) -> int:
        """Get total number of registered students."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) as count FROM students")
                row = cursor.fetchone()
                return row['count']
        except Exception as e:
            print(f"Error getting total students: {e}")
            return 0
    
    def get_present_count(self, date: Optional[str] = None) -> int:
        """Get count of present students for a date."""
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) as count FROM attendance
                    WHERE date = ? AND status = 'Present'
                """, (date,))
                row = cursor.fetchone()
                return row['count']
        except Exception as e:
            print(f"Error getting present count: {e}")
            return 0
    
    def get_recent_attendance(self, limit: int = 10) -> List[Dict]:
        """
        Get recent attendance records.
        
        Args:
            limit: Number of records to retrieve
        
        Returns:
            List of recent attendance records
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT a.id, a.student_id, s.name, a.date, a.time,
                           a.date || ' ' || a.time as time, a.status,
                           s.department
                    FROM attendance a
                    JOIN students s ON a.student_id = s.student_id
                    ORDER BY a.date DESC, a.time DESC
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting recent attendance: {e}")
            return []
    
    def search_students(self, search_term: str) -> List[Dict]:
        """
        Search students by name, ID, or department.
        
        Args:
            search_term: Search keyword
        
        Returns:
            List of matching students
        """
        try:
            search_pattern = f"%{search_term}%"
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT id, student_id, name, email, department, batch,
                           photo_path, registration_date
                    FROM students
                    WHERE student_id LIKE ? OR name LIKE ? OR department LIKE ?
                    ORDER BY name
                """, (search_pattern, search_pattern, search_pattern))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error searching students: {e}")
            return []
    
    def get_departments(self) -> List[str]:
        """Get list of all unique departments."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT DISTINCT department FROM students
                    WHERE department IS NOT NULL AND department != ''
                    ORDER BY department
                """)
                rows = cursor.fetchall()
                return [row['department'] for row in rows]
        except Exception as e:
            print(f"Error getting departments: {e}")
            return []
    
    def get_batches(self) -> List[str]:
        """Get list of all unique batches."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT DISTINCT batch FROM students
                    WHERE batch IS NOT NULL AND batch != ''
                    ORDER BY batch
                """)
                rows = cursor.fetchall()
                return [row['batch'] for row in rows]
        except Exception as e:
            print(f"Error getting batches: {e}")
            return []
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path for backup file
        
        Returns:
            bool: True if successful
        """
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Error backing up database: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
        
        Returns:
            bool: True if successful
        """
        try:
            import shutil
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception as e:
            print(f"Error restoring database: {e}")
            return False
    
    def clear_all_data(self) -> bool:
        """
        Clear all data from database (dangerous operation).
        
        Returns:
            bool: True if successful
        """
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM attendance")
                conn.execute("DELETE FROM students")
                conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False
    
    def update_attendance_status(self, student_id: str, date: str, status: str) -> bool:
        """
        Update attendance status for a student on a specific date.
        
        Args:
            student_id: Student ID
            date: Date in YYYY-MM-DD format
            status: New status ('Present', 'Absent', 'Late')
        
        Returns:
            bool: True if successful
        """
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "UPDATE attendance SET status = ? WHERE student_id = ? AND date = ?",
                    (status, student_id, date)
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"Error updating attendance status: {e}")
            return False
    
    def delete_attendance_record(self, student_id: str, date: str) -> bool:
        """
        Delete attendance record for a student on a specific date.
        
        Args:
            student_id: Student ID
            date: Date in YYYY-MM-DD format
        
        Returns:
            bool: True if successful
        """
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "DELETE FROM attendance WHERE student_id = ? AND date = ?",
                    (student_id, date)
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting attendance record: {e}")
            return False
