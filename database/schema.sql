-- Face Attendance System Database Schema

-- Students Table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT,
    department TEXT,
    batch TEXT,
    face_encoding BLOB NOT NULL,
    photo_path TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    status TEXT DEFAULT 'Present',
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    UNIQUE(student_id, date)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id);
