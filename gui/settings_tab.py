"""
Settings Tab Module
Application settings and configuration.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import hashlib


class SettingsTab:
    """Settings tab for application configuration."""
    
    def __init__(self, parent, config, colors, logger, on_settings_changed):
        """
        Initialize settings tab.
        
        Args:
            parent: Parent widget
            config: ConfigParser instance
            colors: Color scheme dictionary
            logger: Logger instance
            on_settings_changed: Callback function when settings are saved
        """
        self.parent = parent
        self.config = config
        self.colors = colors
        self.logger = logger
        self.on_settings_changed = on_settings_changed
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup settings user interface."""
        # Configure grid
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=20)
        
        ttk.Label(header_frame, text="Application Settings", 
                 style='Header.TLabel').pack(side='left')
        
        # Settings container with scrollbar
        self._create_settings_container()
    
    def _create_settings_container(self):
        """Create scrollable settings container."""
        container = ttk.Frame(self.frame)
        container.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        
        # Configure grid
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        
        # Canvas for scrolling
        canvas = tk.Canvas(container, bg=self.colors['white'], 
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient='vertical', 
                                 command=canvas.yview)
        
        self.settings_frame = ttk.Frame(canvas)
        
        self.settings_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.settings_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Add settings sections
        self._create_camera_settings()
        self._create_recognition_settings()
        self._create_database_settings()
        self._create_gui_settings()
        self._create_admin_settings()
        
        # Save button
        self._create_save_button()
    
    def _create_camera_settings(self):
        """Create camera settings section."""
        section = self._create_section("Camera Settings")
        
        # Camera index
        self._create_setting_row(
            section, "Camera Index:", 
            'camera_index',
            self.config.get('CAMERA', 'camera_index', fallback='0'),
            "Camera device index (usually 0 for built-in camera)"
        )
        
        # Frame width
        self._create_setting_row(
            section, "Frame Width:", 
            'frame_width',
            self.config.get('CAMERA', 'frame_width', fallback='640'),
            "Camera frame width in pixels"
        )
        
        # Frame height
        self._create_setting_row(
            section, "Frame Height:", 
            'frame_height',
            self.config.get('CAMERA', 'frame_height', fallback='480'),
            "Camera frame height in pixels"
        )
        
        # FPS
        self._create_setting_row(
            section, "FPS:", 
            'fps',
            self.config.get('CAMERA', 'fps', fallback='30'),
            "Frames per second"
        )
    
    def _create_recognition_settings(self):
        """Create face recognition settings section."""
        section = self._create_section("Face Recognition Settings")
        
        # Tolerance
        self._create_setting_row(
            section, "Tolerance:", 
            'tolerance',
            self.config.get('RECOGNITION', 'tolerance', fallback='0.6'),
            "Recognition tolerance (0.0-1.0, lower is stricter)"
        )
        
        # Model
        row = ttk.Frame(section)
        row.pack(fill='x', pady=10)
        
        ttk.Label(row, text="Detection Model:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w')
        
        self.model_var = tk.StringVar(
            value=self.config.get('RECOGNITION', 'model', fallback='hog')
        )
        
        model_frame = ttk.Frame(row)
        model_frame.pack(anchor='w', pady=(5, 0))
        
        ttk.Radiobutton(model_frame, text="HOG (Faster, CPU)", 
                       variable=self.model_var, 
                       value='hog').pack(side='left', padx=(0, 15))
        ttk.Radiobutton(model_frame, text="CNN (More accurate, GPU)", 
                       variable=self.model_var, 
                       value='cnn').pack(side='left')
        
        tk.Label(row, text="Model for face detection", 
                font=('Arial', 8), fg=self.colors['text']).pack(anchor='w', 
                                                                pady=(5, 0))
        
        # Process every N frames
        self._create_setting_row(
            section, "Process Every N Frames:", 
            'process_every_n_frames',
            self.config.get('RECOGNITION', 'process_every_n_frames', fallback='2'),
            "Process every Nth frame for better performance"
        )
    
    def _create_database_settings(self):
        """Create database settings section."""
        section = self._create_section("Database Settings")
        
        # Database path
        self._create_setting_row(
            section, "Database Path:", 
            'db_path',
            self.config.get('DATABASE', 'db_path', fallback='data/database/attendance.db'),
            "Path to SQLite database file"
        )
    
    def _create_gui_settings(self):
        """Create GUI settings section."""
        section = self._create_section("GUI Settings")
        
        # Theme
        row = ttk.Frame(section)
        row.pack(fill='x', pady=10)
        
        ttk.Label(row, text="Theme:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w')
        
        self.theme_var = tk.StringVar(
            value=self.config.get('GUI', 'theme', fallback='light')
        )
        
        theme_frame = ttk.Frame(row)
        theme_frame.pack(anchor='w', pady=(5, 0))
        
        ttk.Radiobutton(theme_frame, text="Light", 
                       variable=self.theme_var, 
                       value='light').pack(side='left', padx=(0, 15))
        ttk.Radiobutton(theme_frame, text="Dark", 
                       variable=self.theme_var, 
                       value='dark').pack(side='left')
        
        tk.Label(row, text="Application theme (requires restart)", 
                font=('Arial', 8), fg=self.colors['text']).pack(anchor='w', 
                                                                pady=(5, 0))
        
        # Window size
        self._create_setting_row(
            section, "Window Width:", 
            'window_width',
            self.config.get('GUI', 'window_width', fallback='1200'),
            "Application window width"
        )
        
        self._create_setting_row(
            section, "Window Height:", 
            'window_height',
            self.config.get('GUI', 'window_height', fallback='800'),
            "Application window height"
        )
    
    def _create_admin_settings(self):
        """Create admin settings section."""
        section = self._create_section("Admin Settings")
        
        # Username
        self._create_setting_row(
            section, "Admin Username:", 
            'admin_username',
            self.config.get('ADMIN', 'username', fallback='admin'),
            "Administrator username"
        )
        
        # Password change
        row = ttk.Frame(section)
        row.pack(fill='x', pady=10)
        
        ttk.Label(row, text="Change Password:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        password_frame = ttk.Frame(row)
        password_frame.pack(anchor='w')
        
        ttk.Label(password_frame, text="New Password:").grid(row=0, column=0, 
                                                            sticky='w', pady=5)
        self.new_password_var = tk.StringVar()
        ttk.Entry(password_frame, textvariable=self.new_password_var, 
                 show='*', width=25).grid(row=0, column=1, padx=(10, 0), pady=5)
        
        ttk.Label(password_frame, text="Confirm Password:").grid(row=1, column=0, 
                                                                 sticky='w', pady=5)
        self.confirm_password_var = tk.StringVar()
        ttk.Entry(password_frame, textvariable=self.confirm_password_var, 
                 show='*', width=25).grid(row=1, column=1, padx=(10, 0), pady=5)
        
        tk.Label(row, text="Leave blank to keep current password", 
                font=('Arial', 8), fg=self.colors['text']).pack(anchor='w', 
                                                                pady=(5, 0))
    
    def _create_section(self, title):
        """
        Create a settings section.
        
        Args:
            title: Section title
            
        Returns:
            Section frame
        """
        # Section container
        section_container = ttk.Frame(self.settings_frame, style='Card.TFrame')
        section_container.pack(fill='x', padx=20, pady=10)
        
        # Section content
        section = ttk.Frame(section_container)
        section.pack(fill='x', padx=25, pady=20)
        
        # Title
        ttk.Label(section, text=title, style='Title.TLabel').pack(anchor='w', 
                                                                   pady=(0, 15))
        
        return section
    
    def _create_setting_row(self, parent, label, key, default_value, help_text):
        """
        Create a setting row with label, entry, and help text.
        
        Args:
            parent: Parent frame
            label: Setting label
            key: Setting key for storage
            default_value: Default value
            help_text: Help text
        """
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=10)
        
        # Label
        ttk.Label(row, text=label, font=('Arial', 10, 'bold')).pack(anchor='w')
        
        # Entry
        var = tk.StringVar(value=default_value)
        entry = ttk.Entry(row, textvariable=var, width=40)
        entry.pack(anchor='w', pady=(5, 0))
        
        # Store variable reference
        setattr(self, f'{key}_var', var)
        
        # Help text
        tk.Label(row, text=help_text, font=('Arial', 8), 
                fg=self.colors['text']).pack(anchor='w', pady=(5, 0))
    
    def _create_save_button(self):
        """Create save settings button."""
        button_frame = ttk.Frame(self.settings_frame)
        button_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(button_frame, text="💾 Save Settings", 
                  command=self._save_settings,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self._reset_defaults).pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Export Config", 
                  command=self._export_config).pack(side='left', padx=5)
    
    def _save_settings(self):
        """Save settings to config file."""
        try:
            # Camera settings
            self.config.set('CAMERA', 'camera_index', self.camera_index_var.get())
            self.config.set('CAMERA', 'frame_width', self.frame_width_var.get())
            self.config.set('CAMERA', 'frame_height', self.frame_height_var.get())
            self.config.set('CAMERA', 'fps', self.fps_var.get())
            
            # Recognition settings
            self.config.set('RECOGNITION', 'tolerance', self.tolerance_var.get())
            self.config.set('RECOGNITION', 'model', self.model_var.get())
            self.config.set('RECOGNITION', 'process_every_n_frames', 
                          self.process_every_n_frames_var.get())
            
            # Database settings
            self.config.set('DATABASE', 'db_path', self.db_path_var.get())
            
            # GUI settings
            self.config.set('GUI', 'theme', self.theme_var.get())
            self.config.set('GUI', 'window_width', self.window_width_var.get())
            self.config.set('GUI', 'window_height', self.window_height_var.get())
            
            # Admin settings
            self.config.set('ADMIN', 'username', self.admin_username_var.get())
            
            # Password change
            new_password = self.new_password_var.get()
            confirm_password = self.confirm_password_var.get()
            
            if new_password or confirm_password:
                if new_password != confirm_password:
                    messagebox.showerror("Error", "Passwords do not match")
                    return
                
                if len(new_password) < 6:
                    messagebox.showerror("Error", 
                                       "Password must be at least 6 characters")
                    return
                
                # Hash password
                password_hash = hashlib.sha256(new_password.encode()).hexdigest()
                self.config.set('ADMIN', 'password_hash', password_hash)
            
            # Write to file
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
            
            # Clear password fields
            self.new_password_var.set('')
            self.confirm_password_var.set('')
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.logger.info('Settings saved')
            
            # Callback
            if self.on_settings_changed:
                self.on_settings_changed()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            self.logger.error(f'Failed to save settings: {str(e)}')
    
    def _reset_defaults(self):
        """Reset settings to defaults."""
        if not messagebox.askyesno("Confirm Reset", 
                                  "Are you sure you want to reset all settings to defaults?"):
            return
        
        try:
            # Reset to defaults
            self.camera_index_var.set('0')
            self.frame_width_var.set('640')
            self.frame_height_var.set('480')
            self.fps_var.set('30')
            
            self.tolerance_var.set('0.6')
            self.model_var.set('hog')
            self.process_every_n_frames_var.set('2')
            
            self.db_path_var.set('data/database/attendance.db')
            
            self.theme_var.set('light')
            self.window_width_var.set('1200')
            self.window_height_var.set('800')
            
            self.admin_username_var.set('admin')
            
            messagebox.showinfo("Success", "Settings reset to defaults")
            self.logger.info('Settings reset to defaults')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset settings: {str(e)}")
            self.logger.error(f'Failed to reset settings: {str(e)}')
    
    def _export_config(self):
        """Export configuration to file."""
        from tkinter import filedialog
        from datetime import datetime
        import shutil
        
        file_path = filedialog.asksaveasfilename(
            defaultextension='.ini',
            filetypes=[("INI files", "*.ini"), ("All files", "*.*")],
            initialfile=f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ini"
        )
        
        if file_path:
            try:
                shutil.copy('config.ini', file_path)
                messagebox.showinfo("Success", 
                                  f"Configuration exported to:\n{file_path}")
                self.logger.info(f'Configuration exported to: {file_path}')
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
                self.logger.error(f'Configuration export failed: {str(e)}')
