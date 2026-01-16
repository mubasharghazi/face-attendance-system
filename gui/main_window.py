"""
Main Window Module
Main application window with tabbed interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import configparser
from pathlib import Path

from gui.dashboard_tab import DashboardTab
from gui.register_tab import RegisterTab
from gui.attendance_tab import AttendanceTab
from gui.records_tab import RecordsTab
from gui.reports_tab import ReportsTab
from gui.settings_tab import SettingsTab

from database.db_manager import DatabaseManager
from modules.student_manager import StudentManager
from modules.attendance_manager import AttendanceManager
from modules.face_recognition_module import FaceRecognitionModule
from modules.report_generator import ReportGenerator
from utils.camera_handler import CameraHandler
from utils.logger import Logger


class MainWindow:
    """Main application window with tabbed interface."""
    
    def __init__(self, config_path: str = 'config.ini'):
        """
        Initialize main window.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Initialize logger
        log_dir = self.config.get('PATHS', 'logs', fallback='logs')
        self.logger = Logger(log_dir)
        self.logger.log('INFO', 'Application started')
        
        # Initialize core components
        self._initialize_core_components()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Face Attendance System")
        
        # Get window dimensions from config
        width = self.config.getint('GUI', 'window_width', fallback=1200)
        height = self.config.getint('GUI', 'window_height', fallback=800)
        
        # Set window size and position
        self.root.geometry(f"{width}x{height}")
        
        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Set minimum size
        self.root.minsize(1000, 600)
        
        # Configure style
        self._configure_style()
        
        # Setup UI
        self._setup_ui()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.logger.log('INFO', 'Main window initialized')
    
    def _initialize_core_components(self):
        """Initialize core system components."""
        try:
            # Database
            db_path = self.config.get('DATABASE', 'db_path', fallback='data/database/attendance.db')
            self.db_manager = DatabaseManager(db_path)
            
            # Student Manager
            student_images_dir = self.config.get('PATHS', 'student_images', 
                                                 fallback='data/student_images')
            self.student_manager = StudentManager(self.db_manager, student_images_dir)
            
            # Attendance Manager
            self.attendance_manager = AttendanceManager(self.db_manager)
            
            # Face Recognition
            tolerance = self.config.getfloat('RECOGNITION', 'tolerance', fallback=0.6)
            model = self.config.get('RECOGNITION', 'model', fallback='hog')
            process_frames = self.config.getint('RECOGNITION', 'process_every_n_frames', 
                                               fallback=2)
            self.face_recognition = FaceRecognitionModule(tolerance, model, process_frames)
            
            # Load known faces
            students = self.db_manager.get_all_students()
            self.face_recognition.load_known_faces(students)
            
            # Camera Handler
            camera_index = self.config.getint('CAMERA', 'camera_index', fallback=0)
            frame_width = self.config.getint('CAMERA', 'frame_width', fallback=640)
            frame_height = self.config.getint('CAMERA', 'frame_height', fallback=480)
            self.camera_handler = CameraHandler(camera_index, frame_width, frame_height)
            
            # Report Generator
            export_dir = self.config.get('PATHS', 'exports', fallback='exports')
            self.report_generator = ReportGenerator(self.db_manager, export_dir)
            
        except Exception as e:
            messagebox.showerror("Initialization Error", 
                               f"Failed to initialize system components:\n{str(e)}")
            raise
    
    def _configure_style(self):
        """Configure application style and theme."""
        style = ttk.Style()
        
        # Use clam theme as base
        style.theme_use('clam')
        
        # Define color scheme (blue/white theme)
        self.colors = {
            'primary': '#2196F3',      # Blue
            'primary_dark': '#1976D2',
            'primary_light': '#BBDEFB',
            'secondary': '#FFC107',     # Amber
            'success': '#4CAF50',       # Green
            'danger': '#F44336',        # Red
            'warning': '#FF9800',       # Orange
            'info': '#00BCD4',          # Cyan
            'light': '#F5F5F5',
            'dark': '#212121',
            'white': '#FFFFFF',
            'text': '#333333',
            'border': '#DDDDDD'
        }
        
        # Configure ttk styles
        style.configure('TFrame', background=self.colors['white'])
        style.configure('TLabel', background=self.colors['white'], 
                       foreground=self.colors['text'], font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), padding=6)
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'), 
                       padding=8, background=self.colors['primary'])
        
        style.configure('TNotebook', background=self.colors['light'], 
                       borderwidth=0, padding=0)
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'), 
                       padding=[20, 10])
        
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', self.colors['white'])])
        
        style.configure('Card.TFrame', background=self.colors['white'], 
                       relief='solid', borderwidth=1)
        style.configure('Header.TLabel', font=('Arial', 16, 'bold'), 
                       foreground=self.colors['primary'])
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 9), 
                       foreground=self.colors['text'])
        
        # Treeview style
        style.configure('Treeview', font=('Arial', 9), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), 
                       background=self.colors['primary'], 
                       foreground=self.colors['white'])
    
    def _setup_ui(self):
        """Setup user interface."""
        # Create header
        self._create_header()
        
        # Create notebook (tabs)
        self._create_notebook()
        
        # Create status bar
        self._create_statusbar()
    
    def _create_header(self):
        """Create application header."""
        header_frame = ttk.Frame(self.root, style='Card.TFrame')
        header_frame.pack(fill='x', padx=0, pady=0)
        
        # Configure grid weight
        header_frame.columnconfigure(1, weight=1)
        
        # App icon/logo placeholder
        logo_label = ttk.Label(header_frame, text="📸", font=('Arial', 24))
        logo_label.grid(row=0, column=0, padx=20, pady=15, sticky='w')
        
        # App title
        title_label = ttk.Label(header_frame, text="Face Attendance System", 
                               style='Header.TLabel')
        title_label.grid(row=0, column=1, padx=10, pady=15, sticky='w')
        
        # Current date/time
        import datetime
        current_time = datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p")
        time_label = ttk.Label(header_frame, text=current_time, 
                              style='Info.TLabel')
        time_label.grid(row=0, column=2, padx=20, pady=15, sticky='e')
    
    def _create_notebook(self):
        """Create tabbed notebook interface."""
        # Create notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        try:
            # Dashboard Tab
            self.dashboard_tab = DashboardTab(
                self.notebook, 
                self.db_manager,
                self.attendance_manager,
                self.colors,
                self.logger
            )
            self.notebook.add(self.dashboard_tab.frame, text="📊 Dashboard")
            
            # Register Tab
            self.register_tab = RegisterTab(
                self.notebook,
                self.student_manager,
                self.face_recognition,
                self.camera_handler,
                self.colors,
                self.logger
            )
            self.notebook.add(self.register_tab.frame, text="➕ Register Student")
            
            # Attendance Tab
            self.attendance_tab = AttendanceTab(
                self.notebook,
                self.attendance_manager,
                self.face_recognition,
                self.camera_handler,
                self.db_manager,
                self.colors,
                self.logger
            )
            self.notebook.add(self.attendance_tab.frame, text="✓ Mark Attendance")
            
            # Records Tab
            self.records_tab = RecordsTab(
                self.notebook,
                self.db_manager,
                self.colors,
                self.logger
            )
            self.notebook.add(self.records_tab.frame, text="📋 Attendance Records")
            
            # Reports Tab
            self.reports_tab = ReportsTab(
                self.notebook,
                self.report_generator,
                self.db_manager,
                self.colors,
                self.logger
            )
            self.notebook.add(self.reports_tab.frame, text="📈 Reports")
            
            # Settings Tab
            self.settings_tab = SettingsTab(
                self.notebook,
                self.config,
                self.colors,
                self.logger,
                self._on_settings_changed
            )
            self.notebook.add(self.settings_tab.frame, text="⚙️ Settings")
            
        except Exception as e:
            self.logger.log('ERROR', f'Failed to create tabs: {str(e)}')
            messagebox.showerror("Error", f"Failed to create tabs:\n{str(e)}")
    
    def _create_statusbar(self):
        """Create application status bar."""
        statusbar_frame = ttk.Frame(self.root, style='Card.TFrame')
        statusbar_frame.pack(fill='x', side='bottom', padx=0, pady=0)
        
        self.status_label = ttk.Label(statusbar_frame, text="Ready", 
                                     style='Info.TLabel')
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Version info
        version_label = ttk.Label(statusbar_frame, text="v1.0.0", 
                                 style='Info.TLabel')
        version_label.pack(side='right', padx=10, pady=5)
    
    def _on_settings_changed(self):
        """Handle settings change event."""
        self.logger.log('INFO', 'Settings changed, reloading configuration')
        
        # Reload configuration
        self.config.read('config.ini')
        
        # Update components if needed
        messagebox.showinfo("Settings", 
                          "Settings saved. Some changes may require restart.")
    
    def _on_closing(self):
        """Handle window close event."""
        # Confirm exit
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                # Stop camera if running
                if hasattr(self, 'camera_handler') and self.camera_handler.is_running:
                    self.camera_handler.stop()
                
                # Stop any running camera feeds in tabs
                if hasattr(self, 'register_tab'):
                    self.register_tab.cleanup()
                if hasattr(self, 'attendance_tab'):
                    self.attendance_tab.cleanup()
                
                self.logger.log('INFO', 'Application closed')
                
            except Exception as e:
                self.logger.log('ERROR', f'Error during cleanup: {str(e)}')
            
            self.root.destroy()
    
    def update_status(self, message: str):
        """
        Update status bar message.
        
        Args:
            message: Status message to display
        """
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Run the application main loop."""
        self.root.mainloop()


def main():
    """Main entry point for the application."""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        messagebox.showerror("Fatal Error", 
                           f"Failed to start application:\n{str(e)}")
        raise


if __name__ == '__main__':
    main()
