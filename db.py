import mysql.connector
from mysql.connector import pooling
from flask import g, current_app

_pool = None


def init_pool(app):
    """Create a MySQL connection pool once, using the app's config."""
    global _pool
    _pool = pooling.MySQLConnectionPool(
        pool_name="erp_pool",
        pool_size=5,
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DB"],
        port=app.config["MYSQL_PORT"],
    )


def get_db():
    """Return a pooled connection stored on Flask's application context `g`."""
    if "db" not in g:
        g.db = _pool.get_connection()
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=None, fetchone=False, commit=False):
    """Run a query and return results as list[dict] (or dict if fetchone)."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or ())
    result = None
    if commit:
        conn.commit()
        result = cursor.lastrowid
    else:
        result = cursor.fetchone() if fetchone else cursor.fetchall()
    cursor.close()
    return result
