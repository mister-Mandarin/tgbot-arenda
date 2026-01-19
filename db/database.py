import sqlite3
from pathlib import Path
from services.helpers import LIST_HALLS

DB_PATH = Path("data.sqlite3")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        '''
        Таблица пользователей
        role по плану будет user/admin/manager
        '''
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     BIGINT PRIMARY KEY,
                first_name  TEXT NOT NULL,
                last_name   TEXT,
                phone       TEXT NOT NULL DEFAULT '',
                username    TEXT,
                role        TEXT NOT NULL DEFAULT 'user',
                created_at  TIMESTAMP NOT NULL DEFAULT (datetime('now', '+3 hours')),
                last_update TIMESTAMP NULL DEFAULT (datetime('now', '+3 hours')),
                active      BOOLEAN NOT NULL DEFAULT TRUE
            );
        """)

        '''
        Таблица залов
        alias - уникальное название зала
        '''
        conn.execute("""
            CREATE TABLE IF NOT EXISTS halls (
                alias VARCHAR(50) PRIMARY KEY,
                syncToken TEXT NULL,
                last_update TIMESTAMP NOT NULL DEFAULT (datetime('now', '+3 hours'))    
            );
        """)

        '''Индексы для быстрого поиска'''
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_halls_alias ON halls(alias);
        """)

        halls = [(hall['alias'],) for hall in LIST_HALLS]

        try:
            conn.executemany("""
                INSERT INTO halls (alias) VALUES (?)    
            """, halls)
        except sqlite3.IntegrityError:
            # Если запись уже существует - пропускаем
            pass

        '''
        Записи залов
        ON DELETE CASCADE означает, что если зал удаляется из halls, 
        все связанные с ним события удаляются автоматически.
        '''
        conn.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id TEXT PRIMARY KEY,
                hall_alias VARCHAR(50) NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                FOREIGN KEY (hall_alias) REFERENCES halls(alias) ON DELETE CASCADE
            );
        """)

        '''Тихая миграция'''
        try:
            conn.execute(
                "ALTER TABLE users ADD COLUMN notifications BOOLEAN NOT NULL DEFAULT TRUE;")
        except Exception:
            pass
