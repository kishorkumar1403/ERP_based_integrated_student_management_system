-- ============================================================
-- ERP Integrated Student Management System
-- Database Schema (MySQL)
-- ============================================================

CREATE DATABASE IF NOT EXISTS student_erp;
USE student_erp;

-- ------------------------------------------------------------
-- USERS: login accounts for admin / teacher / student
-- ------------------------------------------------------------
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- COURSES: degree / program offered
-- ------------------------------------------------------------
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    duration_years INT NOT NULL DEFAULT 4
);

-- ------------------------------------------------------------
-- CLASSES: a specific section/batch under a course
-- ------------------------------------------------------------
CREATE TABLE classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    class_name VARCHAR(50) NOT NULL,      -- e.g. "CSE - Year 2 - Section A"
    academic_year VARCHAR(20) NOT NULL,   -- e.g. "2025-2026"
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- TEACHERS
-- ------------------------------------------------------------
CREATE TABLE teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    department VARCHAR(100),
    phone VARCHAR(20),
    joining_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- SUBJECTS: taught within a class, by a teacher
-- ------------------------------------------------------------
CREATE TABLE subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    subject_code VARCHAR(20) NOT NULL,
    class_id INT NOT NULL,
    teacher_id INT,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- STUDENTS
-- ------------------------------------------------------------
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    roll_number VARCHAR(30) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE,
    gender ENUM('Male', 'Female', 'Other'),
    phone VARCHAR(20),
    address VARCHAR(255),
    class_id INT,
    admission_date DATE DEFAULT (CURRENT_DATE),
    guardian_name VARCHAR(100),
    guardian_phone VARCHAR(20),
    photo_path VARCHAR(255),
    status ENUM('active', 'inactive', 'graduated') DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- ATTENDANCE
-- ------------------------------------------------------------
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('present', 'absent', 'late') NOT NULL,
    marked_by INT,  -- teacher_id
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by) REFERENCES teachers(teacher_id) ON DELETE SET NULL,
    UNIQUE KEY unique_attendance (student_id, subject_id, attendance_date)
);

-- ------------------------------------------------------------
-- EXAMS
-- ------------------------------------------------------------
CREATE TABLE exams (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_name VARCHAR(100) NOT NULL,   -- e.g. "Mid Term", "Final"
    class_id INT NOT NULL,
    exam_date DATE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- MARKS / RESULTS
-- ------------------------------------------------------------
CREATE TABLE marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    marks_obtained DECIMAL(5,2) NOT NULL,
    max_marks DECIMAL(5,2) NOT NULL DEFAULT 100,
    grade VARCHAR(5),
    FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    UNIQUE KEY unique_mark (exam_id, student_id, subject_id)
);

-- ------------------------------------------------------------
-- FEES
-- ------------------------------------------------------------
CREATE TABLE fee_structure (
    fee_structure_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

CREATE TABLE fee_payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_date DATE DEFAULT (CURRENT_DATE),
    payment_mode ENUM('cash', 'card', 'online', 'cheque') DEFAULT 'online',
    remarks VARCHAR(255),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- NOTICES / ANNOUNCEMENTS
-- ------------------------------------------------------------
CREATE TABLE notices (
    notice_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    content TEXT NOT NULL,
    posted_by INT,
    posted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (posted_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- SEED DATA: default admin login (password: admin123)
-- Hash below is a bcrypt/werkzeug hash generated at setup time by seed.py
-- ------------------------------------------------------------
-- Run `python seed.py` after creating the schema to insert sample data safely.
