import os
from functools import wraps
from datetime import date

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
import db

app = Flask(__name__)
app.config.from_object(Config)
db.init_pool(app)
app.teardown_appcontext(db.close_db)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# ------------------------------------------------------------------
# Auth helpers
# ------------------------------------------------------------------
def login_required(roles=None):
    """Decorator to require login, optionally restricted to specific roles."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            if roles and session.get("role") not in roles:
                flash("You do not have permission to view that page.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


# ------------------------------------------------------------------
# Auth routes
# ------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = db.query(
            "SELECT * FROM users WHERE username = %s", (username,), fetchone=True
        )
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------
@app.route("/dashboard")
@login_required()
def dashboard():
    stats = {}
    stats["total_students"] = db.query(
        "SELECT COUNT(*) AS c FROM students WHERE status='active'", fetchone=True
    )["c"]
    stats["total_teachers"] = db.query(
        "SELECT COUNT(*) AS c FROM teachers", fetchone=True
    )["c"]
    stats["total_classes"] = db.query(
        "SELECT COUNT(*) AS c FROM classes", fetchone=True
    )["c"]
    stats["fees_collected"] = db.query(
        "SELECT COALESCE(SUM(amount_paid),0) AS s FROM fee_payments", fetchone=True
    )["s"]
    notices = db.query(
        "SELECT * FROM notices ORDER BY posted_on DESC LIMIT 5"
    )
    return render_template("dashboard.html", stats=stats, notices=notices)


# ------------------------------------------------------------------
# Students
# ------------------------------------------------------------------
@app.route("/students")
@login_required(["admin", "teacher"])
def students_list():
    search = request.args.get("q", "").strip()
    if search:
        rows = db.query(
            """SELECT s.*, c.class_name FROM students s
               LEFT JOIN classes c ON s.class_id = c.class_id
               WHERE s.first_name LIKE %s OR s.last_name LIKE %s OR s.roll_number LIKE %s
               ORDER BY s.student_id DESC""",
            (f"%{search}%", f"%{search}%", f"%{search}%"),
        )
    else:
        rows = db.query(
            """SELECT s.*, c.class_name FROM students s
               LEFT JOIN classes c ON s.class_id = c.class_id
               ORDER BY s.student_id DESC"""
        )
    return render_template("students.html", students=rows, search=search)


@app.route("/students/add", methods=["GET", "POST"])
@login_required(["admin"])
def add_student():
    classes = db.query("SELECT * FROM classes")
    if request.method == "POST":
        f = request.form
        photo_path = None
        photo = request.files.get("photo")
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            photo.save(photo_path)

        db.query(
            """INSERT INTO students
               (roll_number, first_name, last_name, dob, gender, phone,
                address, class_id, guardian_name, guardian_phone, photo_path)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f["roll_number"], f["first_name"], f["last_name"], f["dob"] or None,
             f["gender"], f["phone"], f["address"], f["class_id"] or None,
             f["guardian_name"], f["guardian_phone"], photo_path),
            commit=True,
        )
        flash("Student added successfully.", "success")
        return redirect(url_for("students_list"))
    return render_template("student_form.html", classes=classes, student=None)


@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
@login_required(["admin"])
def edit_student(student_id):
    classes = db.query("SELECT * FROM classes")
    student = db.query("SELECT * FROM students WHERE student_id=%s", (student_id,), fetchone=True)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("students_list"))

    if request.method == "POST":
        f = request.form
        db.query(
            """UPDATE students SET first_name=%s, last_name=%s, dob=%s, gender=%s,
               phone=%s, address=%s, class_id=%s, guardian_name=%s, guardian_phone=%s
               WHERE student_id=%s""",
            (f["first_name"], f["last_name"], f["dob"] or None, f["gender"],
             f["phone"], f["address"], f["class_id"] or None,
             f["guardian_name"], f["guardian_phone"], student_id),
            commit=True,
        )
        flash("Student updated.", "success")
        return redirect(url_for("students_list"))
    return render_template("student_form.html", classes=classes, student=student)


@app.route("/students/delete/<int:student_id>", methods=["POST"])
@login_required(["admin"])
def delete_student(student_id):
    db.query("DELETE FROM students WHERE student_id=%s", (student_id,), commit=True)
    flash("Student removed.", "info")
    return redirect(url_for("students_list"))


