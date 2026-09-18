"""A tiny SQLite layer for the sample shop."""
import sqlite3


def connect(path=":memory:"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users "
        "(id INTEGER PRIMARY KEY, email TEXT, salt TEXT, password_hash TEXT)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS orders "
        "(id INTEGER PRIMARY KEY, user_id INTEGER, total REAL, status TEXT)"
    )
    return conn


def find_user_by_email(conn, email):
    query = "SELECT * FROM users WHERE email = ?"
    return conn.execute(query, (email,)).fetchone()


def find_order(conn, order_id):
    query = "SELECT * FROM orders WHERE id = ?"
    return conn.execute(query, (order_id,)).fetchone()


def insert_order(conn, user_id, total):
    cursor = conn.execute(
        "INSERT INTO orders (user_id, total, status) VALUES (?, ?, ?)",
        (user_id, total, "new"),
    )
    conn.commit()
    return cursor.lastrowid


def list_orders(conn, user_id, page=1, page_size=10):
    offset = (page - 1) * page_size
    query = "SELECT * FROM orders WHERE user_id = ? ORDER BY id LIMIT ? OFFSET ?"
    return conn.execute(query, (user_id, page_size, offset)).fetchall()
