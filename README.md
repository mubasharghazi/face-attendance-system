# Face Recognition Attendance System

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

A complete AI-powered Face Recognition Attendance System with a professional desktop GUI for automated attendance marking using facial recognition technology.

## 📋 Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Features
- **Student Registration** - Register students with facial recognition
  - Capture multiple photos using webcam
  - Store face encodings securely in database
  - Validate duplicate student IDs
  - Image quality checks and preprocessing
  - Edit/delete student records

- **Real-time Face Recognition** - Automatic face detection and recognition
  - Recognize multiple faces simultaneously
  - Display confidence scores
  - Adjustable recognition threshold
  - Support for different lighting conditions
  - Unknown face detection

- **Automated Attendance Marking** - Intelligent attendance system
  - Automatic marking when face is recognized
  - Prevent duplicate entries for same day
  - Visual and audio confirmation
  - Manual attendance override option
  - Bulk attendance view

- **Comprehensive Reports & Analytics**
  - Daily attendance reports
  - Student-wise attendance history
  - Department-wise statistics
  - Monthly summaries with percentages
  - Defaulters list (low attendance)
  - Export to CSV, Excel, and PDF formats

- **Professional GUI Interface**
  - Modern tabbed interface (Dashboard, Register, Attendance, Records, Reports, Settings)
  - Real-time statistics and visualizations
  - Search and filter functionality
  - Context menus and keyboard shortcuts
  - Responsive design with professional color scheme

- **Database Management**
  - SQLite database with efficient indexing
  - Secure data storage with BLOB support
  - Backup and restore functionality
  - Transaction support for data integrity

- **Advanced Settings**
  - Camera selection (multiple cameras support)
  - Recognition threshold adjustment
  - Theme toggle (light/dark mode)
  - Database backup/restore
  - Admin authentication

## 📸 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)
*Overview of attendance statistics and recent entries*

### Student Registration
![Registration](screenshots/registration.png)
*Register new students with face capture*

### Attendance Marking
![Attendance](screenshots/attendance.png)
*Real-time face recognition and attendance marking*

### Reports
![Reports](screenshots/reports.png)
*Generate and export attendance reports*

## 📦 Prerequisites

- **Python**: Version 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Webcam**: Required for face capture and recognition
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: At least 500MB free space

### System Requirements

**Windows:**
- Windows 10 or later
- Visual C++ Redistributable (for dlib)

**macOS:**
- macOS 10.14 (Mojave) or later
- Xcode Command Line Tools

**Linux:**
- Ubuntu 18.04 or later (or equivalent)
- CMake and build-essential packages

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/mubasharghazi/face-attendance-system.git
cd face-attendance-system
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install system dependencies first (Linux only)
sudo apt-get update
sudo apt-get install cmake build-essential

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** Installing `dlib` may take several minutes as it needs to be compiled.

### Step 4: Verify Installation

```bash
python -c "import cv2, face_recognition, numpy, pandas, PIL; print('All dependencies installed successfully!')"
```

### Step 5: Initialize Database

The database will be automatically created on first run. Alternatively, you can manually initialize it:

```bash
python -c "from database.db_manager import DatabaseManager; DatabaseManager('data/database/attendance.db')"
```

## 💻 Usage

### Starting the Application

```bash
python main.py
```

### Default Admin Credentials

- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Important:** Change the default password in Settings after first login.

### Registering Students

1. Navigate to the **Register Student** tab
2. Fill in student information (ID, Name, Email, Department, Batch)
3. Click **Start Camera** to begin webcam capture
4. Click **Capture Photo** to take a photo (capture 5-10 photos from different angles)
5. Review captured images in the gallery
6. Click **Save Student** to register

### Marking Attendance

1. Navigate to the **Mark Attendance** tab
2. Click **Start Camera** to begin face recognition
3. Face will be automatically detected and recognized
4. Attendance is marked automatically when a registered face is detected
5. Green highlight indicates successful attendance marking
6. View current session attendance in the table below

### Viewing Records

1. Navigate to the **View Records** tab
2. Use search box to find students by name, ID, or department
3. Apply filters for date range, department, or batch
4. Click on records to view details
5. Right-click for edit/delete options

### Generating Reports

1. Navigate to the **Reports** tab
2. Select report type:
   - **Daily Report**: Attendance for a specific date
   - **Student Report**: Individual student history
   - **Date Range Report**: Attendance within a date range
   - **Department Report**: Statistics by department
   - **Defaulters Report**: Students with low attendance
3. Set filters (date range, department, batch, threshold)
4. Click **Generate Report**
5. Preview report in table
6. Click **Export to CSV**, **Export to Excel**, or **Export to PDF**

