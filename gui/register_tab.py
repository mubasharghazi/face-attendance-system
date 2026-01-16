"""
Register Tab Module
Student registration form with camera capture.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import threading
import os
from datetime import datetime


class RegisterTab:
    """Student registration tab with face capture."""
    
    def __init__(self, parent, student_manager, face_recognition, 
                 camera_handler, colors, logger):
        """
        Initialize register tab.
        
        Args:
            parent: Parent widget
            student_manager: Student manager instance
            face_recognition: Face recognition module instance
            camera_handler: Camera handler instance
            colors: Color scheme dictionary
            logger: Logger instance
        """
        self.parent = parent
        self.student_manager = student_manager
        self.face_recognition = face_recognition
        self.camera_handler = camera_handler
        self.colors = colors
        self.logger = logger
        
        # State variables
        self.camera_active = False
        self.captured_frame = None
        self.face_encoding = None
        self.update_thread = None
        self.is_updating = False
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup registration user interface."""
        # Configure grid
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', 
                         padx=20, pady=20)
        
        ttk.Label(header_frame, text="Register New Student", 
                 style='Header.TLabel').pack(side='left')
        
        # Left side - Registration form
        self._create_registration_form()
        
        # Right side - Camera feed
        self._create_camera_section()
    
    def _create_registration_form(self):
        """Create registration form section."""
        form_frame = ttk.Frame(self.frame, style='Card.TFrame')
        form_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        
        # Inner frame with padding
        inner_frame = ttk.Frame(form_frame)
        inner_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Form title
        ttk.Label(inner_frame, text="Student Information", 
                 style='Title.TLabel').grid(row=0, column=0, columnspan=2, 
                                           sticky='w', pady=(0, 20))
        
        # Student ID
        ttk.Label(inner_frame, text="Student ID:").grid(row=1, column=0, 
                                                        sticky='w', pady=10)
        self.student_id_var = tk.StringVar()
        self.student_id_entry = ttk.Entry(inner_frame, textvariable=self.student_id_var, 
                                         font=('Arial', 10), width=30)
        self.student_id_entry.grid(row=1, column=1, sticky='ew', pady=10)
        
        # Name
        ttk.Label(inner_frame, text="Full Name:").grid(row=2, column=0, 
                                                       sticky='w', pady=10)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(inner_frame, textvariable=self.name_var, 
                                   font=('Arial', 10), width=30)
        self.name_entry.grid(row=2, column=1, sticky='ew', pady=10)
        
        # Email
        ttk.Label(inner_frame, text="Email:").grid(row=3, column=0, 
                                                   sticky='w', pady=10)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(inner_frame, textvariable=self.email_var, 
                                    font=('Arial', 10), width=30)
        self.email_entry.grid(row=3, column=1, sticky='ew', pady=10)
        
        # Department
        ttk.Label(inner_frame, text="Department:").grid(row=4, column=0, 
                                                        sticky='w', pady=10)
        self.department_var = tk.StringVar()
        department_combo = ttk.Combobox(inner_frame, textvariable=self.department_var,
                                       font=('Arial', 10), width=28, state='readonly')
        department_combo['values'] = ('Computer Science', 'Information Technology', 
                                      'Electronics', 'Mechanical', 'Civil', 'Other')
        department_combo.grid(row=4, column=1, sticky='ew', pady=10)
        
        # Batch
        ttk.Label(inner_frame, text="Batch:").grid(row=5, column=0, 
                                                   sticky='w', pady=10)
        self.batch_var = tk.StringVar()
        current_year = datetime.now().year
        batch_combo = ttk.Combobox(inner_frame, textvariable=self.batch_var,
                                   font=('Arial', 10), width=28, state='readonly')
        batch_combo['values'] = tuple(str(year) for year in range(current_year-4, current_year+2))
        batch_combo.grid(row=5, column=1, sticky='ew', pady=10)
        
        # Face capture status
        self.capture_status_label = tk.Label(inner_frame, text="No face captured", 
                                           font=('Arial', 10), 
                                           fg=self.colors['warning'])
        self.capture_status_label.grid(row=6, column=0, columnspan=2, 
                                      sticky='w', pady=20)
        
        # Buttons frame
        button_frame = ttk.Frame(inner_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        # Register button
        self.register_btn = ttk.Button(button_frame, text="Register Student", 
                                      command=self._register_student,
                                      style='Accent.TButton')
        self.register_btn.pack(side='left', padx=5)
        
        # Clear button
        clear_btn = ttk.Button(button_frame, text="Clear Form", 
                              command=self._clear_form)
        clear_btn.pack(side='left', padx=5)
        
        # Configure column weights
        inner_frame.columnconfigure(1, weight=1)
    
    def _create_camera_section(self):
        """Create camera feed section."""
        camera_frame = ttk.Frame(self.frame, style='Card.TFrame')
        camera_frame.grid(row=1, column=1, sticky='nsew', padx=20, pady=10)
        
        # Inner frame
        inner_frame = ttk.Frame(camera_frame)
        inner_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(inner_frame, text="Face Capture", 
                 style='Title.TLabel').pack(pady=(0, 15))
        
        # Camera display
        self.camera_label = tk.Label(inner_frame, bg='black', 
                                    text="Camera Off", fg='white',
                                    font=('Arial', 14))
        self.camera_label.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(inner_frame, 
                              text="Position your face in the frame\nand click Capture Face",
                              font=('Arial', 9), justify='center',
                              fg=self.colors['text'])
        instructions.pack(pady=10)
        
        # Camera controls
        controls_frame = ttk.Frame(inner_frame)
        controls_frame.pack(pady=15)
        
        # Start/Stop camera button
        self.camera_btn = ttk.Button(controls_frame, text="Start Camera", 
                                    command=self._toggle_camera,
                                    style='Accent.TButton')
        self.camera_btn.pack(side='left', padx=5)
        
        # Capture face button
        self.capture_btn = ttk.Button(controls_frame, text="Capture Face", 
                                     command=self._capture_face,
                                     state='disabled')
        self.capture_btn.pack(side='left', padx=5)
        
        # Load from file button
        load_btn = ttk.Button(controls_frame, text="Load from File", 
                            command=self._load_image_file)
        load_btn.pack(side='left', padx=5)
    
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
                self.capture_btn.config(state='normal')
                
                # Start update thread
                self.is_updating = True
                self.update_thread = threading.Thread(target=self._update_camera_feed, 
                                                     daemon=True)
                self.update_thread.start()
                
                self.logger.log('INFO', 'Camera started for registration')
            else:
                messagebox.showerror("Error", "Failed to start camera")
                
        except Exception as e:
            messagebox.showerror("Error", f"Camera error: {str(e)}")
            self.logger.log('ERROR', f'Failed to start camera: {str(e)}')
    
    def _stop_camera(self):
        """Stop camera feed."""
        try:
            self.is_updating = False
            if self.update_thread:
                self.update_thread.join(timeout=1.0)
            
            self.camera_handler.stop()
            self.camera_active = False
            self.camera_btn.config(text="Start Camera")
            self.capture_btn.config(state='disabled')
            
            # Clear camera display
            self.camera_label.config(image='', text="Camera Off")
            
            self.logger.log('INFO', 'Camera stopped')
            
        except Exception as e:
            self.logger.log('ERROR', f'Error stopping camera: {str(e)}')
    
    def _update_camera_feed(self):
        """Update camera feed in separate thread."""
        while self.is_updating and self.camera_active:
            try:
                frame = self.camera_handler.read_frame()
                
                if frame is not None:
                    # Store current frame
                    self.captured_frame = frame.copy()
                    
                    # Detect faces
                    face_locations = self.face_recognition.detect_faces(frame)
                    
                    # Draw rectangles around faces
                    for top, right, bottom, left in face_locations:
                        cv2.rectangle(frame, (left, top), (right, bottom), 
                                    (0, 255, 0), 2)
                    
                    # Convert to PhotoImage
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img = img.resize((480, 360), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image=img)
                    
                    # Update label
                    self.camera_label.config(image=photo, text='')
                    self.camera_label.image = photo
                
            except Exception as e:
                self.logger.log('ERROR', f'Camera feed error: {str(e)}')
                break
    
    def _capture_face(self):
        """Capture face from camera."""
        if self.captured_frame is None:
            messagebox.showwarning("Warning", "No frame available to capture")
            return
        
        try:
            # Detect and encode face
            face_locations = self.face_recognition.detect_faces(self.captured_frame)
            
            if not face_locations:
                messagebox.showwarning("Warning", "No face detected in frame")
                return
            
            if len(face_locations) > 1:
                messagebox.showwarning("Warning", 
                                     "Multiple faces detected. Please ensure only one face is visible")
                return
            
            # Get face encoding
            face_encoding = self.face_recognition.encode_face(self.captured_frame, 
                                                             face_locations[0])
            
            if face_encoding is not None:
                self.face_encoding = face_encoding
                self.capture_status_label.config(
                    text="✓ Face captured successfully", 
                    fg=self.colors['success']
                )
                messagebox.showinfo("Success", "Face captured successfully!")
                self.logger.log('INFO', 'Face captured for registration')
            else:
                messagebox.showerror("Error", "Failed to encode face")
                
        except Exception as e:
            messagebox.showerror("Error", f"Face capture failed: {str(e)}")
            self.logger.log('ERROR', f'Face capture failed: {str(e)}')
    
    def _load_image_file(self):
        """Load image from file."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Load and process image
            image = cv2.imread(file_path)
            
            if image is None:
                messagebox.showerror("Error", "Failed to load image")
                return
            
            # Detect face
            face_locations = self.face_recognition.detect_faces(image)
            
            if not face_locations:
                messagebox.showwarning("Warning", "No face detected in image")
                return
            
            if len(face_locations) > 1:
                messagebox.showwarning("Warning", 
                                     "Multiple faces detected. Please use image with single face")
                return
            
            # Get encoding
            face_encoding = self.face_recognition.encode_face(image, face_locations[0])
            
            if face_encoding is not None:
                self.face_encoding = face_encoding
                self.captured_frame = image.copy()
                
                # Display image
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(image_rgb)
                img = img.resize((480, 360), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image=img)
                
                self.camera_label.config(image=photo, text='')
                self.camera_label.image = photo
                
                self.capture_status_label.config(
                    text="✓ Face loaded successfully", 
                    fg=self.colors['success']
                )
                
                self.logger.log('INFO', f'Face loaded from file: {file_path}')
            else:
                messagebox.showerror("Error", "Failed to encode face")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.logger.log('ERROR', f'Failed to load image: {str(e)}')
    
    def _register_student(self):
        """Register student with captured face."""
        # Validate inputs
        student_id = self.student_id_var.get().strip()
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        department = self.department_var.get().strip()
        batch = self.batch_var.get().strip()
        
        if not student_id:
            messagebox.showwarning("Warning", "Please enter Student ID")
            return
        
        if not name:
            messagebox.showwarning("Warning", "Please enter student name")
            return
        
        if self.face_encoding is None:
            messagebox.showwarning("Warning", "Please capture face first")
            return
        
        try:
            # Save face image
            photo_path = None
            if self.captured_frame is not None:
                image_dir = self.student_manager.image_dir
                os.makedirs(image_dir, exist_ok=True)
                photo_path = os.path.join(image_dir, f"{student_id}.jpg")
                cv2.imwrite(photo_path, self.captured_frame)
            
            # Register student
            success, message = self.student_manager.register_student(
                student_id=student_id,
                name=name,
                face_encoding=self.face_encoding,
                email=email if email else None,
                department=department if department else None,
                batch=batch if batch else None,
                photo_path=photo_path
            )
            
            if success:
                messagebox.showinfo("Success", message)
                self.logger.log('INFO', f'Student registered: {student_id}')
                
                # Reload known faces in face recognition module
                students = self.student_manager.db.get_all_students()
                self.face_recognition.load_known_faces(students)
                
                # Clear form
                self._clear_form()
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
            self.logger.log('ERROR', f'Registration failed: {str(e)}')
    
    def _clear_form(self):
        """Clear registration form."""
        self.student_id_var.set('')
        self.name_var.set('')
        self.email_var.set('')
        self.department_var.set('')
        self.batch_var.set('')
        self.face_encoding = None
        self.captured_frame = None
        self.capture_status_label.config(text="No face captured", 
                                        fg=self.colors['warning'])
    
    def cleanup(self):
        """Cleanup resources."""
        if self.camera_active:
            self._stop_camera()
