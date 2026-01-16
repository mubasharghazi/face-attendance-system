"""
Reports Tab Module
Generate and export reports.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import threading


class ReportsTab:
    """Reports tab for generating and exporting attendance reports."""
    
    def __init__(self, parent, report_generator, db_manager, colors, logger):
        """
        Initialize reports tab.
        
        Args:
            parent: Parent widget
            report_generator: Report generator instance
            db_manager: Database manager instance
            colors: Color scheme dictionary
            logger: Logger instance
        """
        self.parent = parent
        self.report_generator = report_generator
        self.db = db_manager
        self.colors = colors
        self.logger = logger
        
        # State variables
        self.current_report = None
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup reports user interface."""
        # Configure grid
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', 
                         padx=20, pady=20)
        
        ttk.Label(header_frame, text="Generate Reports", 
                 style='Header.TLabel').pack(side='left')
        
        # Left side - Report configuration
        self._create_report_config_section()
        
        # Right side - Report preview
        self._create_report_preview_section()
    
    def _create_report_config_section(self):
        """Create report configuration section."""
        config_frame = ttk.Frame(self.frame, style='Card.TFrame')
        config_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        
        # Inner frame
        inner_frame = ttk.Frame(config_frame)
        inner_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        ttk.Label(inner_frame, text="Report Configuration", 
                 style='Title.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Report type
        type_frame = ttk.Frame(inner_frame)
        type_frame.pack(fill='x', pady=10)
        
        ttk.Label(type_frame, text="Report Type:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.report_type_var = tk.StringVar(value='Daily')
        
        report_types = [
            ('Daily Report', 'Daily'),
            ('Date Range Report', 'Range'),
            ('Student Report', 'Student'),
            ('Department Report', 'Department'),
            ('Summary Report', 'Summary')
        ]
        
        for text, value in report_types:
            ttk.Radiobutton(type_frame, text=text, variable=self.report_type_var,
                          value=value, command=self._on_report_type_changed).pack(anchor='w', 
                                                                                  pady=2)
        
        # Date selection frame
        self.date_frame = ttk.Frame(inner_frame)
        self.date_frame.pack(fill='x', pady=15)
        
        # Single date (for daily report)
        self.single_date_frame = ttk.Frame(self.date_frame)
        self.single_date_frame.pack(fill='x')
        
        ttk.Label(self.single_date_frame, text="Select Date:").pack(anchor='w', 
                                                                    pady=(0, 5))
        self.report_date = DateEntry(self.single_date_frame, width=20, 
                                     background='darkblue',
                                     foreground='white', borderwidth=2,
                                     date_pattern='yyyy-mm-dd')
        self.report_date.pack(anchor='w')
        
        # Date range (for range report)
        self.range_frame = ttk.Frame(self.date_frame)
        
        ttk.Label(self.range_frame, text="Start Date:").pack(anchor='w', pady=(0, 5))
        self.start_date = DateEntry(self.range_frame, width=20, 
                                    background='darkblue',
                                    foreground='white', borderwidth=2,
                                    date_pattern='yyyy-mm-dd')
        self.start_date.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(self.range_frame, text="End Date:").pack(anchor='w', pady=(0, 5))
        self.end_date = DateEntry(self.range_frame, width=20, 
                                 background='darkblue',
                                 foreground='white', borderwidth=2,
                                 date_pattern='yyyy-mm-dd')
        self.end_date.pack(anchor='w')
        
        # Student selection (for student report)
        self.student_frame = ttk.Frame(self.date_frame)
        
        ttk.Label(self.student_frame, text="Select Student:").pack(anchor='w', 
                                                                   pady=(0, 5))
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(self.student_frame, 
                                         textvariable=self.student_var,
                                         width=30, state='readonly')
        self.student_combo.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(self.student_frame, text="Date Range:").pack(anchor='w', 
                                                              pady=(0, 5))
        ttk.Label(self.student_frame, text="From:").pack(anchor='w')
        self.student_start_date = DateEntry(self.student_frame, width=20,
                                           background='darkblue',
                                           foreground='white', borderwidth=2,
                                           date_pattern='yyyy-mm-dd')
        self.student_start_date.pack(anchor='w', pady=(0, 5))
        
        ttk.Label(self.student_frame, text="To:").pack(anchor='w')
        self.student_end_date = DateEntry(self.student_frame, width=20,
                                         background='darkblue',
                                         foreground='white', borderwidth=2,
                                         date_pattern='yyyy-mm-dd')
        self.student_end_date.pack(anchor='w')
        
        # Load students
        self._load_students()
        
        # Department selection (for department report)
        self.department_frame = ttk.Frame(self.date_frame)
        
        ttk.Label(self.department_frame, text="Select Department:").pack(anchor='w', 
                                                                         pady=(0, 5))
        self.dept_var = tk.StringVar()
        dept_combo = ttk.Combobox(self.department_frame, textvariable=self.dept_var,
                                 width=30, state='readonly')
        dept_combo['values'] = ('Computer Science', 'Information Technology', 
                               'Electronics', 'Mechanical', 'Civil', 'Other')
        dept_combo.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(self.department_frame, text="Date Range:").pack(anchor='w', 
                                                                  pady=(0, 5))
        ttk.Label(self.department_frame, text="From:").pack(anchor='w')
        self.dept_start_date = DateEntry(self.department_frame, width=20,
                                        background='darkblue',
                                        foreground='white', borderwidth=2,
                                        date_pattern='yyyy-mm-dd')
        self.dept_start_date.pack(anchor='w', pady=(0, 5))
        
        ttk.Label(self.department_frame, text="To:").pack(anchor='w')
        self.dept_end_date = DateEntry(self.department_frame, width=20,
                                      background='darkblue',
                                      foreground='white', borderwidth=2,
                                      date_pattern='yyyy-mm-dd')
        self.dept_end_date.pack(anchor='w')
        
        # Summary period (for summary report)
        self.summary_frame = ttk.Frame(self.date_frame)
        
        ttk.Label(self.summary_frame, text="Summary Period:").pack(anchor='w', 
                                                                   pady=(0, 5))
        self.summary_var = tk.StringVar(value='This Month')
        summary_combo = ttk.Combobox(self.summary_frame, textvariable=self.summary_var,
                                    width=30, state='readonly')
        summary_combo['values'] = ('Today', 'This Week', 'This Month', 
                                   'Last Month', 'Custom Range')
        summary_combo.pack(anchor='w')
        summary_combo.bind('<<ComboboxSelected>>', self._on_summary_period_changed)
        
        self.summary_range_frame = ttk.Frame(self.summary_frame)
        ttk.Label(self.summary_range_frame, text="From:").pack(anchor='w', 
                                                              pady=(10, 5))
        self.summary_start_date = DateEntry(self.summary_range_frame, width=20,
                                           background='darkblue',
                                           foreground='white', borderwidth=2,
                                           date_pattern='yyyy-mm-dd')
        self.summary_start_date.pack(anchor='w', pady=(0, 5))
        
        ttk.Label(self.summary_range_frame, text="To:").pack(anchor='w')
        self.summary_end_date = DateEntry(self.summary_range_frame, width=20,
                                         background='darkblue',
                                         foreground='white', borderwidth=2,
                                         date_pattern='yyyy-mm-dd')
        self.summary_end_date.pack(anchor='w')
        
        # Export format
        format_frame = ttk.Frame(inner_frame)
        format_frame.pack(fill='x', pady=15)
        
        ttk.Label(format_frame, text="Export Format:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.format_var = tk.StringVar(value='CSV')
        ttk.Radiobutton(format_frame, text="CSV (.csv)", 
                       variable=self.format_var, value='CSV').pack(anchor='w', pady=2)
        ttk.Radiobutton(format_frame, text="Excel (.xlsx)", 
                       variable=self.format_var, value='Excel').pack(anchor='w', pady=2)
        ttk.Radiobutton(format_frame, text="PDF (.pdf)", 
                       variable=self.format_var, value='PDF').pack(anchor='w', pady=2)
        
        # Buttons
        button_frame = ttk.Frame(inner_frame)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="Generate Preview", 
                  command=self._generate_preview,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Export Report", 
                  command=self._export_report).pack(side='left', padx=5)
        
        # Initialize view
        self._on_report_type_changed()
    
    def _create_report_preview_section(self):
        """Create report preview section."""
        preview_frame = ttk.Frame(self.frame, style='Card.TFrame')
        preview_frame.grid(row=1, column=1, sticky='nsew', padx=20, pady=10)
        
        # Configure grid
        preview_frame.rowconfigure(1, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        
        # Inner frame
        inner_frame = ttk.Frame(preview_frame)
        inner_frame.pack(fill='both', expand=True, padx=20, pady=20)
        inner_frame.rowconfigure(2, weight=1)
        inner_frame.columnconfigure(0, weight=1)
        
        # Title
        ttk.Label(inner_frame, text="Report Preview", 
                 style='Title.TLabel').grid(row=0, column=0, sticky='w', 
                                           pady=(0, 10))
        
        # Info label
        self.preview_info_label = ttk.Label(inner_frame, text="No report generated", 
                                           style='Info.TLabel')
        self.preview_info_label.grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        # Preview table container
        table_container = ttk.Frame(inner_frame)
        table_container.grid(row=2, column=0, sticky='nsew')
        table_container.rowconfigure(0, weight=1)
        table_container.columnconfigure(0, weight=1)
        
        # Create treeview for preview
        self.preview_tree = ttk.Treeview(table_container, show='headings', height=20)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_container, orient='vertical', 
                           command=self.preview_tree.yview)
        hsb = ttk.Scrollbar(table_container, orient='horizontal', 
                           command=self.preview_tree.xview)
        self.preview_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack
        self.preview_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
    
    def _on_report_type_changed(self):
        """Handle report type change."""
        report_type = self.report_type_var.get()
        
        # Hide all date frames
        self.single_date_frame.pack_forget()
        self.range_frame.pack_forget()
        self.student_frame.pack_forget()
        self.department_frame.pack_forget()
        self.summary_frame.pack_forget()
        
        # Show appropriate frame
        if report_type == 'Daily':
            self.single_date_frame.pack(fill='x')
        elif report_type == 'Range':
            self.range_frame.pack(fill='x')
        elif report_type == 'Student':
            self.student_frame.pack(fill='x')
        elif report_type == 'Department':
            self.department_frame.pack(fill='x')
        elif report_type == 'Summary':
            self.summary_frame.pack(fill='x')
    
    def _on_summary_period_changed(self, event=None):
        """Handle summary period change."""
        if self.summary_var.get() == 'Custom Range':
            self.summary_range_frame.pack(fill='x', pady=(10, 0))
        else:
            self.summary_range_frame.pack_forget()
    
    def _load_students(self):
        """Load students for selection."""
        try:
            students = self.db.get_all_students()
            student_list = [f"{s['student_id']} - {s['name']}" for s in students]
            self.student_combo['values'] = student_list
        except Exception as e:
            self.logger.error(f'Failed to load students: {str(e)}')
    
    def _generate_preview(self):
        """Generate report preview."""
        try:
            report_type = self.report_type_var.get()
            
            # Generate report based on type
            if report_type == 'Daily':
                report_df = self._generate_daily_report()
            elif report_type == 'Range':
                report_df = self._generate_range_report()
            elif report_type == 'Student':
                report_df = self._generate_student_report()
            elif report_type == 'Department':
                report_df = self._generate_department_report()
            elif report_type == 'Summary':
                report_df = self._generate_summary_report()
            else:
                messagebox.showwarning("Warning", "Please select a report type")
                return
            
            if report_df is None or report_df.empty:
                messagebox.showinfo("Info", "No data available for selected criteria")
                return
            
            # Store current report
            self.current_report = report_df
            
            # Display preview
            self._display_preview(report_df)
            
            self.logger.info(f'Generated {report_type} report preview')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            self.logger.error(f'Report generation failed: {str(e)}')
    
    def _generate_daily_report(self):
        """Generate daily report."""
        date_str = self.report_date.get_date().strftime('%Y-%m-%d')
        return self.report_generator.generate_daily_report(date_str)
    
    def _generate_range_report(self):
        """Generate date range report."""
        start = self.start_date.get_date().strftime('%Y-%m-%d')
        end = self.end_date.get_date().strftime('%Y-%m-%d')
        return self.report_generator.generate_date_range_report(start, end)
    
    def _generate_student_report(self):
        """Generate student-specific report."""
        if not self.student_var.get():
            messagebox.showwarning("Warning", "Please select a student")
            return None
        
        student_id = self.student_var.get().split(' - ')[0]
        start = self.student_start_date.get_date().strftime('%Y-%m-%d')
        end = self.student_end_date.get_date().strftime('%Y-%m-%d')
        
        return self.report_generator.generate_student_report(student_id, start, end)
    
    def _generate_department_report(self):
        """Generate department report."""
        if not self.dept_var.get():
            messagebox.showwarning("Warning", "Please select a department")
            return None
        
        department = self.dept_var.get()
        start = self.dept_start_date.get_date().strftime('%Y-%m-%d')
        end = self.dept_end_date.get_date().strftime('%Y-%m-%d')
        
        return self.report_generator.generate_department_report(department, start, end)
    
    def _generate_summary_report(self):
        """Generate summary report."""
        period = self.summary_var.get()
        
        # Calculate date range based on period
        today = datetime.now()
        
        if period == 'Today':
            start = end = today.strftime('%Y-%m-%d')
        elif period == 'This Week':
            start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
            end = today.strftime('%Y-%m-%d')
        elif period == 'This Month':
            start = today.replace(day=1).strftime('%Y-%m-%d')
            end = today.strftime('%Y-%m-%d')
        elif period == 'Last Month':
            last_month = today.replace(day=1) - timedelta(days=1)
            start = last_month.replace(day=1).strftime('%Y-%m-%d')
            end = last_month.strftime('%Y-%m-%d')
        elif period == 'Custom Range':
            start = self.summary_start_date.get_date().strftime('%Y-%m-%d')
            end = self.summary_end_date.get_date().strftime('%Y-%m-%d')
        else:
            return None
        
        return self.report_generator.generate_summary_report(start, end)
    
    def _display_preview(self, df):
        """Display report preview in table."""
        # Clear existing preview
        self.preview_tree.delete(*self.preview_tree.get_children())
        
        # Configure columns
        columns = list(df.columns)
        self.preview_tree['columns'] = columns
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=120)
        
        # Add data
        for _, row in df.iterrows():
            values = [str(row[col]) for col in columns]
            self.preview_tree.insert('', 'end', values=values)
        
        # Update info label
        self.preview_info_label.config(
            text=f"Showing {len(df)} records | {len(columns)} columns"
        )
    
    def _export_report(self):
        """Export report to file."""
        if self.current_report is None or self.current_report.empty:
            messagebox.showwarning("Warning", 
                                 "Please generate a report preview first")
            return
        
        # Get format
        format_type = self.format_var.get()
        
        # Get file extension
        if format_type == 'CSV':
            ext = '.csv'
            filetypes = [("CSV files", "*.csv")]
        elif format_type == 'Excel':
            ext = '.xlsx'
            filetypes = [("Excel files", "*.xlsx")]
        elif format_type == 'PDF':
            ext = '.pdf'
            filetypes = [("PDF files", "*.pdf")]
        else:
            return
        
        # Get save location
        default_name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        file_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=filetypes,
            initialfile=default_name
        )
        
        if not file_path:
            return
        
        # Export in thread to avoid UI freeze
        def export_thread():
            try:
                if format_type == 'CSV':
                    self.report_generator.export_to_csv(self.current_report, file_path)
                elif format_type == 'Excel':
                    self.report_generator.export_to_excel(self.current_report, file_path)
                elif format_type == 'PDF':
                    self.report_generator.export_to_pdf(self.current_report, file_path)
                
                self.frame.after(0, lambda: messagebox.showinfo(
                    "Success", f"Report exported successfully to:\n{file_path}"
                ))
                self.logger.info(f'Report exported: {file_path}')
                
            except Exception as e:
                self.frame.after(0, lambda: messagebox.showerror(
                    "Error", f"Export failed: {str(e)}"
                ))
                self.logger.error(f'Export failed: {str(e)}')
        
        threading.Thread(target=export_thread, daemon=True).start()