### Settings Configuration

Navigate to **Settings** tab to configure:
- **Camera**: Select camera device and resolution
- **Recognition**: Adjust tolerance threshold (0.4-0.8)
- **Theme**: Toggle between light and dark mode
- **Database**: Backup, restore, or clear data
- **Admin**: Change password

## ⚙️ Configuration

### Configuration File (config.ini)

The `config.ini` file contains application settings:

```ini
[CAMERA]
camera_index = 0              # Camera device index (0 for default)
frame_width = 640             # Frame width in pixels
frame_height = 480            # Frame height in pixels
fps = 30                      # Frames per second

[RECOGNITION]
tolerance = 0.6               # Recognition threshold (0.4-0.8, lower is stricter)
model = hog                   # Detection model (hog or cnn)
process_every_n_frames = 2    # Process every nth frame for performance

[DATABASE]
db_path = data/database/attendance.db  # Database file path

[PATHS]
student_images = data/student_images   # Student photos directory
exports = exports                      # Exported reports directory
logs = logs                            # Log files directory

[GUI]
theme = light                 # Theme (light or dark)
window_width = 1200           # Window width
window_height = 800           # Window height

[ADMIN]
username = admin              # Admin username
password_hash = 8c6976e5b5... # SHA-256 hashed password
```

### Changing Admin Password

1. Go to **Settings** > **Admin** section
2. Enter current password
3. Enter new password
4. Click **Change Password**

Alternatively, generate a new password hash:

```python
import hashlib
password = "your_new_password"
hash_value = hashlib.sha256(password.encode()).hexdigest()
print(hash_value)
```

Update the `password_hash` in `config.ini` with the new hash.

## 📁 Project Structure

```
face-attendance-system/
├── main.py                          # Application entry point
├── config.ini                       # Configuration file
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── .gitignore                       # Git ignore file
│
├── database/                        # Database module
│   ├── __init__.py
│   ├── db_manager.py                # Database operations
│   └── schema.sql                   # Database schema
│
├── modules/                         # Core modules
│   ├── __init__.py
│   ├── face_recognition_module.py   # Face detection/recognition
│   ├── student_manager.py           # Student CRUD operations
│   ├── attendance_manager.py        # Attendance operations
│   └── report_generator.py          # Report generation
│
├── gui/                             # GUI modules
│   ├── __init__.py
│   ├── main_window.py               # Main application window
│   ├── dashboard_tab.py             # Dashboard tab
│   ├── register_tab.py              # Registration tab
│   ├── attendance_tab.py            # Attendance marking tab
│   ├── records_tab.py               # View records tab
│   ├── reports_tab.py               # Reports tab
│   └── settings_tab.py              # Settings tab
│
├── utils/                           # Utility modules
│   ├── __init__.py
│   ├── camera_handler.py            # Camera operations
│   ├── image_processor.py           # Image preprocessing
│   ├── validators.py                # Input validation
│   └── logger.py                    # Logging configuration
│
├── assets/                          # Assets (icons, images)
│   └── .gitkeep
│
├── data/                            # Data directory
│   ├── student_images/              # Student photos
│   │   └── .gitkeep
│   └── database/                    # Database files
│       └── .gitkeep
│
├── logs/                            # Log files
│   └── .gitkeep
│
└── exports/                         # Exported reports
    └── .gitkeep
```

## 🛠️ Technologies Used

| Technology | Description | Version |
|------------|-------------|---------|
| **Python** | Programming language | 3.8+ |
| **OpenCV** | Computer vision library | 4.5.0+ |
| **face_recognition** | Face recognition library | 1.3.0+ |
| **dlib** | Machine learning toolkit | 19.22.0+ |
| **Tkinter** | GUI framework | Built-in |
| **SQLite3** | Database | Built-in |
| **NumPy** | Numerical computing | 1.19.0+ |
| **Pandas** | Data analysis | 1.2.0+ |
| **Pillow** | Image processing | 8.0.0+ |
| **openpyxl** | Excel file handling | 3.0.0+ |

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Camera Not Working

**Problem:** Camera feed not displaying or "Camera not available" error

**Solutions:**
- Check if webcam is properly connected
- Ensure no other application is using the camera
- Try changing camera index in Settings (0, 1, 2, etc.)
- On Linux, check camera permissions: `sudo usermod -a -G video $USER`
- Restart the application

#### 2. Face Not Detected

**Problem:** System doesn't detect faces during registration or attendance

