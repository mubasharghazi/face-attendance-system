"""
Records Tab Module
View and search attendance records.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry


class RecordsTab:
    """Attendance records tab with search and filter capabilities."""
    
    def __init__(self, parent, db_manager, colors, logger):
        """
        Initialize records tab.
        
        Args:
            parent: Parent widget
            db_manager: Database manager instance
            colors: Color scheme dictionary
            logger: Logger instance
        """
        self.parent = parent
        self.db = db_manager
        self.colors = colors
        self.logger = logger
        
        # State variables
        self.current_records = []
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup records user interface."""
        # Configure grid
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)
        
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=20)
        
        ttk.Label(header_frame, text="Attendance Records", 
                 style='Header.TLabel').pack(side='left')
        
        # Search and filter section
        self._create_search_section()
        
        # Records table
        self._create_records_table()
        
        # Statistics section
        self._create_statistics_section()
        
        # Load initial data (today's records)
        self._load_today_records()
    
    def _create_search_section(self):
        """Create search and filter section."""
        search_frame = ttk.Frame(self.frame, style='Card.TFrame')
        search_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=10)
        
        # Inner frame
        inner_frame = ttk.Frame(search_frame)
        inner_frame.pack(fill='x', padx=20, pady=20)
        
        # First row - Date filters
        date_frame = ttk.Frame(inner_frame)
        date_frame.pack(fill='x', pady=(0, 15))
        
        # Date range
        ttk.Label(date_frame, text="Date Range:").pack(side='left', padx=(0, 10))
        
        ttk.Label(date_frame, text="From:").pack(side='left', padx=(0, 5))
        self.start_date = DateEntry(date_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2,
                                    date_pattern='yyyy-mm-dd')
        self.start_date.pack(side='left', padx=(0, 15))
        
        ttk.Label(date_frame, text="To:").pack(side='left', padx=(0, 5))
        self.end_date = DateEntry(date_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2,
                                  date_pattern='yyyy-mm-dd')
        self.end_date.pack(side='left', padx=(0, 15))
        
        # Quick date buttons
        ttk.Button(date_frame, text="Today", 
                  command=self._load_today_records).pack(side='left', padx=2)
        ttk.Button(date_frame, text="This Week", 
                  command=self._load_week_records).pack(side='left', padx=2)
        ttk.Button(date_frame, text="This Month", 
                  command=self._load_month_records).pack(side='left', padx=2)
        
        # Second row - Search filters
        filter_frame = ttk.Frame(inner_frame)
        filter_frame.pack(fill='x')
        
        # Student ID search
        ttk.Label(filter_frame, text="Student ID:").pack(side='left', padx=(0, 5))
        self.student_id_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.student_id_var, 
                 width=15).pack(side='left', padx=(0, 15))
        
        # Student name search
        ttk.Label(filter_frame, text="Name:").pack(side='left', padx=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.name_var, 
                 width=20).pack(side='left', padx=(0, 15))
        
        # Status filter
        ttk.Label(filter_frame, text="Status:").pack(side='left', padx=(0, 5))
        self.status_var = tk.StringVar(value='All')
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var,
                                   width=12, state='readonly')
        status_combo['values'] = ('All', 'Present', 'Absent', 'Late')
        status_combo.pack(side='left', padx=(0, 15))
        
        # Department filter
        ttk.Label(filter_frame, text="Department:").pack(side='left', padx=(0, 5))
        self.department_var = tk.StringVar(value='All')
        dept_combo = ttk.Combobox(filter_frame, textvariable=self.department_var,
                                 width=15, state='readonly')
        dept_combo['values'] = ('All', 'Computer Science', 'Information Technology', 
                               'Electronics', 'Mechanical', 'Civil', 'Other')
        dept_combo.pack(side='left', padx=(0, 15))
        
        # Search button
        ttk.Button(filter_frame, text="🔍 Search", 
                  command=self._search_records,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        # Clear button
        ttk.Button(filter_frame, text="Clear Filters", 
                  command=self._clear_filters).pack(side='left', padx=5)
    
    def _create_records_table(self):
        """Create records table."""
        table_frame = ttk.Frame(self.frame, style='Card.TFrame')
        table_frame.grid(row=2, column=0, sticky='nsew', padx=20, pady=10)
        
        # Configure grid
        table_frame.rowconfigure(1, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # Header with count
        header = ttk.Frame(table_frame)
        header.grid(row=0, column=0, sticky='ew', padx=20, pady=(20, 10))
        header.columnconfigure(0, weight=1)
        
        ttk.Label(header, text="Records", 
                 style='Title.TLabel').grid(row=0, column=0, sticky='w')
        
        self.count_label = ttk.Label(header, text="0 records", 
                                    style='Info.TLabel')
        self.count_label.grid(row=0, column=1, sticky='e')
        
        # Table container
        table_container = ttk.Frame(table_frame)
        table_container.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0, 20))
        table_container.rowconfigure(0, weight=1)
        table_container.columnconfigure(0, weight=1)
        
        # Create treeview
        columns = ('Date', 'Time', 'Student ID', 'Name', 'Department', 
                  'Batch', 'Status')
        self.records_tree = ttk.Treeview(table_container, columns=columns, 
                                        show='headings', height=15)
        
        # Configure columns
        self.records_tree.heading('Date', text='Date')
        self.records_tree.heading('Time', text='Time')
        self.records_tree.heading('Student ID', text='Student ID')
        self.records_tree.heading('Name', text='Name')
        self.records_tree.heading('Department', text='Department')
        self.records_tree.heading('Batch', text='Batch')
        self.records_tree.heading('Status', text='Status')
        
        self.records_tree.column('Date', width=100, anchor='center')
        self.records_tree.column('Time', width=80, anchor='center')
        self.records_tree.column('Student ID', width=100, anchor='center')
        self.records_tree.column('Name', width=150)
        self.records_tree.column('Department', width=120)
        self.records_tree.column('Batch', width=80, anchor='center')
        self.records_tree.column('Status', width=80, anchor='center')
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_container, orient='vertical', 
                           command=self.records_tree.yview)
        hsb = ttk.Scrollbar(table_container, orient='horizontal', 
                           command=self.records_tree.xview)
        self.records_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack
        self.records_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Context menu
        self._create_context_menu()
    
    def _create_context_menu(self):
        """Create context menu for records table."""
        self.context_menu = tk.Menu(self.records_tree, tearoff=0)
        self.context_menu.add_command(label="View Details", 
                                     command=self._view_record_details)
        self.context_menu.add_command(label="Edit Status", 
                                     command=self._edit_record_status)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Record", 
                                     command=self._delete_record)
        
        # Bind right-click
        self.records_tree.bind('<Button-3>', self._show_context_menu)
    
    def _create_statistics_section(self):
        """Create statistics section."""
        stats_frame = ttk.Frame(self.frame, style='Card.TFrame')
        stats_frame.grid(row=3, column=0, sticky='ew', padx=20, pady=10)
        
        # Inner frame
        inner_frame = ttk.Frame(stats_frame)
        inner_frame.pack(fill='x', padx=20, pady=15)
        
        # Statistics labels
        self.total_label = tk.Label(inner_frame, text="Total: 0", 
                                   font=('Arial', 10, 'bold'),
                                   fg=self.colors['text'])
        self.total_label.pack(side='left', padx=15)
        
        self.present_label = tk.Label(inner_frame, text="Present: 0", 
                                     font=('Arial', 10, 'bold'),
                                     fg=self.colors['success'])
        self.present_label.pack(side='left', padx=15)
        
        self.absent_label = tk.Label(inner_frame, text="Absent: 0", 
                                    font=('Arial', 10, 'bold'),
                                    fg=self.colors['danger'])
        self.absent_label.pack(side='left', padx=15)
        
        self.late_label = tk.Label(inner_frame, text="Late: 0", 
                                  font=('Arial', 10, 'bold'),
                                  fg=self.colors['warning'])
        self.late_label.pack(side='left', padx=15)
    
    def _search_records(self):
        """Search records based on filters."""
        try:
            # Get filter values
            start_date = self.start_date.get_date().strftime('%Y-%m-%d')
            end_date = self.end_date.get_date().strftime('%Y-%m-%d')
            student_id = self.student_id_var.get().strip()
            name = self.name_var.get().strip()
            status = self.status_var.get()
            department = self.department_var.get()
            
            # Get records from database
            records = self.db.get_attendance_by_date_range(start_date, end_date)
            
            # Apply filters
            filtered_records = []
            for record in records:
                # Student ID filter
                if student_id and student_id not in record['student_id']:
                    continue
                
                # Name filter
                if name and name.lower() not in record['name'].lower():
                    continue
                
                # Status filter
                if status != 'All' and record['status'] != status:
                    continue
                
                # Department filter
                if department != 'All':
                    student = self.db.get_student(record['student_id'])
                    if not student or student.get('department') != department:
                        continue
                
                filtered_records.append(record)
            
            # Display results
            self._display_records(filtered_records)
            
            self.logger.info(f'Search completed: {len(filtered_records)} records found')
            
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
            self.logger.error(f'Search failed: {str(e)}')
    
    def _display_records(self, records):
        """
        Display records in table.
        
        Args:
            records: List of attendance records
        """
        # Clear existing items
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        
        self.current_records = records
        
        # Add records to tree
        for record in records:
            # Parse date and time
            datetime_str = record['time']
            try:
                dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                date_str = dt.strftime('%Y-%m-%d')
                time_str = dt.strftime('%H:%M:%S')
            except:
                date_str = datetime_str.split()[0] if ' ' in datetime_str else datetime_str
                time_str = datetime_str.split()[1] if ' ' in datetime_str else ''
            
            # Get student details
            student = self.db.get_student(record['student_id'])
            department = student.get('department', '') if student else ''
            batch = student.get('batch', '') if student else ''
            
            values = (
                date_str,
                time_str,
                record['student_id'],
                record['name'],
                department,
                batch,
                record['status']
            )
            
            # Add with tag based on status
            status = record['status']
            tag = 'present' if status == 'Present' else ('late' if status == 'Late' else 'absent')
            self.records_tree.insert('', 'end', values=values, tags=(tag,))
        
        # Configure tags
        self.records_tree.tag_configure('present', foreground=self.colors['success'])
        self.records_tree.tag_configure('absent', foreground=self.colors['danger'])
        self.records_tree.tag_configure('late', foreground=self.colors['warning'])
        
        # Update statistics
        self._update_statistics(records)
        
        # Update count
        self.count_label.config(text=f"{len(records)} records")
    
    def _update_statistics(self, records):
        """
        Update statistics display.
        
        Args:
            records: List of attendance records
        """
        total = len(records)
        present = len([r for r in records if r['status'] == 'Present'])
        absent = len([r for r in records if r['status'] == 'Absent'])
        late = len([r for r in records if r['status'] == 'Late'])
        
        self.total_label.config(text=f"Total: {total}")
        self.present_label.config(text=f"Present: {present}")
        self.absent_label.config(text=f"Absent: {absent}")
        self.late_label.config(text=f"Late: {late}")
    
    def _clear_filters(self):
        """Clear all filters."""
        self.student_id_var.set('')
        self.name_var.set('')
        self.status_var.set('All')
        self.department_var.set('All')
        self.start_date.set_date(datetime.now())
        self.end_date.set_date(datetime.now())
        self._load_today_records()
    
    def _load_today_records(self):
        """Load today's records."""
        today = datetime.now()
        self.start_date.set_date(today)
        self.end_date.set_date(today)
        self._search_records()
    
    def _load_week_records(self):
        """Load this week's records."""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        self.start_date.set_date(start_of_week)
        self.end_date.set_date(today)
        self._search_records()
    
    def _load_month_records(self):
        """Load this month's records."""
        today = datetime.now()
        start_of_month = today.replace(day=1)
        self.start_date.set_date(start_of_month)
        self.end_date.set_date(today)
        self._search_records()
    
    def _show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select item under cursor
        item = self.records_tree.identify_row(event.y)
        if item:
            self.records_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _view_record_details(self):
        """View details of selected record."""
        selection = self.records_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.records_tree.item(item, 'values')
        
        # Create details dialog
        details_window = tk.Toplevel(self.frame)
        details_window.title("Record Details")
        details_window.geometry("400x300")
        
        # Center window
        details_window.transient(self.frame)
        details_window.grab_set()
        
        # Display details
        details_frame = ttk.Frame(details_window)
        details_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        fields = ['Date', 'Time', 'Student ID', 'Name', 'Department', 'Batch', 'Status']
        for i, (field, value) in enumerate(zip(fields, values)):
            ttk.Label(details_frame, text=f"{field}:", 
                     font=('Arial', 10, 'bold')).grid(row=i, column=0, 
                                                      sticky='w', pady=5)
            ttk.Label(details_frame, text=value).grid(row=i, column=1, 
                                                     sticky='w', pady=5, padx=10)
        
        # Close button
        ttk.Button(details_frame, text="Close", 
                  command=details_window.destroy).grid(row=len(fields), column=0, 
                                                      columnspan=2, pady=20)
    
    def _edit_record_status(self):
        """Edit status of selected record."""
        selection = self.records_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.records_tree.item(item, 'values')
        student_id = values[2]
        date = values[0]
        current_status = values[6]
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.frame)
        edit_window.title("Edit Status")
        edit_window.geometry("300x150")
        edit_window.transient(self.frame)
        edit_window.grab_set()
        
        # Status selection
        ttk.Label(edit_window, text="New Status:").pack(pady=10)
        status_var = tk.StringVar(value=current_status)
        status_combo = ttk.Combobox(edit_window, textvariable=status_var,
                                   state='readonly', width=15)
        status_combo['values'] = ('Present', 'Absent', 'Late')
        status_combo.pack(pady=5)
        
        def save_status():
            new_status = status_var.get()
            try:
                # Update in database
                success = self.db.update_attendance_status(student_id, date, new_status)
                if success:
                    messagebox.showinfo("Success", "Status updated successfully")
                    edit_window.destroy()
                    self._search_records()  # Refresh
                else:
                    messagebox.showerror("Error", "Failed to update status")
            except Exception as e:
                messagebox.showerror("Error", f"Update failed: {str(e)}")
        
        # Buttons
        btn_frame = ttk.Frame(edit_window)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Save", command=save_status).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=edit_window.destroy).pack(side='left', padx=5)
    
    def _delete_record(self):
        """Delete selected record."""
        selection = self.records_tree.selection()
        if not selection:
            return
        
        if not messagebox.askyesno("Confirm Delete", 
                                  "Are you sure you want to delete this record?"):
            return
        
        item = selection[0]
        values = self.records_tree.item(item, 'values')
        student_id = values[2]
        date = values[0]
        
        try:
            success = self.db.delete_attendance_record(student_id, date)
            if success:
                messagebox.showinfo("Success", "Record deleted successfully")
                self._search_records()  # Refresh
                self.logger.info(f'Deleted attendance record: {student_id} on {date}')
            else:
                messagebox.showerror("Error", "Failed to delete record")
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed: {str(e)}")
            self.logger.error(f'Failed to delete record: {str(e)}')
