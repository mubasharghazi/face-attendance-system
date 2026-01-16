"""
Attendance Tab Module
Attendance marking with live camera feed.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import threading
from datetime import datetime
from collections import deque


class AttendanceTab:
    """Attendance marking tab with live face recognition."""
    
    def __init__(self, parent, attendance_manager, face_recognition, 
                 camera_handler, db_manager, colors, logger):
        """
        Initialize attendance tab.
        
        Args:
            parent: Parent widget
            attendance_manager: Attendance manager instance
            face_recognition: Face recognition module instance
            camera_handler: Camera handler instance
            db_manager: Database manager instance
            colors: Color scheme dictionary
            logger: Logger instance
        """
        self.parent = parent
        self.attendance_manager = attendance_manager
        self.face_recognition = face_recognition
        self.camera_handler = camera_handler
        self.db = db_manager
        self.colors = colors
        self.logger = logger
        
        # State variables
        self.camera_active = False
        self.recognition_active = False
        self.update_thread = None
        self.is_updating = False
        
        # Recent recognitions (to avoid duplicate marking)
        self.recent_recognitions = deque(maxlen=10)
        self.cooldown_seconds = 5
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup attendance user interface."""
        # Configure grid
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', 
                         padx=20, pady=20)
        
        ttk.Label(header_frame, text="Mark Attendance", 
                 style='Header.TLabel').pack(side='left')
        
        # Current date/time
        self.datetime_label = ttk.Label(header_frame, text="", 
                                       style='Info.TLabel')
        self.datetime_label.pack(side='right')
        self._update_datetime()
        
        # Left side - Camera feed
        self._create_camera_section()
        
        # Right side - Today's attendance list
        self._create_attendance_list_section()
    
    def _create_camera_section(self):
        """Create camera feed section."""
        camera_frame = ttk.Frame(self.frame, style='Card.TFrame')
        camera_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        
        # Inner frame
        inner_frame = ttk.Frame(camera_frame)
        inner_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_frame = ttk.Frame(inner_frame)
        title_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(title_frame, text="Live Camera Feed", 
                 style='Title.TLabel').pack(side='left')
        
        # Status indicator
        self.status_indicator = tk.Label(title_frame, text="● Inactive", 
                                        font=('Arial', 10), 
                                        fg=self.colors['warning'])
        self.status_indicator.pack(side='right')
        
        # Camera display
        self.camera_label = tk.Label(inner_frame, bg='black', 
                                    text="Camera Off", fg='white',
                                    font=('Arial', 14))
        self.camera_label.pack(pady=10, fill='both', expand=True)
        
        # Recognition info
        self.recognition_label = tk.Label(inner_frame, text="", 
                                         font=('Arial', 12, 'bold'),
                                         bg=self.colors['white'])
        self.recognition_label.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(inner_frame, 
                              text="Start camera and enable recognition to mark attendance automatically",
                              font=('Arial', 9), justify='center',
                              fg=self.colors['text'], wraplength=400)
        instructions.pack(pady=5)
        
        # Camera controls
        controls_frame = ttk.Frame(inner_frame)
        controls_frame.pack(pady=15)
        
        # Start/Stop camera button
        self.camera_btn = ttk.Button(controls_frame, text="Start Camera", 
                                    command=self._toggle_camera,
                                    style='Accent.TButton')
        self.camera_btn.pack(side='left', padx=5)
        
        # Enable/Disable recognition button
        self.recognition_btn = ttk.Button(controls_frame, 
                                         text="Enable Recognition", 
                                         command=self._toggle_recognition,
                                         state='disabled')
        self.recognition_btn.pack(side='left', padx=5)
        
        # Reload faces button
        reload_btn = ttk.Button(controls_frame, text="Reload Faces", 
                               command=self._reload_faces)
        reload_btn.pack(side='left', padx=5)
    
    def _create_attendance_list_section(self):
        """Create today's attendance list section."""
        list_frame = ttk.Frame(self.frame, style='Card.TFrame')
        list_frame.grid(row=1, column=1, sticky='nsew', padx=20, pady=10)
        
        # Configure grid
        list_frame.rowconfigure(2, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Inner frame
        inner_frame = ttk.Frame(list_frame)
        inner_frame.pack(fill='both', expand=True, padx=20, pady=20)
        inner_frame.rowconfigure(2, weight=1)
        inner_frame.columnconfigure(0, weight=1)
        
        # Title
        title_frame = ttk.Frame(inner_frame)
        title_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        title_frame.columnconfigure(0, weight=1)
        
        ttk.Label(title_frame, text="Today's Attendance", 
                 style='Title.TLabel').grid(row=0, column=0, sticky='w')
        
        # Statistics
        stats_frame = ttk.Frame(inner_frame)
        stats_frame.grid(row=1, column=0, sticky='ew', pady=(0, 15))
        
        self.stats_label = tk.Label(stats_frame, 
                                   text="Present: 0 | Absent: 0 | Total: 0",
                                   font=('Arial', 10, 'bold'),
                                   fg=self.colors['primary'])
        self.stats_label.pack()
        
        # Table frame
        table_frame = ttk.Frame(inner_frame)
        table_frame.grid(row=2, column=0, sticky='nsew')
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # Create treeview
        columns = ('Time', 'Student ID', 'Name', 'Status')
        self.attendance_tree = ttk.Treeview(table_frame, columns=columns, 
                                           show='headings', height=15)
        
        # Configure columns
        self.attendance_tree.heading('Time', text='Time')
        self.attendance_tree.heading('Student ID', text='Student ID')
        self.attendance_tree.heading('Name', text='Name')
        self.attendance_tree.heading('Status', text='Status')
        
        self.attendance_tree.column('Time', width=100, anchor='center')
        self.attendance_tree.column('Student ID', width=100, anchor='center')
        self.attendance_tree.column('Name', width=150)
        self.attendance_tree.column('Status', width=80, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', 
                                 command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.attendance_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Refresh button
        refresh_btn = ttk.Button(inner_frame, text="🔄 Refresh List", 
                                command=self._refresh_attendance_list)
        refresh_btn.grid(row=3, column=0, pady=(15, 0))
        
        # Load initial data
        self._refresh_attendance_list()
    
    def _update_datetime(self):
        """Update date/time display."""
        current_time = datetime.now().strftime("%A, %B %d, %Y - %I:%M:%S %p")
        self.datetime_label.config(text=current_time)
        
        # Schedule next update
        self.frame.after(1000, self._update_datetime)
    
    def _toggle_camera(self):
        """Toggle camera on/off."""
        if not self.camera_active:
            self._start_camera()
        else:
            self._stop_camera()
    
    def _start_camera(self):
        """Start camera feed."""
        try:
            if self.camera_handler.start():
                self.camera_active = True
                self.camera_btn.config(text="Stop Camera")
                self.recognition_btn.config(state='normal')
                self.status_indicator.config(text="● Camera Active", 
                                           fg=self.colors['info'])
                
                # Start update thread
                self.is_updating = True
                self.update_thread = threading.Thread(target=self._update_camera_feed, 
                                                     daemon=True)
                self.update_thread.start()
                
                self.logger.info('Camera started for attendance')
            else:
                messagebox.showerror("Error", "Failed to start camera")
                
        except Exception as e:
            messagebox.showerror("Error", f"Camera error: {str(e)}")
            self.logger.error(f'Failed to start camera: {str(e)}')
    
    def _stop_camera(self):
        """Stop camera feed."""
        try:
            # Stop recognition first
            if self.recognition_active:
                self._toggle_recognition()
            
            self.is_updating = False
            if self.update_thread:
                self.update_thread.join(timeout=1.0)
            
            self.camera_handler.stop()
            self.camera_active = False
            self.camera_btn.config(text="Start Camera")
            self.recognition_btn.config(state='disabled')
            self.status_indicator.config(text="● Inactive", 
                                       fg=self.colors['warning'])
            
            # Clear camera display
            self.camera_label.config(image='', text="Camera Off")
            self.recognition_label.config(text="")
            
            self.logger.info('Camera stopped')
            
        except Exception as e:
            self.logger.error(f'Error stopping camera: {str(e)}')
    
    def _toggle_recognition(self):
        """Toggle face recognition on/off."""
        if not self.recognition_active:
            self.recognition_active = True
            self.recognition_btn.config(text="Disable Recognition")
            self.status_indicator.config(text="● Recognition Active", 
                                       fg=self.colors['success'])
            self.logger.info('Face recognition enabled')
        else:
            self.recognition_active = False
            self.recognition_btn.config(text="Enable Recognition")
            self.status_indicator.config(text="● Camera Active", 
                                       fg=self.colors['info'])
            self.recognition_label.config(text="")
            self.logger.info('Face recognition disabled')
    
    def _update_camera_feed(self):
        """Update camera feed and perform face recognition."""
        while self.is_updating and self.camera_active:
            try:
                frame = self.camera_handler.read_frame()
                
                if frame is not None:
                    display_frame = frame.copy()
                    
                    # Perform recognition if enabled
                    if self.recognition_active:
                        recognized_name = None
                        recognized_id = None
                        
                        # Recognize faces (detect and recognize in one call)
                        results = self.face_recognition.recognize_faces(frame)
                        
                        for result in results:
                            top, right, bottom, left = result['location']
                            student_id = result['student_id']
                            name = result['name']
                            confidence = result['confidence']
                            
                            # Draw rectangle
                            color = (0, 255, 0) if result['is_known'] else (0, 0, 255)
                            cv2.rectangle(display_frame, (left, top), 
                                        (right, bottom), color, 2)
                            
                            # Draw label
                            label = f"{name} ({confidence:.2f})" if result['is_known'] else name
                            cv2.rectangle(display_frame, (left, bottom - 35), 
                                        (right, bottom), color, cv2.FILLED)
                            cv2.putText(display_frame, label, (left + 6, bottom - 6), 
                                      cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                            
                            # Mark attendance for recognized student
                            if result['is_known'] and student_id:
                                recognized_name = name
                                recognized_id = student_id
                                self._mark_attendance_for_student(student_id, name)
                        
                        # Update recognition label
                        if recognized_name:
                            self.recognition_label.config(
                                text=f"Recognized: {recognized_name}",
                                fg=self.colors['success']
                            )
                        else:
                            self.recognition_label.config(
                                text="No face recognized",
                                fg=self.colors['text']
                            )
                    
                    # Convert to PhotoImage
                    frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img = img.resize((480, 360), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image=img)
                    
                    # Update label
                    self.camera_label.config(image=photo, text='')
                    self.camera_label.image = photo
                
            except Exception as e:
                self.logger.error(f'Camera feed error: {str(e)}')
                break
    
    def _mark_attendance_for_student(self, student_id, name):
        """
        Mark attendance for recognized student.
        
        Args:
            student_id: Student ID
            name: Student name
        """
        # Check cooldown
        current_time = datetime.now()
        
        # Check if recently marked
        for prev_id, prev_time in self.recent_recognitions:
            if prev_id == student_id:
                time_diff = (current_time - prev_time).total_seconds()
                if time_diff < self.cooldown_seconds:
                    return
        
        # Mark attendance
        success, message = self.attendance_manager.mark_attendance(student_id)
        
        if success:
            # Add to recent recognitions
            self.recent_recognitions.append((student_id, current_time))
            
            # Refresh attendance list
            self._refresh_attendance_list()
            
            self.logger.info(f'Attendance marked: {student_id} - {name}')
    
    def _refresh_attendance_list(self):
        """Refresh today's attendance list."""
        try:
            # Clear existing items
            for item in self.attendance_tree.get_children():
                self.attendance_tree.delete(item)
            
            # Get today's records
            today = datetime.now().strftime('%Y-%m-%d')
            records = self.db.get_attendance_by_date(today)
            
            # Sort by time descending
            records.sort(key=lambda x: x['time'], reverse=True)
            
            # Add to tree
            present_count = 0
            for record in records:
                time_str = record['time'].split()[1] if ' ' in record['time'] else record['time']
                values = (
                    time_str,
                    record['student_id'],
                    record['name'],
                    record['status']
                )
                
                # Add with tag based on status
                tag = 'present' if record['status'] == 'Present' else 'absent'
                self.attendance_tree.insert('', 'end', values=values, tags=(tag,))
                
                if record['status'] == 'Present':
                    present_count += 1
            
            # Configure tags
            self.attendance_tree.tag_configure('present', 
                                              foreground=self.colors['success'])
            self.attendance_tree.tag_configure('absent', 
                                             foreground=self.colors['danger'])
            
            # Update statistics
            total_students = len(self.db.get_all_students())
            absent_count = total_students - present_count
            
            self.stats_label.config(
                text=f"Present: {present_count} | Absent: {absent_count} | Total: {total_students}"
            )
            
        except Exception as e:
            self.logger.error(f'Failed to refresh attendance list: {str(e)}')
    
    def _reload_faces(self):
        """Reload known faces from database."""
        try:
            students = self.db.get_all_students()
            self.face_recognition.load_known_faces(students)
            messagebox.showinfo("Success", 
                              f"Loaded {len(students)} student faces")
            self.logger.info(f'Reloaded {len(students)} faces')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reload faces: {str(e)}")
            self.logger.error(f'Failed to reload faces: {str(e)}')
    
    def cleanup(self):
        """Cleanup resources."""
        if self.camera_active:
            self._stop_camera()