**Solutions:**
- Ensure adequate lighting (avoid too bright or too dark conditions)
- Position face directly in front of camera
- Remove any obstructions (hats, masks, sunglasses)
- Move closer to the camera (optimal distance: 1-2 feet)
- Clean camera lens
- Check image quality in preview

#### 3. Recognition Accuracy Issues

**Problem:** System recognizes wrong person or frequently says "Unknown"

**Solutions:**
- Adjust recognition threshold in Settings (lower for stricter matching)
- Re-register student with more photos from different angles
- Ensure good lighting during registration and recognition
- Capture photos with different facial expressions
- Avoid similar-looking individuals in the same frame
- Clean camera lens

#### 4. Installation Problems

**Problem:** Errors during `pip install` or dependency installation

**Solutions:**

**dlib installation fails:**
```bash
# Windows: Install Visual C++ Build Tools first
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Linux:
sudo apt-get install cmake build-essential

# macOS:
xcode-select --install
brew install cmake
```

**face_recognition installation fails:**
```bash
# Install dlib first, then face_recognition
pip install dlib
pip install face_recognition
```

**OpenCV issues:**
```bash
# Uninstall and reinstall
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python
```

#### 5. Database Errors

**Problem:** Database locked or corruption errors

**Solutions:**
- Close all instances of the application
- Use Database > Backup in Settings to save data
- Delete `data/database/attendance.db`
- Restart application (database will be recreated)
- Use Database > Restore to recover data

#### 6. Performance Issues

**Problem:** Application is slow or laggy

**Solutions:**
- Increase `process_every_n_frames` in config.ini (try 3 or 4)
- Reduce camera resolution in Settings
- Close other resource-intensive applications
- Ensure adequate RAM (8GB recommended)
- Use 'hog' model instead of 'cnn' for detection

#### 7. Export Not Working

**Problem:** Cannot export reports to Excel or PDF

**Solutions:**
- Ensure openpyxl is installed: `pip install openpyxl`
- For PDF: `pip install reportlab`
- Check export directory permissions
- Close any open Excel/PDF files with same name
- Try exporting to CSV first (always works)

### Getting Help

If you encounter issues not covered here:

1. Check log files in `logs/` directory
2. Search existing GitHub issues
3. Create a new issue with:
   - Error message (from logs)
   - Steps to reproduce
   - System information (OS, Python version)
   - Screenshots (if applicable)

## 🚀 Future Enhancements

Potential improvements for future versions:

- [ ] **Web Interface** - Browser-based access using Flask/Django
- [ ] **Mobile App** - Android and iOS applications
- [ ] **Cloud Storage** - AWS S3/Azure integration for photos
- [ ] **Email Notifications** - Send reports and alerts via email
- [ ] **SMS Integration** - Notify students/parents about attendance
- [ ] **Multi-language Support** - Internationalization (i18n)
- [ ] **Biometric Integration** - Fingerprint and RFID support
- [ ] **API Development** - RESTful API for third-party integration
- [ ] **Advanced Analytics** - ML-based predictions and insights
- [ ] **Role-based Access** - Multiple user roles (admin, teacher, student)
- [ ] **Live Dashboard** - Real-time web dashboard
- [ ] **Automated Backups** - Scheduled database backups
- [ ] **Integration with LMS** - Canvas, Moodle, Google Classroom
- [ ] **QR Code Support** - Fallback attendance method
- [ ] **GPU Acceleration** - Faster face recognition using CUDA

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit your changes**: `git commit -m 'Add some AmazingFeature'`
4. **Push to the branch**: `git push origin feature/AmazingFeature`
5. **Open a Pull Request**

### Coding Standards

- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Write meaningful commit messages
- Add unit tests for new features
- Update documentation as needed

### Reporting Bugs

Use GitHub Issues to report bugs. Include:
- Bug description
- Steps to reproduce
- Expected vs actual behavior
- System information
- Screenshots/logs

## 📄 License

This project is licensed under the MIT License. See below for details:

```
MIT License

Copyright (c) 2024 Face Attendance System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👥 Authors

- **Face Attendance System Team** - *Initial work*

## 🙏 Acknowledgments

- [face_recognition](https://github.com/ageitgey/face_recognition) by Adam Geitgey
- [dlib](http://dlib.net/) by Davis King
- [OpenCV](https://opencv.org/) team
- All open-source contributors

---

## 📞 Support

For support and questions:
- 📧 Email: support@faceattendance.com
- 🐛 Issues: [GitHub Issues](https://github.com/mubasharghazi/face-attendance-system/issues)
- 📖 Documentation: [Wiki](https://github.com/mubasharghazi/face-attendance-system/wiki)

---

**Made with ❤️ for educational institutions worldwide**