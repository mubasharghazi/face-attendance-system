"""
Dashboard Tab Module
Dashboard showing statistics and recent attendance.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Dict, Any


class DashboardTab:
    """Dashboard tab showing system statistics and recent activity."""
    
    def __init__(self, parent, db_manager, attendance_manager, colors, logger):
        """
        Initialize dashboard tab.
        
        Args:
            parent: Parent widget
            db_manager: Database manager instance
            attendance_manager: Attendance manager instance
            colors: Color scheme dictionary
            logger: Logger instance
        """
        self.parent = parent
        self.db = db_manager
        self.attendance_manager = attendance_manager
        self.colors = colors
        self.logger = logger
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Setup UI
        self._setup_ui()
        
        # Load initial data
        self.refresh_dashboard()
    
    def _setup_ui(self):
        """Setup dashboard user interface."""
        # Configure grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', 
                         padx=20, pady=20)
        
        ttk.Label(header_frame, text="Dashboard Overview", 
                 style='Header.TLabel').pack(side='left')
        
        # Refresh button
        refresh_btn = ttk.Button(header_frame, text="🔄 Refresh", 
                                command=self.refresh_dashboard)
        refresh_btn.pack(side='right')
        
        # Statistics cards
        self._create_statistics_section()
        
        # Recent attendance section
        self._create_recent_attendance_section()
        
        # Quick stats section
        self._create_quick_stats_section()
    
    def _create_statistics_section(self):
        """Create statistics cards section."""
        stats_frame = ttk.Frame(self.frame)
        stats_frame.grid(row=1, column=0, columnspan=2, sticky='ew', 
                        padx=20, pady=10)
        
        # Configure grid
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1, uniform='stats')
        
        # Total Students Card
        self.total_students_card = self._create_stat_card(
            stats_frame, "Total Students", "0", self.colors['primary'], "👥"
        )
        self.total_students_card.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        # Today's Attendance Card
        self.today_attendance_card = self._create_stat_card(
            stats_frame, "Today's Attendance", "0", self.colors['success'], "✓"
        )
        self.today_attendance_card.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Absent Today Card
        self.absent_today_card = self._create_stat_card(
            stats_frame, "Absent Today", "0", self.colors['warning'], "✗"
        )
        self.absent_today_card.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        
        # Attendance Rate Card
        self.attendance_rate_card = self._create_stat_card(
            stats_frame, "Attendance Rate", "0%", self.colors['info'], "📊"
        )
        self.attendance_rate_card.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
    
    def _create_stat_card(self, parent, title, value, color, icon):
        """
        Create a statistics card widget.
        
        Args:
            parent: Parent widget
            title: Card title
            value: Card value
            color: Card accent color
            icon: Card icon
            
        Returns:
            Card frame
        """
        card = tk.Frame(parent, bg=self.colors['white'], relief='solid', 
                       borderwidth=1, highlightbackground=color, 
                       highlightthickness=3)
        
        # Icon
        icon_label = tk.Label(card, text=icon, font=('Arial', 32), 
                            bg=self.colors['white'], fg=color)
        icon_label.pack(pady=(15, 5))
        
        # Value
        value_label = tk.Label(card, text=value, font=('Arial', 24, 'bold'), 
                             bg=self.colors['white'], fg=self.colors['text'])
        value_label.pack(pady=5)
        card.value_label = value_label
        
        # Title
        title_label = tk.Label(card, text=title, font=('Arial', 10), 
                             bg=self.colors['white'], fg=self.colors['text'])
        title_label.pack(pady=(5, 15))
        
        return card
    
    def _create_recent_attendance_section(self):
        """Create recent attendance section."""
        section_frame = ttk.Frame(self.frame)
        section_frame.grid(row=2, column=0, sticky='nsew', padx=20, pady=10)
        
        # Configure grid
        section_frame.rowconfigure(1, weight=1)
        section_frame.columnconfigure(0, weight=1)
        
        # Header
        header = ttk.Frame(section_frame)
        header.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(header, text="Recent Attendance", 
                 style='Title.TLabel').pack(side='left')
        
        # Table frame
        table_frame = ttk.Frame(section_frame, style='Card.TFrame')
        table_frame.grid(row=1, column=0, sticky='nsew')
        
        # Create treeview
        columns = ('Time', 'Student ID', 'Name', 'Status')
        self.recent_tree = ttk.Treeview(table_frame, columns=columns, 
                                       show='headings', height=10)
        
        # Configure columns
        self.recent_tree.heading('Time', text='Time')
        self.recent_tree.heading('Student ID', text='Student ID')
        self.recent_tree.heading('Name', text='Name')
        self.recent_tree.heading('Status', text='Status')
        
        self.recent_tree.column('Time', width=100, anchor='center')
        self.recent_tree.column('Student ID', width=100, anchor='center')
        self.recent_tree.column('Name', width=150)
        self.recent_tree.column('Status', width=80, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', 
                                 command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.recent_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def _create_quick_stats_section(self):
        """Create quick statistics section."""
        section_frame = ttk.Frame(self.frame)
        section_frame.grid(row=2, column=1, sticky='nsew', padx=20, pady=10)
        
        # Configure grid
        section_frame.rowconfigure(1, weight=1)
        section_frame.columnconfigure(0, weight=1)
        
        # Header
        header = ttk.Frame(section_frame)
        header.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(header, text="Weekly Statistics", 
                 style='Title.TLabel').pack(side='left')
        
        # Stats container
        stats_container = tk.Frame(section_frame, bg=self.colors['white'], 
                                  relief='solid', borderwidth=1)
        stats_container.grid(row=1, column=0, sticky='nsew')
        
        # Scrollable frame
        canvas = tk.Canvas(stats_container, bg=self.colors['white'], 
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(stats_container, orient='vertical', 
                                 command=canvas.yview)
        self.stats_inner_frame = tk.Frame(canvas, bg=self.colors['white'])
        
        self.stats_inner_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.stats_inner_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Placeholder stats
        self.weekly_stats_labels = []
        for i in range(7):
            day_frame = tk.Frame(self.stats_inner_frame, bg=self.colors['white'])
            day_frame.pack(fill='x', padx=20, pady=10)
            
            date_label = tk.Label(day_frame, text="", font=('Arial', 10, 'bold'),
                                bg=self.colors['white'], fg=self.colors['text'])
            date_label.pack(anchor='w')
            
            count_label = tk.Label(day_frame, text="", font=('Arial', 9),
                                 bg=self.colors['white'], fg=self.colors['text'])
            count_label.pack(anchor='w')
            
            self.weekly_stats_labels.append((date_label, count_label))
    
    def refresh_dashboard(self):
        """Refresh dashboard data."""
        try:
            # Update statistics cards
            self._update_statistics()
            
            # Update recent attendance
            self._update_recent_attendance()
            
            # Update weekly stats
            self._update_weekly_stats()
            
            self.logger.info('Dashboard refreshed')
            
        except Exception as e:
            self.logger.error(f'Failed to refresh dashboard: {str(e)}')
    
    def _update_statistics(self):
        """Update statistics cards."""
        # Total students
        total_students = len(self.db.get_all_students())
        self.total_students_card.value_label.config(text=str(total_students))
        
        # Today's attendance
        today = datetime.now().strftime('%Y-%m-%d')
        today_records = self.db.get_attendance_by_date(today)
        today_present = len([r for r in today_records if r['status'] == 'Present'])
        self.today_attendance_card.value_label.config(text=str(today_present))
        
        # Absent today
        absent_today = total_students - today_present
        self.absent_today_card.value_label.config(text=str(absent_today))
        
        # Attendance rate
        if total_students > 0:
            rate = (today_present / total_students) * 100
            self.attendance_rate_card.value_label.config(text=f"{rate:.1f}%")
        else:
            self.attendance_rate_card.value_label.config(text="0%")
    
    def _update_recent_attendance(self):
        """Update recent attendance table."""
        # Clear existing items
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        
        # Get recent records
        today = datetime.now().strftime('%Y-%m-%d')
        records = self.db.get_attendance_by_date(today)
        
        # Sort by time descending
        records.sort(key=lambda x: x['time'], reverse=True)
        
        # Add to tree (limit to 20 recent)
        for record in records[:20]:
            time_str = record['time'].split()[1] if ' ' in record['time'] else record['time']
            values = (
                time_str,
                record['student_id'],
                record['name'],
                record['status']
            )
            
            # Add with tag based on status
            tag = 'present' if record['status'] == 'Present' else 'absent'
            self.recent_tree.insert('', 'end', values=values, tags=(tag,))
        
        # Configure tags
        self.recent_tree.tag_configure('present', foreground=self.colors['success'])
        self.recent_tree.tag_configure('absent', foreground=self.colors['danger'])
    
    def _update_weekly_stats(self):
        """Update weekly statistics."""
        today = datetime.now()
        
        for i in range(7):
            date = today - timedelta(days=6-i)
            date_str = date.strftime('%Y-%m-%d')
            day_name = date.strftime('%A, %b %d')
            
            # Get attendance count for this day
            records = self.db.get_attendance_by_date(date_str)
            present_count = len([r for r in records if r['status'] == 'Present'])
            
            # Update labels
            date_label, count_label = self.weekly_stats_labels[i]
            date_label.config(text=day_name)
            count_label.config(text=f"Present: {present_count}")
