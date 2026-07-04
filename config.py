import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")

    # MySQL connection settings — override with environment variables in production
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "student_erp")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))

    # Uploads (student photos)
    UPLOAD_FOLDER = os.path.join("static", "uploads")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB
