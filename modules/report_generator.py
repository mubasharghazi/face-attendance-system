"""
Report Generator Module
Handles report generation and export functionality.
"""

import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict
import os
from database.db_manager import DatabaseManager


class ReportGenerator:
    """Generates attendance reports in various formats."""
    
    def __init__(self, db_manager: DatabaseManager, export_dir: str):
        """
        Initialize report generator.
        
        Args:
            db_manager: Database manager instance
            export_dir: Directory for exported reports
        """
        self.db = db_manager
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
    
    def generate_daily_report(self, date_str: str) -> pd.DataFrame:
        """
        Generate daily attendance report.
        
        Args:
            date_str: Date in YYYY-MM-DD format
        
        Returns:
            DataFrame with attendance data
        """
        records = self.db.get_attendance_by_date(date_str)
        
        if not records:
            return pd.DataFrame(columns=['Student ID', 'Name', 'Department', 'Batch', 'Time', 'Status'])
        
        df = pd.DataFrame(records)
        df = df.rename(columns={
            'student_id': 'Student ID',
            'name': 'Name',
            'department': 'Department',
            'batch': 'Batch',
            'time': 'Time',
            'status': 'Status'
        })
        
        # Select and order columns
        columns = ['Student ID', 'Name', 'Department', 'Batch', 'Time', 'Status']
        df = df[[col for col in columns if col in df.columns]]
        
        return df
    
    def generate_student_report(self, student_id: str,
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Generate attendance report for a specific student.
        
        Args:
            student_id: Student ID
            start_date: Start date (optional)
            end_date: End date (optional)
        
        Returns:
            DataFrame with student attendance history
        """
        records = self.db.get_attendance_by_student(student_id, start_date, end_date)
        
        if not records:
            return pd.DataFrame(columns=['Date', 'Time', 'Status'])
        
        df = pd.DataFrame(records)
        df = df.rename(columns={
            'date': 'Date',
            'time': 'Time',
            'status': 'Status'
        })
        
        # Select columns
        columns = ['Date', 'Time', 'Status']
        df = df[[col for col in columns if col in df.columns]]
        
        return df
    
    def generate_date_range_report(self, start_date: str, end_date: str,
                                   department: Optional[str] = None,
                                   batch: Optional[str] = None) -> pd.DataFrame:
        """
        Generate report for a date range with optional filters.
        
        Args:
            start_date: Start date
            end_date: End date
            department: Department filter (optional)
            batch: Batch filter (optional)
        
        Returns:
            DataFrame with attendance data
        """
        records = self.db.get_attendance_by_date_range(start_date, end_date, department, batch)
        
        if not records:
            return pd.DataFrame(columns=['Student ID', 'Name', 'Department', 'Batch', 'Date', 'Time', 'Status'])
        
        df = pd.DataFrame(records)
        df = df.rename(columns={
            'student_id': 'Student ID',
            'name': 'Name',
            'department': 'Department',
            'batch': 'Batch',
            'date': 'Date',
            'time': 'Time',
            'status': 'Status'
        })
        
        # Select and order columns
        columns = ['Student ID', 'Name', 'Department', 'Batch', 'Date', 'Time', 'Status']
        df = df[[col for col in columns if col in df.columns]]
        
        return df
    
    def generate_department_report(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Generate department-wise attendance statistics.
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with department statistics
        """
        records = self.db.get_attendance_by_date_range(start_date, end_date)
        
        if not records:
            return pd.DataFrame(columns=['Department', 'Total Students', 'Total Present', 'Attendance %'])
        
        df = pd.DataFrame(records)
        
        # Group by department
        dept_stats = df.groupby('department').agg({
            'student_id': 'nunique',
            'status': lambda x: (x == 'Present').sum()
        }).reset_index()
        
        dept_stats.columns = ['Department', 'Total Students', 'Total Present']
        
        # Calculate percentage
        dept_stats['Attendance %'] = (
            (dept_stats['Total Present'] / dept_stats['Total Students']) * 100
        ).round(2)
        
        return dept_stats
    
    def generate_defaulters_report(self, threshold: float = 75.0,
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Generate report of students with low attendance.
        
        Args:
            threshold: Minimum attendance percentage
            start_date: Start date (optional)
            end_date: End date (optional)
        
        Returns:
            DataFrame with defaulters
        """
        students = self.db.get_all_students()
        defaulters_data = []
        
        for student in students:
            records = self.db.get_attendance_by_student(
                student['student_id'], start_date, end_date
            )
            
            if records:
                present_count = sum(1 for r in records if r['status'] == 'Present')
                total_days = len(records)
                percentage = round((present_count / total_days) * 100, 2)
                
                if percentage < threshold:
                    defaulters_data.append({
                        'Student ID': student['student_id'],
                        'Name': student['name'],
                        'Department': student['department'],
                        'Batch': student['batch'],
                        'Present Days': present_count,
                        'Total Days': total_days,
                        'Attendance %': percentage
                    })
        
        if not defaulters_data:
            return pd.DataFrame(columns=['Student ID', 'Name', 'Department', 'Batch', 
                                        'Present Days', 'Total Days', 'Attendance %'])
        
        df = pd.DataFrame(defaulters_data)
        df = df.sort_values('Attendance %')
        
        return df
    
    def export_to_csv(self, dataframe: pd.DataFrame, filename: str) -> tuple[bool, str]:
        """
        Export dataframe to CSV file.
        
        Args:
            dataframe: Data to export
            filename: Output filename (without path)
        
        Returns:
            Tuple of (success, filepath or error message)
        """
        try:
            filepath = os.path.join(self.export_dir, filename)
            dataframe.to_csv(filepath, index=False)
            return True, filepath
        except Exception as e:
            return False, f"Error exporting to CSV: {str(e)}"
    
    def export_to_excel(self, dataframe: pd.DataFrame, filename: str,
                       sheet_name: str = 'Attendance') -> tuple[bool, str]:
        """
        Export dataframe to Excel file.
        
        Args:
            dataframe: Data to export
            filename: Output filename (without path)
            sheet_name: Sheet name in Excel file
        
        Returns:
            Tuple of (success, filepath or error message)
        """
        try:
            filepath = os.path.join(self.export_dir, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets[sheet_name]
                for idx, col in enumerate(dataframe.columns):
                    max_length = max(
                        dataframe[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            return True, filepath
        except Exception as e:
            return False, f"Error exporting to Excel: {str(e)}"
    
    def generate_summary_statistics(self, start_date: str, end_date: str) -> Dict:
        """
        Generate summary statistics for a date range.
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            Dictionary with statistics
        """
        records = self.db.get_attendance_by_date_range(start_date, end_date)
        students = self.db.get_all_students()
        
        total_students = len(students)
        total_records = len(records)
        present_records = sum(1 for r in records if r['status'] == 'Present')
        
        # Calculate unique dates
        unique_dates = set(r['date'] for r in records)
        total_days = len(unique_dates)
        
        # Calculate average attendance
        avg_attendance = 0.0
        if total_days > 0 and total_students > 0:
            avg_attendance = (present_records / (total_days * total_students)) * 100
        
        return {
            'total_students': total_students,
            'total_days': total_days,
            'total_records': total_records,
            'present_records': present_records,
            'average_attendance': round(avg_attendance, 2),
            'start_date': start_date,
            'end_date': end_date
        }
    
    def get_monthly_summary(self, year: int, month: int) -> pd.DataFrame:
        """
        Generate monthly attendance summary.
        
        Args:
            year: Year
            month: Month (1-12)
        
        Returns:
            DataFrame with daily attendance counts
        """
        import calendar
        
        # Get date range for month
        _, last_day = calendar.monthrange(year, month)
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        
        records = self.db.get_attendance_by_date_range(start_date, end_date)
        
        if not records:
            return pd.DataFrame(columns=['Date', 'Present Count', 'Attendance %'])
        
        df = pd.DataFrame(records)
        
        # Group by date
        daily_stats = df.groupby('date').agg({
            'status': lambda x: (x == 'Present').sum()
        }).reset_index()
        
        daily_stats.columns = ['Date', 'Present Count']
        
        total_students = self.db.get_total_students()
        if total_students > 0:
            daily_stats['Attendance %'] = (
                (daily_stats['Present Count'] / total_students) * 100
            ).round(2)
        else:
            daily_stats['Attendance %'] = 0
        
        return daily_stats
    
    def generate_summary_report(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Generate summary report for date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            DataFrame with summary statistics
        """
        records = self.db.get_attendance_by_date_range(start_date, end_date)
        
        if not records:
            return pd.DataFrame(columns=['Metric', 'Value'])
        
        df = pd.DataFrame(records)
        
        # Calculate statistics
        total_students = self.db.get_total_students()
        unique_dates = df['time'].apply(lambda x: x.split()[0]).nunique()
        total_records = len(records)
        present_count = len([r for r in records if r['status'] == 'Present'])
        absent_count = len([r for r in records if r['status'] == 'Absent'])
        late_count = len([r for r in records if r['status'] == 'Late'])
        
        # Calculate attendance rate
        if total_students > 0 and unique_dates > 0:
            attendance_rate = (present_count / (total_students * unique_dates)) * 100
        else:
            attendance_rate = 0
        
        # Create summary dataframe
        summary_data = {
            'Metric': [
                'Total Students',
                'Total Days',
                'Total Records',
                'Present',
                'Absent',
                'Late',
                'Average Attendance Rate'
            ],
            'Value': [
                total_students,
                unique_dates,
                total_records,
                present_count,
                absent_count,
                late_count,
                f"{attendance_rate:.2f}%"
            ]
        }
        
        return pd.DataFrame(summary_data)
    
    def generate_department_report(self, department: str, 
                                  start_date: str, end_date: str) -> pd.DataFrame:
        """
        Generate attendance report for a specific department.
        
        Args:
            department: Department name
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            DataFrame with department attendance data
        """
        records = self.db.get_attendance_by_date_range(start_date, end_date)
        
        if not records:
            return pd.DataFrame(columns=['Student ID', 'Name', 'Date', 'Status'])
        
        # Filter by department
        dept_records = []
        for record in records:
            student = self.db.get_student(record['student_id'])
            if student and student.get('department') == department:
                dept_records.append(record)
        
        if not dept_records:
            return pd.DataFrame(columns=['Student ID', 'Name', 'Date', 'Status'])
        
        df = pd.DataFrame(dept_records)
        
        # Extract date from time
        df['Date'] = df['time'].apply(lambda x: x.split()[0] if ' ' in x else x)
        
        # Rename and select columns
        df = df.rename(columns={
            'student_id': 'Student ID',
            'name': 'Name',
            'status': 'Status'
        })
        
        columns = ['Student ID', 'Name', 'Date', 'Status']
        df = df[[col for col in columns if col in df.columns]]
        
        return df
    
    def export_to_pdf(self, dataframe: pd.DataFrame, filename: str) -> tuple[bool, str]:
        """
        Export dataframe to PDF.
        
        Args:
            dataframe: DataFrame to export
            filename: Output filename
        
        Returns:
            Tuple of (success, message)
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            
            # Ensure filename has correct extension
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            # Create PDF
            doc = SimpleDocTemplate(filename, pagesize=A4)
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            title = Paragraph("<b>Attendance Report</b>", styles['Title'])
            elements.append(title)
            
            # Prepare data for table
            data = [dataframe.columns.tolist()] + dataframe.values.tolist()
            
            # Create table
            table = Table(data)
            
            # Add style
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            return True, f"Report exported to {filename}"
            
        except ImportError:
            return False, "reportlab library not installed. Install with: pip install reportlab"
        except Exception as e:
            return False, f"Failed to export PDF: {str(e)}"
