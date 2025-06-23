import sqlite3
from pathlib import Path

DB_PATH = Path("data.sqlite3")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     BIGINT PRIMARY KEY,
            first_name  TEXT NOT NULL,
            last_name   TEXT,
            phone       TEXT NOT NULL DEFAULT '',
            username    TEXT,
            role        TEXT NOT NULL DEFAULT 'user',
            created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_update TIMESTAMP NULL,
            active      BOOLEAN NOT NULL DEFAULT TRUE
        );
        """)
