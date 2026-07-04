# Campus ERP — Integrated Student Management System

A full-stack ERP-style web application for managing student records, attendance,
exams/marks, and fee payments — built with **Python (Flask)**, **MySQL**,
**HTML**, **CSS**, and **JavaScript**.

## Features

- 🔐 Role-based login (admin / teacher / student) with hashed passwords
- 🎓 Student management — add, edit, search, delete student records with photo upload
- 🗓 Attendance — mark and store per-subject, per-date attendance for a class
- 📝 Exams & Marks — schedule exams and enter subject-wise marks per student
- 💳 Fees — record and view fee payment history per student
- 📊 Dashboard with live counts (students, teachers, classes, fees collected)
- 📣 Notice board on the dashboard

## Tech Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Backend    | Python 3, Flask                      |
| Database   | MySQL                                |
| Frontend   | HTML5, CSS3, vanilla JavaScript      |
| Templating | Jinja2                               |
| Auth       | Werkzeug password hashing + sessions |

## Project Structure

```
student-erp/
├── app.py                 # Flask application & routes
├── config.py               # App/DB configuration
├── db.py                   # MySQL connection pool + query helper
├── seed.py                 # Creates default admin + sample data
├── requirements.txt
├── database/
│   └── schema.sql          # Full MySQL schema
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   └── uploads/             # Student photo uploads
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── students.html
    ├── student_form.html
    ├── attendance.html
    ├── exams.html
    ├── marks.html
    └── fees.html
```

## Setup Instructions

### 1. Clone / download the project
```bash
git clone <your-repo-url>
cd student-erp
```

### 2. Create a virtual environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create the MySQL database
Make sure MySQL Server is running, then:
```bash
mysql -u root -p < database/schema.sql
```

### 4. Configure database credentials
Either edit `config.py` directly, or set environment variables:
```bash
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=yourpassword
export MYSQL_DB=student_erp
export SECRET_KEY=some-random-secret-string
```

### 5. Seed the default admin account
```bash
python seed.py
```
This creates the login **admin / admin123** plus a sample course, class, and subject.

### 6. Run the app
```bash
python app.py
```
Visit **http://127.0.0.1:5000** and log in with `admin` / `admin123`.

> ⚠️ Change the default admin password and `SECRET_KEY` before deploying anywhere public.

## Uploading This Project to GitHub

From inside the `student-erp` folder:

```bash
git init
git add .
git commit -m "Initial commit: Campus ERP student management system"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

Notes:
- `.gitignore` already excludes `venv/`, `.env`, and uploaded photos, so secrets and
  local junk won't be pushed.
- Never commit real database passwords — use environment variables (see step 4 above)
  or a local `.env` file (excluded from Git) with `python-dotenv`.
- If you renamed the repo folder or are re-initializing, check `git remote -v` to
  confirm the correct remote before pushing.

## Roadmap Ideas (optional extensions)

- Student self-service portal (view own attendance %, marks, fee dues)
- Teacher-specific dashboard filtered to their assigned subjects
- Email/SMS notifications for absentees or fee due dates
- Export attendance/marks/fees reports to PDF or Excel
- REST API layer for a future mobile app

## License

This project is provided as a learning/portfolio template — free to use and modify.
