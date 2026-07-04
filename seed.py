"""
Run this once after creating the schema (database/schema.sql) to insert
a default admin account and a bit of sample data.

Usage:
    python seed.py
"""
import mysql.connector
from werkzeug.security import generate_password_hash
from config import Config

conn = mysql.connector.connect(
    host=Config.MYSQL_HOST,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DB,
    port=Config.MYSQL_PORT,
)
cur = conn.cursor()

# --- Admin user ---------------------------------------------------
cur.execute("SELECT user_id FROM users WHERE username=%s", ("admin",))
if not cur.fetchone():
    cur.execute(
        "INSERT INTO users (username, password_hash, role, email) VALUES (%s,%s,%s,%s)",
        ("admin", generate_password_hash("admin123"), "admin", "admin@campus-erp.local"),
    )
    print("Created default admin (admin / admin123)")

# --- Sample course & class -----------------------------------------
cur.execute("SELECT course_id FROM courses WHERE course_code=%s", ("CSE",))
row = cur.fetchone()
if not row:
    cur.execute(
        "INSERT INTO courses (course_name, course_code, duration_years) VALUES (%s,%s,%s)",
        ("Computer Science & Engineering", "CSE", 4),
    )
    course_id = cur.lastrowid
    print("Created sample course: CSE")
else:
    course_id = row[0]

cur.execute("SELECT class_id FROM classes WHERE class_name=%s", ("CSE - Year 2 - Section A",))
row = cur.fetchone()
if not row:
    cur.execute(
        "INSERT INTO classes (course_id, class_name, academic_year) VALUES (%s,%s,%s)",
        (course_id, "CSE - Year 2 - Section A", "2025-2026"),
    )
    class_id = cur.lastrowid
    print("Created sample class: CSE - Year 2 - Section A")
else:
    class_id = row[0]

# --- Sample subject --------------------------------------------------
cur.execute("SELECT subject_id FROM subjects WHERE subject_code=%s", ("CS201",))
if not cur.fetchone():
    cur.execute(
        "INSERT INTO subjects (subject_name, subject_code, class_id) VALUES (%s,%s,%s)",
        ("Data Structures", "CS201", class_id),
    )
    print("Created sample subject: Data Structures (CS201)")

conn.commit()
cur.close()
conn.close()
print("Seeding complete.")