# ------------------------------------------------------------------
# Attendance
# ------------------------------------------------------------------
@app.route("/attendance", methods=["GET", "POST"])
@login_required(["admin", "teacher"])
def attendance():
    classes = db.query("SELECT * FROM classes")
    class_id = request.args.get("class_id") or request.form.get("class_id")
    att_date = request.args.get("date") or request.form.get("date") or str(date.today())
    subject_id = request.args.get("subject_id") or request.form.get("subject_id")

    subjects = db.query("SELECT * FROM subjects WHERE class_id=%s", (class_id,)) if class_id else []

    if request.method == "POST" and subject_id:
        student_ids = request.form.getlist("student_id")
        for sid in student_ids:
            status = request.form.get(f"status_{sid}", "absent")
            db.query(
                """INSERT INTO attendance (student_id, subject_id, attendance_date, status, marked_by)
                   VALUES (%s,%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE status=VALUES(status)""",
                (sid, subject_id, att_date, status, None),
                commit=True,
            )
        flash("Attendance saved.", "success")
        return redirect(url_for("attendance", class_id=class_id, subject_id=subject_id, date=att_date))

    roster = []
    if class_id:
        roster = db.query(
            "SELECT * FROM students WHERE class_id=%s AND status='active' ORDER BY roll_number",
            (class_id,),
        )

    return render_template(
        "attendance.html", classes=classes, subjects=subjects, roster=roster,
        class_id=class_id, subject_id=subject_id, att_date=att_date,
    )


# ------------------------------------------------------------------
# Fees
# ------------------------------------------------------------------
@app.route("/fees")
@login_required(["admin"])
def fees():
    payments = db.query(
        """SELECT fp.*, s.first_name, s.last_name, s.roll_number
           FROM fee_payments fp JOIN students s ON fp.student_id = s.student_id
           ORDER BY fp.payment_date DESC"""
    )
    students = db.query("SELECT student_id, roll_number, first_name, last_name FROM students")
    return render_template("fees.html", payments=payments, students=students)


@app.route("/fees/add", methods=["POST"])
@login_required(["admin"])
def add_payment():
    f = request.form
    db.query(
        """INSERT INTO fee_payments (student_id, amount_paid, payment_mode, remarks)
           VALUES (%s,%s,%s,%s)""",
        (f["student_id"], f["amount_paid"], f["payment_mode"], f.get("remarks", "")),
        commit=True,
    )
    flash("Payment recorded.", "success")
    return redirect(url_for("fees"))


# ------------------------------------------------------------------
# Exams & Marks
# ------------------------------------------------------------------
@app.route("/exams")
@login_required(["admin", "teacher"])
def exams():
    rows = db.query(
        """SELECT e.*, c.class_name FROM exams e
           JOIN classes c ON e.class_id = c.class_id ORDER BY e.exam_date DESC"""
    )
    classes = db.query("SELECT * FROM classes")
    return render_template("exams.html", exams=rows, classes=classes)


@app.route("/exams/add", methods=["POST"])
@login_required(["admin"])
def add_exam():
    f = request.form
    db.query(
        "INSERT INTO exams (exam_name, class_id, exam_date) VALUES (%s,%s,%s)",
        (f["exam_name"], f["class_id"], f["exam_date"]),
        commit=True,
    )
    flash("Exam created.", "success")
    return redirect(url_for("exams"))


@app.route("/exams/<int:exam_id>/marks", methods=["GET", "POST"])
@login_required(["admin", "teacher"])
def enter_marks(exam_id):
    exam = db.query("SELECT * FROM exams WHERE exam_id=%s", (exam_id,), fetchone=True)
    subjects = db.query("SELECT * FROM subjects WHERE class_id=%s", (exam["class_id"],))
    subject_id = request.args.get("subject_id") or request.form.get("subject_id")
    roster = db.query(
        "SELECT * FROM students WHERE class_id=%s AND status='active' ORDER BY roll_number",
        (exam["class_id"],),
    )

    if request.method == "POST" and subject_id:
        for s in roster:
            marks_val = request.form.get(f"marks_{s['student_id']}")
            if marks_val not in (None, ""):
                db.query(
                    """INSERT INTO marks (exam_id, student_id, subject_id, marks_obtained, max_marks)
                       VALUES (%s,%s,%s,%s,%s)
                       ON DUPLICATE KEY UPDATE marks_obtained=VALUES(marks_obtained)""",
                    (exam_id, s["student_id"], subject_id, marks_val, 100),
                    commit=True,
                )
        flash("Marks saved.", "success")
        return redirect(url_for("enter_marks", exam_id=exam_id, subject_id=subject_id))

    return render_template(
        "marks.html", exam=exam, subjects=subjects, roster=roster, subject_id=subject_id
    )


@app.route("/api/student-report/<int:student_id>")
@login_required(["admin", "teacher", "student"])
def student_report(student_id):
    """Return a JSON report card for a student (used by dashboard charts)."""
    marks = db.query(
        """SELECT m.*, sub.subject_name, e.exam_name FROM marks m
           JOIN subjects sub ON m.subject_id = sub.subject_id
           JOIN exams e ON m.exam_id = e.exam_id
           WHERE m.student_id=%s""",
        (student_id,),
    )
    return jsonify(marks)


if __name__ == "__main__":
    app.run(debug=True)
